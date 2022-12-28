import uuid
import random

import numpy as np

def generate_random_obstacles(s_space,start,end,n):
    """ Generates N random obstacles(HyperRectangles) in the 2D grid.

    Args:
        s_space (search space object): _description_
        start (integer): current position.
        end (integer): goal position.
        n (integer): number of obstacles to be generated.

    Returns:
        obstacles(list): list of obstacles.
    """
    obstacles = []
    for i in range(n):
        center = np.empty(len(s_space.dimension_lengths),np.float32)
        s_collision = True
        f_collision = True
        edge_lengths = []
        for j in range(s_space.dimensions):
            x_dim = s_space.dimension_lengths[j][0]
            y_dim = s_space.dimension_lengths[j][1]
            diff = y_dim - x_dim
            min_edge_length = diff/10.0
            max_edge_length = diff/100.0
            edge_length = random.uniform(min_edge_length,max_edge_length)
            center[j] = random.uniform(x_dim + edge_length,y_dim + edge_length)
            edge_lengths.append(edge_length)

            if(abs(start[j]-center[j])>edge_length):
                s_collision = False
            if(abs(end[j]-center[j])>edge_length):
                f_collision = False

        min_corner = np.empty(s_space.dimensions,np.float32)
        max_corner = np.empty(s_space.dimensions,np.float32)
        for j in range(s_space.dimensions):
            min_corner[j] = center[j] - edge_lengths[j]
            max_corner[j] = center[j] + edge_lengths[j]
        obstacle = np.append(min_corner,max_corner)
        if(len(list(s_space.obs.intersection(obstacle)))>0  or s_collision or f_collision):
            continue
        obstacles.append(obstacle)
        s_space.obs.add(uuid.uuid4(),tuple(obstacle),tuple(obstacle))    

    return obstacles

def obstacle_generator(obstacles):
    for obstacle in obstacles:
        yield (uuid.uuid4(),obstacle,obstacle)
