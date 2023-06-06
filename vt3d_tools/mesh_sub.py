#!/usr/bin/env python3
import sys
import getopt
from vt3d_tools.h5ad_wrapper import H5ADWrapper
from vt3d_tools.obj_wrapper import OBJWrapper

#####################################################
# Usage
#
def meshsub_usage():
    print("""
Usage : vt3d Auxiliary MeshSub [options]

Require:
    pip install trimesh
Options:
       required options:
            -i <input.h5ad>
            -m <mesh.obj>
            -o <output.h5ad>
            --spatial_key [default 'spatial3D', the keyname of coordinate in obsm]

""", flush=True)

#####################################################
# main pipe
#
def meshsub_main(argv:[]):
    #######################################
    # default parameter value
    infile = ''
    inmesh = ''
    outfile = ''
    spatial_key = 'spatial3D'
    try:
        opts, args = getopt.getopt(argv,"hi:m:o:",["help",
                                                   "spatial_key=",])
    except getopt.GetoptError:
        meshsub_usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h' ,'--help'):
            meshsub_usage()
            sys.exit(0)
        elif opt in ("-i"):
            infile = arg
        elif opt in ("-m"):
            inmesh = arg
        elif opt in ("-o"):
            outfile = arg
        elif opt in ("--spatial_key"):
            spatial_key = arg

    # sanity check
    if infile == '' or inmesh == '' or outfile == '' or spatial_key == '':
        meshsub_usage()
        sys.exit(0)
    # load datas
    inh5ad = H5ADWrapper(infile)
    xyz = inh5ad.getBodyXYZ(spatial_key,float).to_numpy()
    mesh = trimesh.load(inmesh)
    # get filter array
    ret = []
    for i in range(xyz):
        ct = mesh.contains([p])
        ret.append(ct[0])
    retdata = inh5ad.data[ret,:]
    retdata.write(outfile,compression='gzip')
