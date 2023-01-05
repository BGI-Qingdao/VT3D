import getopt

def AtlasBrowser_usage():
    print("""
    vt3d AtlasBrowser subaction:
          BuildAtlas            Generate cache files for WebCache action.
          LaunchAtlas           Start the atlas server for VT3D_Browse in WebCache folder.
         """)


def AtlasBrowser_main(argv:[]):
    if len(argv)==1 and (argv[0] == '-h' or argv[0] == '--help') :
            AtlasBrowser_usage()
            exit(0)
    elif len(argv) < 1 or not argv[0] in ( "BuildAtlas",
                                           "LaunchAtlas",
                                                   ):
        AtlasBrowser_usage()
        exit(1)
    elif argv[0] == "BuildAtlas" :
        from vt3d_tools.webcache import webcache_main
        webcache_main(argv[1:])
        exit(0)
    elif argv[0] == "LaunchAtlas" :
        from vt3d_tools.webserver import webserver_main
        webserver_main(argv[1:])
        exit(0)
    else:
        AtlasBrowser_usage()
        exit(1)
