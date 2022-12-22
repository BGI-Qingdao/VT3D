#!/usr/bin/env python3
import sys
import json
import getopt
import numpy as np
import pandas as pd
from skimage import io
from vt3d_tools.h5ad_wrapper import H5ADWrapper

def savedata2json(data,filename):
    text = json.dumps(data)
    textfile = open(filename, "w")
    textfile.write(text)
    textfile.close()

#####################################################
# Usage
#
def grayscaletif_usage():
    print("""
Usage : vt3d Auxiliary GrayScaleTIF [options]

Options:
       required options:
            -i <input.h5ad>
            -o <output prefix>
            -c <conf.json>
            --spatial_key [default 'spatial3D', the keyname of coordinate array in obsm]
Example:
        > vt3d Auxiliary GrayScaleTIF -i in.h5ad -o test -c organ.json
        > cat organ.json
        {
            "binsize" : 10,
            "margin" : 10,
            "keyname" : "annotation",
            "targets": [
                "all",
                "Gut",
                "Pharynx"
                "Neural",
            ],
            "grayvalue": [
                50,
                100,
                150,
                200
            ]
        }
""", flush=True)

class RectBoundary:
    def __init__(self, xmin,xmax,ymin,ymax,margin=10):
        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax
        self.margin = margin

    def W(self,binsize):
        return self.xmax//binsize-self.xmin//binsize + 1 + 2 * self.margin

    def H(self,binsize):
        return self.ymax//binsize-self.ymin//binsize + 1 + 2 * self.margin
 
    def fmtX(self,xya,binsize):
        xya['x'] = xya['x'] // binsize
        xya['x'] = xya['x'] - self.xmin//binsize
        xya['x'] = xya['x'] + self.margin
        xya['x'] = xya['x'].astype(int)
        return xya

    def fmtY(self,xya,binsize):
        xya['y'] = xya['y'] // binsize
        xya['y'] = xya['y'] - self.ymin//binsize
        xya['y'] = xya['y'] + self.margin
        xya['y'] = xya['y'].astype(int)
        return xya

def Slice2TIF(xya, rect, binsize, targets, grayvalues):
    width = rect.W(binsize)   
    height = rect.H(binsize)
    xya = rect.fmtX(xya,binsize)
    xya = rect.fmtY(xya,binsize)
    canvas = np.zeros((height,width),dtype='uint8')
    for i,target in enumerate(targets):
        gray = grayvalues[i]
        if target == 'all':
            thisct = xya
        else:
            thisct = xya[xya['anno']==target]
        if thisct.empty:
            continue
        ypos = thisct['y'].to_numpy()
        xpos = thisct['x'].to_numpy()
        canvas[ypos,xpos] = gray
    return canvas

class Bin3D:
    def __init__(self, xyza , binsize=10,margin=10):
        self.basedata = xyza
        self.binsize = binsize
        self.margin = margin

    def getRect(self):
        xmin = np.min(self.basedata['x'])
        xmax = np.max(self.basedata['x'])
        ymin = np.min(self.basedata['y'])
        ymax = np.max(self.basedata['y'])
        return RectBoundary(xmin,xmax,ymin,ymax,self.margin)

    def binz(self):
        self.zmin = np.min(self.basedata['z'])
        self.zmax = np.max(self.basedata['z'])
        self.basedata['z'] = self.basedata['z'] / self.binsize
        self.basedata['z'] = self.basedata['z'].astype(int)
        zmin = np.min(self.basedata['z'])
        zmax = np.max(self.basedata['z'])
        ret_list = []
        for i in range(zmin,zmax+1,1):
            tmpslice = self.basedata[self.basedata['z'] == i].copy()
            ret_list.append(tmpslice)
        return ret_list

    def ToTIFF(self,targets,grayvalues):
        self.rect = self.getRect()
        slices = self.binz()
        width = self.rect.W(self.binsize)   
        height = self.rect.H(self.binsize)
        canvas = np.zeros( (len(slices),height,width) , dtype='uint8' )
        for i,tmp_slice in enumerate(slices):
            tmp_canvas = Slice2TIF(tmp_slice, self.rect, self.binsize, targets, grayvalues)
            canvas[i,:,:] = tmp_canvas
        return canvas
    def save_coordconf(self,filename):
        conf = {}
        conf['xmin'] = self.rect.xmin  
        conf['ymin'] = self.rect.ymin  
        conf['xmax'] = self.rect.xmax  
        conf['ymax'] = self.rect.ymax
        conf['margin'] = self.rect.margin
        conf['zmin'] = self.zmin 
        conf['zmax'] = self.zmax
        conf['binsize'] = self.binsize
        savedata2json(conf,filename)
#####################################################
# main pipe
#
def grayscaletif_main(argv:[]):
    #######################################
    # default parameter value
    inh5data = ''
    prefix = ''
    conf_file = ''
    coord_key = 'spatial3D'

    try:
        opts, args = getopt.getopt(argv,"hi:o:c:",["spatial_key=","help"])
    except getopt.GetoptError:
        grayscaletif_usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h' ,'--help'):
            grayscaletif_usage()
            sys.exit(0)
        elif opt in ("-o"):
            prefix = arg
        elif opt in ("--spatial_key"):
            coord_key = arg
        elif opt in ("-i"):
            inh5data = arg
        elif opt in ("-c",):
            conf_file = arg

    if inh5data == "" or prefix == ""  or conf_file == "":
        print("Error: incomplete parameters",flush=True)
        grayscaletif_usage()
        sys.exit(1)

    # load conf
    confdata = json.load(open(conf_file))
    # sanity check
    if (not 'binsize' in confdata) \
         or (not 'keyname' in confdata) \
         or (not 'targets' in confdata) \
         or (not 'grayvalue' in confdata) :
        print('Error: incomplete conf.json, please copy from usage!',flush=True)
        sys.exit(3)
    if int(confdata['binsize']) < 1:
        print('Error: too small binsize !',flush=True)
        sys.exit(3)
    if int(confdata['margin']) < 0:
        print('Error: too small margin!',flush=True)
        sys.exit(3)
    if int(confdata['binsize']) < 10:
        print('Warning: small binsize will generate huge tiff file with too much backgroud !',flush=True)
    if confdata['keyname'] == '' :
        print('Error: too small binsize !',flush=True)
        sys.exit(3)
    if len(confdata['targets'])<1 or len(confdata['grayvalue'])<1:
        print('Error: not targets or grayvalue in conf.json!',flush=True)       
        sys.exit(3)
    if len(confdata['targets']) != len(confdata['grayvalue']):
        print('Error: number of targets must be equal to number of grayvalue in conf.json!',flush=True)       
        sys.exit(3)
    #load h5ad 
    inh5ad = H5ADWrapper(inh5data)
    if not inh5ad.hasAnno(confdata['keyname']):
        print('Error: invalid keyname !',flush=True)       
        sys.exit(3)
    xyza = inh5ad.getCellXYZA(coord_key,int,confdata['keyname'])
    bin3d = Bin3D(xyza,int(confdata['binsize']),int(confdata['margin']))
    tiff3d = bin3d.ToTIFF(confdata['targets'],confdata['grayvalue'])
    io.imsave(f'{prefix}.tif',tiff3d)
    bin3d.save_coordconf(f'{prefix}.coord.json')

#####################################################
if __name__ == '__main__':
    grayscaletif_main(sys.argv[1:])
