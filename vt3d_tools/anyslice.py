import numpy as np
import pandas as pd
import getopt
import sys
#import seaborn as sns
#import matplotlib.pyplot as plt
from vt3d_tools.h5ad_wrapper import H5ADWrapper
from sklearn.decomposition import PCA


#def draw2DAnno(prefix, xy, anno):
#    tmp = pd.DataFrame()
#    tmp['v_spatial_x'] = xy[:,0] 
#    tmp['v_spatial_y'] = xy[:,1] 
#    tmp['anno'] = anno.to_list()
#    W = tmp['v_spatial_x'].max() -  tmp['v_spatial_x'].min()+1
#    H = tmp['v_spatial_y'].max() -  tmp['v_spatial_y'].min()+1
#    plt.figure(figsize=((W/72.0)*12.5,(H/72.0)*11.0))
#    sns.scatterplot(data=tmp, x="v_spatial_x", y="v_spatial_y",palette='tab20',hue="anno",legend='full')
#    plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0)
#    plt.subplots_adjust(top=0.95,left=0.05,bottom=0.05,right=0.80)
#    plt.savefig(f'{prefix}.anno.pdf',dpi=72)
#    plt.close()

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
            --slice_num [default 1]
            --slice_step [default equal to thickness]
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
    X = df[['x','y','z']].to_numpy()
    pca = PCA(n_components=2)
    X2 = pca.fit_transform(X)
    df['2d_x'] = X2[:,0] 
    df['2d_y'] = X2[:,1]
    return df, pca

def project2DBy(df,pca):
    X = df[['x','y','z']].to_numpy()
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
    num_of_slices = 1
    slice_gap = thickness
    slice_gap_custom = 0
    #anno_key = 'annotation'
    ##############################################
    # parse parameters
    try:
        opts, args = getopt.getopt(argv,"hi:o:",
                                        ["help",
                                         "p0=",
                                         "p1=",
                                         "p2=",
                                "spatial_key=",
                                  "slice_num=",
                                 "slice_step=",
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
        elif opt == "--thickness" :
            thickness = float(arg)
        elif opt == "--slice_num":
            num_of_slices = int(arg)
        elif opt == "--slice_step":
            slice_gap = float(arg)
            slice_gap_custom=1
        elif opt == "--spatial_key":
            coord_key = arg
        elif opt == "--p0" :
            _, p0 = vector_from_str(arg)
        elif opt == "--p1" :
            _, p1 = vector_from_str(arg)
        elif opt == "--p2" :
            _, p2 = vector_from_str(arg)
    if slice_gap_custom == 0 :
        slice_gap = thickness
    if num_of_slices <1 or indata == '' or prefix == '' or p0 == [] or p1 == [] or p2 == []:
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
    print(thickness/2,flush=True)
    if num_of_slices == 1 :
        xyzc = xyzc[xyzc['abs_dis'] <= (thickness/2)].copy()
        #project 2D
        new_xyzc = plane.project_coord(xyzc,xyzc['dist'].to_numpy())
        new_xyzc = project2D(new_xyzc)
        #create new h5ad 
        out_h5ad = inh5ad.extract_and_assign2D(new_xyzc['cell'].to_numpy(),new_xyzc[['2d_x','2d_y']].to_numpy())
        #draw2DAnno(prefix,new_xyzc[['2d_x','2d_y']].to_numpy(),out_h5ad.obs[anno_key])
        out_h5ad.write(f'{prefix}.h5ad', compression="gzip")
    else:
        slice_keys = [0]
        for i in range(1,num_of_slices*5):
            slice_keys.append(i)
            slice_keys.append(i*-1)
        ret_xyzc = []
        curr_key_id=0
        for i in range(num_of_slices):
            while curr_key_id < len(slice_keys):
                curr_key = slice_keys[curr_key_id]
                curr_slice_center = curr_key * slice_gap
                curr_dist_from = curr_slice_center - thickness/2
                curr_dist_to =  curr_slice_center + thickness/2
                slice_xyzc = xyzc[ ( ( xyzc['dist'] >= curr_dist_from ) & ( xyzc['dist'] <  curr_dist_to ) ) ].copy()
                if slice_xyzc.empty or len(slice_xyzc)<1:
                    if curr_key == 0 :
                        print("FATAL: the assgned panel is not interset with any cell. exit...")
                        sys.exit(111)
                    curr_key_id = curr_key_id + 1
                    continue
                new_xyzc = plane.project_coord(slice_xyzc,slice_xyzc['dist'].to_numpy())
                if curr_key == 0 :
                    new_xyzc, pca = project2D(new_xyzc)
                else:
                    new_xyzc = project2DBy(new_xyzc,pca)
                new_xyzc['vsid'] = [curr_key]*len(new_xyzc)
                print(f"sid: {curr_key} from [{curr_dist_from}, {curr_dist_to}) with #cell {len(new_xyzc)}",flush=True)
                ret_xyzc.append(new_xyzc)
                curr_key_id = curr_key_id + 1
                break
        all_new_xyzc = pd.concat(ret_xyzc,ignore_index=True)
        out_h5ad = inh5ad.extract_and_assign2D(all_new_xyzc['cell'].to_numpy(),all_new_xyzc[['2d_x','2d_y']].to_numpy())
        out_h5ad.obs['vsid'] = all_new_xyzc['vsid'].to_numpy()
        out_h5ad.write(f'{prefix}.h5ad', compression="gzip")
    return None
