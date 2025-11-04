#the 3ds max weight tool, but in maya 
#created by thomas dameris

import maya.cmds as cmds
import maya.mel as mel
from maya.api.OpenMaya import MMatrix

print("hotkey test")
def importLibs():
    import maya.cmds as cmds
    import maya.mel as mel
    from maya.api.OpenMaya import MMatrix

def sanityCheck():
    print("running skin function start up processes")
    mel.eval("ArtPaintSkinWeightsTool;") 
    cmds.setToolTo('selectSuperContext')
    print("skin tools imported. you arent insane... today")

#keep track of tool contexts so you dont accidently delete them or confuse maya     
def contextCheck():
    ctx = cmds.currentCtx()
    if not ctx or not ctx.startswith("artAttrSkinPaintCtx"):
        mel.eval("ArtPaintSkinWeightsTool;") 
        ctx = cmds.currentCtx()
    return ctx

############################### CLEAN UP FUNCTIONS ######################################

#normalize the weights of a skin cluster
def normalizeWeights(mesh):
    mel.eval("PolySelectConvert 3;")
    verts = cmds.ls(sl=True, fl=True)
    shape = cmds.listRelatives(verts[0], p=True)[0]
    mesh = cmds.listRelatives(shape, p=True)[0]   
    skinCluster = (cmds.ls(cmds.listHistory(mesh) or [], type="skinCluster") or [None])[0]
    cmds.skinPercent(skinCluster, mesh, nrm = True)
    print("weights notmalized")
    
#prune weights below the selected value in the UI
def pruneWeights(sel, tolerance):
    cmds.undoInfo(ock = True)
    mel.eval("PolySelectConvert 3;")
    verts = cmds.ls(sl=True, fl=True)
    shape = cmds.listRelatives(verts[0], p=True)[0]
    mesh = cmds.listRelatives(shape, p=True)[0]   
    skinCluster = (cmds.ls(cmds.listHistory(mesh) or [], type="skinCluster") or [None])[0]
    cmds.skinPercent(skinCluster, mesh, pruneWeights= tolerance, normalize=True)
    print(f"weights pruned below {tolerance}")
    cmds.undoInfo(cck = True)

########################### 3DS MAX WEIGHT TOOL FUNCTIONS ################################
#select targets for skinning
def scaleSelection(operation):
    verts = cmds.ls(sl = True)
    if operation == 2 and len(verts) <=1:
        cmds.polySelectConstraint(pp = 0) 
    else: 
        print(operation)
        cmds.polySelectConstraint(pp = operation) 

def selectObject(sel):
    mel.eval("PolySelectConvert 3;")
    verts = cmds.ls(sl=True, fl=True)
    shape = cmds.listRelatives(verts[0], p=True)[0]
    cmds.select(shape)
    cmds.ls(sl=True, fl=True)

#get the weights of a vertex, but from only the selected influence. return it to be plugged into UI
def pickWeight(sel, influence):
     
    sourceVert = sel[0]
    shape = cmds.listRelatives(sourceVert, p=True)[0]
    skinCluster = (cmds.ls(cmds.listHistory(shape) or [], type="skinCluster") or [None])[0]
    vertWeight = cmds.skinPercent(skinCluster, sourceVert, transform = influence, q = True)
    print(f"weight picked: {vertWeight}")
   
    return vertWeight

#set weight of an influence on selected verts
def setInfluenceWeight(sel, influence, weight, normalize = True):
    
    cmds.undoInfo(ock = True)

    mel.eval("PolySelectConvert 3;")

    targetVerts = cmds.ls(cmds.ls(sl=True), fl=True) or []
    if not targetVerts:
        cmds.error("select verts")
    mesh = targetVerts[0].split('.')[0]
    shape = (cmds.listRelatives(mesh, s=True, ni=True, f=True) or [None])[0]
    skinCluster = (cmds.ls(cmds.listHistory(shape) or [], type="skinCluster") or [None])[0]
    if not skinCluster:
        cmds.error("no skin cluster found")
    
    allInfluences = cmds.skinCluster(skinCluster, q=True, influence=True) or []
    if influence not in allInfluences:
        cmds.error("Influence '{}' not on {}.".format(influence, skinCluster))    
    
    cmds.skinPercent(skinCluster, targetVerts,
                     transformValue=[(influence, float(weight))],
                     normalize=normalize)
  
    print(f"weights set on verts: {weight}")

    cmds.undoInfo(cck = True)

