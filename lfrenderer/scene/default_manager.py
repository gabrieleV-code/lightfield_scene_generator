import abc
import copy
import os

import bpy


class SceneManager(abc.ABC):
    def __init__(self, output_dir: str, row_sensors: int = 15, column_sensors: int = 15):
        self.output_dir = output_dir
        self.row_sensors = row_sensors
        self.column_sensors = column_sensors
        # Reference to the camera in the scene
        camera = bpy.context.scene.camera
        # Check if the camera is available
        if camera is None:
            assert False, "No camera available in the scene."
        self.default_camera_location = copy.deepcopy(camera.location)

    @abc.abstractmethod
    def randomize_scene(self, config: dict):
        pass

    @abc.abstractmethod
    def randomize_camera(self, config: dict):
        pass
    
    @abc.abstractmethod
    def show_scene(self, config: dict):
        pass
    
    @abc.abstractmethod
    def depth_map_render(img_idx):
        pass

    def _move_camera(self, sensor_idx_row: int, sensor_idx_column: int,
                     sensors_row_offset: float = 100.0, sensors_column_offset: float = 100, scale: float = 0.000001):
        # Reference to the camera in the scene
        camera = bpy.context.scene.camera
        # Check if the camera is available
        if camera is None:
            assert False, "No camera available in the scene."

        # Camera will move around its starting position
        # We start from 'bottom right' for the sensor (0, 0) and we move 'up left' for the last sensor (N, N)
        base_column_offset = sensors_column_offset * float(self.column_sensors) / 2.0 * scale
        base_row_offset = sensors_row_offset * float(self.row_sensors) / 2.0 * scale
        # Scaled movement
        scaled_column_offset = sensors_column_offset * sensor_idx_column * scale
        scaled_row_offset = sensors_row_offset * sensor_idx_row * scale
        # Update x, y, z coordinates of the camera
        camera.location = (
            self.default_camera_location[0] - base_column_offset + scaled_column_offset,
            self.default_camera_location[1] + base_row_offset - scaled_row_offset,
            self.default_camera_location[2]
        )

        print("Updated camera position to:")
        print(camera.location)

    def render_lightfield(self, img_idx: int, sensors_row_offset: float = 100.0, sensors_column_offset: float = 100,
                          scale: float = 0.000001):
        for sensor_idx_row in range(self.row_sensors):
            for sensor_idx_column in range(self.column_sensors):
                self._move_camera(sensor_idx_row, sensor_idx_column, sensors_row_offset=sensors_row_offset,
                                  sensors_column_offset=sensors_column_offset, scale=scale)
                img_name = f"lf_{img_idx}__row_{sensor_idx_row}__column_{sensor_idx_column}.png"
                bpy.context.scene.render.filepath = os.path.join(self.output_dir, "images", f"lf_{img_idx}", img_name)
                bpy.ops.render.render(write_still=True)
