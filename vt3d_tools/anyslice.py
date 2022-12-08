import numpy as np
import pandas as pd
import getopt
import sys
from vt3d_tools.h5ad_wrapper import H5ADWrapper


def anyslice_usage():
    print("""
Usage : vt3d AnySlice [options]

Options:
       required options:
            -i <input.h5ad>
            -o <output prefix>
            --p0 <coordinate of p0>
            --p1 <coordinate of p1>
            --p2 <coordinate of p2>

       optional options:
            --thickness [default 16]
            --spatial_key [default 'spatial3D', the keyname of coordinate array in obsm]
Example:
    > vt3d AnySlice -i in.h5ad -o test --p0 "0,1,0" --p1 "1,0,0" --p2 "1,1,0"
    > ls
    test.h5ad
     
""")

def vector_from_str(vstr):
    a=np.fromstring(vstr,dtype=int, sep=',')
    if a.shape == (3,):
        return True,a
    else:
        return False, []

class Plane:
    def __init__(self,p0,p1,p2):
        self.p0 = p0 
        self.p1 = p1 
        self.p2 = p2 
        self.n = np.cross((p1-p0),(p2-p0))
        norm=np.linalg.norm(self.n)
        if norm == 0 :
            print("Error: invalid norm vector",flush=True)
            sys.exit(1)
        self.n = self.n / norm
    def distance(self, df):
        corrds = df[['x','y','z']].to_numpy()
        corrds = corrds - self.p0
        distances = np.dot(self.n,corrds.T)
        return distances

    def project_coord(self,df,distance):
        corrds = df[['x','y','z']].to_numpy()
        corrds = corrds + (np.tile(self.n,(len(distance),1)) *((-1*distance)[:,None])  )
        df['x'] = corrds[:,0]
        df['y'] = corrds[:,1]
        df['z'] = corrds[:,2]
        return df

def project2D(df):
    from sklearn.decomposition import PCA
    X = df[['x','y','z']].to_numpy()
    pca = PCA(n_components=2)
    X2 = pca.fit_transform(X)
    df['2d_x'] = X2[:,0] 
    df['2d_y'] = X2[:,1]
    return df
   
def anyslice_main(argv:[]):
    ##############################################
    # default parameters
    thickness = 16
    indata = ''
    prefix = ''
    p0 = []
    p1 = []
    p2 = []
    coord_key = 'spatial3D'

    ##############################################
    # parse parameters
    try:
        opts, args = getopt.getopt(argv,"hi:o:",
                                        ["help",
                                         "p0=",
                                         "p1=",
                                         "p2=",
                                "spatial_key=",
                                  "thickness="])
    except getopt.GetoptError:
        anyslice_usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h' ,'--help'):
            anyslice_usage()
            sys.exit(0)
        elif opt in ("-i"):
            indata = arg
        elif opt in ("-o"):
            prefix = arg
        elif opt == "--thinkness" :
            thickness = int(arg)
        elif opt == "spatial_key":
            coord_key = arg
        elif opt == "--p0" :
            _, p0 = vector_from_str(arg)
        elif opt == "--p1" :
            _, p1 = vector_from_str(arg)
        elif opt == "--p2" :
            _, p2 = vector_from_str(arg)
    if indata == '' or prefix == '' or p0 == [] or p1 == [] or p2 == []:
        print('ERROR: parameter imcomplete or invalid')
        anyslice_usage()
        sys.exit(1)
    #load h5ad
    inh5ad = H5ADWrapper(indata)
    #init plane
    plane = Plane(p0,p1,p2)
    #filter cells
    xyzc = inh5ad.getCellXYZC(coord_key,int)
    dist = plane.distance(xyzc)
    xyzc['dist'] = dist
    xyzc['abs_dis'] = np.abs(dist)
    xyzc = xyzc[xyzc['abs_dis'] <= (thickness/2)].copy()
    #project 2D
    new_xyzc = plane.project_coord(xyzc,xyzc['dist'].to_numpy())
    new_xyzc = project2D(new_xyzc)
    #create new h5ad 
    out_h5ad = inh5ad.extract_and_assign2D(new_xyzc['cell'].to_numpy(),new_xyzc[['2d_x','2d_y']].to_numpy())
    out_h5ad.write(f'{prefix}.VT3D.h5ad', compression="gzip")
    return None
