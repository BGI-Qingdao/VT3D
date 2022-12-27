#!/usr/bin/env python3
import os.path
import sys
import json
import getopt
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from skimage import io as skio
from vt3d_tools.h5ad_wrapper import H5ADWrapper
from vt3d_tools.panel_wrapper import Plane
from sklearn.decomposition import PCA
coord_key = 'spatial3D'

def project3D(df,dist):
    X = df[['x','y','z']].to_numpy()
    pca = PCA(n_components=2)
    X2 = pca.fit_transform(X)
    df['new_x'] = X2[:,0]
    df['new_y'] = X2[:,1]
    df['new_z'] = dist
    return df

#################################################
# BinConf
# 
class BinConf:
    def __init__(self,view,binsize,borderbinsize):
        self.gene_binsize = binsize
        if binsize < borderbinsize :
            self.body_binsize = borderbinsize 
            self.body_scale = int(borderbinsize/binsize) # please make sure borderbinsize/binsize = int
        else :
            self.body_binsize = binsize
            self.body_scale = 1

    def geneBinsize(self):
        return self.gene_binsize

    def bodyBinConf(self):
        return self.body_binsize , self.body_scale

#################################################
# BorderDetect, 2D border detection
# 
class BorderDetect:
    def __init__(self,x,y):
        self.x = x 
        self.y = y

    def Border(self):
        xmin = np.min(self.x)
        xmax = np.max(self.x)
        ymin = np.min(self.y)
        ymax = np.max(self.y)
        self.x = self.x -xmin + 5  #left 5 pixel of margin
        self.y = self.y -ymin + 5  #left 5 pixel of margin
        height = int(ymax-ymin+10) #right 5 pixel of margin
        width = int(xmax-xmin+10)  #right 5 pixel of margin
        mask = np.zeros((height,width),dtype=int)
        mask[self.y,self.x] = 1
        # open and close to remove noise and fill holes
        from scipy import ndimage
        mask = ndimage.binary_closing(mask).astype(int)
        mask = ndimage.binary_opening(mask).astype(int)

        for y in range(0,height):
            for x in range(1,width-1):
                if mask[y,x-1]==0 and mask[y,x]==0 and mask[y,x+1]==1:
                    mask[y,x] = 255
            for x in range(width-2,1,-1):
                if mask[y,x+1]==0 and mask[y,x]==0 and mask[y,x-1]==1:
                    mask[y,x] = 255
        for x in range(0,width):
            for y in range(1,height-1):
                if mask[y-1,x]==0 and mask[y,x]==0 and mask[y+1,x]==1:
                    mask[y,x] = 255
            for y in range(height-2,1,-1):
                if mask[y+1,x]==0 and mask[y,x]==0 and mask[y-1,x]==1:
                    mask[y,x] = 255
        mask[self.y,self.x] = 0
        (y_idx,x_idx) = np.nonzero(mask)
        y_idx = y_idx + ymin - 5 #switch back to raw coord
        x_idx = x_idx + xmin - 5 #switch back to raw coord
        return y_idx,x_idx

#################################################
# ROIManager
#
class ROIManager:
    def __init__(self,xmin,xmax,ymin,ymax,zmin,zmax):
        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax
        self.zmin = zmin
        self.zmax = zmax

    ###################################
    # always filter nax before min
    def filterDFMax(self,df):
        if self.zmax != None:
            df = df[df['z']<=self.zmax].copy()
        if self.xmax != None:
            df = df[df['x']<=self.xmax].copy()
        if self.ymax != None:
            df = df[df['y']<=self.ymax].copy()
        return df

    ###################################
    # always filter nax before min
    def filterAndResetDFMin(self,df):
        if self.xmin == None:
            self.xmin = np.min(df['x'])
        if self.ymin == None:
            self.ymin = np.min(df['y'])
        if self.zmin == None:
            self.zmin = np.min(df['z'])
        df['x'] = df['x'] - self.xmin
        df = df[df['x']>=0].copy()
        df['y'] = df['y'] - self.ymin
        df = df[df['y']>=0].copy()
        df['z'] = df['z'] - self.zmin
        df = df[df['z']>=0].copy()
        return df

