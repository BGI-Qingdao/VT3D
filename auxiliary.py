import getopt

def Auxiliary_usage():
    print("""
    vt3d Auxiliary subaction:
          GrayScaleTIF	Generate 3D TIFF gray scale image as input of Slicer3D.
          Draw2D        Draw 2D images (png/pdf/html)
          DrawSlices 	Draw 2D images (png/pdf/html) groupby slice_id
         """)


def Auxiliary_main(argv:[]):
    if len(argv)==1 and (argv[0] == '-h' or argv[0] == '--help') :
        Auxiliary_usage()
        exit(0)
    elif len(argv) < 1 or not argv[0] in ( "GrayScaleTIF",
                                           "Draw2D",
                                           "DrawSlices",
                                                   ):
        Auxiliary_usage()
        exit(1)
    elif argv[0] == "GrayScaleTIF":
        from vt3d_tools.grayscaletif import grayscaletif_main
        grayscaletif_main(argv[1:])
        exit(0)
    elif argv[0] == "Draw2D" :
        exit(0)
    elif argv[0] == "DrawSlices" :
        exit(0)
    else:
        Auxiliary_usage()
        exit(1)
