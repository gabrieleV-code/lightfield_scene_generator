from math import pi
import random
import bpy
import os
from . import ChessboardSceneManager
from blender_lightfield_addon_main import utils,lightfield



class ChessboardSceneSilvrManager(ChessboardSceneManager):
    def __init__(self, output_dir: str, row_sensors: int = 15, column_sensors: int = 15):
        super().__init__(output_dir, row_sensors, column_sensors)
        lf = bpy.context.scene.lightfield[bpy.context.scene.lightfield_index]
        lf = (utils.get_lightfield_class(lf.lf_type))(lf)

        lf.output_directory = output_dir
    
    def _randomize_camera_settings(self,config: dict):
        # Percentage part in the x direction
        #Prepare the general position of the lightfield render
        lf = bpy.context.scene.lightfield[bpy.context.scene.lightfield_index]
        lf = (utils.get_lightfield_class(lf.lf_type))(lf)

        lf.obj_camera.data.ortho_scale = random.uniform(config["camera"]["ortho_scale"][0],
                                                                            config["camera"]["ortho_scale"][1])
        lf.obj_empty.rotation_euler[2] = random.uniform(config["camera"]["rotation_euler"][0],
                                                                            config["camera"]["rotation_euler"][1])
        print("\n"+str(lf.obj_empty.rotation_euler[2])+"\n")
        
    """ def randomize_scene(self, config: dict):
        # Randomize camera position and rotation
        try:
       super().randomize_scene(config)  
        except AttributeError:
            print("SILVR ADDON NOT INSTALLED!")  """
    
    def render_lightfield(self, img_idx: int, sensors_row_offset: float = 100.0, sensors_column_offset: float = 100,
                          scale: float = 0.000001):
        lf = bpy.context.scene.lightfield[bpy.context.scene.lightfield_index]
        lf = (utils.get_lightfield_class(lf.lf_type))(lf)

        lf.output_directory = os.path.join(self.output_dir, "lf_"+str(img_idx))
        lf.render()
    
