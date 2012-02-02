#!/usr/bin/env python

import sys
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from email import message_from_file
from email.generator import Generator

f = open(sys.argv[1], 'r')
response = message_from_file(f)
f.close()

print >> sys.stdout, "Will send the following response:\n"
Generator(sys.stdout).flatten(response)

status_code, status_msg = response['Status'].split(None, 1)
status_code = int(status_code)
del response['Status']

# Handle headers ourselves: just do nothing (they're emitted by the request-handler's send_header)
response._write_headers = lambda *a,**kw: None

class AsisHTTPRequestHandler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        self.do_HEAD()
        Generator(self.wfile).flatten(response)
    
    def do_HEAD(self):
        print >> sys.stdout, self.raw_requestline, self.headers
        self.send_response(status_code, status_msg)
        for k,v in response.items():
            self.send_header(k, v)
        self.end_headers()

HTTPServer(('', 8888), AsisHTTPRequestHandler).serve_forever()
