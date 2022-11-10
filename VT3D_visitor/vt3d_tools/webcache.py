#!/usr/bin/env python3
import os
import sys
import json
import getopt
import numpy as np
import pandas as pd
from vt3d_tools.h5ad_wrapper import H5ADWrapper

def create_folder(foldername):
    try:
        os.mkdir(foldername)
        print(f'create {foldername} ....')
    except FileExistsError:
        print(f'cache folder -- {foldername} already exists, reuse it now....')

def savedic2json(data,filename):
    json.dumps(data)
    textfile = open(filename, "w")
    textfile.write(textfile)
    textfile.close()
    
#####################################################
# Usage
#
def webcache_usage():
    print("""
Usage : vt3d_visitor WebCache [options]

Options:
       required options:
            -i <input.h5ad>
            -c <conf.json>
            -o [output prefix, default webcace]
Example:
        > vt3d_visitor WebCache -i in.h5ad -c atlas.json
        > cat atlas.json
        {
            "Coordinate" : 'coord3d',
            "Annotatinos" : ["lineage"],
            "Meshes" : [
                "gut" : "gut.obj",
                "nueral" : "nueral.obj",
                "pharynx" : "pharynx.obj"
            ],
            "Genes" : [
               "SMED30033583",
               "SMED30011277",
       ... genes you want to display ...
               "SMED30031463",
               "SMED30033839",
            ]
        }

Notice:
    The most time-consumptional and disk-cost part is the Genes data.
      The more genes you need, the more time of this action and 
           the more disk space of atlas cache folder will cost.

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
        +---Mesh
             +---gut.json
             +---neural.json
             +---pharynx.json
        +---summary.json
        +---gene.json
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
    for meshfile in len(confdata['Meshes']):
        if not os.path.isfile(meshfile):
            print(f'Error: invalid mesh :{meshfile}!' ,flush=True)
            sys.exit(3)
        
    #######################################
    # load h5ad and sanity check
    inh5ad = H5ADWrapper(inh5data)
    for annokey in confdata['Annotatinos']:
        if not inh5ad.hasAnno(annokey):
            print(f'Error: invalid Annotatino :{annokey}!' ,flush=True)
            sys.exit(3)
    for genename in confdata['Genes']:
        if not inh5ad.hasGene(genename):
            print(f'Error: invalid Annotatino :{annokey}!' ,flush=True)
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
    create_folder(f'{prefix}/Mesh')
    #######################################
    # generate summary and gene json
    summary = inh5ad.getSummary(confdata['Annotatinos'] , confdata['Genes'])
    savedic2json(summary, f'{prefix}/summary.json')      
    #######################################
    # generate annotation json

    #######################################
    # generate mesh json

    #######################################
    # generate gene json

