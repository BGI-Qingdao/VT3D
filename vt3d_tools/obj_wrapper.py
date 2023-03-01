import json
import numpy as np
import pandas as pd
#from vt3d_tools.is_inside_mesh import IsPointsInsideMesh
class Mesh:
    def __init__(self,vs,fs):
        self.vectors = vs.to_numpy()
        self.faces = fs.to_numpy()
        self.xmin = vs['x'].min();
        self.xmax = vs['x'].max();
        self.ymin = vs['y'].min();
        self.ymax = vs['y'].max();
        self.zmin = vs['z'].min();
        self.zmax = vs['z'].max();

    def toobj(self,prefix):
        vs = pd.DataFrame()
        vs['x'] = self.vectors[:,0]
        vs['y'] = self.vectors[:,1]
        vs['z'] = self.vectors[:,2]
        vs['t'] = 'v'
        fs = pd.DataFrame()
        fs['x'] = self.faces[:,0]
        fs['x'] = fs['x']+1
        fs['y'] = self.faces[:,1]
        fs['y'] = fs['y']+1
        fs['z'] = self.faces[:,2]
        fs['z'] = fs['z']+1
        fs['t'] = 'f'
        dt = pd.concat([vs,fs],ignore_index=True)
        dt = dt[['t','x','y','z']]
        dt.to_csv(f'{prefix}.obj',sep=' ',header=False,index=False)

    def totriangles(self):
        tris = []
        for i in range(self.faces.shape[0]):
            v1i = self.faces[i,0]
            v2i = self.faces[i,1]
            v3i = self.faces[i,2]
            tri = self.vectors[[v1i,v2i,v3i],:]
            tris.append(tris)
        return np.array(tris)

    def grids(self,step=10):
        # create grids
        xn = int((self.xmax-self.xmin+1)//step)
        yn = int((self.ymax-self.ymin+1)//step)
        zn = int((self.zmax-self.zmin+1)//step)
        x = np.linspace(self.xmin,self.xmax,xn)
        y = np.linspace(self.ymin,self.ymax,yn)
        z = np.linspace(self.zmin,self.zmax,zn)
        xv, yv, zv = np.meshgrid(x, y, z)
        ret = pd.DataFrame()
        ret['x'] = xv.reshape(-1)
        ret['y'] = yv.reshape(-1)
        ret['z'] = zv.reshape(-1)
        print(f'check point in mesh {len(ret)} ',flush=True)
        print(f'check point in mesh {ret.shape} ',flush=True)

        # modify based on codes from spateo
        from scipy.spatial import ConvexHull, Delaunay, cKDTree
        hull = ConvexHull(self.vectors)
        hull = hull.points[hull.vertices, :]
        if not isinstance(hull, Delaunay):
            hull = Delaunay(hull)
        res = hull.find_simplex(ret.to_numpy()) >= 0
        ret['in_hull'] = res
        ret  = ret [ ret['in_hull'] ][['x','y','z']].copy()
        #ret = ret[IsPointsInsideMesh(self.totriangles(), ret.to_numpy())].copy()
        print(f'check point in mesh {len(ret)} ',flush=True)
        print(f'check point in mesh {ret.shape} ',flush=True)
        print(f'check point in mesh done',flush=True)
        return ret.to_numpy()

class OBJWrapper:
    def __init__(self,coordfile=None):
        self.data = [[],[],[]] # legend, vector, faces
        if coordfile != None:
            self.init_coord(coordfile)
        else:
            self.xmin = 0
            self.ymin = 0
            self.zmin = 0
            self.margin = 0
            self.binsize = 1
            self.x_shift = 0
            self.y_shift = 0
        self.mesh_xmin = 0
        self.mesh_xmax = 0
        self.mesh_ymin = 0
        self.mesh_ymax = 0
        self.mesh_zmin = 0
        self.mesh_zmax = 0
        self.x_shift = 0 
        self.y_shift = 0
        self.binsize = 1

    def init_coord(self,coordfile):
        confdata = json.load(open(coordfile))
        self.xmin = confdata['xmin']
        self.ymin = confdata['ymin']
        self.zmin = confdata['zmin']
        self.margin = confdata['margin']
        self.binsize = confdata['binsize']
        self.x_shift = self.xmin//self.binsize - self.margin
        self.y_shift = self.ymin//self.binsize - self.margin

    def reset_coord(self, vectors):
        vectors = vectors.astype(float)
        vectors['x'] = vectors['x'] + self.x_shift
        vectors['y'] = vectors['y'] + self.y_shift
        vectors['x'] = vectors['x'] * self.binsize
        vectors['y'] = vectors['y'] * self.binsize
        vectors['z'] = vectors['z'] * self.binsize
        vectors['z'] = vectors['z'] + self.zmin 
        return vectors

    def load_mesh(self, objfile):
        cache = pd.read_csv(objfile, sep='\s+',header=None, compression='infer', comment='#',low_memory=False)
        cache.columns = ['type','v1','v2','v3']
        vectors = cache[cache['type'] == 'v'].copy()
        vectors = vectors[['v1','v2','v3']].copy()
        vectors.columns = ['x','y','z']
        vectors = self.reset_coord(vectors)
        faces = cache[cache['type'] == 'f'].copy()
        if faces.dtypes['v1'] == object:
            faces['i'] = faces.apply(lambda row: int(row['v1'].split('/')[0])-1, axis=1)
            faces['j'] = faces.apply(lambda row: int(row['v2'].split('/')[0])-1, axis=1)
            faces['k'] = faces.apply(lambda row: int(row['v3'].split('/')[0])-1, axis=1)
        else:
            faces['i'] = faces['v1'] -1
            faces['j'] = faces['v2'] -1 
            faces['k'] = faces['v3'] -1
        faces = faces[['i','j','k']].copy()
        return Mesh(vectors,faces)

    def add_mesh(self, organname, objfile):
        cache = pd.read_csv(objfile, sep='\s+',header=None, compression='infer', comment='#',low_memory=False)
        cache.columns = ['type','v1','v2','v3']
        vectors = cache[cache['type'] == 'v'].copy()
        vectors = vectors[['v1','v2','v3']].copy()
        vectors.columns = ['x','y','z']
        vectors = self.reset_coord(vectors)
        xmin = vectors['x'].min();
        xmax = vectors['x'].max();
        ymin = vectors['y'].min();
        ymax = vectors['y'].max();
        zmin = vectors['z'].min();
        zmax = vectors['z'].max();
        if len(self.data[0])==0:
            self.mesh_xmin = xmin
            self.mesh_xmax = xmax
            self.mesh_ymin = ymin
            self.mesh_ymax = ymax
            self.mesh_zmin = zmin
            self.mesh_zmax = zmax
        else:
            if xmin < self.mesh_xmin :
                self.mesh_xmin = xmin
            if ymin < self.mesh_ymin :
                self.mesh_ymin = ymin
            if zmin < self.mesh_zmin :
                self.mesh_zmin = zmin
            if xmax > self.mesh_xmax :
                self.mesh_xmax = xmax
            if ymax > self.mesh_ymax :
                self.mesh_ymax = ymax
            if zmax > self.mesh_zmax :
                self.mesh_zmax = zmax

        faces = cache[cache['type'] == 'f'].copy()
        if faces.dtypes['v1'] == object:
            faces['i'] = faces.apply(lambda row: int(row['v1'].split('/')[0])-1, axis=1)
            faces['j'] = faces.apply(lambda row: int(row['v2'].split('/')[0])-1, axis=1)
            faces['k'] = faces.apply(lambda row: int(row['v3'].split('/')[0])-1, axis=1)
        else:
            faces['i'] = faces['v1'] -1
            faces['j'] = faces['v2'] -1 
            faces['k'] = faces['v3'] -1
        faces = faces[['i','j','k']].copy()

        self.data[0].append(organname)
        self.data[1].append(vectors.to_numpy().tolist())
        self.data[2].append(faces.to_numpy().tolist())

    def get_data(self):
        return self.data

    def update_summary(self,summary):
        ret = summary
        if self.mesh_xmin < ret['box']['xmin']:
           ret['box']['xmin'] = self.mesh_xmin
        if self.mesh_xmax > ret['box']['xmax']:
           ret['box']['xmax'] = self.mesh_xmax
        if self.mesh_ymin < ret['box']['ymin']:
           ret['box']['ymin'] = self.mesh_ymin
        if self.mesh_ymax > ret['box']['ymax']:
           ret['box']['ymax'] = self.mesh_ymax
        if self.mesh_zmin < ret['box']['zmin']:
           ret['box']['zmin'] = self.mesh_zmin
        if self.mesh_zmax > ret['box']['zmax']:
           ret['box']['zmax'] = self.mesh_zmax
        return ret

    def fitpca(self,pca):
        newvects = []
        for i in self.data[1]:
            newvects.append(pca.transform(i))
        self.data[1] = newvects

    def toobj(self,prefix):
        for i, name in enumerate(self.data[0]):
            vects = np.array(self.data[1][i])#.copy()
            faces = np.array(self.data[2][i])#.copy()
            vs = pd.DataFrame()
            vs['x'] = vects[:,0]
            vs['y'] = vects[:,1]
            vs['z'] = vects[:,2]
            vs['t'] = 'v'
            fs = pd.DataFrame()
            fs['x'] = faces[:,0]
            fs['x'] = fs['x']+1
            fs['y'] = faces[:,1]
            fs['y'] = fs['y']+1
            fs['z'] = faces[:,2]
            fs['z'] = fs['z']+1
            fs['t'] = 'f'
            dt = pd.concat([vs,fs],ignore_index=True)
            dt = dt[['t','x','y','z']]
            dt.to_csv(f'{prefix}_{name}.obj',sep=' ',header=False,index=False)
