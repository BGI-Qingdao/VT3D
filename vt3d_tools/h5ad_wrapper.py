import sys
import numpy as np
import pandas as pd
import anndata as ad

class H5ADWrapper:
    def __init__(self,h5ad_filename):
        self.data = ad.read_h5ad(h5ad_filename)

    def getXY(self,key):
        xy = self.data.obsm[key]
        df = pd.DataFrame(data=xy,columns=['x','y'],)
        return df
    def getOBS(self,key):
        return self.data.obs[key].to_numpy()

    def getGene(self,genename):
        genedata = self.data[:,genename]
        exp = genedata.X.toarray()
        return exp
    #######################################################
    # get xyzv
    ######################################################
    def getBodyXYZ(self,obsm_key='spatial3D',dtype=int):
        xyz = self.data.obsm[obsm_key]
        df = pd.DataFrame(data=xyz,columns=['x','y','z'])
        df = df.astype(dtype)
        return df

    def setXYZ(self,obsm_key,array):
        self.data.obsm[obsm_key] = array

    def getCellXYZC(self,obsm_key='spatial3D',dtype=int):
        df = self.getBodyXYZ(obsm_key,dtype)
        df['cell'] = self.data.obs.index.to_numpy()
        return df

    def getCellXYZA(self,obsm_key='spatial3D',dtype=int,obs_key='lineage'):
        df = self.getBodyXYZ(obsm_key,dtype)
        df['anno'] = self.data.obs[obs_key].to_numpy()
        return df 

    def getGeneXYZE(self,genename,exp_cutoff=0,obsm_key='spatial3D',dtype=int):
        df = self.getBodyXYZ(obsm_key,dtype)
        genedata = self.data[:,genename]
        exp = genedata.X.toarray()
        df['exp'] = exp
        df = df[df['exp']>exp_cutoff].copy()
        return df

    def getGeneExp(self, genename):
        genedata = self.data[:,genename]
        exp = genedata.X.toarray()
        return exp.reshape(-1)

    #######################################################
    # for any slice
    ######################################################
    def extract_and_assign2D(self,cellarray,coord2D,newkey="spatial2D"):
        tmpdata = self.data[cellarray,:].copy()
        tmpdata.obsm[newkey] = coord2D
        return tmpdata

    #######################################################
    # check names API
    ######################################################
    def hasAnno(self, keyname):
        return keyname in  self.data.obs.columns

    def hasGene(self, genename):
        return genename in self.data.var.index

    def hasCoord(self, coordkey):
        return coordkey in self.data.obsm

    def AllGenesList(self):
        return self.data.var.index.tolist()

    #######################################################
    # Json API for webcache
    ######################################################
    def getSummary(self, coord, annos,genes):
        ret = {}
        # get the total xxx
        ret['total_cell'] = len(self.data.obs.index)
        ret['total_gene'] = len(genes)
        # get Annotation factors
        ret['annokeys'] = []
        ret['annomapper'] = {}
        for anno in annos:
            unique_anno = np.unique(self.data.obs[anno])
            if len(unique_anno)<1:
                print("ERROR: invalid annokey : {anno} exit..." )
                sys.exit(101)
            ret['annokeys'].append(anno)
            legend2int = {}
            int2legend = {}
            for i,key in enumerate(unique_anno):
                legend2int[key]=i
                int2legend[i]=key   
            ret['annomapper'][f'{anno}_legend2int'] = legend2int
            ret['annomapper'][f'{anno}_int2legend'] = int2legend
        # prepare box-space
        ret['box'] = {}
        coordarray = self.data.obsm[coord]
        ret['box']['xmin'] = np.min(coordarray[:,0]) 
        ret['box']['xmax'] = np.max(coordarray[:,0]) 
        ret['box']['ymin'] = np.min(coordarray[:,1]) 
        ret['box']['ymax'] = np.max(coordarray[:,1]) 
        ret['box']['zmin'] = np.min(coordarray[:,2]) 
        ret['box']['zmax'] = np.max(coordarray[:,2]) 
        return ret
