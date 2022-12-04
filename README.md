# VT3D
VT3D: a versatile Visualization Toolbox for 3D spatial transcriptomics atlas

![image](https://user-images.githubusercontent.com/8720584/199003210-983dd4b5-01e8-4668-b9ee-36a006f49b77.png)


## Dependences

A python3 environment with below packages:

* json
* numpy
* pandas
* skimage
* sklearn
* anndata

## Dowload

```
git clone https://github.com/BGI-Qingdao/VT3D.git ./VT3D
```

## Quick introduction of vt3d with test data

* enter VT3D folder
``` cd ./VT3D/```
* prepare the test data
```
cd ./example_data
gzip -dc WT.VT3D.h5ad.gz >WT.VT3D.h5ad
cd ../
```

The input data is h5ad base and save 3D corrdinate in obsm:

![image](https://user-images.githubusercontent.com/8720584/199381217-96741181-13ae-4b88-b4f4-817544e50eea.png)

### Browser your data in two step

#### Generate web cache folder

```
./vt3d WebCache -i  example_data/WT.VT3D.h5ad -c  example_data/atlas.json -o WebCache
```

#### Start web server and browser your data now!

```
cd WebCache
../vt3d_visitor WebServer -p 8010
```

now open your broswer and try ```http://127.0.0.1:8010/index.html```

![image](https://user-images.githubusercontent.com/8720584/202903832-e68ab510-2fac-4efd-9d4c-58d477e6e164.png)

### Generate MEP image

```
./vt3d MEP -i example_data/WT.VT3D.h5ad -o gut.SMED30007704 -g SMED30007704
```
The output gut.SMED30007704.tif (opened by any image tool is OK) :

![image](https://user-images.githubusercontent.com/8720584/199372843-7fafc175-e8fa-4806-966b-9beaef7201f4.png)


### AnySlice

```
./vt3d AnySlice -i example_data/WT.VT3D.h5ad -o test --p0 '0,0,200' --p1 '1,0,200' --p2 '1,1,200'
```

### Generate grayscale 3D tiff

```
./vt3d GrayScaleTif -i  example_data/WT.VT3D.h5ad  -o test3d -c example_data/organ.json
```

The test3d.tif (opened by ImageJ 3DViewer)  :

![image](https://user-images.githubusercontent.com/8720584/199373130-87fa5d7f-f07e-43e6-a402-a5e9176bbc64.png)




## Full usage of vt3d_visitor

### the entry usage of vt3d_visitor
```
>./vt3d_visitor -h
Usage : vt3d_visitor <action> [options ]
          -h/--help           show this short usage
Action:
          -------------------------------------------------------------------------------
          MEP                   Maximun Expression Projection. (suit 3D structure to 2D)
          AnySlice              Extract 2D slice from any angle.
          GrayScaleTif          Generate 3D TIFF gray scale image as input of Slicer3D.
          WebCache              Generate cache files for WebCache action.
          WebServer             Start the atlas server for VT3D_Browse in WebCache folder.
          -------------------------------------------------------------------------------

Detail usage of each action:
        vt3d_visitor <action> -h

```

### Detail usage of MEP action

```
>./vt3d_visitor MEP -h

Usage : vt3d_visitor MEP  [options]

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
            --scalebar [default 200]
            --drawborder [default 1, must be 1/0]
            --spatial_key [defaut coord3D, the keyname of coordinate array in obsm]
            
       optional ROI options:
            --xmin [default None]
            --ymin [default None]
            --zmin [default None]
            --xmax [default None]
            --ymax [default None]
            --zmax [default None]
Example :
     vt3d_visitor MEP -i in.h5ad -o test -r notum -g wnt1 -m foxD
```

### Detail usage of AnySlice

```
>./vt3d_visitor AnySlice -h

Usage : vt3d_visitor AnySlice [options]

Options:
       required options:
            -i <input.h5ad>
            -o <output prefix>
            --p0 <coordinate of p0>
            --p1 <coordinate of p1>
            --p2 <coordinate of p2>

       optional options:
            --thickness [default 16]
            --spatial_key [default 'coord3D', the keyname of coordinate array in obsm]
Example:
    > vt3d_visitor AnySlice -i in.h5ad -o test --p0 "0,1,0" --p1 "1,0,0" --p2 "1,1,0"
    > ls
    test.h5ad
```

### Detail usage of GrayScaleTif

```
>./vt3d_visitor GrayScaleTif -h

Usage : vt3d_visitor GrayScaleTif [options]

Options:
       required options:
            -i <input.h5ad>
            -o <output prefix>
            -c <conf.json>
            --spatial_key [default 'coord3D', the keyname of coordinate array in obsm]
Example:
        > vt3d_visitor GrayScaleTif -i in.h5ad -o test -c organ.json
        > cat organ.json
        {
            "binsize" : 10,
            "keyname" : "lineage",
            "targets": [
                "all",
                "Gut",
                "Pharynx"
                "Neural",
            ],
            "grayvalue": [
                50,
                100,
                150,
                200
            ]
        }
```

### Detail usage of WebCache

```
>./vt3d_visitor WebCache -h

Usage : vt3d_visitor WebCache [options]

Options:
       required options:
            -i <input.h5ad>
            -c <conf.json>
            -o [output prefix, default webcace]
Example:
        > vt3d_visitor WebCache -i in.h5ad -c atlas.json
        > cat atlas.json
        {
            "Coordinate" : "coord3D",
            "Annotatinos" : [ "lineage" ],
            "Meshes" : {
                "body" : "example_data/body.obj" ,
                "gut" : "example_data/gut.obj"     ,
                "nueral" : "example_data/neural.obj" ,
                "pharynx" : "example_data/pharynx.obj"
            },
            "mesh_coord" : "example_data/WT.coord.json",
            "Genes" : [
               "SMED30033583" ,
               "SMED30011277" ,
       ... genes you want to display ...
               "SMED30031463" ,
               "SMED30033839"
            ]
        }

Notice:
    The most time-consumptional and disk-cost part is the Genes data.
      The more genes you need, the more time of this action and
           the more disk space of atlas cache folder will cost.

The structure of output atlas folder:
      webcache
        +---Anno
             +---lineage.json
        +---Gene
             +---SMED30033583.json
             +---SMED30011277.json
             ...
             +---SMED30031463.json
             +---SMED30033839.json
        +---summary.json
        +---gene.json
        +---meshes.json

```

### Detail usage of WebServer
```
>./vt3d_visitor WebServer -h

Usage : vt3d_visitor WebServer [options]

Options:
            -p [port, default 8050]
Example:
        > vt3d_visitor WebServer

        ...
        never stop until you press Ctrl-C

```
