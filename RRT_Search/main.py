# !/usr/bin/python

import numpy as np

from rrt import RRT
from search_space import Search_Space
from obs_generator import generate_random_obstacles
from plotting import Plot


if __name__ == "__main__":
    """main function to generate obstacles and search space and run rrt code.
    """
    dimensions = np.array([(0, 100), (0, 100)]) 
    # Obstacles = np.array([(20, 20, 40, 40), (20, 60, 40, 80), (60, 20, 80, 40), (60, 60, 80, 80)])
    x_init = (0, 0) 
    x_goal = (90, 80)
    max_samples = 1024
    res = 1
    prc = 0.15

    n = 50
    s_space = Search_Space(dimensions)
    Obstacles = generate_random_obstacles(s_space, x_init, x_goal, n)
    edge_list = np.array([(8, 4)])

    rrt = RRT(s_space, edge_list, x_init, x_goal, max_samples, res, prc)
    path = rrt.search()

    plot = Plot("rrt_2d_with_50_obstacles")
    plot.plot_tree(rrt.trees)
    if(path):
        plot.plot_path(path)
    plot.plot_obstacles(Obstacles)
    plot.plot(x_init,x_goal)
    plot.draw(True)
