import bpy
import os
import random
import re
import sys
from bounding_box import calculate_combined_bounding_box
import math

path_to_glb_folder = r"C:\Users\gabri\.objaverse\hf-objaverse-v1\glbs" #If you are using Windows use r"\Users\Path\To\Folder"
path_to_jpeg_folder = "/Users/Path/To/Folder"

def roundup(x):
    return math.ceil(x / 10.0) * 10

def deleteAllObjects():
    """
    Deletes all objects in the current scene
    """
    deleteListObjects = ['MESH', 'CURVE', 'SURFACE', 'META', 'FONT', 'HAIR', 'POINTCLOUD', 'VOLUME', 'GPENCIL',
                         'ARMATURE', 'LATTICE', 'EMPTY', 'LIGHT', 'LIGHT_PROBE', 'CAMERA', 'SPEAKER']

    collection = bpy.data.collections.get("MyTestCollection")
    # Select all objects in the scene to be deleted:
    if collection:
        for obj in collection.objects:
            bpy.data.objects.remove(obj, do_unlink=True)
        bpy.data.collections.remove(collection)
#    for o in bpy.context.scene.objects:
#        if(o in bpy.context.selected_objects):
#            for i in deleteListObjects:
#                if o.type == i:
#                    o.select_set(False)
#                else:
#                    o.select_set(True)
#    if len(bpy.context.scene.objects)>0:
#        bpy.ops.object.delete(True) # Deletes all selected objects in the scene

deleteAllObjects()

glb_dirList = os.listdir(path_to_glb_folder)
print(glb_dirList)

random.seed(43)
glb_dirList = random.sample(glb_dirList, 5)

print(glb_dirList)

glb_truePaths = []

removeList = [".gitignore", ".DS_Store"]
for x in glb_dirList:
    glb_folder_path = os.path.join(path_to_glb_folder,x)
    glb_folder_dirList = os.listdir(glb_folder_path)
    
    print(glb_folder_dirList)
    for glb_in_folder in glb_folder_dirList:
        if (re.search('\.glb',glb_in_folder)):
            glb_truePaths.append(os.path.join(glb_folder_path,glb_in_folder))
            print(glb_truePaths)

print(glb_truePaths[0])

#removeList = [".gitignore", ".DS_Store"] # If you have . files in your directory
#glb_dirList = [x for x in glb_dirList if (x not in removeList)]
glb_dirList = glb_truePaths

collection_name="MyTestCollection"
bpy.ops.collection.create(name  = "MyTestCollection")
bpy.context.scene.collection.children.link(bpy.data.collections["MyTestCollection"])
collection = bpy.data.collections.get(collection_name)

for i in glb_dirList:
    bpy.ops.import_scene.gltf(filepath=i) # Import .glb file to scene
    obj = bpy.context.object
    
   
#    if obj and collection:
#        collection.objects.link(obj)
#        
#    for col in obj.users_collection:
#        if col != collection:
#         col.objects.unlink(obj)
    
    min_corner,max_corner = calculate_combined_bounding_box(obj)
    dim = max_corner - min_corner
    print(bpy.context.object.dimensions)
    vol = abs(dim[0] * dim[1] * dim[2])
    if (vol)>24:
        vol=roundup(max(dim))
        obj.scale[0] = 1/vol#abs(dim[0])
        obj.scale[1] = 1/vol#abs(dim[1])
        obj.scale[2] = 1/vol#abs(dim[2])
    obj = bpy.context.active_object
    
    bpy.ops.object.select_all(action='DESELECT')
    
    # Traverse up to the root parent
    while obj.parent:
        obj = obj.parent
        
     # Function to move an object and its children to the new collection
    def move_to_collection(obj, collection):
        # Unlink the object from all current collections
        for col in obj.users_collection:
            col.objects.unlink(obj)
        
        # Link the object to the new collection
        collection.objects.link(obj)
        
        # Recursively move all children
        for child in obj.children:
            move_to_collection(child, collection)
    
    # Move the parent object and all its children
    move_to_collection(obj, collection)
           
    # Select the root object
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    
    bpy.ops.object.randomize_transform(random_seed =random.randint(0,100), loc=(2, 2, 0), scale=(1, 1, 1))
#    bpy.context.scene.render.filepath = path_to_jpeg_folder # Set save path for images
#    bpy.context.scene.render.image_settings.file_format = "JPEG" # Set image file format
#    bpy.ops.render.render(write_still=True) # Tell Blender to render an image
