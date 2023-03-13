import sys
import math
import getopt
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from vt3d_tools.h5ad_wrapper import H5ADWrapper

def draw2DAnno(xys, annoname,anno , prefix,pt):
    xysa = pd.DataFrame()
    xysa['x'] = xys['x']
    xysa['y'] = xys['y']
    xysa['vsid'] = xys['vsid']
    xysa['virtual_sid'] = xysa.apply(lambda row: f's_{int(row["vsid"])}',axis=1)
    xysa[annoname] = anno
    sub_num = len(np.unique(xysa['virtual_sid']))
    w = math.ceil(math.sqrt(sub_num))
    print(f'#slices= {sub_num}')
    print(f'#draw col= {w}')
    sns.relplot(data=xysa, x="x", y="y", col="virtual_sid", col_wrap=w, hue=annoname, kind="scatter")
    plt.axis('equal')
    if pt == 'pdf':
        plt.savefig(f'{prefix}.anno.pdf')
    else:
        plt.savefig(f'{prefix}.anno.png',dpi=300)
    plt.close()

def draw2DGene(xys, genename, gene, prefix,pt):
    xysa = pd.DataFrame()
    xysa['x'] = xys['x']
    xysa['y'] = xys['y']
    xysa['vsid'] = xys['vsid']
    xysa['virtual_sid'] = xysa.apply(lambda row: f's_{int(row["vsid"])}',axis=1)
    xysa[genename] =gene 
    sub_num = len(np.unique(xysa['virtual_sid']))
    w = math.ceil(math.sqrt(sub_num))
    print(f'#slices= {sub_num}')
    print(f'#draw col= {w}')
    sns.relplot(data=xysa, x="x", y="y", col="virtual_sid", col_wrap=w, hue=genename, kind="scatter")
    if pt == 'pdf':
        plt.savefig(f'{prefix}.gene.pdf')
    else:
        plt.savefig(f'{prefix}.gene.png',dpi=300)
    plt.close()

def draw2D_sliced_usage():
    print("""
      vt3d Auxiliary DrawVitrualSlices [options]
            -i                  input h5ad
            -o                  output prefix
            --color_by          gene name or annotation keywork
            --vsid_key          [default vsid, key of virtual slice id]
            --coord2D           [default spatial2D, keyname in obsm]
            -t                  [default pdf, output type (png or pdf)]
            -h/--help 		display this usage and exit
      """)       
     
def draw2D_sliced_main(argv:[]):
    inh5ad = ''
    prefix = ''
    color_by = ''
    vsid_key = 'vsid'
    coord2D = 'spatial2D'
    pt = 'pdf'
    if len(argv)<1:
        draw2D_sliced_usage()
        sys.exit(1)
    try:
        opts, args = getopt.getopt( argv,"hi:o:t:", ["help","color_by=","vsid_key=","coord2D="] )
    except getopt.GetoptError:
        draw2D_sliced_usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h' ,'--help'):
            draw2D_sliced_usage()
            sys.exit(0)
        elif opt in ("-i"):
            inh5ad = arg
        elif opt in ("-o"):
            prefix = arg
        elif opt in ("-t"):
            pt = arg 
        elif opt in ("--color_by"):
            color_by = arg
        elif opt in ("--vsid_key"):
            vsid_key = arg
        elif opt in ("--coord2D"):
            coord2D = arg
    if inh5ad == '' or prefix == '' or color_by == '' or ( not pt in ['pdf','png'] ):
        print('parameter incomplete or invalid, exit...',flush=True)
        sys.exit(102)
    inh5ad = H5ADWrapper(inh5ad)    
    xy = inh5ad.getXY(coord2D)
    xy['vsid'] = inh5ad.getOBS(vsid_key)
    if inh5ad.hasAnno(color_by):
        anno = inh5ad.getOBS(color_by)
        draw2DAnno(xy,color_by,anno,prefix,pt)
    elif inh5ad.hasGene(color_by):
        gene = inh5ad.getGene(color_by) 
        draw2DGene(xy,color_by,gene,prefix,pt)