#################################################
# BodyInfo 
# 
class BodyInfo:
    def __init__(self,bin_border,bin_draw_scale):
        self.bin_border = bin_border
        self.bin_draw_scale = bin_draw_scale

    def loadAllPoints(self,inh5, roi):
        bd = inh5.getBodyXYZ(coord_key,int)
        #format x axis by roi first
        bd = roi.filterDFMax(bd)
        bd = roi.filterAndResetDFMin(bd)
        #bin x axis now
        bd['x']= bd['x']/self.bin_border
        bd['x']= bd['x'].astype(int)
        bd['x']=bd['x']+1
        #bin y axis now
        bd['y']= bd['y']/self.bin_border
        bd['y']= bd['y'].astype(int)
        bd['y']= bd['y']+1
        #bin z axis now
        bd['z']= bd['z']/self.bin_border
        bd['z']= bd['z'].astype(int)
        bd['z']= bd['z']+1
        # save final body
        self.body = bd

    #################################
    #  AP = x axis , ML = y axis
    #
    def calcAPML_border(self):              
        # agg all z coordinate
        bd = self.body.groupby(['x', 'y']).agg(z=('z','max')).reset_index()
        height = int(np.max(bd['y'])+2) #right 1 pixel margin
        width = int(np.max(bd['x'])+2)  #right 1 pixel margin
        # get basic infos
        self.APML_W  = width * self.bin_draw_scale
        self.APML_H  = height * self.bin_draw_scale
        self.APML_points_num = len(bd)*self.bin_draw_scale*self.bin_draw_scale
        # get border dash points
        graph_matrix = np.zeros((height,width),dtype='uint8')
        graph_matrix[bd['y'],bd['x']]=1
        ( body_y, body_x ) = np.nonzero(graph_matrix)
        y_idx,x_idx = BorderDetect(body_x,body_y).Border()
        # save final border
        self.APML_x_idx = x_idx*self.bin_draw_scale
        self.APML_y_idx = y_idx*self.bin_draw_scale

    def getAPML_num_points(self):
        return self.APML_points_num

    def getAPML_WH(self):
        return self.APML_W,self.APML_H

    def getAPML_border(self):   
        return self.APML_x_idx , self.APML_y_idx           

    #################################
    #  AP = x axis , DV = y axis
    #
    def calcAPDV_border(self):              
        # agg all y coordinate
        bd = self.body.groupby(['x', 'z']).agg(y=('y','max')).reset_index()
        height = int(np.max(bd['z'])+2)
        width = int(np.max(bd['x'])+2)
        # get basic infos
        self.APDV_W  = width * self.bin_draw_scale
        self.APDV_H  = height * self.bin_draw_scale
        self.APDV_points_num = len(bd)*self.bin_draw_scale*self.bin_draw_scale
        # get border dash points
        graph_matrix = np.zeros((height,width),dtype='uint8')
        graph_matrix[bd['z'],bd['x']]=1
        ( body_y, body_x ) = np.nonzero(graph_matrix)
        y_idx,x_idx = BorderDetect(body_x,body_y).Border()
        # save final border
        self.APDV_x_idx = x_idx*self.bin_draw_scale
        self.APDV_y_idx = y_idx*self.bin_draw_scale

    def getAPDV_num_points(self):
        return self.APDV_points_num

    def getAPDV_WH(self):
        return self.APDV_W, self.APDV_H

    def getAPDV_border(self):
        return self.APDV_x_idx , self.APDV_y_idx

    #################################
    #  ML = x axis , DV = x axis
    #
    def calcMLDV_border(self):              
        # agg all y coordinate
        bd = self.body.groupby(['y', 'z']).agg(x=('x','max')).reset_index()
        height = int(np.max(bd['y'])+2)
        width = int(np.max(bd['z'])+2)
        # get basic infos
        self.MLDV_W  = width * self.bin_draw_scale
        self.MLDV_H  = height * self.bin_draw_scale
        self.MLDV_points_num = len(bd)*self.bin_draw_scale*self.bin_draw_scale
        # get border dash points
        graph_matrix = np.zeros((height,width),dtype='uint8')
        graph_matrix[bd['y'],bd['z']]=1
        ( body_y, body_x ) = np.nonzero(graph_matrix)
        y_idx,x_idx = BorderDetect(body_x,body_y).Border()
        # save final border
        self.MLDV_x_idx = x_idx*self.bin_draw_scale
        self.MLDV_y_idx = y_idx*self.bin_draw_scale

    def getMLDV_num_points(self):
        return self.MLDV_points_num

    def getMLDV_WH(self):
        return self.MLDV_W, self.MLDV_H

    def getMLDV_border(self):   
        return self.MLDV_x_idx , self.MLDV_y_idx           

