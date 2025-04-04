from math import pi
import random
import re
import bpy
import os
from .. import SceneManager
from blender_lightfield_addon_main import utils,lightfield
import src.lfrenderer.scene.custom.utils.random_camera_pos as random_camera_pos
import src.lfrenderer.scene.custom.utils.blender_loader as blender_loader_
from src.lfrenderer.scene.custom.utils.bounding_box import calculate_combined_bounding_box
import mathutils
import numpy as np
import pip
import sys
import io
import struct
import math

# 2. watch blender's python path in console output at this moment
# 3. insert the path to packages_path below and uncomment

packages_path = r"C:\Users\gabri\AppData\Roaming\Python\Python310\Scripts" + r"\\..\\site-packages" # the path you see in console

# 4. uncomment the next code and launch script in blender interpreter again

sys.path.insert(0, packages_path )
from PIL import Image

def _randomize_color(color):
    # Randomize a bit the color and normalize its value between [0, 1]
    normalized_color = [0.0, 0.0, 0.0, 1.0]
    normalized_color[0] = max(0.0, min(1.0, color[0] + random.uniform(-0.1, 0.1)))
    normalized_color[1] = max(0.0, min(1.0, color[1] + random.uniform(-0.1, 0.1)))
    normalized_color[2] = max(0.0, min(1.0, color[2] + random.uniform(-0.1, 0.1)))
    normalized_color[3] = color[3]
    return normalized_color

