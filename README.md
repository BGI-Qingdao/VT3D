# VT3D
VT3D: a versatile visualization toolbox for 3D spatially resolved transcriptomic atlas

![image](https://user-images.githubusercontent.com/8720584/199003210-983dd4b5-01e8-4668-b9ee-36a006f49b77.png)

## <a name=contents>Table of Contents</a>

- [Installation](#install)
    - [Dependencies](#dependencies)
    - [Download](#download)
- [Quick Start](#quick_start)
    - [Where can I download example datasets](#examples)
    - [How can I use AtlasBroser to browse your data](#quick_atlasbrowser)
    - [How can I create and visualize virtual slices](#quick_anyslicer)
    - [How can I create MEP images](#quick_mep)
    - [How can I create surface models from omics data](#quick_models)
- [Frequent Q & A](#q_a)
- [Contact Us](#contact)
- [Detailed Usages](#usages)

## <a name=install>Installation</a>

### <a name=dependencies>Dependencies</a>

A python3 environment with the following packages is required:

* json
* numpy
* pandas
* skimage
* sklearn
* anndata
* matplotlib
* seaborn

Note that we have not tested different versions of those packages yet, but below are the versions in our developing environment:
```
>>> json.__version__
'2.0.9'
>>> numpy.__version__
'1.19.5'
>>> pandas.__version__
'1.3.4'
>>> sklearn.__version__
'0.24.2'
>>> anndata.__version__
'0.8.0'
>>> matplotlib.__version__
'3.4.3'
>>> seaborn.__version__
'0.11.2'
```

### <a name=download>Dowload</a>

```
git clone https://github.com/BGI-Qingdao/VT3D.git ./VT3D
```
All scripts are written in Python package. Thus, there is no need for any compilation.

This package contains compiled vt3d_browser. If your need the source codes, please go to https://github.com/BGI-Qingdao/VT3D_Browser 

## <a name=quick_start>Quick start</a>

### <a name=examples>Where to download example data</a>

#### data format requirement 
The basic input data is h5ad base and saves 3D coordinates in obsm. Surface models must be stored in .obj format.
![image](https://user-images.githubusercontent.com/8720584/210737884-cd33f297-3ce3-47ea-b8b2-07ee260e0c41.png)

#### All example datasets can be downloaded from http://www.bgiocean.com/vt3d_example/

In addition to the click-to-download mode from the above website, you can also download them by command line:

```
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
#--------- Hypo Preoptic hypothalamic 
mkdir hypo_preoptic
cd hypo_preoptic
wget -c http://www.bgiocean.com/vt3d_example/download/merfish/hypo_preoptic.h5ad
wget -c http://www.bgiocean.com/vt3d_example/download/merfish/mesh.tar.gz
wget -c http://www.bgiocean.com/vt3d_example/download/merfish/hypo_preoptic.atlas.json
wget -c http://www.bgiocean.com/vt3d_example/download/merfish/hypo_preoptic.coord.json
wget -c http://www.bgiocean.com/vt3d_example/download/merfish/hypo_preoptic.organ.json
tar -xzf mesh.tar.gz
cd ../
```

You can find all download commands from [website](http://www.bgiocean.com/vt3d_example/)

### <a name=quick_atlasbrowser>How to use AtlasBroser to browse your data</a>

You can find a step-by-step tutorial for building an atlas from [website](http://www.bgiocean.com/vt3d_example/).

Here we use L1 atlas as an example:

#### Generate web cache folder

```
cd L1
vt3d AtlasBrowser BuildAtlas -i L1_a_count_normal_stereoseq.h5ad -o L1_Atlas -c L1_a.atlas.json

```

#### Start the web server and browse your data now!

```
cd L1_Atlas && vt3d AtlasBrowser LaunchAtlas -p 80
```

now open your web browser and try ```http://127.0.0.1/index.html```

![image](https://user-images.githubusercontent.com/8720584/210740473-3554fe92-4d12-493b-9cb1-c2d9986622da.png)


### <a name=quick_anyslicer>How to create and visualize virtual slices</a>

we use the E16-18h dataset as an example:

#### create one virtual slice 
```
cd E16_E18h 
vt3d AnySlice -i E16-18h_a_count_normal_stereoseq.h5ad  -o test --spatial_key spatial  --p0 '25,0,10', --p1 '50,30,0' --p2 '5,30,0' --thickness 1
```
#### or create five continuous virtual slices
```
cd E16_E18h 
vt3d AnySlice -i E16-18h_a_count_normal_stereoseq.h5ad  -o test_s5 --spatial_key spatial  --p0 '25,0,10', --p1 '50,30,0' --p2 '5,30,0' --thickness 1 --slice_num 5
```
#### visualize virtual slices colored by annotations
```
vt3d  Auxiliary DrawSlices -i test_s5.h5ad -o drawan --color_by annotation
```
![image](https://user-images.githubusercontent.com/8720584/210742577-5b445440-94f5-4eb0-bf22-4b8a422c0d96.png)

#### visualize virtual slices colored by raw slice id ( another column from obs dataframe )
```
vt3d  Auxiliary DrawSlices -i test_s5.h5ad -o drawrs --color_by slice_ID
```
![image](https://user-images.githubusercontent.com/8720584/210742982-0eb4fbb9-ec69-4e20-95ce-b4fe167f17c8.png)

#### visualize virtual slices colored by gene expression
```
vt3d  Auxiliary DrawSlices -i test_s5.h5ad -o drawgn --color_by Acbp2
```
![image](https://user-images.githubusercontent.com/8720584/210743105-2a954054-51df-4b3a-9a30-b2436cfefa3d.png)

### <a name=quick_mep>How to create MEP images</a>
#### create an MEP image
```
cd hypo_preoptic
vt3d MEP  -i hypo_preoptic.h5ad --gene Baiap2 -o Baiap2
```
![image](https://user-images.githubusercontent.com/8720584/210746260-3b3fa2ba-9a3d-4579-b203-9420047367e3.png)


#### create an MEP image in pseudoFISH mode
```
cd hypo_preoptic
vt3d MEP  -i hypo_preoptic.h5ad -m Baiap2 -o Baiap2 
```
![image](https://user-images.githubusercontent.com/8720584/210746047-17b7f709-ec8d-4440-a942-a22866f3f449.png)

Note: in pseudoFISH mode, you can use one of the following fluorescence colors
```
-m refers to magenta 
-g refers to green
-y refers to yellow
-c refers to cyan
-r refers to red
-b refers to blue
```

#### How to create an MEP image at a user-defined angle?
First of all, the default view is APML plane (xy plane). You can switch to another view plane perpendicular to coordinate axes using ```--view=MLDV``` (yz plane)  or  ```--view=APDV``` (xz plane)

To get the 2D projection to an arbitrary plane defined by three non-collinear points, plesase use ```--view=[[0,0,0],[1,0,0],[1,1,0]]``` 


### <a name=quick_models>How to create surface models from omics data</a>
![fa00f9efe371da658bd59e3ca0c78be](https://user-images.githubusercontent.com/8720584/210744364-af476dbb-9f49-4be4-ac9e-c7ffc3435bc7.png)


```
cd hypo_preoptic
vt3d Auxiliary GrayScaleTIF -i  hypo_preoptic.h5ad  -o test3d -c  hypo_preoptic.organ.json
```
Note: This action will generate hypo_preoptic.coord.json

The test3d.tif (opened by ImageJ 3DViewer)  :
![image](https://user-images.githubusercontent.com/8720584/210910747-d376be6c-7434-4fcb-83d0-f97adf6fbfa0.png)


## <a name=q_a>Frequent Q & A</a>

#### Why can't I extract 3D coordinates from the input file?

The default keyname for 3D spatial coordinates is spatial3D. Please make sure your coordinates are stored in obsm. You can use ```--spatial_key xxx``` to assign a different keyname.

#### Why do we need fixed.json?
Use fixed.json if you want to display the surface model in the same coordinate system of h5ad data. 
fixed.json
```
{"xmin": 0, "ymin": 0,  "margin": 0, "zmin": 0, "binsize": 1}
```
Sometimes the surface model need to be shifted and scaled to fit the h5ad data, for example:
hypo_preoptic.coord.json
```
{"xmin": -897, "ymin": -897, "xmax": 897, "ymax": 897, "margin": 10, "zmin": -290, "zmax": 260, "binsize": 50}
```
the surface model coordinate will be changed to

1. multiple by 50
2. x add -897
2. y add -897
3. z add -290

#### How can I get coordinates for three points to define a plane of interest?

There are lots of ways for obtaining 3D coordinates of three non-collinear points. One straightforward way is to freely acquire coordinates using our 3D atlas browser.

## <a name=contact>Contact us</a>

1. Raising an issue is always a good way for questions
2. Email us if you need: guolidong@genomics.cn;liyao1@genomics.cn;xumengyang@genomics.cn

## <a name=usages>Detailed usages</a>

### entry usage of vt3d
```
> vt3d -h
Usage : vt3d <action> [options ]
          -h/--help           show this short usage
Action:
          -------------------------------------------------------------------------------
          MEP                   Maximun Expression Projection. (project 3D structure to 2D)
          AnySlice              Extract a 2D slice from any given angle
          AtlasBrowser          Browse your data interactively
          Auxiliary             More auxiliary tools
          -------------------------------------------------------------------------------

Detailed usage of each action:
        vt3d <action> -h
```

### Detailed usage of MEP action

```
Usage: vt3d MEP  [options]

Options:
       required configurations:
            -i <input.h5ad>
            -o <output prefix>

       RdRlBu_r mode
            --gene geneid
            [note: enable --gene will override all pseudoFISH mode parameters]

       pseudoFISH mode
            -r [geneid shown in Red(#ff0000) channel]
            -g [geneid shown in Green(#00ff00) channel]
            -c [geneid shown in Cyan(#00ffff) channel]
            -m [geneid shown in Magenta(#ff00ff) channel]
            -y [geneid shown in Yellow(#ffff00) channel]
            -b [geneid shown in Blue(#0000ff) channel]

       optional configurations:
            --binsize [default 5]
            --spatial_key [defaut spatial3D, the keyname of coordinate array in obsm]
            --view [default APML, must be APML/APDV/MLDV]
                   [APML -> xy plane]
                   [APDV -> xz plane]
                   [MLDV -> yz plane]
            --plane [default '', example: "[[0,0,0],[1,0,0],[1,1,0]]" ]
                    [define any plane by three points]
                    [note: enable --plane will override --view]
            --drawborder [default 0, must be 1/0]
            --symbolsize [default 10, only used in RdYlBu_r mode]

       optional ROI options:
            --xmin [default None]
            --ymin [default None]
            --zmin [default None]
            --xmax [default None]
            --ymax [default None]
            --zmax [default None]
Example:
     #example of RdYlBu_r mode, will generate test.png
     vt3d MEP -i in.h5ad -o test --gene wnt1 --view APML

     #example of pseudoFISH mode, will generate test.tif :
     vt3d MEP -i in.h5ad -o test -r notum -g wnt1 -m foxD --view APML

     #example of RdYlBu_r mode with an assigned plane
     vt3d MEP -i in.h5ad -o test --gene wnt1 --plane '[[0,0,0],[1,0,0],[1,1,0]]'

```

### Detailed usage of AnySlice

```
Usage: vt3d AnySlice [options]

Options:
       required configurations:
            -i <input.h5ad>
            -o <output prefix>
            --p0 <coordinate of p0>
            --p1 <coordinate of p1>
            --p2 <coordinate of p2>

       optional configurations:
            --thickness [default 16]
            --slice_num [default 1]
            --slice_step [default equal to thickness]
            --spatial_key [default 'spatial3D', the keyname of coordinate array in obsm]
Example:
    > vt3d AnySlice -i in.h5ad -o test --p0 "0,1,0" --p1 "1,0,0" --p2 "1,1,0"
    > ls
    test.h5ad

```

### Detailed usage of AtlasBrowser

```
    vt3d AtlasBrowser subaction:
          BuildAtlas            Generate cache files for WebCache action.
          LaunchAtlas           Start the atlas server for VT3D_Browse in the WebCache folder.
```

####  Detailed usage of AtlasBrowser - BuildAtlas

```
Usage: vt3d AtlasBrowser BuildAtlas [options]

Options:
       required configurations:
            -i <input.h5ad>
            -c <conf.json>
            -o [output prefix, default webcace]
Example:
        > vt3d AtlasBrowser BuildAtlas -i in.h5ad -c atlas.json
        > cat atlas.json
        {
            "Coordinate" : "spatial3D",
            "Annotations" : [ "lineage" ],
            "Meshes" : {
                "body" : "example_data/body.obj" ,
                "gut" : "example_data/gut.obj"     ,
                "neural" : "example_data/neural.obj" ,
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

Note:
     Set "Genes" : ["all"] to export all genes in var.

The structure of the output atlas folder:
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

#### Detailed usage of AtlasBrowser LaunchAtlas

```
Usage: vt3d AtlasBrowser LaunchAtlas [options]

Options:
            -p [port, default 80]
Example:
        > vt3d WebServer

        ...
        never stop until you press Ctrl-C
```

### Detailed usage of Auxiliary
```
  vt3d Auxiliary subaction:
          GrayScaleTIF          Generate 3D TIFF grayscale image as input of Slicer3D.
          DrawVitrualSlices     Draw 2D image group as virtual slices
```
####  Detailed usage of Auxiliary - GrayScaleTIF
```
Usage: vt3d Auxiliary GrayScaleTIF [options]

Options:
       required configurations:
            -i <input.h5ad>
            -o <output prefix>
            -c <conf.json>
            --spatial_key [default 'spatial3D', the keyname of coordinate array in obsm]
Example:
        > vt3d Auxiliary GrayScaleTIF -i in.h5ad -o test -c organ.json
        > cat organ.json
        {
            "binsize" : 10,
            "margin" : 10,
            "keyname" : "annotation",
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
####  Detailed usage of Auxiliary - DrawVitrualSlices

```
    vt3d Auxiliary DrawVitrualSlices [options]
            -i                  input h5ad
            -o                  output prefix
            --color_by          gene name or annotation keywork
            --vsid_key          [default vsid, key of virtual slice id]
            --coord2D           [default spatial2D, keyname in obsm]
            -t                  [default pdf, output type (png or pdf)]
            -h/--help           display this usage and exit
```
