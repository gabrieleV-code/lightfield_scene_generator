import bpy
import os
import random
import re
import sys
from src.lfrenderer.scene.custom.utils.bounding_box import calculate_combined_bounding_box
import math
from src.lfrenderer.scene.custom.utils.random_displacement import displace_objects
import numpy as np

path_to_glb_folder = r"C:\Users\gabri\.objaverse\hf-objaverse-v1\glbs" #If you are using Windows use r"\Users\Path\To\Folder"
path_to_jpeg_folder = "/Users/Path/To/Folder"

def roundup_(number):
    if number == 0:
        return 0
    # Find the nearest power of 10 by rounding the log10 of the number
    power = round(math.log10(abs(number)))
    return 10 ** power

def roundup(number):
    i = 0
    while(number>=1):
        number = number/10
        i +=1 
    return i    

def deleteObject(obj):
        for c in obj.children:
            deleteObject(c)
        bpy.data.objects.remove(obj, do_unlink=True)

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

def load_Objects(object_number):
    deleteAllObjects()

    glb_dirList = os.listdir(path_to_glb_folder)
    print(glb_dirList)

    #random.seed(random.random())
    glb_dirList = random.sample(glb_dirList, object_number)

    glb_truePaths = []

    removeList = [".gitignore", ".DS_Store"]
    for x in glb_dirList:
        glb_folder_path = os.path.join(path_to_glb_folder,x)
        glb_folder_dirList = os.listdir(glb_folder_path)
        
        for glb_in_folder in glb_folder_dirList:
            if (re.search('\.glb',glb_in_folder)):
                glb_truePaths.append(os.path.join(glb_folder_path,glb_in_folder))

    #removeList = [".gitignore", ".DS_Store"] # If you have . files in your directory
    #glb_dirList = [x for x in glb_dirList if (x not in removeList)]
    glb_dirList = glb_truePaths
    glb_dirList = random.sample(glb_dirList, object_number)

    collection_name="MyTestCollection"
    bpy.ops.collection.create(name  = "MyTestCollection")
    bpy.context.scene.collection.children.link(bpy.data.collections["MyTestCollection"])
    collection = bpy.data.collections.get(collection_name)

    for i in glb_dirList:
        print(i)

        bpy.ops.object.select_all(action='DESELECT')
        
        bpy.ops.import_scene.gltf(filepath=i) # Import .glb file to scene
        obj = bpy.context.object
    #    if obj and collection:
    #        collection.objects.link(obj)
    #        
    #    for col in obj.users_collection:
    #        if col != collection:
    #         col.objects.unlink(obj)
        repeat_reduction = True
        repeat_reduction_times = 1

        min_corner,max_corner = calculate_combined_bounding_box(obj)

        while(repeat_reduction and repeat_reduction_times<5):
            dim = max_corner - min_corner

            vol = abs(dim[0] * dim[1] * dim[2])
            repeat_reduction = (vol)>20
            if repeat_reduction:
                #vol=roundup(np.linalg.norm(vol))
                #d_ = vol#*1.5#vol*math.log(vol)
                d = (10**(-1*repeat_reduction_times))
                obj.scale[0] = d#abs(dim[0])
                obj.scale[1] = d#abs(dim[1])
                obj.scale[2] = d#abs(dim[2])
            repeat_reduction_times += 1
            
            bpy.context.view_layer.update()
            min_corner,max_corner = calculate_combined_bounding_box(obj)

        if repeat_reduction:
            deleteObject(obj)
            object_number-=1
            print("Deleted")
            continue;
        
        
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


    bpy.ops.object.select_all(action='DESELECT') 
    # Get a list of all mesh objects in the current collection
    objects = [obj for obj in bpy.data.collections["MyTestCollection"].objects if obj.type=='EMPTY' and not obj.parent]
    for obj in objects:
        obj.location.z =  0
    #bpy.ops.object.randomize_transform(random_seed =random.randint(0,100), loc=(1, 1, 0), scale=(1, 1, 1))
    #print(objects)
    #first_displace_objects(objects)
    # Displace objects to avoid intersections

    
    print("Displacement Started")
    
    for i in range(0,1):
        displace_objects(objects)

    print("Displacement completed")

    #bpy.ops.object.randomize_transform(random_seed =random.randint(0,100), loc=(-0.5, -0.5, 0), scale=(1, 1, 1))
    return object_number
    #    bpy.context.scene.render.filepath = path_to_jpeg_folder # Set save path for images
#    bpy.context.scene.render.image_settings.file_format = "JPEG" # Set image file format
#    bpy.ops.render.render(write_still=True) # Tell Blender to render an image
