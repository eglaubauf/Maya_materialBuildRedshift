## A MaterialBuilder Script for Redshift in Autodesks Maya 

### Features

- Provides a Materialbuilder for a Redhshift Material
- The Function checks if OCIO is enabled and set ColorSpaces accordingly
- creates a tree based on Filnames and works best with strings provided by Substance
  - base_color or basecolor
  - roughness
  - normal
  - metallic
  - reflect
  - height
  - displace
  - bump
- The strings to look for can easily be changed at the bottom of each script
- A shelf is provided in the shelves folder 

###  Example Node tree for MaterialBuilder

![alt text](https://raw.githubusercontent.com/eglaubauf/Maya_materialBuildRedshift/master/images/Tree.png "The Tree created by one of the Scripts")

### Installation:

1. Create a new Folder called 'materialBuildRedshift' at this location: C:\Users\<User>\Documents\maya\2019\scripts 
2. Copy the content from the provided scripts folder into the newly created folder
3. To access the shelf copy the file  shelf_MaterialBuildArnold.mel to your shelves directory (C:\Users\<user>\Documents\maya\2019\prefs\shelves)
4. Optionally you can create your shelf yourself via the following python-command:

```
import materialBuildArnold.materialBuildArnold as mb
reload(mb)
mb.open()
```
### TODO:
   -  tx conversion
   -  checkboxes for user
   -  better configuration for searched names


### Notes:

All of the scripts are free of charge for free use, commercial or non commercial whatsoever. 
But this scripts may brake your workflow.

### Contact/Issues/Features/Questions

Please check out my other Repos as well, they might be handy to you. For any questions and/or improvement suggestions just contact me via twitter or mail.<br>
Twitter: @eglaubauf <br>
Web: www.elmar-glaubauf.at