class Gene3D:
    def __init__(self,binsize):
        self.binsize = binsize

    def loadExpr(self,inh5,genes,roi):
        a = []
        for gene in genes:  #hanle multi files here
            aa = inh5.getGeneXYZE(gene,0,coord_key,int)
            if not aa.empty:
                a.append(aa)
        if len(a) == 0 :
           self.valid = False   
           return
        show_data = pd.concat(a,ignore_index=True)
        show_data.columns=['x','y','z','value']
        show_data = roi.filterDFMax(show_data)
        show_data = roi.filterAndResetDFMin(show_data)
        if len(show_data) <1 :
            self.valid = False
            return
        self.valid = True
        self.gene_expr = show_data

    def getMIR_APML(self):
        show_data = self.gene_expr.copy()
        show_data['x'] = show_data['x']/self.binsize
        show_data['x'] = show_data['x'].astype(int)
        show_data['y'] = show_data['y']/self.binsize
        show_data['y'] = show_data['y'].astype(int)
        show_data = show_data.groupby(['x', 'y']).agg(value=('value', 'max')).reset_index()
        return show_data

    def getMIR_APDV(self):
        show_data = self.gene_expr.copy()
        show_data['x'] = show_data['x']/self.binsize
        show_data['x'] = show_data['x'].astype(int)
        show_data['z'] = show_data['z']/self.binsize
        show_data['z'] = show_data['z'].astype(int)
        show_data = show_data.groupby(['x', 'z']).agg(value=('value', 'max')).reset_index()
        return show_data

    def getMIR_MLDV(self):
        show_data = self.gene_expr.copy()
        show_data['y'] = show_data['y']/self.binsize
        show_data['y'] = show_data['y'].astype(int)
        show_data['z'] = show_data['z']/self.binsize
        show_data['z'] = show_data['z'].astype(int)
        show_data = show_data.groupby(['y', 'z']).agg(value=('value', 'max')).reset_index()
        return show_data

def GetBodyInfo(inh5,binconf,roi):
    body_binsize, body_scale = binconf.bodyBinConf()
    body_info = BodyInfo(body_binsize,body_scale)
    body_info.loadAllPoints(inh5,roi)
    return body_info

def GetBackground(view,body_info,binconf,drawborder):
    if view == "APML" :
        body_info.calcAPML_border()
        W,H = body_info.getAPML_WH()
        draw_array = np.zeros((H,W,3),dtype='int')
        if drawborder==1:
            xids,yids = body_info.getAPML_border()
            # draw background
            draw_array[yids,xids,:] = 255
        return draw_array
    elif view == "APDV" :
        body_info.calcAPDV_border()
        W,H = body_info.getAPDV_WH()
        draw_array = np.zeros((H,W,3),dtype='int')
        if drawborder==1:
            xids,yids = body_info.getAPDV_border()
            # draw background
            draw_array[yids,xids,:] = 255
        return draw_array
    elif view == "MLDV" :
        body_info.calcMLDV_border()
        W,H = body_info.getMLDV_WH()
        draw_array = np.zeros((H,W,3),dtype='int')
        if drawborder==1:
            xids,yids = body_info.getMLDV_border()
            # draw background
            draw_array[yids,xids,:] = 255
        return draw_array

def GetGeneExpr(inh5,genes,binconf,roi):
    gene_expr = Gene3D(binconf.geneBinsize())
    gene_expr.loadExpr(inh5,genes,roi)
    return gene_expr

def FISH_scale(num_points, panel_expr):
    from sklearn.preprocessing import QuantileTransformer
    min_value = np.min(panel_expr)
    max_value = np.percentile(panel_expr,95)
    num_light_panel=len(panel_expr)
    temp_list = np.zeros(num_points)
    temp_list[0:num_light_panel]=panel_expr
    qt = QuantileTransformer(output_distribution='uniform', random_state=0)
    temp_list_scale = qt.fit_transform(temp_list.reshape(-1, 1))
    temp_list_scale = temp_list_scale.reshape(-1)
    ret_data = panel_expr/max_value  #temp_list_scale[0:num_light_panel]
    ret_data = ret_data*8
    ret_data = np.power((np.ones(len(ret_data))*2),ret_data);
    ret_data [ ret_data >255 ] = 255
    ret_data = ret_data.astype(int)
    return ret_data

