#!/usr/bin/env python2

from __future__ import print_function

import os
import sys
import time
import threading
import argparse
import Queue
import boto3
import graph as makefile_graph
import pylaunch
import json
import traceback
import copy
import pprint

from BaseHTTPServer import HTTPServer
from callback_server import CallbackHandler

s3_client = boto3.client('s3')

condition = threading.Condition()

remaining_targets =  set([])
run_queue = set([])
running_queue = set([])

def get_callback_fn(graph):
    global run_queue, running_queue

    def callback_fn(job_id, status):
        with condition:
            if status != 0:
                print("failed: {} => {}".format(job_id, status), file=sys.stderr)
                sys.exit(1)

            running_queue.discard(job_id)
            remaining_targets.remove(job_id)

            # update the graph and run_queue
            for k, v in graph.items():
                if job_id in v:
                    v.remove(job_id)
                    if len(v) == 0: run_queue.add(k)

    return callback_fn

def create_payload(node, graph, bucket, region, callback_url):
    payload = {
        'job_id': node.target_name,
        'callback_url': callback_url,
        'bucket': bucket,
        'region': region,
        'commands_list': node.commands_list,
        'inputs': list(graph[node.target_name]),
        'outputs': [node.target_name]
    }

    return json.dumps(payload)

def run(graph, nodes, configuration):
    original_graph = copy.deepcopy(graph)

    global run_queue, running_queue
    run_queue = {k for k, v in graph.items() if len(v) == 0}

    output_files = graph['all'].copy()

    # upload already-existing targets to s3
    print("Uploading necessary files to S3...", file=sys.stderr, end='')
    for item in run_queue:
        s3_client.upload_file(item, configuration['bucket'], item)
        print(".", file=sys.stderr, end='')

    rq_copy = run_queue.copy()
    run_queue.clear()
    for item in rq_copy:
        CallbackHandler.callback_fn(item, 0)

    print('done.', file=sys.stderr)

    while len(remaining_targets) > 1:
        with condition:
            payloads = []
            to_remove = set([])

            for r in run_queue:
                if len(running_queue) > configuration.get('max_lambdas', 100):
                    break

                payloads.append(
                    create_payload(
                        nodes[r], original_graph, configuration['bucket'],
                        configuration['regions'][0], configuration['callback_url']
                    )
                )

                running_queue.add(r)
                to_remove.add(r)

            run_queue -= to_remove

        # now it's time to launch fucking Lambdas
        if len(payloads) > 0:
            pylaunch.launchpar(
                len(payloads), configuration['fn_name'],
                configuration['access_key'], configuration['secret_key'],
                payloads, configuration['regions']
            )

        time.sleep(5)

    # download final output files from S3
    print('Downloading output files from S3...', file=sys.stderr, end='')
    for item in output_files:
        s3_client.download_file(configuration['bucket'], item, item)
        print(".", file=sys.stderr, end='')
    print('done.', file=sys.stderr)

def main(data, configuration):
    global remaining_targets

    httpd = None

    try:
        print("Parsing the input...", file=sys.stderr, end='')
        graph, nodes = makefile_graph.build_graph(data)
        remaining_targets = set(nodes.keys())
        print("done.", file=sys.stderr)

        server_addr = "0.0.0.0"
        server_port = 9090

        print("Starting callback server on {addr}:{port}...".format(addr=server_addr, port=server_port),
              file=sys.stderr, end='')
        CallbackHandler.callback_fn = staticmethod(get_callback_fn(graph))
        httpd = HTTPServer((server_addr, server_port), CallbackHandler)
        server_thread = threading.Thread(target=httpd.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        print("done.", file=sys.stderr)

        print("Running jobs on AWS Lambda...", file=sys.stderr)
        run(graph, nodes, configuration)

    except Exception as ex:
        traceback.print_exc()

    finally:
        if httpd:
            httpd.shutdown()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--jobs', '-j', metavar='jobs', dest='jobs', type=int,
                        default=1,
                        help='Maximum number of Lambdas to run simultaneously.')
    parser.add_argument('--callback-server', '-c', metavar='callback_server', dest='callback_server',
                       type=str)
    parser.add_argument('--bucket', '-b', dest='s3_bucket', type=str)
    parser.add_argument('--aws-access-key', '-a', dest='aws_access_key', type=str,
                       default=os.environ.get('AWS_ACCESS_KEY_ID'))
    parser.add_argument('--aws-secrect-key', '-s', dest='aws_secret_key', type=str,
                       default=os.environ.get('AWS_SECRET_ACCESS_KEY'))
    parser.add_argument('--region', '-r', dest='aws_region', type=str,
                       default='us-west-2')
    parser.add_argument('--fn-name', '-f', dest='fn_name', type=str)

    args = parser.parse_args()

    configuration = {
        'bucket': args.s3_bucket,
        'access_key': args.aws_access_key,
        'secret_key': args.aws_secret_key,
        'regions': [args.aws_region],
        'callback_url': 'http://{}/'.format(args.callback_server),
        'fn_name': args.fn_name
    }

    pprint.pprint(configuration)
    main(sys.stdin, configuration)
