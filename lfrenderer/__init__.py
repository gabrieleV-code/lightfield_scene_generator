from src.lfrenderer.scene import SceneManager
from src.lfrenderer.scene.custom import ChessboardSceneManager
from src.lfrenderer.scene.custom import ChessboardSceneSilvrManager
from src.lfrenderer.scene.custom import ObjaverseSceneManager


def get_scene_manager(manager_name: str, output_dir: str,
                      row_sensors: int = 15, column_sensors: int = 15) -> SceneManager:
    match manager_name.lower():
        case "chessboard":
            return ChessboardSceneManager(output_dir, row_sensors=row_sensors, column_sensors=column_sensors)
        case "chessboard_silvr":
            return ChessboardSceneSilvrManager(output_dir, row_sensors=row_sensors, column_sensors=column_sensors)
        case "objaverse":
            return ObjaverseSceneManager(output_dir, row_sensors=row_sensors, column_sensors=column_sensors)
        case _:
            assert False, f"get_scene_manager -> manager_name: '{manager_name.lower()}' not managed yet."
