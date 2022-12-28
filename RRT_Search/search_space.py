import numpy as np
from rtree import index

from obs_generator import obstacle_generator
from rrt import get_points

class Search_Space(object):

    def __init__(self,dimension_lengths,Obs_list=None) -> None:
        """Initialize the Search Space

        Args:
            dimension_lengths (_type_): range/length of each dimensions. 
            Obs_list (None): list of Obstacles.
        """
        if(len(dimension_lengths)<2):
            raise Exception("Must have atleast 2 dimensions.")

        self.dimensions = len(dimension_lengths)
        if(any(len(i) != 2 for i in dimension_lengths) or any(i[0] >= i[1] for i in dimension_lengths)):
            raise Exception("Dimensions should have start and end only and Start must be less than End")
        self.dimension_lengths = dimension_lengths
        p = index.Property()
        p.dimension = self.dimensions
        if(Obs_list is None):
            self.obs = index.Index(interleaved=True,properties=p)
        else:
            if(any(len(o)/2 != len(dimension_lengths) for o in Obs_list)):
                raise Exception("Obstacle has incorrect dimension definition")
            if(any(obs_dim[i] >= obs_dim[i+ len(obs_dim)//2] for obs_dim in Obs_list for i in range(len(obs_dim)//2))):
                raise Exception("Obstacle start must be less than obstacle end")
            self.obs = index.Index(obstacle_generator(Obs_list),interleaved=True,properties=p)

    def obstacle_free(self,x):
        return self.obs.count(x)==0

    def sample_free(self):
        while(True):
            sample = self.sample()
            if(self.obstacle_free(sample)):
                return sample

    def collision_free(self,start,end,r):
        points = get_points(start,end,r)
        collision_free = all(map(self.obstacle_free, points))
        return collision_free
    
    def sample(self):
        x = np.random.uniform(self.dimension_lengths[:,0],self.dimension_lengths[:,1])
        return tuple(x)