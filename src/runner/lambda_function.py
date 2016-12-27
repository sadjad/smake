#!/usr/bin/env python2

from __future__ import print_function

import tempfile
import os
import boto3
import subprocess as sub
import requests
import traceback

s3_client = boto3.client('s3')

def run_command(command):
    res_code = sub.call(command, shell=True)

    if res_code:
        raise Exception("command failed: {}".format(res_code))

def preprocess(bucket, inputs):
    env_dir = tempfile.mkdtemp()
    os.chdir(env_dir)

    for f in inputs:
        s3_client.download_file(bucket, f, f)

    print(os.listdir())

    return env_dir

def postprocess(bucket, root_dir, outputs):
    for f in outputs:
        s3_client.upload_file(os.path.join(root_dir, f), bucket, f)

def callback(callback_url, job_id, status=0):
    requests.post(callback_url, data={'job_id': job_id, 'status': status})

def handler(event, context):
    job_id = event['job_id']
    callback_url = event['callback_url']
    bucket = event['bucket']
    region = event['region']
    commands_list = event['commands_list']
    inputs = event['inputs']
    outputs = event['outputs']

    try:
        root_dir = preprocess(bucket, inputs)

        for command in commands_list:
            run_command(command)

        postprocess(bucket, root_dir, outputs)
    except Exception as ex:
        callback(callback_url, job_id, 1)
        traceback.print_exc()
    else:
        callback(callback_url, job_id, 0)
