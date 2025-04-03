import sys

from src.blender_utilities import yaml


def load_from_args(args):
    if hasattr(args, "config"):
        with open(args.config, "r") as stream:
            try:
                config = yaml.safe_load(stream)
                config["parsed"] = {}
                config["parsed"]["name"] = args.name
                config["parsed"]["seed"] = args.seed
            except yaml.YAMLError as exc:
                print(exc)
                sys.exit(-1)
    else:
        assert False, "Args does not contain 'config' attribute."
    return config
