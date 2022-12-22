#!/usr/bin/env python3
import sys
import getopt
import json
from http.server import *
#####################################################
# Usage
#
def webserver_usage():
    print("""
Usage : vt3d AtlasBrowser LaunchAtlas [options]

Options:
            -p [port, default 80]
Example:
        > vt3d WebServer 
        
        ...
        never stop until you press Ctrl-C
""", flush=True)

class CORSRequestHandler (SimpleHTTPRequestHandler):
    def end_headers (self):
        self.send_header('Access-Control-Allow-Origin', '*')
        SimpleHTTPRequestHandler.end_headers(self)
#####################################################
# main pipe
#
def webserver_main(argv:[]):
    #######################################
    # default parameter value
    port = 8050

    try:
        opts, args = getopt.getopt(argv,"hp:",["help"])
    except getopt.GetoptError:
        webserver_usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h' ,'--help'):
            webserver_usage()
            sys.exit(0)
        elif opt in ("-p"):
            port = int(arg)

    # sanity check
    # run server
    print(f'server run in port {port} now ...')
    server_address = ('', port)
    httpd = HTTPServer(server_address, CORSRequestHandler)
    httpd.serve_forever()
