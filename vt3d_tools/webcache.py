#!/usr/bin/env python3
import os
import sys
import shutil
import json
import getopt
import numpy as np
import pandas as pd
from vt3d_tools.h5ad_wrapper import H5ADWrapper
from vt3d_tools.obj_wrapper import OBJWrapper

def check_file(filename):
    if not os.path.isfile(filename):
        print(f'Error: invalid input file :{filename}!' ,flush=True)
        sys.exit(3)

def create_folder(foldername):
    try:
        os.mkdir(foldername)
        print(f'create {foldername} ....')
    except FileExistsError:
        print(f'cache folder -- {foldername} already exists, reuse it now....')

def savedata2json(data,filename):
    text = json.dumps(data)
    textfile = open(filename, "w")
    textfile.write(text)
    textfile.close()
    
#####################################################
# Usage
#
def webcache_usage():
    print("""
Usage : vt3d WebCache [options]

Options:
       required options:
            -i <input.h5ad>
            -c <conf.json>
            -o [output prefix, default webcace]
Example:
        > vt3d WebCache -i in.h5ad -c atlas.json
        > cat atlas.json
        {
            "Coordinate" : "coord3D",
            "Annotatinos" : [ "lineage" ],
            "Meshes" : {
                "body" : "example_data/body.obj" ,
                "gut" : "example_data/gut.obj"     ,
                "nueral" : "example_data/neural.obj" ,
                "pharynx" : "example_data/pharynx.obj"
            },
            "mesh_coord" : "example_data/WT.coord.json",
            "Genes" : [
               "SMED30033583" ,
               "SMED30011277" ,
       ... genes you want to display ...
               "SMED30031463" ,
               "SMED30033839"
            ]
        }

Notice:
     Set "Genes" : ["all"] to export all genes in var.

The structure of output atlas folder:
      webcache
        +---Anno
             +---lineage.json
        +---Gene
             +---SMED30033583.json
             +---SMED30011277.json
             ...
             +---SMED30031463.json
             +---SMED30033839.json
        +---summary.json
        +---gene.json
        +---meshes.json
""", flush=True)

#####################################################
# main pipe
#
def webcache_main(argv:[]):
    #######################################
    # default parameter value
    inh5data = ''
    conf_file = ''
    prefix = 'webcache'

    try:
        opts, args = getopt.getopt(argv,"hi:o:c:",["help"])
    except getopt.GetoptError:
        webcache_usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h' ,'--help'):
            webcache_usage()
            sys.exit(0)
        elif opt in ("-o"):
            prefix = arg
        elif opt in ("-i"):
            inh5data = arg
        elif opt in ("-c"):
            conf_file = arg

    #######################################
    # sanity check
    if inh5data == '' or prefix == '' or conf_file == '':
        print('Error: incomplete parameters, exit ...')
        webcache_usage()
        sys.exit(2)
        
    #######################################
    # load conf json and sanity check
    confdata = json.load(open(conf_file))
    # sanity check
    if (not 'Coordinate' in confdata) \
         or (not 'Annotatinos' in confdata) \
         or (not 'Meshes' in confdata) \
         or (not 'Genes' in confdata) :
        print('Error: incomplete conf.json, please copy from usage!',flush=True)
        sys.exit(3)
    if len(confdata['Annotatinos']) <1 and len(confdata['Genes']) < 1 and len(confdata['Meshes']) <1:
        print('Error: nothing to show! exit ...',flush=True)
        sys.exit(4)
    for meshkey in confdata['Meshes']:
        if not 'mesh_coord' in  confdata:
            print('Error: no mesh_coord exit ...',flush=True)
            sys.exit(4)
        meshfile = confdata['Meshes'][meshkey]
        check_file(confdata['mesh_coord'])
        check_file(meshfile)
        
    #######################################
    # load h5ad and sanity check
    inh5ad = H5ADWrapper(inh5data)
    for annokey in confdata['Annotatinos']:
        if not inh5ad.hasAnno(annokey):
            print(f'Error: invalid Annotatino :{annokey}!' ,flush=True)
            sys.exit(3)
    if "all" in confdata['Genes']:
        confdata['Genes'] = inh5ad.AllGenesList()
    else :
        for genename in confdata['Genes']:
            if not inh5ad.hasGene(genename):
                print(f'Error: invalid gene :{genename}!' ,flush=True)
                sys.exit(3)
    if not inh5ad.hasCoord(confdata['Coordinate']):
        print(f'Error: invalid Coordinate :{confdata["Coordinate"]}!' ,flush=True)
        sys.exit(3)  

    #######################################
    # load objs
        
    #######################################
    # create main folder, summary.json gene.json
    create_folder(f'{prefix}')
    create_folder(f'{prefix}/Anno')
    create_folder(f'{prefix}/Gene')
    #######################################
    # generate summary and gene json
    summary = inh5ad.getSummary(confdata['Coordinate'] ,confdata['Annotatinos'] , confdata['Genes'])
    savedata2json(summary, f'{prefix}/summary.json')      
    savedata2json(confdata['Genes'],f'{prefix}/gene.json')
    #######################################
    # generate annotation json
    for anno in confdata['Annotatinos']:
        xyza = inh5ad.getCellXYZA(confdata['Coordinate'],int,anno)
        mapper = summary['annomapper'][f'{anno}_legend2int']
        xyza['annoid'] = xyza.apply(lambda row : mapper[row['anno']],axis=1)
        savedata2json(xyza[['x','y','z','annoid']].to_numpy().tolist(),f'{prefix}/Anno/{anno}.json')
    #######################################
    # generate mesh json
    coord_file = confdata['mesh_coord']
    meshes = OBJWrapper(coord_file)
    for meshname in confdata['Meshes']:
        meshes.add_mesh(meshname,confdata['Meshes'][meshname]) 
    savedata2json(meshes.get_data(),f'{prefix}/meshes.json')
    #######################################
    # generate gene json
    for gene in confdata['Genes']:
        xyze = inh5ad.getGeneXYZE(gene,0,confdata['Coordinate'],int)
        savedata2json(xyze.to_numpy().tolist(),f'{prefix}/Gene/{gene}.json')
    #######################################
    # cp html and js
    base=os.path.dirname(os.path.realpath(__file__))
    base=f'{base}/../vt3d_browser'
    flist = [  '6f0a76321d30f3c8120915e57f7bd77e.ttf',
               'index.html',
               'index.js',
               'index.js.map',
               'manifest.js',
               'manifest.js.map',
               'vendor.js',
               'vendor.js.map',]
    for xx in flist:
        shutil.copyfile(f'{base}/{xx}', f'{prefix}/{xx}')

