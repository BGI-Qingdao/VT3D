#!/usr/bin/env python3
import os
import sys
import json
import numpy as np

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

class int64_encoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.int64) or isinstance(obj, np.int32):
            return int(obj)
        if isinstance(obj, np.float32) or isinstance(obj, np.float64):
            return float(obj)
        return json.JSONEncoder.default(self, obj)

def savedata2json(data,filename):
    text = json.dumps(data,cls=int64_encoder)
    textfile = open(filename, "w")
    textfile.write(text)
    textfile.close()


