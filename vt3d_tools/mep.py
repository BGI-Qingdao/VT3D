#!/usr/bin/env python3

import os.path
import sys
import getopt
import numpy as np
import pandas as pd
from skimage import io as skio
from vt3d_tools.h5ad_wrapper import H5ADWrapper


coord_key = 'coord3D'

#################################################
# BinConf
# 
class BinConf:
    def __init__(self,view,binsize,scalebar,borderbinsize):
        self.gene_binsize = binsize
        if binsize < borderbinsize :
            self.body_binsize = borderbinsize 
            self.body_scale = int(borderbinsize/binsize) # please make sure borderbinsize/binsize = int
        else :
            self.body_binsize = binsize
            self.body_scale = 1
        self.Scalebar_H = int(scalebar / binsize)
        self.Scalebar_W = self.Scalebar_H // 5 
        self.Scalebar_S = 3 
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
        # draw scale bar
        #draw_array[H-binconf.Scalebar_H-binconf.Scalebar_S : H-binconf.Scalebar_S,W-binconf.Scalebar_W-binconf.Scalebar_S:W-binconf.Scalebar_S,:]=255
        return draw_array
    elif view == "APDV" :
        body_info.calcAPDV_border()
        W,H = body_info.getAPDV_WH()
        draw_array = np.zeros((H,W,3),dtype='int')
        if drawborder==1:
            xids,yids = body_info.getAPDV_border()
            # draw background
            draw_array[yids,xids,:] = 255
            # draw scale bar
        #draw_array[[H-10,H-9,H-8],W-15:W-5,:]=255
        #draw_array[H-binconf.Scalebar_H-binconf.Scalebar_S : H-binconf.Scalebar_S,W-binconf.Scalebar_W-binconf.Scalebar_S:W-binconf.Scalebar_S,:]=255
        #draw_array[H-20:H-10,W-15:W-12,:]=255
        return draw_array
        #return None
    elif view == "MLDV" :
        body_info.calcMLDV_border()
        W,H = body_info.getMLDV_WH()
        draw_array = np.zeros((H,W,3),dtype='int')
        if drawborder==1:
            xids,yids = body_info.getMLDV_border()
            # draw background
            draw_array[yids,xids,:] = 255
        # draw scale bar
        #draw_array[[H-10,H-9,H-8],W-15:W-5,:]=255
        #draw_array[H-20:H-10,W-15:W-12,:]=255
        #draw_array[H-binconf.Scalebar_H-binconf.Scalebar_S : H-binconf.Scalebar_S,W-binconf.Scalebar_W-binconf.Scalebar_S:W-binconf.Scalebar_S,:]=255
        #draw_array[H-20:H-10,W-15:W-12,:]=255
        return draw_array

def GetGeneExpr(inh5,genes,binconf,roi):
    gene_expr = Gene3D(binconf.geneBinsize())
    gene_expr.loadExpr(inh5,genes,roi)
    return gene_expr

def FISH_scale(num_points, panel_expr):
    from sklearn.preprocessing import QuantileTransformer
    min_value = np.min(panel_expr)
    max_value = np.percentile(panel_expr,95)
    #print(f'min = {min_value}; max={max_value}',flush=True)
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
    
def DrawSingleFISH_APML( body_info, expr, colors):
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

def DrawSingleFISH_APDV(body_info, expr, colors):
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

def DrawSingleFISH_DVML(body_info, expr, colors):
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

def DrawSingleFISH(view, body_info, gene_expr, color):
    if view == "APML" :
        return DrawSingleFISH_APML(body_info, gene_expr, color)
    elif view == "APDV":
        return DrawSingleFISH_APDV(body_info, gene_expr, color)
    elif view == "MLDV":
        return DrawSingleFISH_DVML(body_info, gene_expr, color)

