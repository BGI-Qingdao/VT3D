#!/usr/bin/env python3
import sys
import json
import getopt
from sklearn.decomposition import PCA
from vt3d_tools.h5ad_wrapper import H5ADWrapper
from vt3d_tools.obj_wrapper import OBJWrapper
#####################################################
# Usage
#
def pca3d_usage():
    print("""
Usage : vt3d Auxiliary PCA3D [options]

Options:
       required options:
            -i <input.h5ad>
            -o <output prefix>
            --spatial_key [default 'spatial3D', the keyname of coordinate in obsm]
            --model_json [default None, the model.json]

Notice: data is priceless, no replace mode supported! 

Example of model.json
{
    "Meshes" : {
        "body" : "example_data/body.obj" ,
        "gut" : "example_data/gut.obj"     ,
        "nueral" : "example_data/neural.obj" ,
        "pharynx" : "example_data/pharynx.obj"
    },
    "mesh_coord" : "example_data/WT.coord.json"
}
""", flush=True)

#####################################################
# main pipe
#
def pca3d_main(argv:[]):
    #######################################
    # default parameter value
    infile = ''
    prefix = ''
    spatial_key = 'spatial3D'
    model_json = ''
    try:
        opts, args = getopt.getopt(argv,"hi:o:",["help","spatial_key=","model_json="])
    except getopt.GetoptError:
        pca3d_usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h' ,'--help'):
            pca3d_usage()
            sys.exit(0)
        elif opt in ("-i"):
            infile = arg
        elif opt in ("-o"):
            prefix = arg
        elif opt in ("--spatial_key"):
            spatial_key = arg
        elif opt in ("--model_json"):
            model_json = arg

    # sanity check
    if infile == '' or prefix == '' or spatial_key == '':
        pca3d_usage()
        sys.exit(0)
    # run pca
    inh5ad = H5ADWrapper(infile)
    xyz = inh5ad.getBodyXYZ(spatial_key,float)
    pca = PCA(n_components=3)
    pca.fit(xyz)
    X2 = pca.transform(xyz)
    inh5ad.setXYZ(spatial_key,X2)
    inh5ad.data.write(f'{prefix}.h5ad', compression="gzip")
    if model_json != '':
        confdata = json.load(open(model_json))
        if len(confdata['Meshes'])>1:
            coord_file = confdata['mesh_coord']
            meshes = OBJWrapper(coord_file)
            for meshname in confdata['Meshes']:
                meshes.add_mesh(meshname,confdata['Meshes'][meshname])
            meshes.fitpca(pca)
            meshes.toobj(prefix)
