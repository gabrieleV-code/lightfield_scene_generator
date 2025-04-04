# Lightfield Scene Generator

Synthetic Dataset Generation of Lightfields for Intra-Prediction training.
---

## Table of Contents

- [About](#about)
- [Installation](#installation)
- [Usage](#usage)

---
## About
This project has been developed in the context of intra-prediction training. It allows the generation of a dataset of synthetic lightfields through Blender 3.3. 

## Installation

The lightfield generator requires the installation of the lightfield camera add-on [blender_lightfield_addon_main
](https://github.com/gabrieleV-code/blender_lightfield_addon_main.git) for Blender 3.3.
It is then possible to generate a lightfield plane inside a scene that will be used as main camera.


## Usage
- Generate a lightfield plane inside a scene throught the modified IdLabMedia add-on (it will be used as main camera).
- Configure the [yaml](configs/generic_lenslets.yaml) file for the scene settings.
- Launch the script in [main.py](main.py) through command line over a blender scene (.blender) to start the lightfield generation (the file contains informations on what commad use).


