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

        #Configure the settings to dispose the camera around a object center
        theta = random.randint( config["camera"]["theta"][0],config["camera"]["theta"][1])
        phi = random.randint(config["camera"]["phi"][0],config["camera"]["phi"][1])
        r = config["camera"]["distance"] #in meters
        x=random.uniform(-0.05, 0.05)

        objects = [obj for obj in bpy.data.collections["MyTestCollection"].objects if obj.type=='EMPTY' and not obj.parent]
        self.current_camera_obj = objects[self.current_camera_obj_inx]

        self.current_camera_obj_inx +=1
        if(len(objects) <= self.current_camera_obj_inx):
            self.current_camera_obj_inx = 0

        ob = self.current_camera_obj

        #Calculate the bounding box of an object to displace a camera at the right distance
        min1, max1 = calculate_combined_bounding_box(ob)
        center = mathutils.Vector((ob.location.x+x, ob.location.y + x*-1, (max1.z-min1.z)/2 + 0.1))

        lf = bpy.context.scene.lightfield[bpy.context.scene.lightfield_index]
        lf = (utils.get_lightfield_class(lf.lf_type))(lf)

        lf.scale = config["camera"]["camera_scale"]#Need to be checked in Lightfield file of addon (it could be useless)
        lf.obj_empty.scale = config["camera"]["camera_scale"]

        lf.obj_camera.data.ortho_scale = random.uniform(config["camera"]["ortho_scale"][0],
                                                                            config["camera"]["ortho_scale"][1])
        lf.obj_camera.data.dof.focus_distance = config["camera"]["dof"]
        lf.obj_empty.rotation_euler[1] = random.uniform(config["camera"]["rotation_euler"][0],
                                                                            config["camera"]["rotation_euler"][1])
        
        
        random_camera_pos.random_position_on_semi_sphere(lf.obj_empty,center,r,theta,phi)
    
    def render_lightfield(self, img_idx: int, sensors_row_offset: float = 100.0, sensors_column_offset: float = 100,
                          scale: float = 0.004):
        lf = bpy.context.scene.lightfield[bpy.context.scene.lightfield_index]
        lf = (utils.get_lightfield_class(lf.lf_type))(lf)

        lf.output_directory = os.path.join(self.output_dir, "lf_"+str(img_idx))

        lf.render()

    def randomize_camera(self,config: dict):
        self._randomize_camera_settings(config)
        self._randomize_photoset(config)
        self.show_scene(config)

    def _randomize_scene(self,config: dict):
        # Path tracing samples
        bpy.context.scene.cycles.samples = random.randint(config["scene"]["samples"][0], config["scene"]["samples"][1])

        bpy.ops.object.select_all(action='DESELECT')
        #tested with object_number = 15
        loaded_objects_number = blender_loader_.load_Objects(config)

        for obj in bpy.context.scene.objects:
            if obj.type == 'LIGHT':
                obj.rotation_euler[2] = math.radians(random.randrange(20,70))
                obj.data.energy = random.uniform(4.5,5.5)

        """ obj_to_load = object_number
        i=0
        while(obj_to_load>0 and i<10):
            loaded_objects_number = blender_loader_.load_Objects(object_number)
            obj_to_load -= loaded_objects_number
            i+=1 """
        
        
    def _randomize_photoset(self, config:dict):
        # Prepare photoset
        colors = random.choice(self.colors)
        """ node_color1_value = _randomize_color(colors[0] if colors is not None else (1.0, 1.0, 1.0, 1.0))
        node_color2_value = _randomize_color(colors[1] if colors is not None else (0.0, 0.0, 0.0, 1.0))
        
        # Randomize color1 and color2
        if random.uniform(0, 1) < 0.5:
            tmp_color = node_color1_value
            node_color1_value = node_color2_value
            node_color2_value = tmp_color """

        # Prepare photoset object
        photoset_obj_name = "PhotoSet"
        main_mat_name = "mat_photoset"
        #bg_mat_name = "mat_photoset_background"
        photoset_obj = bpy.data.objects.get(photoset_obj_name)
        # TODO: MAKE THESE GETTERS INTO A METHOD
        # Set colors to the chessboard
        if photoset_obj is None:
            assert False, f"ObjaverseSceneManager -> Object with name: '{photoset_obj_name}' " \
                          f"does not exist in the scene."
        main_mat = bpy.data.materials.get(main_mat_name)
        #bg_mat = bpy.data.materials.get(bg_mat_name)

        if main_mat is None:
            assert False, f"ObjaverseSceneManager -> Material with name: '{main_mat_name}' does not exist."
        node_color1 = main_mat.node_tree.nodes.get('Color1')
        node_color2 = main_mat.node_tree.nodes.get('Color2')

        if node_color1 is None or node_color2 is None:
            assert False, "ObjaverseSceneManager -> node_color1 or node_color2 not available in the nodetree."
        node_color1.inputs['Value'].default_value = random.uniform(0.3,0.6)
        node_color2.inputs['Value'].default_value = random.uniform(0.3,0.6)

        main_mat.node_tree.nodes.get('Checker Texture').inputs['Scale'].default_value = random.uniform(10,20)



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
    
