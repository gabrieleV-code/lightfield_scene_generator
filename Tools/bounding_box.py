import bpy
import mathutils

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

    def traverse_hierarchy(obj):
        if obj.type == 'MESH':
            bbox_corners = get_bounding_box_of_object(obj)
            update_bounds(bbox_corners)
        
        for child in obj.children:
            traverse_hierarchy(child)
    
    # Traverse the hierarchy starting from the given object
    traverse_hierarchy(obj)
    
    # Return the min and max corners of the combined bounding box
    return min_corner, max_corner

# Select the object that contains the meshes within empties
selected_object = bpy.context.object

# Calculate the combined bounding box
min_corner, max_corner = calculate_combined_bounding_box(selected_object)

# Output the results
print("Bounding Box Min Corner:", min_corner)
print("Bounding Box Max Corner:", max_corner)