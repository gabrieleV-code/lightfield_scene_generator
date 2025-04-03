import bpy
import mathutils
import bmesh
from mathutils import Vector


def get_mesh_objects_in_hierarchy(obj):
    """
    Get all mesh objects in the hierarchy of the given object (including itself).
    """
    mesh_objects = []

    if obj.type == 'MESH':
        mesh_objects.append(obj)

    for child in obj.children:
        mesh_objects.extend(get_mesh_objects_in_hierarchy(child))

    return mesh_objects

def get_world_vertices(obj):
    """
    Get the world space vertices of a mesh object.
    """
    vertices = []
    if obj.type == 'MESH':
        mesh = obj.data
        bm = bmesh.new()
        bm.from_mesh(mesh)
        bm.transform(obj.matrix_world)  # Convert all vertices to world space
        for vert in bm.verts:
            vertices.append(vert.co.copy())
        bm.free()
    return vertices

def bounding_box_overlap(bb1_min, bb1_max, bb2_min, bb2_max):
    """
    Checks if two bounding boxes overlap.
    """
    return all(bb1_min[i] <= bb2_max[i] and bb1_max[i] >= bb2_min[i] for i in range(3))

def calculate_translation_vector(bb1_min, bb1_max, bb2_min, bb2_max):
    """
    Calculate the minimum translation vector to separate the bounding boxes.
    """
    translation = Vector((0, 0, 0))
    
    # Calculate overlap distances in each axis
    overlap_x = min(bb1_max.x - bb2_min.x, bb2_max.x - bb1_min.x)
    overlap_y = min(bb1_max.y - bb2_min.y, bb2_max.y - bb1_min.y)
    overlap_z = min(bb1_max.z - bb2_min.z, bb2_max.z - bb1_min.z)

    # Find the smallest overlap
    if overlap_x <= overlap_y and overlap_x <= overlap_z:
        translation.x = overlap_x if bb1_min.x < bb2_min.x else -overlap_x
    elif overlap_y <= overlap_x and overlap_y <= overlap_z:
        translation.y = overlap_y if bb1_min.y < bb2_min.y else -overlap_y
    else:
        translation.z = overlap_z if bb1_min.z < bb2_min.z else -overlap_z

    return translation

def check_intersection_and_translation(obj1, obj2):
    """
    Check if two objects' meshes are intersecting and return the translation vector.
    """
    obj1_meshes = get_mesh_objects_in_hierarchy(obj1)
    obj2_meshes = get_mesh_objects_in_hierarchy(obj2)

    for mesh1 in obj1_meshes:
        verts1 = get_world_vertices(mesh1)

        for mesh2 in obj2_meshes:
            verts2 = get_world_vertices(mesh2)

            # Bounding box for obj1 and obj2
            bb_min1 = Vector((min(v[0] for v in verts1), min(v[1] for v in verts1), min(v[2] for v in verts1)))
            bb_max1 = Vector((max(v[0] for v in verts1), max(v[1] for v in verts1), max(v[2] for v in verts1)))

            bb_min2 = Vector((min(v[0] for v in verts2), min(v[1] for v in verts2), min(v[2] for v in verts2)))
            bb_max2 = Vector((max(v[0] for v in verts2), max(v[1] for v in verts2), max(v[2] for v in verts2)))

            if bounding_box_overlap(bb_min1, bb_max1, bb_min2, bb_max2):
                print(f"Intersection found between {mesh1.name} and {mesh2.name}")
                translation_vector = calculate_translation_vector(bb_min1, bb_max1, bb_min2, bb_max2)
                print(f"Translation vector to resolve intersection: {translation_vector}")
                return translation_vector

    print("No intersection found")
    return None


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
            if desc_n >=10000:
                return desc_n
            desc_n += traverse_hierarchy(child,desc_n+1)
        return desc_n
    
    # Traverse the hierarchy starting from the given object
    traverse_hierarchy(obj,1)
    # Return the min and max corners of the combined bounding box
    return min_corner, max_corner

# Select the object that contains the meshes within empties
selected_object = bpy.context.object

# Calculate the combined bounding box
min_corner, max_corner = calculate_combined_bounding_box(selected_object)

# Calculate the center and size of the bounding box
bbox_center = (min_corner + max_corner) / 2
bbox_size = max_corner - min_corner

# Create a new cube object to represent the bounding box
bpy.ops.mesh.primitive_cube_add(size=1, location=bbox_center)
bbox_obj = bpy.context.object

# Scale the cube to match the bounding box dimensions
bbox_obj.dimensions = bbox_size   # Cube's size is 2x2x2, so divide by 2

# Optional: Set the bounding box object to wireframe mode
bbox_obj.display_type = 'WIRE'
bbox_obj.name = f"BoundingBox_{selected_object.name}"

# Output the results
print("Bounding Box Min Corner:", min_corner)
print("Bounding Box Max Corner:", max_corner) 

dim = max_corner-min_corner

vol = abs(dim.x*dim.y*dim.z)

print(vol)