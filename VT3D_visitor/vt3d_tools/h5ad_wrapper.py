import numpy as np
import pandas as pd
import anndata as ad

class H5ADWrapper:
    def __init__(self,h5ad_filename):
        self.data = ad.read_h5ad(h5ad_filename)

    def getBodyXYZ(self,obsm_key='coord3D',dtype=int):
        xyz = self.data.obsm[obsm_key]
        df = pd.DataFrame(data=xyz,columns=['x','y','z'],dtype=dtype)
        return df

    def getCellXYZC(self,obsm_key='coord3D',dtype=int):
        df = self.getBodyXYZ(obsm_key,dtype)
        df['cell'] = self.data.obs.index.to_numpy()
        return df

    def getCellXYZA(self,obsm_key='coord3D',dtype=int,obs_key='lineage'):
        df = self.getBodyXYZ(obsm_key,dtype)
        df[obs_key] = self.data.obs[obs_key].to_numpy()
        return df 

    def getGeneXYZE(self,genename,exp_cutoff=0,obsm_key='coord3D',dtype=int):
        df = self.getBodyXYZ(obsm_key,dtype)
        genedata = self.data[:,genename]
        exp = genedata.X.toarray()
        df['exp'] = exp
        df = df[df['exp']>exp_cutoff].copy()
        return df
    def extract2D(self,cellarray,coord2D):
        tmpdata = self.data[cellarray,:].copy()
        tmpdata.obsm['coord2D'] = coord2D
        return tmpdata
