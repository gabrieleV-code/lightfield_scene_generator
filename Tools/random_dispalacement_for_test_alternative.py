import bpy
import mathutils
import random
from mathutils import Vector
import math

def get_bounding_box_of_object(obj):
    """Get the world-space bounding box of an object."""
    bbox_corners = [obj.matrix_world @ mathutils.Vector(corner) for corner in obj.bound_box]
    return bbox_corners

def calculate_combined_bounding_box(obj):
    """Calculate a combined bounding box for all meshes under the object."""
    # Initialize the min and max values
    min_corner = mathutils.Vector((float('inf'), float('inf'), float('inf')))
    max_corner = mathutils.Vector((float('-inf'), float('-inf'), float('-inf')))
    
    def update_bounds(bbox_corners):
        nonlocal min_corner, max_corner
        for corner in bbox_corners:
            min_corner = mathutils.Vector((min(min_corner[i], corner[i]) for i in range(3)))
            max_corner = mathutils.Vector((max(max_corner[i], corner[i]) for i in range(3)))

    def traverse_hierarchy(obj,desc_n):
        if obj.type == 'MESH':
            bbox_corners = get_bounding_box_of_object(obj)
            update_bounds(bbox_corners)
        
        for child in obj.children: 
            """ if desc_n >=10**10:
                return desc_n """
            desc_n += traverse_hierarchy(child,desc_n+1)
        return desc_n
    
    # Traverse the hierarchy starting from the given object
    traverse_hierarchy(obj,1)
    # Return the min and max corners of the combined bounding box
    return min_corner, max_corner

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
                box1[3] < box2[2] or box1[2] > box2[3])

def find_non_overlapping_position(new_box, placed_boxes):
    
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
        y_offset = 0
        
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
    selected_objects = objects
    if len(selected_objects) < 2:
        print("Select more than one object to displace")
        return
    
    # Calculate bounding boxes
    bounding_boxes = {obj.name: calculate_bounding_box(obj) for obj in selected_objects}
    
    placed_boxes = []
    
    for obj in selected_objects:

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
                obj.location.z = obj.location.z + abs(min1.z)

        box = bounding_boxes[obj.name]
        # Try to find a non-overlapping position for the object
        if not placed_boxes:
            placed_boxes.append(box)  # Place the first object without any displacement
        else:
            x_offset, y_offset = find_non_overlapping_position(box, placed_boxes)

            x_ = (box[1]-box[0])/2
            y_ = (box[2]-box[3])/2
            # Apply the displacement to the object's position
            obj.location.x += x_offset 
            obj.location.y += y_offset 
            # Update the bounding box with the new position
            box = calculate_bounding_box(obj)
            placed_boxes.append(box)
    
    print("Objects have been displaced to avoid intersection")
    
objects = bpy.context.selected_objects

displace_objects(objects)