class ObjaverseSceneManager(SceneManager):
    def __init__(self, output_dir: str, row_sensors: int = 15, column_sensors: int = 15):
        super().__init__(output_dir, row_sensors, column_sensors)
        lf = bpy.context.scene.lightfield[bpy.context.scene.lightfield_index]
        lf = (utils.get_lightfield_class(lf.lf_type))(lf)

        lf.output_directory = output_dir

        self.colors = [
            [(1.0, 1.0, 1.0, 1.0), (0.0, 0.0, 0.0, 1.0), (0.9, 0.9, 0.9, 1.0)],  # Black and White, White
            [(0.96, 0.87, 0.68, 1.0), (0.64, 0.44, 0.25, 1.0), (0.8, 0.6, 0.4, 1.0)],  # Brown and Yellow, Yellow
            [(0.91, 0.85, 0.79, 1.0), (0.25, 0.18, 0.2, 1.0), (0.81, 0.75, 0.69, 1.0)],  # DBrown and DWhite, DWhite
            [(0.99, 0.97, 0.93, 1.0), (0.53, 0.13, 0.19, 1.0), (0.84, 0.82, 0.78, 1.0)],  # Red and White, White
            [(0.93, 1.0, 0.99, 1.0), (0.22, 0.65, 0.77, 1.0), (0.78, 0.85, 0.84, 1.0)],  # LBlue and White, White
            [(0.99, 0.99, 0.99, 1.0), (0.2, 0.62, 0.36, 1.0), (0.84, 0.84, 0.84, 1.0)],  # Green and White, White
        ]

        bpy.context.scene.render.film_transparent = False

        self.current_camera_obj = None
        self.current_camera_obj_inx = 0

        self.camera_locations = []
        self.camera_rotations = []

        self.original_lf_location = lf.obj_empty.location
    
    def _randomize_camera_settings(self,config: dict):
        # Percentage part in the x direction
        #Prepare the general position of the lightfield render

        theta = random.randint(175,320)
        phi = random.randint(75,91)
        r = config["camera"]["distance"] #in meters
        x=random.uniform(-0.05, 0.05)

        objects = [obj for obj in bpy.data.collections["MyTestCollection"].objects if obj.type=='EMPTY' and not obj.parent]
        self.current_camera_obj = objects[self.current_camera_obj_inx]

        self.current_camera_obj_inx +=1
        if(len(objects) <= self.current_camera_obj_inx):
            self.current_camera_obj_inx = 0

        ob = self.current_camera_obj

        min1, max1 = calculate_combined_bounding_box(ob)
        center = mathutils.Vector((ob.location.x+x, ob.location.y + x*-1, (max1.z-min1.z)/2 + 0.1))

        lf = bpy.context.scene.lightfield[bpy.context.scene.lightfield_index]
        lf = (utils.get_lightfield_class(lf.lf_type))(lf)

        lf.obj_camera.data.ortho_scale = random.uniform(config["camera"]["ortho_scale"][0],
                                                                            config["camera"]["ortho_scale"][1])
        
        lf.obj_camera.data.dof.focus_distance = config["camera"]["dof"]

        lf.obj_empty.rotation_euler[1] = random.uniform(config["camera"]["rotation_euler"][0],
                                                                            config["camera"]["rotation_euler"][1])
        
        
        random_camera_pos.random_position_on_semi_sphere(lf.obj_empty,center,r,theta,phi)

        print("\n"+str(lf.obj_empty.rotation_euler[2])+"\n")
    
    def render_lightfield(self, img_idx: int, sensors_row_offset: float = 100.0, sensors_column_offset: float = 100,
                          scale: float = 0.000001):
        lf = bpy.context.scene.lightfield[bpy.context.scene.lightfield_index]
        lf = (utils.get_lightfield_class(lf.lf_type))(lf)

        lf.output_directory = os.path.join(self.output_dir, "lf_"+str(img_idx))

        lf.render()

    def randomize_camera(self,config: dict):
        self._randomize_camera_settings(config)
        self.show_scene(config)

    def _randomize_scene(self,config: dict):
        # Path tracing samples
        bpy.context.scene.cycles.samples = random.randint(config["scene"]["samples"][0], config["scene"]["samples"][1])

        bpy.ops.object.select_all(action='DESELECT')
        object_number = 15
        loaded_objects_number = blender_loader_.load_Objects(object_number)

        for obj in bpy.context.scene.objects:
            if obj.type == 'LIGHT':
                obj.rotation_euler[2] = math.radians(random.randrange(20,70))

        """ obj_to_load = object_number
        i=0
        while(obj_to_load>0 and i<10):
            loaded_objects_number = blender_loader_.load_Objects(object_number)
            obj_to_load -= loaded_objects_number
            i+=1 """


    def show_scene(self, config: dict):
        lf = bpy.context.scene.lightfield[bpy.context.scene.lightfield_index]
        lf = (utils.get_lightfield_class(lf.lf_type))(lf)
        
        lf.obj_camera.data.dof.focus_distance = config["camera"]["dof"]
        
        self.original_lf_location = lf.obj_empty.location

        r = config["camera"]["distance"] #in meters
        distance = (lf.obj_empty.location-self.current_camera_obj.location).normalized()
        print(lf.obj_empty.location-self.current_camera_obj.location)
        print(distance)
        z_location = lf.obj_empty.location.z
        lf.obj_empty.location = self.current_camera_obj.location + (distance)*r 
        lf.obj_empty.location.z = z_location

        old_filepath = bpy.data.scenes["Scene"].render.filepath
        new_filepath = os.path.join(os.path.dirname(bpy.data.scenes["Scene"].render.filepath) , "somefile")
        bpy.data.scenes["Scene"].render.filepath = new_filepath
        # Render the image without saving
        bpy.ops.render.render(write_still = True)

        image = bpy.data.images['Render Result']

        render_result = image

        bpy.data.scenes["Scene"].render.filepath = old_filepath
        if render_result is None:
            print("Render result not found!")
        else:
            #render_result.save_render("somefile.tga")
            print(os.path.dirname(bpy.data.scenes["Scene"].render.filepath))
            #image = Image.open(os.path.join(os.path.dirname(bpy.data.scenes["Scene"].render.filepath) , "somefile.tga"))
            image = Image.open('C:/tmp/somefile.png')

            im_crop = image
            # Display the image
            im_crop.show()

    def randomize_scene(self, config: dict):
        self._randomize_scene(config)


    def _depth_map_render(self,img_idx):
        # Enable Z-pass (Depth map)
        lf = bpy.context.scene.lightfield[bpy.context.scene.lightfield_index]
        lf = (utils.get_lightfield_class(lf.lf_type))(lf)

        bpy.context.scene.view_layers["ViewLayer"].use_pass_z = True

        # Define the output directory for the depth map
        output_filepath =  os.path.join(self.output_dir, "lf_"+str(img_idx))

        # Setup nodes to process the Z-pass in the compositor
        bpy.context.scene.use_nodes = True
        tree = bpy.context.scene.node_tree
        links = tree.links

        # Clear existing nodes
        for node in tree.nodes:
            tree.nodes.remove(node)

        # Add Render Layers node
        render_layers = tree.nodes.new(type="CompositorNodeRLayers")
        render_layers.location = (0, 0)

        # Add Map Range node to fine-tune the depth map
        map_range = tree.nodes.new(type="CompositorNodeMapRange")
        map_range.location = (200, 0)
        map_range.inputs[1].default_value = 0.001  # From Min (set to near clipping)
        map_range.inputs[2].default_value = 1000.0  # From Max (adjust based on scene scale)
        map_range.inputs[3].default_value = 0.0  # To Min (output value)
        map_range.inputs[4].default_value = 1.0  # To Max (output value)

        # Add Composite node to output the final image
        composite = tree.nodes.new(type="CompositorNodeComposite")
        composite.location = (400, 0)

        # Add File Output node to save the depth map
        file_output = tree.nodes.new(type="CompositorNodeOutputFile")
        file_output.location = (400, -200)
        file_output.base_path = output_filepath  # Set your output directory
        file_output.file_slots[0].path = "depth_map"

         # prepare depth output node. blender changed their naming convection for render layers in 2.79... so Z became Depth and everthing else got complicated ;)
        if 'Z' in render_layers.outputs:
            depth_key = 'Z'
        else:
            depth_key = 'Depth'

        # Link nodes: Render Layers -> Map Range -> File Output
        links.new(render_layers.outputs[depth_key], map_range.inputs[0])
        links.new(map_range.outputs[0], composite.inputs[0])
        links.new(map_range.outputs[0], file_output.inputs[0])

        # Render the scene (this will output the depth map)
        bpy.ops.render.render(write_still=True)

        

        print("Depth map saved successfully!")

        # Disable Z-pass (depth rendering)
        bpy.context.scene.view_layers["ViewLayer"].use_pass_z = False

        # Clear the compositor and reset it for regular rendering
        tree = bpy.context.scene.node_tree
        links = tree.links

        # Remove all compositor nodes
        for node in tree.nodes:
            tree.nodes.remove(node)

        # Add back basic nodes for standard rendering
        render_layers = tree.nodes.new(type="CompositorNodeRLayers")
        render_layers.location = (0, 0)

        composite = tree.nodes.new(type="CompositorNodeComposite")
        composite.location = (400, 0)

        # Link Render Layers to Composite (for normal image output)
        links.new(render_layers.outputs['Image'], composite.inputs['Image'])

        # Now, the next render will produce a regular color image (not a depth map)
        print("Next render will be a regular image.")


    
    def depth_map_render(self,img_idx):
        lf = bpy.context.scene.lightfield[bpy.context.scene.lightfield_index]
        LF = (utils.get_lightfield_class(lf.lf_type))(lf)
        scene_key = bpy.context.scene.name

        cameras = [LF.obj_camera]
        max_res = max(LF.res_x, LF.res_y)
        print(LF.num_cams_x)
        baseline_x_m = LF.obj_empty.scale[0]/(LF.num_cams_x)
        baseline_y_m = LF.obj_empty.scale[1]/LF.num_cams_y

        old_location = LF.obj_camera.location
        LF.obj_camera.location = (0,0,0)

        old_dof = LF.obj_camera.data.dof.use_dof
        LF.obj_camera.data.dof.use_dof = False 

        # (1) focal_length(pixel) = focal_length(mm) * resolution_x(pixel) / sensor_size_width(mm) (2) disparity = baseline(m) * focal_length(pixel) / depth(m)
        focus_dist = LF.obj_camera.data.dof.focus_distance
        focal_length = LF.obj_camera.data.lens
        factor = baseline_x_m * focal_length * max_res #* focus_dist
        sensor_size = LF.obj_camera.data.sensor_width

        # Set up rendering of depth map:
        bpy.context.scene.use_nodes = True
        bpy.context.scene.view_layers["ViewLayer"].use_pass_z = True
        
        
        old_threshold = bpy.context.scene.cycles.adaptive_threshold 
        bpy.context.scene.cycles.adaptive_threshold = 0.01
        
        tree = bpy.context.scene.node_tree
        links = tree.links

        # clear default nodes
        for n in tree.nodes:
            tree.nodes.remove(n)

        # create input render layer node
        rl = tree.nodes.new('CompositorNodeRLayers')

        map = tree.nodes.new(type="CompositorNodeMapValue")
        # Size is chosen kind of arbitrarily, try out until you're satisfied with resulting depth map.
        map.size = [0.09]
        map.use_min = True
        map.min = [0]
        map.use_max = True
        map.max = [255]
        links.new(rl.outputs[2], map.inputs[0])

        invert = tree.nodes.new(type="CompositorNodeInvert")
        invert
        links.new(map.outputs[0], invert.inputs[1])

        # The viewer can come in handy for inspecting the results in the GUI
        depthViewer = tree.nodes.new(type="CompositorNodeViewer")
        links.new(invert.outputs[0], depthViewer.inputs[0])
        # Use alpha from input.
        links.new(rl.outputs[1], depthViewer.inputs[1])

        # create a file output node and set the path
        fileOutput = tree.nodes.new(type="CompositorNodeOutputFile")
        fileOutput.base_path = os.path.join(self.output_dir, "lf_"+str(img_idx))
        fileOutput.file_slots[0].path = "depth_map0001"
        links.new(invert.outputs[0], fileOutput.inputs[0])
        
        # Render the scene (this will output the depth map)
        bpy.ops.render.render(write_still=True)

        print(fileOutput.file_slots)
        
        bpy.context.scene.cycles.adaptive_threshold = old_threshold

        depth_path = os.path.join(self.output_dir, "lf_"+str(img_idx))
        for dir in os.listdir(depth_path):
            if re.search("depth_map*",dir):
                depth_path = os.path.join(depth_path,dir)
            break
        #Calculate disparity map by getting the depth map
        depth = Image.open(depth_path)
        depth_array = np.array(depth)
        # Convert depth to disparity
        disparity_array = factor / (depth_array + 1e-6)  # Add a small epsilon to avoid division by zero
        #disparity_array = (factor / (depth_array + 1e-6) - baseline_x_m * focal_length * max_res) / focus_dist / sensor_size
        # Normalize disparity values to the range [0, 255] for visualization
        disparity_normalized = 255 * (disparity_array - np.min(disparity_array)) / (np.max(disparity_array) - np.min(disparity_array))
        disparity_image = Image.fromarray(disparity_normalized.astype(np.uint8))
        #disparity_image = Image.fromarray(disparity_array.astype(np.uint8))
        #disparity_image = Image.fromarray(depth_array.astype(np.uint8))
        # Save disparity map
        disparity_image.save(os.path.join(os.path.join(self.output_dir, "lf_"+str(img_idx)),"disparity_map.png"))

        # Disable Z-pass (depth rendering)
        bpy.context.scene.view_layers["ViewLayer"].use_pass_combined = True
        bpy.context.scene.view_layers["ViewLayer"].use_pass_z = False

        LF.obj_camera.location = old_location
        LF.obj_camera.data.dof.use_dof = old_dof
        # Clear the compositor and reset it for regular rendering
        tree = bpy.context.scene.node_tree
        links = tree.links

        # Remove all compositor nodes
        for node in tree.nodes:
            tree.nodes.remove(node)

        # Add back basic nodes for standard rendering
        render_layers = tree.nodes.new(type="CompositorNodeRLayers")
        render_layers.location = (0, 0)

        composite = tree.nodes.new(type="CompositorNodeComposite")
        composite.location = (400, 0)

        # Link Render Layers to Composite (for normal image output)
        links.new(render_layers.outputs['Image'], composite.inputs['Image'])

        bpy.context.scene.cycles.adaptive_threshold = old_threshold

        """ img = bpy.data.images['Render Result']

        pixels = [int(px * 255) for px in img.pixels[:]]
        bytes = struct.pack("%sB" % len(pixels), *pixels)

        image = Image.frombytes('RGBA', (img.size[0], img.size[1]), bytes)
        image = image.transpose(Image.FLIP_LEFT_RIGHT).rotate(180)

        # Create an image from the NumPy array
        img = Image.fromarray(pixels, 'RGBA') """
        """ bpy_image = image
        img = bpy_image
        pixels = [int(px * 255) for px in bpy_image.pixels[:]]
        bytes = struct.pack("%sB" % len(pixels), *pixels)
        im = Image.frombytes('RGBA', (bpy_image.size[0], bpy_image.size[1]), bytes)
        im = im.transpose(Image.FLIP_LEFT_RIGHT).rotate(45) """
        
        """ x=625
        y=434
        (left, upper, right, lower) = (0, 0, x, y)
        img = Image.fromarray(pixels, 'RGBA')
        print(img)
        # Here the image "im" is cropped and assigned to new variable im_crop
        im_crop = img.crop((left, upper, right, lower))
        im_crop = image
        # Display the image
        im_crop.show() """
        """ node_bg_color_value = _randomize_color(colors[2] if colors is not None else (0.9, 0.9, 0.9, 1.0))
        table_node_color_value = [random.uniform(0.0, 1.0), random.uniform(0.0, 1.0), random.uniform(0.0, 1.0), 1.0] """
        # Randomize color1 and color2
        """ if random.uniform(0, 1) < 0.5:
            tmp_color = node_color1_value
            node_color1_value = node_color2_value
            node_color2_value = tmp_color

        # Prepare chessboard objects
        chessboard_obj_name = "Chessboard"
        main_mat_name = "mat_chessboard"
        bg_mat_name = "mat_chessboard_background"
        chessboard_obj = bpy.data.objects.get(chessboard_obj_name)

        # TODO: MAKE THESE GETTERS INTO A METHOD
        # Set colors to the chessboard
        if chessboard_obj is None:
            assert False, f"ChessboardSceneManager -> Object with name: '{chessboard_obj_name}' " \
                          f"does not exist in the scene."
        main_mat = bpy.data.materials.get(main_mat_name)
        bg_mat = bpy.data.materials.get(bg_mat_name)

        if main_mat is None:
            assert False, f"ChessboardSceneManager -> Material with name: '{main_mat_name}' does not exist."
        node_color1 = main_mat.node_tree.nodes.get('chessboard_color1')
        node_color2 = main_mat.node_tree.nodes.get('chessboard_color2')

        if node_color1 is None or node_color2 is None:
            assert False, "ChessboardSceneManager -> node_color1 or node_color2 not available in the nodetree."
        node_color1.outputs["Color"].default_value = node_color1_value
        node_color2.outputs["Color"].default_value = node_color2_value """

        """ if bg_mat is None:
            assert False, f"ChessboardSceneManager -> Material with name: '{bg_mat_name}' does not exist."
        node_bg_color = bg_mat.node_tree.nodes.get('chessboard_color_background')

        if node_bg_color is None:
            assert False, "ChessboardSceneManager -> node_bg_color not available in the nodetree."
        node_bg_color.outputs["Color"].default_value = node_bg_color_value

        # Set colors to the table
        table_obj_name = "Table"
        table_mat_name = "mat_table_background"
        table_obj = bpy.data.objects.get(table_obj_name)
        if table_obj is None:
            assert False, f"ChessboardSceneManager -> Object with name: '{table_obj}' " \
                          f"does not exist in the scene."
        main_mat = bpy.data.materials.get(table_mat_name)

        if main_mat is None:
            assert False, f"ChessboardSceneManager -> Material with name: '{table_mat_name}' does not exist."
        table_node_color1 = main_mat.node_tree.nodes.get('table_color')

        if table_node_color1 is None:
            assert False, "ChessboardSceneManager -> table_node_color1 not available in the nodetree."
        table_node_color1.outputs["Color"].default_value = table_node_color_value
        """
        print("\nRandomization done\n")
    
