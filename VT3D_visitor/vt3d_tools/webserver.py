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
Usage : vt3d_visitor WebServer [options]

Options:
            -p [port, default 8050]
Example:
        > vt3d_visitor WebServer 
        
        ...
        never stop until you press Ctrl-C
""", flush=True)

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
    server_address = ('', 8050)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    httpd.serve_forever()
