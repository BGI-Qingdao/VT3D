#!/usr/bin/env python3
import sys
import json
import getopt
import numpy as np
import pandas as pd
import anndata as ad
from sklearn.svm import SVC
from sklearn.svm import SVR
from vt3d_tools.h5ad_wrapper import H5ADWrapper
from vt3d_tools.obj_wrapper import OBJWrapper
#####################################################
# Usage:
#
def buildgrids_usage():
    print("""
Usage : vt3d Auxiliary PCA3D [options]

Options:
       required options:
            -i <input.h5ad>
            -o <output prefix>
            -m <mesh.obj>
            -c <conf.json>

Example of conf.json
{
    "spatial_key" : "spatial",
    "annotation" : "clusters",
    "step": 10,
    "genes" : [genename1,genename2]
}
""", flush=True)


#####################################################
# SVM
#
def TrainAndPredict_CellType(train_xyz, train_label, predict_xyz):
    return SVC().fit(train_xyz,train_label).predict(predict_xyz)

def TrainAndPredict_GeneExpression(train_xyz,train_exp,predict_xyz):
    return SVR().fit(train_xyz,train_exp).predict(predict_xyz)

#####################################################
# main pipe
#
def buildgrids_main(argv:[]):
    #######################################
    # default parameter value
    infile = ''
    prefix = ''
    inmesh = ''
    conf_json = ''

    try:
        opts, args = getopt.getopt(argv,"hi:o:m:c:",["help"])
    except getopt.GetoptError:
        buildgrids_usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h' ,'--help'):
            buildgrids_usage()
            sys.exit(0)
        elif opt in ("-i"):
            infile = arg
        elif opt in ("-o"):
            prefix = arg
        elif opt in ("-m"):
            inmesh = arg
        elif opt in ("-c"):
            conf_json = arg

    # sanity check
    if infile == '' or prefix == '' or inmesh == '' or conf_json== '' :
        buildgrids_usage()
        sys.exit(0)

    conf = json.load(open(conf_json))
    inh5ad = H5ADWrapper(infile)
    meshes = OBJWrapper()
    mesh = meshes.load_mesh(inmesh)
    predict_xyz = mesh.grids(conf["step"])
    new_obs = pd.DataFrame()
    new_obs['x'] = new_obs[:,0]
    new_obs['y'] = new_obs[:,1]
    new_obs['z'] = new_obs[:,2]
    new_obs['c'] = np.arange(1,len(new_obs)+1)
    new_obs['c'] = new_obs.apply(lambda row: f'cell_{row["c"]}',axis=1)
    new_obs = new_obs.set_index('c')
    train_xyzc = inh5ad.getBodyXYZA(conf["spatial_key"],float,conf["annotation"])
    train_xyz = train_xyzc[['x','y','z']].to_numpy()
    ###########################################
    # Train celltypes
    id_label = []
    label_id = {}
    for i,l in enumerate(train_label.unique()):
        id_label.append(l)
        label_id[l]=i
    train_xyzc['label'] = train_xyzc.apply( lambda row: label_id[row['anno']],axis=1)
    train_id = train_xyzc['label'].to_numpy()
    predict_id = TrainAndPredict_CellType(train_xyz, train_id, predict_xyz)
    new_obs[conf["annotation"]] = predict_id
    new_obs[conf["annotation"]] = new_obs.apply(lambda row:id_label[row[conf["annotation"]]],axis=1)
    ###########################################
    # Train genes
    gene_exp = []
    for gene in conf["genes"]:
        train_exp = inh5ad.getGeneExp(gene)
        predict_exp = TrainAndPredict_GeneExpression(train_xyz, train_exp, predict_xyz)
        gene_exp.append(predict_exp)

    ###########################################
    # Construct h5ad
    matrix = np.hstack(gene_exp)
    adata = ad.AnnData(sparse.csr_matrix(matrix),dtype='float32')
    adata.obs = new_obs
    adata.var_names =  data.columns.to_list()
    adata.obsm[conf["spatial_key"]] = new_obs[['x','y','z']].to_numpy()
    adata.write(f'{prefix}.h5ad',compression='gzip')

