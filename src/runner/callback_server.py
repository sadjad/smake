#!/usr/bin/env python2

from __future__ import print_function

import sys
import urlparse

from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler

class CallbackHandler(BaseHTTPRequestHandler):
    callback_fn = None

    def do_POST(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        length = int(self.headers.getheader('content-length'))
        post_data = urlparse.parse_qs(self.rfile.read(length).decode('utf-8'))

        job_id = post_data['job_id'][0]
        status = int(post_data['status'][0])

        if CallbackHandler.callback_fn:
            CallbackHandler.callback_fn(job_id=job_id, status=status)

    def log_message(self, format, *args):
        pass

if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 9000
    httpd = HTTPServer(("", port), CallbackHandler)

    try:
        print("Starting server - 0.0.0.0:{}".format(port))
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass

    httpd.server_close()
