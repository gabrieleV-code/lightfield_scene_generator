# Run as:
# "C:\Program Files\Blender Foundation\Blender 3.3\blender.exe" -b "C:\Users\gabri\OneDrive\Documenti\UniTO-DOCS\Stage\LightfieldsRenderer\lightfield_objaverse_3_36_BiggerScale.blend" -P main.py -- --name test

import sys
import time
from pathlib import Path
import bpy

# use installed packages here

def prepare():
    # Append the project folder in the system paths, so we can use all the other scripts in this project.
    # This is a very bad way to do this but for now it works
    if str(Path(__file__).resolve().parent.parent) not in sys.path:
        sys.path.append(str(Path(__file__).resolve().parent.parent))


def main(config: dict):
    from src.blender_utilities import init
    from src.lfrenderer import get_scene_manager
    output_dir = init(config)

    number_of_renders = config["global"]["dataset_size"]
    row_sensors = config["camera"]["sensors_row"]
    column_sensors = config["camera"]["sensors_column"]
    row_sensors_offset = config["camera"]["sensors_row_offset"]
    column_sensors_offset = config["camera"]["sensors_column_offset"]
    scale = config["camera"]["sensors_scale"]
    full_generation_start = time.time()

    scenes_n = 25
    number_of_renders = 10
    for scene_idx in range(scenes_n):
        scene_name = "Scene_"+str(scene_idx)
        from src.blender_utilities import init_for_render,save_scene

        output_scene_dir = init_for_render(scene_name,config)
        scene_manager = get_scene_manager(config["global"]["manager"], output_scene_dir,
                                        row_sensors=row_sensors, column_sensors=column_sensors)
        loop = "No"
        while(loop=="No"):
            scene_manager.randomize_scene(config)
            
            scene_manager.randomize_camera(config)
     
            loop = input("Keep scene models? (Yes/No)")
        save_scene(scene_name,output_scene_dir,config)

        for img_idx in range(number_of_renders):           
            print(f"\nSTATUS: [{img_idx + 1}/{number_of_renders}]\n")

            loop = "No"
            while(loop!="Yes" and loop!="Quit"):
                loop = input("Can the lightfiled be rendered? (Yes/No/Quit/Dof/Distance)")
                if(loop=="Dof"):
                    config["camera"]["dof"] = float(input("Set a Dof value: "))
                    scene_manager.show_scene(config)
                if(loop=="Distance"):
                    config["camera"]["distance"] = float(input("Set a distance value: "))
                    scene_manager.show_scene(config)
                if(loop=="No"):
                    scene_manager.randomize_camera(config)
            if loop =="Quit":
                scene_idx-=1
                break;
            
            scene_manager.depth_map_render(img_idx)
            scene_manager.render_lightfield(img_idx, sensors_row_offset=row_sensors_offset,
                                            sensors_column_offset=column_sensors_offset, scale=scale)
    print(f"Time: {time.time() - full_generation_start}")


def parse_arguments():
    from src.blender_utilities import get_arguments
    from src.my_utils.config_loader import load_from_args
    return load_from_args(get_arguments())


if __name__ == '__main__':
    prepare()
    main(parse_arguments())