def drawRdBu(x,y,e,prefix,W,H,symbolsize):
    tmp = pd.DataFrame()
    tmp['x'] = x
    tmp['y'] = y
    tmp['exp'] = e
    tmp = tmp.sort_values(by=['exp'])
    sns.scatterplot(data=tmp,x='x',y='y',hue='exp',palette="RdYlBu_r",s=symbolsize, edgecolors='none',linewidths=0)
    plt.xlabel('project_x')
    plt.ylabel('project_y')
    plt.xlim(0,W)
    plt.ylim(0,H)
    plt.legend(bbox_to_anchor=(1.02, 0.8), loc='upper left', borderaxespad=0)
    plt.tight_layout()
    plt.savefig(f'{prefix}.pdf',dpi=72)
    plt.close()

def DrawAPDV_RdBu(body_info, expr,prefix,symbolsize):
    W,H = body_info.getAPDV_WH()
    APDV_expr = expr.getMIR_APDV()
    APDV_expr['x'] = APDV_expr['x']
    APDV_expr['z'] = APDV_expr['z']
    drawRdBu(APDV_expr['x'],APDV_expr['z'],APDV_expr['value'],f'{prefix}.raw',W,H,symbolsize)
    draw_expr = FISH_scale(body_info.getAPDV_num_points(),APDV_expr['value'])
    draw_expr = draw_expr.astype(float)
    draw_expr = draw_expr / 255.0
    drawRdBu(APDV_expr['x'],APDV_expr['z'],draw_expr,prefix,W,H,symbolsize)
    ret = pd.DataFrame()
    ret['x'] = APDV_expr['x'].to_numpy()
    ret['y'] = APDV_expr['z'].to_numpy()
    ret['MEP'] = APDV_expr['value'].to_numpy()
    ret['eMEP'] = draw_expr
    ret.to_csv(f'{prefix}.result.csv',sep='\t',header=True,index=False)

def DrawMLDV_RdBu(body_info, expr,prefix,symbolsize):
    W,H = body_info.getMLDV_WH()
    MLDV_expr = expr.getMIR_MLDV()
    MLDV_expr['y'] = MLDV_expr['y']
    MLDV_expr['z'] = MLDV_expr['z']
    drawRdBu(MLDV_expr['y'],MLDV_expr['z'],MLDV_expr['value'],f'{prefix}.raw',W,H,symbolsize)
    draw_expr = FISH_scale(body_info.getMLDV_num_points(),MLDV_expr['value'])
    draw_expr = draw_expr.astype(float)
    draw_expr = draw_expr / 255.0
    drawRdBu(MLDV_expr['y'],MLDV_expr['z'],draw_expr,prefix,W,H,symbolsize)
    ret = pd.DataFrame()
    ret['x'] = MLDV_expr['y'].to_numpy()
    ret['y'] = MLDV_expr['z'].to_numpy()
    ret['MEP'] = MLDV_expr['value'].to_numpy()
    ret['eMEP'] = draw_expr
    ret.to_csv(f'{prefix}.result.csv',sep='\t',header=True,index=False)

def DrawAPML_RdBu(body_info, expr,prefix,symsize):
    W,H = body_info.getAPML_WH()
    APML_expr = expr.getMIR_APML()
    APML_expr['y'] = APML_expr['y']#//+body_info.bin_draw_scale 
    APML_expr['x'] = APML_expr['x']#//+body_info.bin_draw_scale 
    drawRdBu(APML_expr['x'],APML_expr['y'],APML_expr['value'],f'{prefix}.raw',W,H,symsize)
    draw_expr =  FISH_scale(body_info.getAPML_num_points(),APML_expr['value'])
    draw_expr = draw_expr.astype(float)
    draw_expr = draw_expr / 255.0
    drawRdBu(APML_expr['x'],APML_expr['y'],draw_expr,prefix,W,H,symsize)
    ret = pd.DataFrame()
    ret['x'] = APML_expr['x'].to_numpy()
    ret['y'] = APML_expr['y'].to_numpy()
    ret['MEP'] = APML_expr['value'].to_numpy()
    ret['eMEP'] = draw_expr
    ret.to_csv(f'{prefix}.result.csv',sep='\t',header=True,index=False)