############################################################################
# common codes for one channel
#
class OneChannelData:
    def __init__(self,gene_list, channel_color):
        if len(gene_list) == 0 :
            self.valid = False
            return
        self.valid = True
        self.genes= gene_list
        self.colors = channel_color

    def PrepareData(self,inh5, binconf,roi):
        if self.valid:
            self.gene_expr = GetGeneExpr(inh5,self.genes,binconf,roi) 
            if self.gene_expr.valid == False:
                self.valid = False
            #else:
            #    print(self.files)
            #    print(self.colors)
            #    print('-------------',flush=True)

    def GetImage(self, view, body_info):
        if self.valid:
            return DrawSingleFISH(view,body_info,self.gene_expr,self.colors)
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

       atleast one options:
            -r [geneid that draw in Red(#ff0000) channel]
            -g [geneid that draw in Green(#00ff00) channel]
            -c [geneid that draw in Cyan(#00ffff) channel]
            -m [geneid that draw in Magenta(#ff00ff) channel]
            -y [geneid that draw in Yellow(#ffff00) channel]
            -b [geneid that draw in Blue(#008fff) channel]
            -p [geneid that draw in Peru(#CD853F) channel]

       optional configure options:
            --binsize [default 5]
            --borderbinsize [default 20]
            --view [default APML, must be APML/APDV/MLDV]
                   [APML -> xy panel]
                   [APDV -> xz panel]
                   [MLDV -> yz panel]
            --drawborder [default 0, must be 1/0]
            --spatial_key [defaut coord3D, the keyname of coordinate array in obsm]

       optional ROI options:
            --xmin [default None]
            --ymin [default None]
            --zmin [default None]
            --xmax [default None]
            --ymax [default None]
            --zmax [default None]
Example :
     vt3d MEP -i in.h5ad -o test -r notum -g wnt1 -m foxD 
""")

def saveimage(fname ,draw_matrix):
    used_draw_matrix = draw_matrix.copy()
    used_draw_matrix[draw_matrix>255] = 255
    new_draw_matrix = np.zeros(used_draw_matrix.shape , dtype='uint8') 
    new_draw_matrix[:,:,:] = used_draw_matrix[:,:,:];
    skio.imsave(fname,new_draw_matrix)

def mergeImage(base_img, new_img):
    base_max_img = np.max(base_img,axis=2)
    new_max_img = np.max(new_img,axis=2)
    tmp_img = np.stack([base_max_img,new_max_img],axis=2)
    new_index = np.argmax(tmp_img,axis=2)
    ret_img = base_img.copy()
    y,x = np.nonzero(new_index)
    ret_img[y,x,:]=new_img[y,x,:]
    return ret_img

def mep_main(argv:[]):
    ###############################################################################
    # Default values
    indata = ''
    prefix = ''
    r_gene = []
    b_gene = []
    c_gene = []
    p_gene = []
    g_gene = []
    m_gene = []
    y_gene = []
    colors = [
       [ 255, 0  , 0  ], #Red
       [ 0  , 126, 255], #Blue -> cyan-blue
       [ 0  , 255, 255], #Cyan
       [ 205, 133, 63 ], #Peru
       [ 0  , 255, 0  ], #Green
       [ 255, 0  , 255], #Megenta
       [ 255, 255, 0  ], #Yellow
    ]
    view = 'APML'
    xmin = ymin = zmin = None
    xmax = ymax = zmax = None
    binsize = 5
    borderbinsize = 20
    scalebar = 200
    drawborder=0

    ###############################################################################
    # Parse the arguments
    try:
        opts, args = getopt.getopt(argv,"hi:o:m:r:g:y:b:c:p:",
                                        ["help",
                                         "view=",
                                         "xmin=",
                                         "ymin=",
                                         "zmin=",
                                         "xmax=",
                                         "ymax=",
                                         "zmax=",
                                      "binsize=",
                                  "spatial_key=",
                                   "drawborder=",
                                "borderbinsize=",
                                     "scalebar="])
    except getopt.GetoptError:
        mep_usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h' ,'--help'):
            mep_usage()
            sys.exit(0)
        elif opt in ("-i"):
            indata = arg
        elif opt in ("-o"):
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
        elif opt == "--scalebar":
            scalebar = int(arg)
        elif opt == "--borderbinsize":
            borderbinsize = int(arg)

    ###############################################################################
    # Sanity check
    if indata == "" or prefix == "":
        mep_usage()
        sys.exit(3)
    roi = ROIManager(xmin,xmax,ymin,ymax,zmin,zmax)
    binconf = BinConf(view,binsize,scalebar,borderbinsize)
    print(f"the drawing view : {view}")
    ###############################################################################
    # Load the data
    inh5ad = H5ADWrapper(indata)
    ###############################################################################
    # Load the body points 
    print('Loading body now ...',flush=True)
    body_info = GetBodyInfo(inh5ad,binconf,roi)

    ###############################################################################
    # Load the gene expr points and draw
    target_lists = [ r_gene , b_gene, c_gene, p_gene, g_gene, m_gene, y_gene ]
    draw_list = []
    for i in range(len(target_lists)):
        draw_list.append(OneChannelData(target_lists[i],colors[i]))

    print('Loading expression now ...',flush=True)
    for ocd in draw_list:
        ocd.PrepareData(inh5ad,binconf,roi)
    # get sample border
    draw_image = GetBackground(view,body_info,binconf,drawborder)
    for ocd in draw_list:
        ocd_image = ocd.GetImage(view,body_info)
        if ocd_image is None:
            continue
        draw_image = mergeImage(draw_image,ocd_image)
        ocd_image = None

    saveimage(f'{prefix}.tif',draw_image)
    ###############################################################################
    # Done
    print('__ALL DONE__',flush=True)

if __name__ == "__main__":
    mep_main(sys.argv[1:])
