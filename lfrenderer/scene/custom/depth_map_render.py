import bpy

import sys
from pathlib import Path
import os
from blender_lightfield_addon_main import utils
import re

packages_path = r"C:\Users\gabri\AppData\Roaming\Python\Python310\Scripts" + r"\\..\\site-packages" # the path you see in console

# 4. uncomment the next code and launch script in blender interpreter again

sys.path.insert(0, packages_path )
from PIL import Image
import numpy as np

def depth_map_render(output_dir,img_idx):
        lf = bpy.context.scene.lightfield[bpy.context.scene.lightfield_index]
        LF = (utils.get_lightfield_class(lf.lf_type))(lf)
        scene_key = bpy.context.scene.name

        cameras = [LF.obj_camera]
        max_res = max(LF.res_x, LF.res_y)
        print(LF.num_cams_x)
        baseline_x_m = LF.obj_empty.scale[0]/(LF.num_cams_x-1)
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
        fileOutput.base_path = os.path.join(output_dir, "lf_"+str(img_idx))
        fileOutput.file_slots[0].path = "depth_map0001"
        links.new(invert.outputs[0], fileOutput.inputs[0])
        
        # Render the scene (this will output the depth map)
        bpy.ops.render.render(write_still=True)

        print(fileOutput.file_slots)
        
        bpy.context.scene.cycles.adaptive_threshold = old_threshold

        depth_path = os.path.join(output_dir, "lf_"+str(img_idx))
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
        disparity_image.save(os.path.join(os.path.join(output_dir, "lf_"+str(img_idx)),"disparity_map.png"))

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
        
output_dir = r'C:\Users\gabri\OneDrive\Documenti\UniTO-DOCS\Stage\LightfieldsRenderer\Lightfield_015\LF_Scene_1'        
depth_map_render(output_dir,2)