def DrawSingleFISH_APML( body_info, expr, colors,prefix ):
    W,H = body_info.getAPML_WH()
    draw_array = np.zeros((H,W,3),dtype='uint8')
    APML_expr = expr.getMIR_APML()
    APML_expr['y'] = APML_expr['y']+body_info.bin_draw_scale #shift the 1 pixel margin for border
    APML_expr['x'] = APML_expr['x']+body_info.bin_draw_scale #shift the 1 pixel margin for border
    draw_expr =  FISH_scale(body_info.getAPML_num_points(),APML_expr['value'])
    draw_expr = draw_expr.astype(float)
    draw_expr = draw_expr / 255.0
    r_channel = draw_expr * colors[0] 
    g_channel = draw_expr * colors[1] 
    b_channel = draw_expr * colors[2] 
    draw_array[APML_expr['y'],APML_expr['x'],0] = r_channel.astype(int) 
    draw_array[APML_expr['y'],APML_expr['x'],1] = g_channel.astype(int)
    draw_array[APML_expr['y'],APML_expr['x'],2] = b_channel.astype(int)
    return draw_array

def DrawSingleFISH_APDV(body_info, expr, colors, prefix):
    W,H = body_info.getAPDV_WH()
    draw_array = np.zeros((H,W,3),dtype='uint8')
    APDV_expr = expr.getMIR_APDV()
    APDV_expr['x'] = APDV_expr['x']+body_info.bin_draw_scale #shift the 1 pixel margin for border
    APDV_expr['z'] = APDV_expr['z']+body_info.bin_draw_scale #shift the 1 pixel margin for border
    draw_expr = FISH_scale(body_info.getAPDV_num_points(),APDV_expr['value'])
    draw_expr = draw_expr.astype(float)
    draw_expr = draw_expr / 255.0
    r_channel = draw_expr * colors[0] 
    g_channel = draw_expr * colors[1] 
    b_channel = draw_expr * colors[2] 
    draw_array[APDV_expr['z'],APDV_expr['x'],0] = r_channel.astype(int) 
    draw_array[APDV_expr['z'],APDV_expr['x'],1] = g_channel.astype(int)
    draw_array[APDV_expr['z'],APDV_expr['x'],2] = b_channel.astype(int)
    return draw_array 

def DrawSingleFISH_DVML(body_info, expr, colors, prefix):
    W,H = body_info.getMLDV_WH()
    draw_array = np.zeros((H,W,3),dtype='uint8')
    MLDV_expr = expr.getMIR_MLDV()
    MLDV_expr['y'] = MLDV_expr['y']+body_info.bin_draw_scale #shift the 1 pixel margin for border
    MLDV_expr['z'] = MLDV_expr['z']+body_info.bin_draw_scale #shift the 1 pixel margin for border
    draw_expr = FISH_scale(body_info.getMLDV_num_points(),MLDV_expr['value'])
    draw_expr = draw_expr.astype(float)
    draw_expr = draw_expr / 255.0
    r_channel = draw_expr * colors[0] 
    g_channel = draw_expr * colors[1] 
    b_channel = draw_expr * colors[2] 
    draw_array[MLDV_expr['y'],MLDV_expr['z'],0] = r_channel.astype(int) 
    draw_array[MLDV_expr['y'],MLDV_expr['z'],1] = g_channel.astype(int)
    draw_array[MLDV_expr['y'],MLDV_expr['z'],2] = b_channel.astype(int)
    return draw_array 

def DrawSingleFISH(view, body_info, gene_expr, color,prefix):
    if view == "APML" :
        return DrawSingleFISH_APML(body_info, gene_expr, color,prefix)
    elif view == "APDV":
        return DrawSingleFISH_APDV(body_info, gene_expr, color,prefix)
    elif view == "MLDV":
        return DrawSingleFISH_DVML(body_info, gene_expr, color,prefix)

def DrawSingleRdBu(view,body_info, expr,prefix,symsize):
    if view == "APML" :
        return DrawAPML_RdBu(body_info, expr,prefix,symsize)
    elif view == "APDV":
        return DrawAPDV_RdBu(body_info, expr,prefix,symsize)
    elif view == "MLDV":
        return DrawMLDV_RdBu(body_info, expr,prefix,symsize)

