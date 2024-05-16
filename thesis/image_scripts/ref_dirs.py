import numpy as np
from pymoo.util.ref_dirs import get_reference_directions
from mpl_toolkits.mplot3d import Axes3D

import matplotlib.pyplot as plt

# Get reference directions for inside layer
ref_dirs_inside = get_reference_directions("das-dennis", 3, n_partitions=1, scaling=0.4)

# Get reference directions for boundary layer
ref_dirs_boundary = get_reference_directions("das-dennis", 3, n_partitions=2)

# Plotting
fig = plt.figure(figsize=(5, 5))
ax = fig.add_subplot(111, projection='3d')
ax.scatter(ref_dirs_inside[:, 0], ref_dirs_inside[:, 1], ref_dirs_inside[:, 2], label='Inside Layer', alpha=1)
ax.scatter(ref_dirs_boundary[:, 0], ref_dirs_boundary[:, 1], ref_dirs_boundary[:, 2], label='Boundary Layer', alpha=1)
ax.set_xlabel("f1")
ax.set_ylabel("f2")
ax.set_zlabel("f3")
ax.view_init(45, 45)
plt.legend()
plt.show()
