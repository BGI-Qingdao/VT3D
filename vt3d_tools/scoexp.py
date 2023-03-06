#!/user/bin/env python3

import sys
import numpy as np
import pandas as pd
import anndata as ad
import getopt
from scipy.spatial import distance_matrix
from scipy.stats import rankdata
from sklearn.preprocessing import scale 
from vt3d_tools.folder_file_wraper import *
#-----------------------------------------------------------------------------#
# Radial basis function kernel
#
# @param dis_mat Distance matrix
# @param sigm Width of rbfk
# @param zero_diag
#-----------------------------------------------------------------------------#
# 
# @The raw R scripts:
# rbfk <- function (dis_mat, sigm, zero_diag=T) {
#   rbfk_out <- exp(-1*(dis_mat^2)/(2*sigm^2))
#   if (zero_diag) diag(rbfk_out) <- 0
#   return(rbfk_out)
# }
# @The new python scripts:
def rbfk(dis_mat, sigm, zero_diag=True):
    rbfk_out = np.exp(-1 * np.square(dis_mat) / (2*sigm**2) )
    if zero_diag:
        rbfk_out[np.diag_indices_from(rbfk_out)]=0
    return rbfk_out

#-----------------------------------------------------------------------------#
# Weighted cross correlation
#
# @param X Expression matrix, n X p
# @param W Weight matrix, n X n
# @param method Correlation method, pearson or spearman
# @param na_zero Na to zero
#-----------------------------------------------------------------------------#
#
# @The raw R scripts:
# wcor <- function(X, W, method=c('pearson', 'spearman')[1], na_zero=T) {
#   if (method=='spearman') X <- apply(X, 2, rank)
#   X <- scale(X)
#   X[is.nan(X)] <- NA
#   W_cov_temp <- (t(X) %*% W %*% X)
#   W_diag_mat <- sqrt(diag(W_cov_temp) %*% t(diag(W_cov_temp)))
#   cor_mat <- W_cov_temp/W_diag_mat
#   if (na_zero) cor_mat[which(is.na(cor_mat), arr.ind=T)] <- 0
#   cor_mat
# }
# @The new python scripts:
def wcor(X, W, method='pearson', na_zero=True) :
    if method == 'spearman':
        X = np.apply_along_axis(rankdata ,0, X) # rank each columns
    X = scale(X,axis=0) # scale for each columns
    W_cov_temp = np.matmul( np.matmul(X.T, W), X )  
    W_diag_mat = np.sqrt( np.matmul(np.diag(W_cov_temp), np.diag(W_cov_temp).T ) )
    cor_mat = W_cov_temp / W_diag_mat
    if na_zero:
        np.nan_to_num(cor_mat,False)
    return cor_mat

