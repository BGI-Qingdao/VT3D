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
* plotly

## Dowload

```
git clone https://github.com/BGI-Qingdao/VT3D.git ./VT3D
```

## Quick introduction of vt3d_visitor with test data

* enter VT3D_visitor folder
``` cd ./VT3D/VT3D_visitor ```
* prepare the test data
```
cd ./example_data
gzip -dc WT.VT3D.h5ad.gz >WT.VT3D.h5ad
cd ../
```

### Generate MEP image

```
./vt3d_visitor MEP -i example_data/WT.VT3D.h5ad -o gut.SMED30007704 -g SMED30007704
```

### AnySlice

```
./vt3d_visitor  AnySlice -i example_data/WT.VT3D.h5ad -o test --p0 '0,0,200' --p1 '1,0,200' --p2 '1,1,200'
```

### Generate grayscale 3D tiff

```
./vt3d_visitor GrayScaleTif -i  example_data/WT.VT3D.h5ad  -o test3d -c example_data/organ.json
```

## Quick introduction of vt3d_browser
```
TODO
```

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
          GrayScaleTif          Generate 3D TIFF gray scale image as input of Slicer3D
          WebCache              Generate cache files as input VT3D_browser.
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
