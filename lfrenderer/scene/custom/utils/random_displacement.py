import bpy
import mathutils
import random
from src.lfrenderer.scene.custom.utils.bounding_box import calculate_combined_bounding_box
from mathutils import Vector
import math


def calculate_displacement(min1, max1, min2, max2):
    displacement = mathutils.Vector((0.0, 0.0, 0.0))

    # Calculate displacement along the X-axis
    if max1.x > min2.x and min1.x < max2.x:  # Intersection on the X-axis
        displacement.x = max1.x - min2.x  # Add a small offset to avoid touching

        # Calculate displacement along the Y-axis
        if max1.y > min2.y and min1.y < max2.y:  # Intersection on the Y-axis
            displacement.y = max1.y - min2.y   # Add a small offset to avoid touching

    # Calculate displacement along the Z-axis
    if max1.z > min2.z and min1.z < max2.z:  # Intersection on the Z-axis
        displacement.z = max1.z - min2.z   # Add a small offset to avoid touching
    
    return displacement

                
""" def _displace_objects(objects):
    # Check for intersections between every pair of objects
    for i in range(len(objects)):
        for j in range(i + 1, len(objects)):
            obj1 = objects[i]
            obj2 = objects[j]

            translation_vector = check_intersection_and_translation(obj1, obj2)

            if translation_vector:
                # Move the first object by the translation vector to resolve the intersection
                obj1.location += translation_vector

    print("All intersections resolved.") """

def _displace_objects_(objects):
    loop = 0
    limit = 1
    
    rot = 0    
    while(loop<limit):
        loop +=1
        for i, obj1 in enumerate(objects):
            obj1.location.z = 0

            min1, max1 = calculate_combined_bounding_box(obj1)
            if i == 0:
                if min1.z<=0:
                    obj1.location.z = (-1*min1.z) - abs(max1.z -  min1.z)/2
                continue

            
            if min1.z>0:
                obj1.location.z = obj1.location.z - abs(min1.z)            
            elif max1.z<=0:
                obj1.location.z = obj1.location.z - (max1.z) + abs(max1.z -  min1.z)
            elif min1.z<0:
                obj1.location.z = obj1.location.z + abs(min1.z)
            

            #Avoid to enter the second loop if the object is very big, like a building
            a = 0
            b = 0
            if(rot==0 or rot >=3):     
                rot = 0
                a = 1
                b = 0
            elif(rot==1):
                a = 0
                b = 1
            elif(rot==2):
                a = 1
                b = 1 
            rot+=1
            
            for  j,obj2 in enumerate(objects[:i-1:-1]):
            #obj2 = objects[i-1]
                min1, max1 = calculate_combined_bounding_box(obj1)
                """ if j==i:
                    break; """
                
                """ d = random.choice((0,1,0.5))
                
                d1 = random.random() 
                displacement = obj2.location
                    
                displacement.x = displacement.x  +0.7*(1-d)+ 0.25*d1#+ random.random()*0.3*d
                displacement.y = displacement.y  +0.7*(d)+ 0.25*d1#+ random.random()*0.3*d
            
                obj2.location = Vector((displacement.x,displacement.y,0))#*(random.random()*0.1)
                
 """
                min2, max2 = calculate_combined_bounding_box(obj2)

                dim = max2 -  min2
                vol = abs(dim[0] * dim[1] * dim[2])
                if vol>50:
                    continue;
                
                displacement = calculate_displacement(min2, max2, min1, max1)


                #Move the object a little more than the bounding box thresholds
                displacement.x += 0.01
                displacement.y += 0.01

                obj1.location += Vector((displacement.x*a,displacement.y*b,0))

        for obj in objects:
            obj.location.x *= 0.5
            obj.location.y *= 0.5


def calculate_bounding_box(obj):
    # Assuming obj has coordinates in 3D, we project it onto the XY plane
    min,max = calculate_combined_bounding_box(obj)
    min_x = min[0]
    max_x = max[0]
    min_y = min[1]
    max_y = max[1]
    return (min_x, max_x, min_y, max_y)

def does_intersect(box1, box2):
    # Check if two bounding boxes intersect
    return not (box1[1] < box2[0] or box1[0] > box2[1] or 
                box1[3] < box2[2] or box1[2] > box2[3]) or not (box1[0] < box2[1] or box1[1] > box2[0] or 
                box1[2] < box2[3] or box1[3] > box2[2])

