import os
import random
import sys
from argparse import ArgumentParser

import bpy
import numpy as np


def _get_argv_after_doubledash() -> list[str] | list:
    try:
        idx = sys.argv.index("--")
        return sys.argv[idx + 1:]  # the list after '--'
    except ValueError as e:  # '--' not in the list:
        return []


class ArgumentParserForBlender(ArgumentParser):
    # overrides superclass
    def parse_args(self, args=None, namespace=None):
        return super().parse_args(args=_get_argv_after_doubledash())


def get_arguments():
    from src.root import ROOT
    parser = ArgumentParserForBlender()
    parser.add_argument("--name", type=str, required=True, help="Main directory name.")
    parser.add_argument("--config", type=str, default=os.path.join(ROOT, "src", "configs", "generic_lenlets.yaml"),
                        help="Config file path.")
    parser.add_argument("--seed", type=int, default=0, help="Random seed")
    parser.add_argument("--debug", default=False, action="store_true", help="Enter debug mode.")
    return parser.parse_args()

def init_for_render(scene_name,config: dict) -> str:
     # Create main folder
    main_dir = os.path.join(config["global"]["main_dir"], config["parsed"]["name"],"LF_"+str(scene_name))

    try:
        os.makedirs(main_dir)
    except OSError:
        print(main_dir)
        print(f"ERROR. Folder of name {config['parsed']['name']} already exists!")
        #if not get_arguments().debug:
            #sys.exit(1)


        # Init blender properties
    bpy.ops.object.mode_set(mode='OBJECT')
    # Deselect all eventually selected objects
    bpy.ops.object.select_all(action='DESELECT')
    # Set render engine and GPUs
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES' if config["render"]["cycles"] else "BLENDER_EEVEE"
    activated_gpus = _enable_gpus(config["render"]["engine"], True)
    print("Using: {}".format(activated_gpus))
    if scene.render.engine == "CYCLES":
        bpy.context.scene.cycles.use_denoising = True

    # Set transparent background
    bpy.context.scene.render.film_transparent = True

    # Path tracing samples
    scene.cycles.samples = config["scene"]["samples"][0]

    # Performance increase
    bpy.context.scene.cycles.debug_use_spatial_splits = True
    
    # Render resolution
    scene.render.resolution_x = config["scene"]["resolution_x"]
    scene.render.resolution_y = config["scene"]["resolution_y"]

    return main_dir

def init(config: dict) -> str:
    """
    Init output folders data, blender settings and scene settings.

    :param config: A dict containing settings-preferences
    :return: A string containing the path of the main directory created
    """
    import src.blender_utilities.yaml as yaml
    # Set seed for reproducibility
    random.seed(config["parsed"]["seed"])
    np.random.seed(config["parsed"]["seed"])

    # Create main folder
    main_dir = os.path.join(config["global"]["main_dir"], config["parsed"]["name"])
    try:
        os.makedirs(main_dir)
    except OSError:
        print(main_dir)
        print(f"ERROR. Folder of name {config['parsed']['name']} already exists!")
        if not get_arguments().debug:
            sys.exit(1)

    # Save the config file
    with open(os.path.join(main_dir, "config.yaml"), 'w') as f:
        yaml.dump(config, f, sort_keys=False)

    return main_dir

def save_scene(scene_name,output_scene_dir,config: dict):
    """ try:
        os.makedirs(output_scene_dir)
    except OSError:
        print(output_scene_dir)
        if not get_arguments().debug:
            sys.exit(1) """
    saving_file = os.path.join(output_scene_dir,scene_name+".blend")
    bpy.ops.wm.save_as_mainfile(filepath=saving_file,copy=True)


def _enable_gpus(device_type: str, use_cpus: bool = False) -> list:
    """
    Update the available devices and activate them.

    :param device_type: Type of devices to use
    :param use_cpus: Use only CPU devices or GPU ones
    :return: List of devices that will be used
    """
    cycles_preferences = bpy.context.preferences.addons["cycles"].preferences
    # Get devices
    cycles_preferences.get_devices()  # update devices in the preferences
    devices = [device for device in cycles_preferences.devices]  # from struct to list
    # Set activated gpus
    activated_gpus = []
    for device in devices:
        if device.type == "CPU":
            device.use = use_cpus
            if use_cpus:
                activated_gpus.append(device.name)
        else:
            device.use = True
            activated_gpus.append(device.name)
    # Update compute devices
    cycles_preferences.compute_device_type = device_type
    bpy.context.scene.cycles.device = "GPU" if device_type == "CUDA" else "CPU"
    return activated_gpus
