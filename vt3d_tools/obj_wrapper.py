import json
import numpy as np
import pandas as pd

class OBJWrapper:
    def __init__(self,coordfile):
        self.data = [[],[],[]] # legend, vector, faces
        self.init_coord(coordfile)

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
        
        faces = cache[cache['type'] == 'f'].copy()
        faces['i'] = faces.apply(lambda row: int(row['v1'].split('/')[0])-1, axis=1)
        faces['j'] = faces.apply(lambda row: int(row['v2'].split('/')[0])-1, axis=1)
        faces['k'] = faces.apply(lambda row: int(row['v3'].split('/')[0])-1, axis=1)
        faces = faces[['i','j','k']].copy()

        self.data[0].append(organname)
        self.data[1].append(vectors.to_numpy().tolist())
        self.data[2].append(faces.to_numpy().tolist())

    def get_data(self):
        return self.data