#-----------------------------------------------------------------------------#
# SCoexp module
#
# @param celltrek_inp CellTrek input on cell of interests
# @param sigm
# @param assay
# @param gene_select
# @param zero_cutoff
# @param cor_method
#-----------------------------------------------------------------------------#
#
# @The raw R scripts:
#scoexp <- function(celltrek_inp, sigm=NULL, assay='RNA', gene_select=NULL, zero_cutoff=5, cor_method='spearman', approach=c('cc', 'wgcna')[1              ], maxK=8, k=8, avg_con_min=.5, avg_cor_min=.5, min_gen=20, max_gen=100, keep_cc=T, keep_wgcna=T, keep_kern=T, keep_wcor=T, ...) {
#  if (!all(c('coord_x', 'coord_y') %in% colnames(celltrek_inp@meta.data))) stop('coord_x and coord_y not detected in the metadata')
#  if (is.null(sigm)) sigm <- celltrek_inp@images[[1]]@scale.factors$spot_dis
#  if (is.null(gene_select)) {
#    cat('gene filtering...\n')
#    feature_nz <- apply(celltrek_inp[[assay]]@data, 1, function(x) mean(x!=0)*100)
#    features <- names(feature_nz)[feature_nz > zero_cutoff]
#    cat(length(features), 'features after filtering...\n')
#  } else if (length(gene_select) > 1) {
#    features <- intersect(gene_select, rownames(celltrek_inp[[assay]]@data))
#    if (length(features)==0) stop('No genes in gene_select detected')
#  }
#  celltrek_inp <- Seurat::ScaleData(celltrek_inp, features=features)
#  res <- list(gs=c(), cc=c(), rbfk=c(), wcor=c())
#  dist_mat <- dist(celltrek_inp@meta.data[, c('coord_x', 'coord_y')]) %>% as.matrix
#  kern_mat <- rbfk(dist_mat, sigm=sigm, zero_diag=F)
#  expr_mat <- t(as.matrix(celltrek_inp[[assay]]@scale.data))
#  cat('Calculating spatial-weighted cross-correlation...\n')
#  wcor_mat <- wcor(X=expr_mat, W=kern_mat, method=cor_method)
# @The new python scripts:
def scoexp( adata ,
            spatialKey,
            sigm=15,                          # default 15 um as sigm
            gene_select=[],                   # filter gene by exp cell > zero_cutoff% of all cells if len(gene_select)<2, otherwise use this gene set
            assay=None,                       # none will use X matrix, otherwise use layer[assay]
            zero_cutoff=5,                    # filter gene if len(gene_select)<2
            cor_method='spearman',            # spearman or pearson
            ) :
    if (not spatialKey in adata.obsm ):
        print(f'{spatialKey} not detected in adata.obsm. exit...',flush=True)
        sys.exit(11)
    if assay is None:
        cell_gene_matrix = adata.X
    else :
        cell_gene_matrix = adata.layers[assay]
    if not isinstance(cell_gene_matrix,np.ndarray):
        cell_gene_matrix = cell_gene_matrix.toarray()
    if len(gene_select)<2:
        print('gene filtering...',flush=True)
        feature_nz = np.apply_along_axis(lambda x: np.mean(x!=0)*100,0, cell_gene_matrix)
        features = adata.var.index.to_numpy()[feature_nz > zero_cutoff]
        print(f'{len(features)} features after filtering...',flush=True)
    else:
        features = np.intersect1d(np.array(gene_select),np.array(adata.var.index.to_numpy()))
        if len(features)<2:
            print('No enough genes in gene_select detected, exit...',flush=True)
            sys.exit(12)
    celltrek_inp = adata[:,features.tolist()]
    if assay is None:
        expr_mat = celltrek_inp.X.toarray()
    else :
        expr_mat = celltrek_inp.layers[assay].toarray()
    dist_mat = distance_matrix( celltrek_inp.obsm[spatialKey],
                                celltrek_inp.obsm[spatialKey] )
    kern_mat = rbfk(dist_mat, sigm=sigm, zero_diag=False)
    print('Calculating spatial-weighted cross-correlation...',flush=True)
    wcor_mat = wcor(X=expr_mat, W=kern_mat, method=cor_method)
    print('Calculating spatial-weighted cross-correlation done.',flush=True)
    df = pd.DataFrame(data=wcor_mat, index=features, columns=features)
    return df

#####################################################
# Print scoexp score of one gene as one json
#####################################################
def printJsonPerGene(data):
    create_folder('gene_scoexp')
    genes = data.columns.tolist()
    savedata2json(genes,f'gene_scoexp/genenames.json')
    for gene in data.columns :
        scores = data[gene].tolist()
        savedata2json(scores,f'gene_scoexp/{gene}.json')

def printTop100Pair(data):
    genes = data.columns
    data1 = data.to_numpy()
    data1 = np.triu(data1)
    row, col = np.diag_indices_from(data1)
    data1[row,col] = 0
    data2 = data1.reshape(-1)

    for i in range(100):
        maxid = np.argmax(data2)
        row = maxid // int(len(genes))
        col = maxid % int(len(genes))
        print(f'{i+1}th pair {genes[row]} -- {genes[col]} : {data1[row,col]}')
        data2[maxid] = 0

#####################################################
# Usage
#
def scoexp_usage():
    print("""
Usage : vt3d Auxiliary SCoexp [options]

Options:
    -i <input.h5ad>
    -o <output prefix>
    --spatial_key [default 'spatial3D', the keyname of coordinate in obsm]
    --sigma [sigma of RBF kernel, default 15]
    --genes [default None, file that contain target gene list. if None, all gene used]

Notice: too much genes will lead to huge memory cost and dist cost.
""", flush=True)

#####################################################
# main pipe
#
def scoexp_main(argv:[]):
    #######################################
    # default parameter value
    infile = ''
    prefix = ''
    gene_file = None
    sigma = 15
    spatial_key = 'spatial3D'
    try:
        opts, args = getopt.getopt(argv,"hi:o:",["help","spatial_key=","gene_file=", "sigma="])
    except getopt.GetoptError:
        scoexp_usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h' ,'--help'):
            scoexp_usage()
            sys.exit(0)
        elif opt in ("-i"):
            infile = arg
        elif opt in ("-o"):
            prefix = arg
        elif opt in ("--spatial_key"):
            spatial_key = arg
        elif opt in ("--gene_file"):
            gene_file = arg

    # sanity check
    if infile == '' or prefix == '' or spatial_key == '':
        scoexp_usage()
        sys.exit(0)
    adata = ad.read_h5ad(infile)
    if not gene_file is None:
        genes = np.loadtxt(gene_file,dtype='str').tolist()
    else:
        genes = []
    ret = scoexp(adata,spatial_key,sigma,genes)
    ret.to_csv(f'{prefix}.csv',sep='\t',header=True,index=False)
    printJsonPerGene(ret)
    printTop100Pair(ret)
