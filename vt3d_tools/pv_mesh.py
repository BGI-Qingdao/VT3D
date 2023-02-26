#!/usr/bin/env python3
import sys
import json
import getopt
from vt3d_tools.h5ad_wrapper import H5ADWrapper
from vt3d_tools.obj_wrapper import OBJWrapper
import pyvista as pv
from pyvista import PolyData
import pymeshfix as mf
import meshio
#####################################################
# Usage
#
def pvmesh_usage():
    print("""
Usage : vt3d Auxiliary PVMesh [options]

Require:
    pip install pymeshfix
    pip install pyvista
    pip install meshio
Options:
       required options:
            -i <input.h5ad>
            -o <output prefix>
            --target_cluster [default 'all']
            --cluster_key [default 'clusters', the keyname of cell type in obs]
            --spatial_key [default 'spatial3D', the keyname of coordinate in obsm]
            --smooth 1000 [niter of Laplacian smoothing]
            --alpha [default 2.0]

Notice: if target_cluster is all, cluster_key will be ignored.
""", flush=True)

#####################################################
# main pipe
#
def pvmesh_main(argv:[]):
    #######################################
    # default parameter value
    infile = ''
    prefix = ''
    spatial_key = 'spatial3D'
    cluster_key = 'clusters'
    target_cluster = 'all'
    smooth = 1000
    alpha = 2.0
    try:
        opts, args = getopt.getopt(argv,"hi:o:",["help","spatial_key=",
                                                        "smooth=",
                                                        "alpha=",
                                                        "target_cluster=",
                                                        "cluster_key="])
    except getopt.GetoptError:
        pvmesh_usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h' ,'--help'):
            pvmesh_usage()
            sys.exit(0)
        elif opt in ("-i"):
            infile = arg
        elif opt in ("-o"):
            prefix = arg
        elif opt in ("--spatial_key"):
            spatial_key = arg
        elif opt in ("--cluster_key"):
            cluster_key = arg
        elif opt in ("--target_cluster"):
            target_cluster = arg
        elif opt in ("--smooth"):
            smooth = int(arg)
        elif opt in ("--alpha"):
            alpha = float(arg)

    # sanity check
    if infile == '' or prefix == '' or spatial_key == '':
        pvmesh_usage()
        sys.exit(0)
    # run pca
    inh5ad = H5ADWrapper(infile)
    if target_cluster == 'all':
        xyz = inh5ad.getBodyXYZ(spatial_key,float)
        pc = pv.PolyData(xyz.values)
    else :
        xyza = inh5ad.getCellXYZA(spatial_key,float,cluster_key)
        target_xyz = xyza[ xyza['anno'] == target_cluster ][['x','y','z']]
        pc = pv.PolyData(target_xyz.values)
    # construct mesh, copy from spateo
    mesh = pc.delaunay_3d(alpha=alpha).extract_surface().triangulate().clean()
    # merge meshes
    sub_meshes = mesh.split_bodies()
    if len(sub_meshes) > 1:
        mesh = sub_meshes[0]
        for next_mesh in sub_meshes[1:]:
            mesh.merge(next_mesh)
    # fixed mesh, copy from spateo
    meshfix = mf.MeshFix(mesh)
    meshfix.repair(verbose=False)
    fixed_mesh = meshfix.mesh.triangulate().clean()
    # smooth, copy from spateo
    smoothed_mesh = fixed_mesh.smooth(n_iter=smooth)
    # save obj
    pv.save_meshio(f'{prefix}.obj',smoothed_mesh)
    #pv.save_meshio(f'{prefix}.vtk',smoothed_mesh)
