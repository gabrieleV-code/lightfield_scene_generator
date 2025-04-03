import bpy,random
from math import *
from mathutils.bvhtree import BVHTree

import bmesh
import numpy as np
from mathutils import Vector

def numpy_apply_transforms(ob, co):
    m = np.array(ob.matrix_world)    
    mat = m[:3, :3].T 
    loc = m[:3, 3]
    return co @ mat + loc

def are_inside(points, bool_name, boundary='inside'):
    """
    input: 
        points
        - a list of vectors (can also be tuples/lists)
        bm
        - a manifold bmesh with verts and (edge/faces) for which the 
          normals are calculated already. (add bm.normal_update() otherwise)
    returns:
        a list
        - a mask lists with True if the point is inside the bmesh, False otherwise
    """

    
    rpoints = []
    addp = rpoints.append
    
    target_object = bpy.context.object
    bool_object   = bpy.data.objects[bool_name]

    #create mesh data
    bm = bmesh.new()
    bm.from_mesh(bool_object.data)
    bmesh.ops.transform(bm, matrix=bool_object.matrix_world, verts=bm.verts) #local to global coord
    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    bvh = BVHTree.FromBMesh(bm, epsilon=0.0001)
    
    points = numpy_apply_transforms(target_object, points) #local to global coord

    # return points on polygons
    for point in points:
        fco, normal, _, _ = bvh.find_nearest(point)
        p2 = fco - Vector(point)
        v = p2.dot(normal)
        if boundary == 'outside':
            addp(not v < 0.0) # addp(v >= 0.0) ?
        else:    
            addp(v < 0.0)

    return rpoints

def intersection_check(target_name, bool_name):
    
    target_object = bpy.data.objects[target_name]
    bool_object   = bpy.data.objects[bool_name]
    
    #create mesh data
    bm = bmesh.new()
    bm.from_mesh(target_object.data)
    bmesh.ops.transform(bm, matrix=target_object.matrix_world, verts=bm.verts) #local to global coord
    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    bvh = BVHTree.FromBMesh(bm, epsilon=0.0001)
    
    #create mesh data
    bm1 = bmesh.new()
    bm1.from_mesh(bool_object.data)
    bmesh.ops.transform(bm1, matrix=bool_object.matrix_world, verts=bm1.verts) #local to global coord
    bm1.verts.ensure_lookup_table()
    bm1.edges.ensure_lookup_table()
    bm1.faces.ensure_lookup_table()
    bvh1 = BVHTree.FromBMesh(bm1, epsilon=0.0001)
    
    if bvh.overlap( bvh1 ):
        return True
    else:
        return False

obj_list = [obj.name for obj in bpy.context.scene.objects if (obj.type=='MESH' and obj.name!='Floor' and obj.name!='Wall')]

#print(bpy.data.objects['Wall'].dimensions.x)
#print(bpy.data.objects['Wall'].dimensions.y)

for obj in obj_list:    
    obj = bpy.context.scene.objects.get(obj)
    bpy.context.view_layer.objects.active = obj
    if obj: obj.select_set(True)
    
    maxIter = 3
    placed = False

    print("Object: {}".format(obj.name))
    print( "origLocation: {}".format(obj.location) )
    
    while(not placed):
        print("Iteration: {}".format(maxIter))
        
        if maxIter < 0:
            print("gave up!!!")
            break
        
        # set object back to original location on each loop, to try again from that loc:
        obj.location.x = bpy.data.objects['Floor'].location.x
        obj.location.y = bpy.data.objects['Floor'].location.y
        
        print( "startingLocation: {}".format(obj.location) )
        
        # put object in new location
        bpy.ops.object.randomize_transform( random_seed =random.randint(0,100), use_loc=True, loc=(bpy.data.objects['Floor'].dimensions.x/2, bpy.data.objects['Wall'].dimensions.y/2, 0.0), scale=(1, 1, 1))
        
        print( "newLocation: {}".format(obj.location) )
        
        # Check if object is out of wall boundary
        rvalAry = are_inside(obj.bound_box, "Wall")
        print(rvalAry)
        
        if all(rvalAry):
            
            # Check if object is colliding with other objects
            rvalAry_ = []
            for ob in obj_list:
                ob = bpy.context.scene.objects.get(ob)
                if obj == ob:
                    continue
                
#                rvalAry_ = are_inside(obj.bound_box, ob.name, 'outside')
                rvalAry_.append( intersection_check(obj.name, ob.name) )
                print(rvalAry_)
                
            if not any(rvalAry_):
                print("Object placed!!!")
                placed = True
            
        maxIter -= 1
    bpy.ops.object.select_all(action='DESELECT') # Deselect all objects