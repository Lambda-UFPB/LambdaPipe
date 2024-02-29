import pandas as pd
import numpy as np


class PharmaSphere:
    def __init__(self, x, y, z, radius, interaction_type, is_donor):
        self.x = x
        self.y = y
        self.z = z
        self.radius = radius
        self.interaction_type = interaction_type
        self.is_donor = is_donor

    def distance_to(self, other_sphere):
        dx = self.x - other_sphere.x
        dy = self.y - other_sphere.y
        dz = self.z - other_sphere.z
        center_distance = np.sqrt(dx**2 + dy**2 + dz**2)

        return center_distance
