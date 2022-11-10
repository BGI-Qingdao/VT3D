import numpy as np
import pandas as pd

class OBJWrapper:
    def __init__(self,objfile):
          self.filename = objfile
    
    def obj2json(obj_file,zmin):
        if obj_file == '' :
            return "[ [ ] , [ ] ]"
        print(f'parse {obj_file} now ...',flush=True)
        ###load mesh obj
        mesh = pd.read_csv(obj_file, sep=' ',header=None, compression='infer', comment='#')
        mesh.columns = ['type', 'x', 'y', 'z']
    
        ###convert vectors
        v = mesh[mesh['type']=='v']
        v = v[['x','y','z']]
        v = v.copy()
        v = v.astype('float')
        v['z'] = v['z'] + zmin
    
        ###convert faces
        f = mesh[ mesh['type']=='f' ]
        f = f[ ['x','y','z'] ]
        f = f.copy()
        f.columns = [ 'v1','v2','v3' ]
        f = f.astype('int')
        f = f-1
    
        ###convert to json
        vs = '['+v['x'].map(str)+','+v['y'].map(str)+','+v['z'].map(str)+']'
        fs = '['+f['v1'].map(str)+','+f['v2'].map(str)+','+f['v3'].map(str)+']'
        json_print = '['+ str(vs.tolist()).replace("'","") + ',' + '\n' + str(fs.tolist()).replace("'","") + ']'
        return json_print

