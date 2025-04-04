# Lightfield Scene Generator

Synthetic Dataset Generation of Lightfields for Intra-Prediction training.
---

## Table of Contents

- [About](#about)
- [Installation](#installation)
- [Scene Prerequisits](#sceneprerequisits)
- [Usage](#usage)

---
## About
This project has been developed in the context of intra-prediction training. It allows the generation of a dataset of synthetic lightfields through Blender 3.3. 


## Installation

The lightfield generator requires the installation of the lightfield camera add-on [blender_lightfield_addon_main
](https://github.com/gabrieleV-code/blender_lightfield_addon_main.git) for Blender 3.3.
It is then possible to generate a lightfield plane inside a scene that will be used as main camera. 

## Scene Prerequisits
- Use the predefined [Blender Scene](lightfield_objaverse_3_36_BiggerScale.blend).
- The scene requires a object called PhotoSet with a material called mat_photoset placed on it.
- The mat_photoset has a checker texture which colors are modified by the program. Their nodes should be HSV, named Color1 and Color2.
- The scene should contain a lightfield plane inside a scene throught the modified IdLabMedia add-on (it will be used as main camera).

## Usage
- Configure the [yaml](configs/generic_lenslets.yaml) file for the scene settings.
- Launch the script in [main.py](main.py) through command line over a blender scene (.blender) to start the lightfield generation (the file contains informations on what commad use).