############################################################################
# common codes for one channel
#
class OneChannelData:
    def __init__(self,gene_list, channel_color, channel_name ):
        if len(gene_list) == 0 :
            self.valid = False
            return
        self.valid = True
        self.genes= gene_list
        self.colors = channel_color
        self.channel_name = channel_name

    def PrepareData(self,inh5, binconf,roi):
        if self.valid:
            self.gene_expr = GetGeneExpr(inh5,self.genes,binconf,roi) 
            if self.gene_expr.valid == False:
                self.valid = False

    def GetImage(self, view, body_info, prefix):
        if self.valid:
            return DrawSingleFISH(view,body_info,self.gene_expr,self.colors,prefix)
        else:
            return None

############################################################################
# Usage
#
def mep_usage():
    print("""
Usage : vt3d MEP  [options]

Options:
       required options:
            -i <input.h5ad>
            -o <output prefix>

       RdRlBu_r mode  
            --gene geneid
            [notice: enable --gene will override all pseudoFISH mode parameters]

       pseudoFISH mode
            -r [geneid that draw in Red(#ff0000) channel]
            -g [geneid that draw in Green(#00ff00) channel]
            -c [geneid that draw in Cyan(#00ffff) channel]
            -m [geneid that draw in Magenta(#ff00ff) channel]
            -y [geneid that draw in Yellow(#ffff00) channel]
            -b [geneid that draw in Blue(#0000ff) channel]

       optional configure options:
            --binsize [default 5]
            --spatial_key [defaut spatial3D, the keyname of coordinate array in obsm]
            --view [default APML, must be APML/APDV/MLDV]
                   [APML -> xy plane]
                   [APDV -> xz plane]
                   [MLDV -> yz plane]
            --plane [default '', example: "[[0,0,0],[1,0,0],[1,1,0]]" ]
                    [define any plane by three points]
                    [notice: enable --plane will override --view]
            --drawborder [default 0, must be 1/0]
            --symbolsize [default 10, only used in RdYlBu_r mode]

       optional ROI options:
            --xmin [default None]
            --ymin [default None]
            --zmin [default None]
            --xmax [default None]
            --ymax [default None]
            --zmax [default None]
Example :
     #example of RdYlBu_r mode, will generate test.png     
     vt3d MEP -i in.h5ad -o test --gene wnt1 --view APML 

     #example of pseudoFISH mode, will generate test.tif :
     vt3d MEP -i in.h5ad -o test -r notum -g wnt1 -m foxD --view APML

     #example of RdYlBu_r mode with assigned plane
     vt3d MEP -i in.h5ad -o test --gene wnt1 --plane '[[0,0,0],[1,0,0],[1,1,0]]'
""")

def saveimage(fname ,draw_matrix):
    used_draw_matrix = draw_matrix.copy()
    used_draw_matrix[draw_matrix>255] = 255
    new_draw_matrix = np.zeros(used_draw_matrix.shape , dtype='uint8') 
    new_draw_matrix[:,:,:] = used_draw_matrix[:,:,:];
    skio.imsave(fname,new_draw_matrix)

def mergeImage(base_img, new_img):
    ret_img = np.zeros(base_img.shape , dtype='int') 
    ret_img = ret_img + base_img
    ret_img = ret_img + new_img 
    return ret_img

