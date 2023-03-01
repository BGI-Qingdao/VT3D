#!/usr/bin/env python3
import sys
import getopt
from vt3d_tools.obj_wrapper import OBJWrapper
#####################################################
# Usage
#
def formatmesh_usage():
    print("""
Usage : vt3d Auxiliary FormatMesh [options]

Options:
       required options:
            -i <input.mesh>
            -c <coord.json>
            -o <output prefix>

Example of coord.json
{"xmin": 10, "ymin": 20,  "margin": 10, "zmin": 10, "binsize": 2}

(x,y,z) --> ( (x+(xmin/binsize)-margin)*binsize,
              (y+(ymin/binsize)-margin)*binsize,
              (z+(zmin/binsize)-margin)*binsize )

""", flush=True)

#####################################################
# main pipe
#
def formatmesh_main(argv:[]):
    #######################################
    # default parameter value
    infile = ''
    prefix = ''
    conf_json = ''
    try:
        opts, args = getopt.getopt(argv,"hi:o:c:",["help"])
    except getopt.GetoptError:
        formatmesh_usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h' ,'--help'):
            pca3d_usage()
            sys.exit(0)
        elif opt in ("-i"):
            infile = arg
        elif opt in ("-o"):
            prefix = arg
        elif opt in ("-c"):
            conf_json = arg

    # sanity check
    if infile == '' or prefix == '' or conf_json == '':
        formatmesh_usage()
        sys.exit(0)
    meshes = OBJWrapper(conf_json)
    mesh = meshes.load_mesh(infile)
    mesh.toobj(prefix)