def scaleWeights(sel, influence, scaleVal, clamp=True):
    
    cmds.undoInfo(ock = True)

    verts = cmds.ls(sel or cmds.ls(sl=True, fl=True), fl=True) or []
    if not verts:
        cmds.error("select verts")
    if not isinstance(influence, str):
        cmds.error("must select a joint in skin cluster")

    #get skin cluster
    shape = cmds.listRelatives(verts[0], p=True)[0]
    skinCluster = (cmds.ls(cmds.listHistory(shape) or [], type="skinCluster") or [None])[0]   
    #make sure the influence is in the skin cluster
    all_infs = cmds.skinCluster(skinCluster, q=True, influence=True) or []
    if influence not in all_infs:
        cmds.error(f"influence {influence} is not in skinCluster {skinCluster}.")

    scaleVal = float(scaleVal)

    for vert in verts:
        weight = cmds.skinPercent(skinCluster, vert, q=True, transform=influence, value=True)
        if isinstance(weight, (list, tuple)):
            weight = weight[0]

        scaledWeight = weight * scaleVal
        if clamp:
            scaledWeight = max(0.0, min(1.0, scaledWeight))
        cmds.skinPercent(skinCluster, vert, transformValue=[(influence, scaledWeight)], normalize=True)
    print(f"weights scaled by {scaleVal}")

    cmds.undoInfo(cck = True)
       
def copyWeights(sel):
    mel.eval("PolySelectConvert 3;")
    sel = cmds.ls(sl=True, fl=True)
    sourceVert = sel[0]
    shape = cmds.listRelatives(sourceVert, p=True)[0]
    skinCluster = (cmds.ls(cmds.listHistory(shape) or [], type="skinCluster") or [None])[0]
    influences = cmds.skinCluster(sourceVert, query=True, influence=True) or []
    weights = cmds.skinPercent(skinCluster, sourceVert, q = True, value = True)
    copiedWeights = list(zip(influences, weights))
    print(copiedWeights)
    return copiedWeights

def pasteWeights(copiedWeights, sel):
    mel.eval("PolySelectConvert 3;")
    verts = cmds.ls(sl=True, fl=True)
    targetVerts = verts[0:]
    #targetVerts[0].split('.')[0]
    print(f"copied weights = {copiedWeights}") 
    shape = cmds.listRelatives(targetVerts, p=True)[0]
    skinCluster = (cmds.ls(cmds.listHistory(shape) or [], type="skinCluster") or [None])[0]   
    print(skinCluster)
    cmds.skinPercent(skinCluster, targetVerts, transformValue = copiedWeights)
    print("weights pasted")

def getCurrentInfluences(sel=None, threshold=0.0001):
    mel.eval("PolySelectConvert 3;")    
    verts = cmds.ls(cmds.ls(sl=True), fl=True) or []
    if not verts:
        cmds.error("select verts")
    
    mesh = verts[0].split('.')[0]
    shape = (cmds.listRelatives(mesh, s=True, ni=True, f=True) or [None])[0]
    skinCluster = (cmds.ls(cmds.listHistory(shape) or [], type="skinCluster") or [None])[0]
    if not skinCluster:
        cmds.error("no skin cluster found")
    
    influenceList = []
    influences = cmds.skinCluster(skinCluster, q=True, influence=True) or []

    for vert in verts:
        weights = cmds.skinPercent(skinCluster, vert, q=True, value=True)  
        for joint, w in zip(influences, weights):
            if w > threshold:
                if joint in influenceList:
                    continue
                else:
                    influenceList.append(joint)
    
    print(f"influence list = {influenceList}")

    return influenceList

########################### PAINT WEIGHT FUNCTIONS ################################

def setIntensity(value):
    ctx = "artAttrSkinContext"
    cmds.artAttrSkinPaintCtx(ctx, e = True, value = value)

def updateIntensity():
    ctx = "artAttrSkinContext"
    return cmds.artAttrSkinPaintCtx(ctx, q = True, value = True)

def contextCheck():
    ctx = cmds.currentCtx()
    if not ctx or not ctx.startswith('artAttrSkinPaintCtx'):
        mel.eval('ArtPaintSkinWeightsTool;')
        ctx = cmds.currentCtx()
    print(f"current context = {ctx}")
    return ctx

def updateViewport(influence): 
     ctx = contextCheck() 
     currentInfluence = cmds.artAttrSkinPaintCtx(ctx, q=True, influence = True) 
     mel.eval(f' artAttrSkinToolScript 3; artSkinInflListChanging {currentInfluence} 0; artSkinInflListChanging "{influence}" 1; artSkinInflListChanged artAttrSkinPaintCtx; artAttrSkinPaintModePaintSelect 1 artAttrSkinPaintCtx;')
     #print("viewport updated in func file")