def find_non_overlapping_position(new_box, placed_boxes):
    
    """Finds a position for a new bounding box that does not overlap."""
    x_offset = 0
    y_offset = 0
    step = 0.05  # Step size for trying new positions
    candidate_box = (0,0,0,0)
    min = math.inf
    min_x_offest = 0
    min_y_offest = 0
    e = True
    while e:
        y_offset = 0
        while e:     
            candidate_box = (new_box[0] + x_offset, new_box[1] + x_offset, 
                            new_box[2] + y_offset, new_box[3] + y_offset)
            
            e = not all(not does_intersect(candidate_box, placed_box) for placed_box in placed_boxes)
            y_offset += step
                 
        y_offset -= step      
        dist = math.sqrt((candidate_box[0])**2 + (candidate_box[2])**2)
        if dist<min:
            min = dist
            min_x_offest =  x_offset
            min_y_offest =  y_offset
        x_offset += step
        
        e = y_offset>0

    candidate_box = (new_box[0] + x_offset, new_box[1] + x_offset, 
                            new_box[2] + y_offset, new_box[3] + y_offset)
    dist = math.sqrt((candidate_box[0])**2 + (candidate_box[2])**2)
    if dist<min:
        min = dist
        min_x_offest =  x_offset
        min_y_offest =  y_offset

    return min_x_offest,min_y_offest

    
def find_non_overlapping_position_(new_box, placed_boxes):
    """Finds a position for a new bounding box that does not overlap."""
    x_offset = 0
    y_offset = 0
    step = 0.1  # Step size for trying new positions
    candidate_box = (0,0,0,0)
    min = math.inf
    min_x_offest = 0
    min_y_offest = 0
    e = True
    while e:
        while e:         
            candidate_box = (new_box[0] + x_offset, new_box[1] + x_offset, 
                            new_box[2] + y_offset, new_box[3] + y_offset)
            
            e = not all(not does_intersect(candidate_box, placed_box) for placed_box in placed_boxes)
            y_offset += step
        dist = math.sqrt((candidate_box[0])**2 + (candidate_box[2])**2)
        if dist<min:
            min = dist
            min_x_offest =  x_offset
            min_y_offest =  y_offset
        x_offset += step
        y_offset = 0

        e = not all(not does_intersect(candidate_box, placed_box) for placed_box in placed_boxes)


    return min_x_offest,min_y_offest

def displace_objects(objects):
    """Main function to displace objects in Blender to avoid intersections."""
    # Get all selected objects in the scene
    if len(objects) < 2:
        print("Select more than one object to displace")
        return
    
    # Calculate bounding boxes
    bounding_boxes = {obj.name: calculate_bounding_box(obj) for obj in objects}
    
    placed_boxes = []
    
    for obj in objects:
        min1, max1 = calculate_combined_bounding_box(obj)

        """ if not placed_boxes:
            if min1.z<=0:
                obj.location.z = (-1*min1.z) - abs(max1.z -  min1.z)/2
            continue """
          
        if min1.z>0:
                obj.location.z = obj.location.z - abs(min1.z)            
        elif max1.z<=0:
                obj.location.z = obj.location.z - (max1.z) + abs(max1.z -  min1.z)
        elif min1.z<0:
                obj.location.z += abs(obj.location.z + min1.z)

        box = bounding_boxes[obj.name]
        # Try to find a non-overlapping position for the object
        if not placed_boxes:
            placed_boxes.append(box)  # Place the first object without any displacement
        else:
            x_offset, y_offset = find_non_overlapping_position(box, placed_boxes)

            # Apply the displacement to the object's position
            obj.location.x += x_offset
            obj.location.y += y_offset

            bpy.context.view_layer.update() 
            # Update the bounding box with the new position
            box = calculate_bounding_box(obj)
            placed_boxes.append(box)

    print("Objects have been displaced to avoid intersection")

""" # Get a list of all mesh objects in the current collection
objects = [obj for obj in bpy.context.collection.objects if obj.type == 'MESH' and obj.name!='Floor' or obj.type=='EMPTY']
# Displace objects to avoid intersections
displace_objects(objects) """

