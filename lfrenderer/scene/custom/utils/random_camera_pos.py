import bpy

import random

import math

import mathutils

import numpy as np

random.seed(random.random())

def spherical_to_cartesian(r, theta, phi):
    x = r * math.sin(phi) * math.cos(theta)
    y = r * math.sin(phi) * math.sin(theta)
    z = abs(r * math.cos(phi))
    return x, y, z

def random_position_on_semi_sphere(obj,center,r,theta,phi):
    theta_rad = math.radians(theta)
    phi_rad = math.radians(phi)

    v = spherical_to_cartesian(r,theta_rad,phi_rad)
    v = mathutils.Vector(v)
    
    t = 1
    direction = (v + center)
    #direction.normalize()
    obj.location = t*direction
    
    direction = -1*v
    direction.normalize()
    # Calculate the rotation matrix that aligns the Z axis of the camera with the direction
    rotation_matrix = direction.to_track_quat('Y', 'Z').to_matrix().to_4x4()
    
    # Convert the rotation matrix to Euler angles (in radians)
    euler_angles = rotation_matrix.to_euler()
    print(euler_angles)
    # Set the camera's rotation to the computed Euler angles
    obj.rotation_euler = euler_angles
    print(obj.rotation_euler)
    #input("Press enter to processed...")
    bpy.context.view_layer.update()
    


""" theta = random.randint(80,90)
phi = random.randint(80,90)
r = 2 #in meters
center = mathutils.Vector((0.0, 0.0, 1.0))

obj = bpy.context.view_layer.objects.active
random_position_on_semi_sphere(obj,center,r,theta,phi) """