def mep_main(argv:[]):
    ###############################################################################
    # Default values
    indata = ''
    prefix = ''
    gene = ''
    r_gene = []
    b_gene = []
    c_gene = []
    g_gene = []
    m_gene = []
    y_gene = []
    colors = [
       [ 255, 0  , 0  ], #Red
       [ 0  , 0  , 255], #Blue 
       [ 0  , 255, 255], #Cyan
       [ 0  , 255, 0  ], #Green
       [ 255, 0  , 255], #Megenta
       [ 255, 255, 0  ], #Yellow
    ]
    view = 'APML'
    plane=''
    xmin = ymin = zmin = None
    xmax = ymax = zmax = None
    binsize = 5
    borderbinsize = 20
    drawborder=0
    symbolsize=10
    ###############################################################################
    # Parse the arguments
    try:
        opts, args = getopt.getopt(argv,"hi:o:m:r:g:y:b:c:p:",
                                        [ "help",
                                         "gene=",
                                         "view=",
                                         "xmin=",
                                         "ymin=",
                                         "zmin=",
                                         "xmax=",
                                         "ymax=",
                                         "zmax=",
                                        "plane=",
                                      "binsize=",
                                   "symbolsize=",
                                  "spatial_key=",
                                   "drawborder=",
                                    ])
    except getopt.GetoptError:
        mep_usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h' ,'--help'):
            mep_usage()
            sys.exit(0)
        elif opt == "--gene":
            gene = arg
        elif opt == "--plane":
            plane = arg
        elif opt == "-i":
            indata = arg
        elif opt == "-o":
            prefix = arg
        elif opt == "-r" :
            r_gene.append(arg)
        elif opt == "-g" :
            g_gene.append(arg)
        elif opt == "-b" :
            b_gene.append(arg)
        elif opt == "-m" :
            m_gene.append(arg)
        elif opt == "-y" :
            y_gene.append(arg)
        elif opt == "-c" :
            c_gene.append(arg)
        elif opt == "-p" :
            p_gene.append(arg)
        elif opt == "--symbolsize":
            symbolsize=int(arg)
        elif opt == "--drawborder":
            drawborder=int(arg)
        elif opt == "--xmin":
            xmin = int(arg)
        elif opt == "--ymin":
            ymin = int(arg)
        elif opt == "--zmin":
            zmin = int(arg)
        elif opt == "--xmax":
            xmax = int(arg)
        elif opt == "--ymax":
            ymax = int(arg)
        elif opt == "--zmax":
            zmax = int(arg)
        elif opt == "--view":
            view = arg
        elif opt == "--spatial_key":
            global coord_key 
            coord_key = arg
        elif opt == "--binsize":
            binsize = int(arg)

    borderbinsize = binsize
    ###############################################################################
    # Sanity check
    if indata == "" or prefix == "":
        mep_usage()
        sys.exit(3)
    #print(f"the drawing view : {view}")
    ###############################################################################
    # Load the data
    inh5ad = H5ADWrapper(indata)
    if plane != '' :
        xmin = ymin = zmin = None
        xmax = ymax = zmax = None
        view = 'APML'
        points = json.loads(plane)
        # override spatial3D to new coordinate system now
        plane = Plane(np.array(points[0]),np.array(points[1]),np.array(points[2]))
        xyzc = inh5ad.getCellXYZC(coord_key,int)
        dist = plane.distance(xyzc)
        xyzc['dist'] = dist
        plane.project_coord(xyzc,dist)
        xyzc = project3D(xyzc,dist)
        inh5ad.setXYZ(coord_key,xyzc[['new_x','new_y','new_z']].to_numpy())
     
    roi = ROIManager(xmin,xmax,ymin,ymax,zmin,zmax)
    binconf = BinConf(view,binsize,borderbinsize)
    ###############################################################################
    # Load the body points 
    print('Loading body now ...',flush=True)
    body_info = GetBodyInfo(inh5ad,binconf,roi)
    if gene == '':
        ###############################################################################
        # Load the gene expr points and draw
        cnames       = [ 'red',   'blue', 'cyan','green','magenta','yellow' ]
        target_lists = [ r_gene , b_gene, c_gene, g_gene, m_gene, y_gene ]
        draw_list = []
        for i in range(len(target_lists)):
            draw_list.append(OneChannelData(target_lists[i],colors[i],cnames[i]))
        print('Loading expression now ...',flush=True)
        for ocd in draw_list:
            ocd.PrepareData(inh5ad,binconf,roi)
        # get sample border
        draw_image = GetBackground(view,body_info,binconf,drawborder)
        for ocd in draw_list:
            ocd_image = ocd.GetImage(view,body_info,prefix)
            if ocd_image is None:
                continue
            draw_image = mergeImage(draw_image,ocd_image)
            ocd_image = None
        saveimage(f'{prefix}.tif',draw_image)
    else:
        GetBackground(view,body_info,binconf,drawborder)
        print('Loading expression now ...',flush=True)
        expr = GetGeneExpr(inh5ad,[gene],binconf,roi)
        DrawSingleRdBu(view,body_info, expr,prefix,symbolsize)
         
    ###############################################################################
    # Done
    print('__ALL DONE__',flush=True)

if __name__ == "__main__":
    mep_main(sys.argv[1:])
