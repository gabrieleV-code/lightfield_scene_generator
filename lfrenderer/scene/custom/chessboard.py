import random

import bpy

from src.lfrenderer import SceneManager


def _randomize_color(color):
    # Randomize a bit the color and normalize its value between [0, 1]
    normalized_color = [0.0, 0.0, 0.0, 1.0]
    normalized_color[0] = max(0.0, min(1.0, color[0] + random.uniform(-0.1, 0.1)))
    normalized_color[1] = max(0.0, min(1.0, color[1] + random.uniform(-0.1, 0.1)))
    normalized_color[2] = max(0.0, min(1.0, color[2] + random.uniform(-0.1, 0.1)))
    normalized_color[3] = color[3]
    return normalized_color


def _randomize_camera_settings(config: dict):
    # Deselect all objects in the scene
    bpy.ops.object.select_all(action='DESELECT')

    # Select main camera and randomize its ortho scale
    bpy.context.view_layer.objects.active = bpy.context.scene.objects['Camera']
    bpy.context.scene.objects['Camera'].select_set(True)

    bpy.context.object.data.ortho_scale = random.uniform(config["camera"]["ortho_scale"][0],
                                                         config["camera"]["ortho_scale"][1])
    bpy.context.object.rotation_euler[2] = random.uniform(config["camera"]["rotation_euler"][0],
                                                          config["camera"]["rotation_euler"][1])


class ChessboardSceneManager(SceneManager):
    def __init__(self, output_dir: str, row_sensors: int = 15, column_sensors: int = 15):
        super().__init__(output_dir, row_sensors, column_sensors)
        # (color1, color2, bg_color)
        self.colors = [
            [(1.0, 1.0, 1.0, 1.0), (0.0, 0.0, 0.0, 1.0), (0.9, 0.9, 0.9, 1.0)],  # Black and White, White
            [(0.96, 0.87, 0.68, 1.0), (0.64, 0.44, 0.25, 1.0), (0.8, 0.6, 0.4, 1.0)],  # Brown and Yellow, Yellow
            [(0.91, 0.85, 0.79, 1.0), (0.25, 0.18, 0.2, 1.0), (0.81, 0.75, 0.69, 1.0)],  # DBrown and DWhite, DWhite
            [(0.99, 0.97, 0.93, 1.0), (0.53, 0.13, 0.19, 1.0), (0.84, 0.82, 0.78, 1.0)],  # Red and White, White
            [(0.93, 1.0, 0.99, 1.0), (0.22, 0.65, 0.77, 1.0), (0.78, 0.85, 0.84, 1.0)],  # LBlue and White, White
            [(0.99, 0.99, 0.99, 1.0), (0.2, 0.62, 0.36, 1.0), (0.84, 0.84, 0.84, 1.0)],  # Green and White, White
        ]

    def _randomize_camera_settings(self,config: dict):
        # Deselect all objects in the scene
        bpy.ops.object.select_all(action='DESELECT')

        # Select main camera and randomize its ortho scale
        bpy.context.view_layer.objects.active = bpy.context.scene.objects['Camera']
        bpy.context.scene.objects['Camera'].select_set(True)

        bpy.context.object.data.ortho_scale = random.uniform(config["camera"]["ortho_scale"][0],
                                                            config["camera"]["ortho_scale"][1])
        bpy.context.object.rotation_euler[2] = random.uniform(config["camera"]["rotation_euler"][0],
                                                            config["camera"]["rotation_euler"][1])

    def randomize_scene(self, config: dict):
        # Path tracing samples
        bpy.context.scene.cycles.samples = random.randint(config["scene"]["samples"][0], config["scene"]["samples"][1])
        # Randomize camera position and rotation
        self._randomize_camera_settings(config)

        # Prepare chessboard colors
        colors = random.choice(self.colors)
        node_color1_value = _randomize_color(colors[0] if colors is not None else (1.0, 1.0, 1.0, 1.0))
        node_color2_value = _randomize_color(colors[1] if colors is not None else (0.0, 0.0, 0.0, 1.0))
        node_bg_color_value = _randomize_color(colors[2] if colors is not None else (0.9, 0.9, 0.9, 1.0))
        table_node_color_value = [random.uniform(0.0, 1.0), random.uniform(0.0, 1.0), random.uniform(0.0, 1.0), 1.0]
        # Randomize color1 and color2
        if random.uniform(0, 1) < 0.5:
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
        node_color2.outputs["Color"].default_value = node_color2_value

        if bg_mat is None:
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

        print("\nRandomization done\n")
