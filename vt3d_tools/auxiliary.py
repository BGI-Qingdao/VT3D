import getopt

def Auxiliary_usage():
    print("""
    vt3d Auxiliary subaction:
          GrayScaleTIF          Generate 3D TIFF gray scale image as input of Slicer3D.
          PVMesh                Generate Mesh obj automaticly by pc.delaunay_3d
          DrawVitrualSlices     Draw 2D images groupby vitrual slice
          PCA3D                 Reset 3d coordinate by PCA.
          FormatMesh            Shift and scale the mesh model.
          BuildGrids            Build grids( continuous model )
          SCoexp                Spatial-related co-expression matrix calculation.
          MeshSub               Filter data by only keep within mesh points. 
         """)


def Auxiliary_main(argv:[]):
    if len(argv)==1 and (argv[0] == '-h' or argv[0] == '--help') :
        Auxiliary_usage()
        exit(0)
    elif len(argv) < 1 or not argv[0] in ( "GrayScaleTIF",
                                           "DrawVitrualSlices",
                                           "PCA3D",
                                           "PVMesh",
                                           "FormatMesh",
                                           "BuildGrids",
                                           "SCoexp",
                                           "MeshSub",
                                                   ):
        Auxiliary_usage()
        exit(1)
    elif argv[0] == "GrayScaleTIF":
        from vt3d_tools.grayscaletif import grayscaletif_main
        grayscaletif_main(argv[1:])
        exit(0)
    elif argv[0] == "DrawVitrualSlices":
        from vt3d_tools.draw2d_sliced import draw2D_sliced_main
        draw2D_sliced_main(argv[1:])
        exit(0)
    elif argv[0] == "PCA3D":
        from vt3d_tools.pca3d import pca3d_main
        pca3d_main(argv[1:])
        exit(0)
    elif argv[0] == "PVMesh":
        from vt3d_tools.pv_mesh import pvmesh_main
        pvmesh_main(argv[1:])
        exit(0)
    elif argv[0] == "FormatMesh":
        from vt3d_tools.format_mesh import formatmesh_main
        formatmesh_main(argv[1:])
        exit(0)
    elif argv[0] == "BuildGrids":
        from vt3d_tools.build_grids import buildgrids_main
        buildgrids_main(argv[1:])
        exit(0)
    elif argv[0] == "SCoexp":
        from vt3d_tools.scoexp import scoexp_main
        scoexp_main(argv[1:])
        exit(0)
    elif argv[0] == "MeshSub":
        from vt3d_tools.mesh_sub import meshsub_main
        meshsub_main(argv[1:])
        exit(0)
    else:
        Auxiliary_usage()
        exit(1)
