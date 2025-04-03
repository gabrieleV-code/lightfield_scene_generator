import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

# Create figure
fig = plt.figure(figsize=(7,7))
ax = fig.add_subplot(111, projection='3d')

# Define first vertical plane (YZ plane at X=0, orange)
plane1 = np.array([
    [0, 0, 0],  # Bottom-left
    [0, 2, 0],  # Top-left (origin for v)
    [0, 2, 3],  # Top-right
    [0, 0, 3]   # Bottom-right
])

# Define second vertical plane (YZ plane at X=2, blue)
plane2 = np.array([
    [2, 0, 0],  # Bottom-left
    [2, 2, 0],  # Top-left
    [2, 2, 3],  # Top-right
    [2, 0, 3]   # Bottom-right
])

# Add planes to plot
ax.add_collection3d(Poly3DCollection([plane1], color='orange', alpha=0.5))
ax.add_collection3d(Poly3DCollection([plane2], color='blue', alpha=0.5))

# Plot rectangle edges for both planes
for plane in [plane1, plane2]:
    for i in range(4):
        ax.plot([plane[i][0], plane[(i+1)%4][0]], 
                [plane[i][1], plane[(i+1)%4][1]], 
                [plane[i][2], plane[(i+1)%4][2]], color='black')

vector_origins = np.array([
    plane1[3],  # Bottom-left
    plane1[3],  # Top-left
    plane2[3],  # Top-right
    plane2[3]   # Bottom-right
])

vector_targets = np.array([
    [0,3,0],  # Bottom-left
    [0,0,-3],  # Top-left
])

vector_name = ["u","v","s","t"]

for i in range(4):
    # Draw horizontal vector "v" (along Y-axis)
    v_origin = vector_origins[i]  # Upper-left corner of the first plane
    v_target =vector_origins[i] + vector_targets[i%2]  # Moves along Y-axis
    ax.quiver(v_origin[0], v_origin[1], v_origin[2], 
            v_target[0]-v_origin[0], v_target[1]-v_origin[1], v_target[2]-v_origin[2], 
            color='red', linewidth=2, arrow_length_ratio=0.1)

    # Label the vector "v"
    space = 0.2
    ax.text(v_target[0], v_target[1] + space, v_target[2]+space*-2*((i)%2), vector_name[i], color='red', fontsize=12)

# Set labels
ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.set_zlabel("Z")

# Set axis limits
ax.set_xlim([-1, 3])
ax.set_ylim([-1, 4])
ax.set_zlim([-1, 4])

# Viewing angle
ax.view_init(elev=20, azim=155)

plt.show()
