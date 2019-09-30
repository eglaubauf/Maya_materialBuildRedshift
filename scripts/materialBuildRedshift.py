#####################################
#LICENSE                            #
#####################################
#
# Copyright (C) 2019  Elmar Glaubauf
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
"""

This script will create a Redshift Node Network based on a file selection

Twitter: @eglaubauf
Web: www.elmar-glaubauf.at

"""

#import pymel.core as pm
import maya.cmds as cmds
import maya.OpenMayaUI as omui


# Where is this script?
#SCRIPT_LOC = os.path.split(__file__)[0]

'''
Open with

import copyToFarm.controller as copyToFarmCtrl
reload(copyToFarmCtrl)
copyToFarmCtrl.open()
    
'''

#Create Object
def open():
    MaterialBuilder()

class MaterialBuilder():

    def __init__(self):
        
        self.initVars()
        #Ask the User for Files
        self.getName()
        if self.destroy == 1:
            return
        #Get Files from user
        self.getFiles()
        if self.destroy == 1:
            return
        self.createMaterial()

    def initVars(self):
        self.destroy = 0
        self.ocio = cmds.colorManagementPrefs(q=True, cfe=True)

    def getFiles(self):

        self.files = cmds.fileDialog2(cap='Choose Files to Create a Material from',fm=4)
        if self.files is None:
            self.destroy = 1

    def getName(self):
        #Get Shadername by user
        
        result = cmds.promptDialog(m='Please give a name for the new Material', t='MaterialName')
        #Check if okay
        if result == 'dismiss':
            self.destroy = 1
            return
        #Get Result now -- MayaThings....            
        self.username = cmds.promptDialog(query=True, text=True)

    def createMaterial(self):
  
        #Create StandardSurface
        myShader = cmds.shadingNode('RedshiftMaterial', n=self.username, asShader=True)
        sg = cmds.sets(name=self.username+'_SG', empty=True, renderable=True, noSurfaceShader=True)
        #Connect
        cmds.connectAttr( self.username+'.outColor', self.username+'_SG.surfaceShader' )

        #Create A Text Node for each File
        for f in self.files:
            self.createTexture(f, myShader,sg)
            
    
    def createTexture(self, tex, parent, sg):

        #Remove Spaces
        tex = tex.rstrip(' ')
        tex = tex.lstrip(' ')
        
        #Get Name of File
        name = tex.split(".")
        k = name[0].rfind("/")
        name = name[0][k+1:]

        #Check which types have been selected. Config as you need
        if "base_color" in name.lower() or "basecolor" in name.lower():
            self.createFile(tex, parent, 'diffuse_color')         
        elif "roughness" in name.lower() or "rough" in name.lower():
            self.createFileSingleChannel(tex, parent, 'refl_roughness')
        elif "specular" in name.lower() or "spec" in name.lower():
            self.createFileSingleChannel(tex, parent, 'refl_weight')
        elif "normal" in name.lower():
            self.createNormal(tex, parent)
        elif "metallic" in name.lower():
            self.createFileSingleChannel(tex, parent, 'refl_metalness')
        elif "reflect" in name.lower():
            self.createFileSingleChannel(tex, parent, 'refl_weight')
        elif "height" in name.lower() or "displace" in name.lower() or "displacement" in name.lower():
            self.createDisplacement(tex, sg)    
        elif "bump" in name.lower():
            self.createBump(tex, parent)  
    
    def createFile(self, tex, parent, connector):

        #Create File Texture
        fileNodeName = parent + '_' + connector
        fileNode = cmds.shadingNode('file', n=fileNodeName, asTexture=True)
        cmds.setAttr(fileNode+'.fileTextureName', tex, type="string")
        
        #Set ColorSpace
        if self.ocio is False:
            if self.checkLinear(tex) is False: 
                cmds.setAttr(fileNode+'.colorSpace','sRGB', type='string')
            else:
                cmds.setAttr(fileNode+'.colorSpace','Raw', type='string')
        else:
            if self.checkLinear(tex) is True:  
                cmds.setAttr(fileNode+'.colorSpace','Utility - Raw', type='string')
            else:
                cmds.setAttr(fileNode+'.colorSpace','Utility - sRGB - Texture', type='string')

        #Create UV Node
        uvNodeName = 'place2d_'+ fileNodeName
        uvNode = cmds.shadingNode('place2dTexture', n=uvNodeName, asUtility=True)

        self.connectUvFile(fileNode, uvNode)

        #Connects All Channels
        cmds.connectAttr( fileNode+'.outColor', parent+'.'+connector)

    def checkLinear(self, path):

        checkList = ['png', 'jpg', 'jpeg']

        for c in checkList:
            if path.endswith(c):
                return False
            pass
        return True

    
    def createFileSingleChannel(self, tex, parent, connector):

        #Create File Texture
        fileNodeName = parent + '_' + connector
        fileNode = cmds.shadingNode('file', n=fileNodeName, asTexture=True)
        cmds.setAttr(fileNode+'.fileTextureName', tex, type="string")
        
        #Set ColorSpace
        if self.ocio is False:
                cmds.setAttr(fileNode+'.colorSpace','Raw', type='string')
        else:
                cmds.setAttr(fileNode+'.colorSpace','Utility - Raw', type='string')

        #Create UV Node
        uvNodeName = 'place2d_'+ fileNodeName
        uvNode = cmds.shadingNode('place2dTexture', n=uvNodeName, asUtility=True)

        self.connectUvFile(fileNode, uvNode)

        #Connects only the R Channel
        cmds.connectAttr( fileNode+'.outColorR', parent+'.'+connector)


    def createNormal(self, tex, parent):
        
        #Create NormalMapNode
        normalName = parent + '_normal'
        normal = cmds.shadingNode('RedshiftBumpMap', n=normalName, asTexture=True)
        #Connect to Shader
        cmds.connectAttr( normal+'.out', parent+'.bump_input')
        cmds.setAttr(normal+'.inputType', 1)

        #Create File Texture
        fileNodeName = parent + '_NormalFile'
        fileNode = cmds.shadingNode('file', n=fileNodeName, asTexture=True)
        cmds.setAttr(fileNode+'.fileTextureName', tex, type="string")
        #Connect to NormalMap
        cmds.connectAttr( fileNode+'.outColor', normal+'.input')
        
        #Set ColorSpace
        if self.ocio is False:
                cmds.setAttr(fileNode+'.colorSpace','Raw', type='string')
        else:
                cmds.setAttr(fileNode+'.colorSpace','Utility - Raw', type='string')
                

        #Create UV Node
        uvNodeName = 'place2d_'+ fileNodeName
        uvNode = cmds.shadingNode('place2dTexture', n=uvNodeName, asUtility=True)

        #Connect UV and Files
        self.connectUvFile(fileNode, uvNode)
        
    def createBump(self,tex,parent):
        
        #Create NormalMapNode
        bumpName = parent + '_bump'
        bump = cmds.shadingNode('RedshiftBumpMap', n=bumpName, asTexture=True)
        #Connect to Shader
        cmds.connectAttr( bump+'.out', parent+'.bump_input')
       
        #Create File Texture
        fileNodeName = parent + '_NormalFile'
        fileNode = cmds.shadingNode('file', n=fileNodeName, asTexture=True)
        cmds.setAttr(fileNode+'.fileTextureName', tex, type="string")
        #Connect to NormalMap
        cmds.connectAttr( fileNode+'.out', bump+'.input')

        #Set ColorSpace
        if self.ocio is False:
                cmds.setAttr(fileNode+'.colorSpace','Raw', type='string')
        else:
                cmds.setAttr(fileNode+'.colorSpace','Utility - Raw', type='string')

        #Create UV Node
        uvNodeName = 'place2d_'+ fileNodeName
        uvNode = cmds.shadingNode('place2dTexture', n=uvNodeName, asUtility=True)

        #Connect UV and Files
        self.connectUvFile(fileNode, uvNode)
        
    def createDisplacement(self, tex, parent):
        
        #Create NormalMapNode
        displaceName = parent + '_displace'
        displace = cmds.shadingNode('RedshiftDisplacement', n=displaceName, asShader=True)
        #Connect to Shader
        cmds.connectAttr( displace+'.out', parent+'.rsDisplacementShader')
       
        #Create File Texture
        fileNodeName = parent + '_NormalFile'
        fileNode = cmds.shadingNode('file', n=fileNodeName, asTexture=True)
        cmds.setAttr(fileNode+'.fileTextureName', tex, type="string")
        
        #Set ColorSpace
        if self.ocio is False:
            cmds.setAttr(fileNode+'.colorSpace','Raw', type='string')
        else:
            cmds.setAttr(fileNode+'.colorSpace','Utility - Raw', type='string')
        
        #Connect to NormalMap
        cmds.connectAttr( fileNode+'.outColor', displace+'.texMap')

        #Create UV Node
        uvNodeName = 'place2d_'+ fileNodeName
        uvNode = cmds.shadingNode('place2dTexture', n=uvNodeName, asUtility=True)

        #Connect UV and Files
        self.connectUvFile(fileNode, uvNode)

    #Connect UV and File node
    def connectUvFile(self, fileNode, uvNode):
        
        cmds.connectAttr(uvNode+'.outUV', fileNode+'.uvCoord')
        cmds.connectAttr(uvNode+'.outUvFilterSize', fileNode+'.uvFilterSize')
        cmds.connectAttr(uvNode+'.coverage', fileNode+'.coverage')
        cmds.connectAttr(uvNode+'.mirrorU', fileNode+'.mirrorU')
        cmds.connectAttr(uvNode+'.mirrorV', fileNode+'.mirrorV')
        cmds.connectAttr(uvNode+'.noiseUV', fileNode+'.noiseUV')
        cmds.connectAttr(uvNode+'.offset', fileNode+'.offset')
        cmds.connectAttr(uvNode+'.repeatUV', fileNode+'.repeatUV')
        cmds.connectAttr(uvNode+'.rotateFrame', fileNode+'.rotateFrame')
        cmds.connectAttr(uvNode+'.rotateUV', fileNode+'.rotateUV')
        cmds.connectAttr(uvNode+'.stagger', fileNode+'.stagger')
        cmds.connectAttr(uvNode+'.translateFrame', fileNode+'.translateFrame')
        cmds.connectAttr(uvNode+'.wrapU', fileNode+'.wrapU')
        cmds.connectAttr(uvNode+'.wrapV', fileNode+'.wrapV')
        cmds.connectAttr(uvNode+'.vertexUvOne', fileNode+'.vertexUvOne')
        cmds.connectAttr(uvNode+'.vertexUvTwo', fileNode+'.vertexUvTwo')
        cmds.connectAttr(uvNode+'.vertexUvThree', fileNode+'.vertexUvThree')
        cmds.connectAttr(uvNode+'.vertexCameraOne', fileNode+'.vertexCameraOne')




        
 