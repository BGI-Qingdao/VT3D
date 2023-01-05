# VT3D
VT3D: a versatile Visualization Toolbox for 3D spatially resolved transcriptomic atlas

![image](https://user-images.githubusercontent.com/8720584/199003210-983dd4b5-01e8-4668-b9ee-36a006f49b77.png)

## <a name=contents>Table of Contents</a>

- [Installation](#install)
    - [Dependences](#dependences)
    - [Download](#download)
- [Quick start](#quick_start)
    - [Where to download example data](#examples)
    - [How to use AtlasBroser to browse your data](#quick_atlasbrowser)
    - [How to create and visulize virtual slices](#quick_anyslicer)
    - [How to create MEP images](#quick_mep)
    - [How to create surface models from omics data](#quick_models)
- [Frequent Q & A](#q_a)
- [Contact us](#contact)
- [Detailed usages](#usages)

## <a name=install>Installation</a>

### <a name=dependences>Dependences</a>

A python3 environment with below packages:

* json
* numpy
* pandas
* skimage
* sklearn
* anndata
* matplotlib
* seaborn

### <a name=download>Dowload</a>

```
git clone https://github.com/BGI-Qingdao/VT3D.git ./VT3D
```

## <a name=quick_start>Quick start</a>

### <a name=examples>Where to download example data</a>

#### data format requirement 
The basic input data is h5ad base and save 3D corrdinate in obsm and Surface models must in .obj format
![image](https://user-images.githubusercontent.com/8720584/210737884-cd33f297-3ce3-47ea-b8b2-07ee260e0c41.png)

#### All example datasets can be downloaded from http://www.bgiocean.com/vt3d_example/

Instead of the click-to-download mode from website, you also can download them by command line, for examples:

```
#--------- Developing drosophila embryos and larvae: E14-16h ----- 
mkdir E14_E16h
cd E14_E16h
wget -c http://www.bgiocean.com/vt3d_example/download/flysta3d/E14-16h_a_count_normal_stereoseq.h5ad
wget -c http://www.bgiocean.com/vt3d_example/download/flysta3d/E14-16h_a.tar.gz
wget -c http://www.bgiocean.com/vt3d_example/download/flysta3d/E14-16h.atlas.json
wget -c http://www.bgiocean.com/vt3d_example/download/flysta3d/fixed.json
cd ../
#--------- Developing drosophila embryos and larvae: E16-18h ----- 
mkdir E16_E18h
cd E16_E18h
wget -c http://www.bgiocean.com/vt3d_example/download/flysta3d/E16-18h_a_count_normal_stereoseq.h5ad
wget -c http://www.bgiocean.com/vt3d_example/download/flysta3d/E16-18h_a.tar.gz
wget -c http://www.bgiocean.com/vt3d_example/download/flysta3d/E16-18h.atlas.json
wget -c http://www.bgiocean.com/vt3d_example/download/flysta3d/fixed.json
tar -xzf E16-18h_a.tar.gz
cd ../
#--------- Developing drosophila embryos and larvae: L1
mkdir L1
cd L1
wget -c http://www.bgiocean.com/vt3d_example/download/flysta3d/L1_a_count_normal_stereoseq.h5ad
wget -c http://www.bgiocean.com/vt3d_example/download/flysta3d/L1_a.tar.gz
wget -c http://www.bgiocean.com/vt3d_example/download/flysta3d/L1_a.atlas.json
wget -c http://www.bgiocean.com/vt3d_example/download/flysta3d/fixed.json
tar -xzf L1_a.tar.gz
cd ../
```

You can find all download commands from the [website](http://www.bgiocean.com/vt3d_example/)

### <a name=quick_atlasbrowser>How to use AtlasBroser to browse your data</a>

You can find step by step tutorial to build example atlas from the [website](http://www.bgiocean.com/vt3d_example/).

Here we use L1 atlas as an example:

#### Generate web cache folder

```
cd L1
vt3d AtlasBrowser BuildAtlas -i L1_a_count_normal_stereoseq.h5ad -o L1_Atlas -c L1_a.atlas.json

```

#### Start web server and browser your data now!

```
cd L1_Atlas && vt3d AtlasBrowser LaunchAtlas -p 80
```

now open your broswer and try ```http://127.0.0.1:8010/index.html```

![image](https://user-images.githubusercontent.com/8720584/210740473-3554fe92-4d12-493b-9cb1-c2d9986622da.png)


### <a name=quick_anyslicer>How to create and visulize virtual slices</a>

```
./vt3d AnySlice -i example_data/WT.VT3D.h5ad -o test --p0 '0,0,200' --p1 '1,0,200' --p2 '1,1,200'
```

### <a name=quick_mep>How to create MEP images</a>

```
./vt3d MEP -i example_data/WT.VT3D.h5ad -o gut.SMED30007704 -g SMED30007704
```
The output gut.SMED30007704.tif (opened by any image tool is OK) :

![image](https://user-images.githubusercontent.com/8720584/199372843-7fafc175-e8fa-4806-966b-9beaef7201f4.png)

### <a name=quick_models>How to create surface models from omics data</a>

```
./vt3d GrayScaleTif -i  example_data/WT.VT3D.h5ad  -o test3d -c example_data/organ.json
```

The test3d.tif (opened by ImageJ 3DViewer)  :

![image](https://user-images.githubusercontent.com/8720584/199373130-87fa5d7f-f07e-43e6-a402-a5e9176bbc64.png)

## <a name=q_a>Frequent Q & A</a>

## <a name=contact>Contact us</a>

## <a name=usages>Detailed usages</a>

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
            --spatial_key [defaut spatial3D, the keyname of coordinate array in obsm]
            
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
            --spatial_key [default 'spatial3D', the keyname of coordinate array in obsm]
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
            --spatial_key [default 'spatial3D', the keyname of coordinate array in obsm]
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
            "Coordinate" : "spatial3D",
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
