import json
import numpy as np
import pandas as pd

class OBJWrapper:
    def __init__(self,coordfile):
        self.data = [[],[],[]] # legend, vector, faces
        self.init_coord(coordfile)
        self.mesh_xmin = 0
        self.mesh_xmax = 0
        self.mesh_ymin = 0
        self.mesh_ymax = 0
        self.mesh_zmin = 0
        self.mesh_zmax = 0

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
