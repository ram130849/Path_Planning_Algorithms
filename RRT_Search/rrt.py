from rtree import index
import numpy as np
import random

from itertools import tee

class Tree(object):
    def __init__(self,s_space) -> None:
        """Tree Class.

        Args:
            s_space (int): search space object.
        """
        properties = index.Property()
        properties.dimension = s_space.dimensions
        self.vertex = index.Index(interleaved=True,properties=properties)
        self.vertex_count = 0
        self.edges = {}


def euclidean_distance(a,b):
    """ Gets Euclidean Distance between two points.

    Args:
        a (tuple): x and y coordinates of start point.
        b (tuple): x and y coordinates of end point.

    Returns:
        integer: euclidean distance between two points.
    """
    return np.linalg.norm(np.array(a)-np.array(b))


def get_points(start,end,resolution):
    dist = euclidean_distance(start,end)
    no_points = int(np.ceil(dist/resolution))

    if(no_points>1):
        step = dist/(no_points-1)
        for i in range(no_points):
            next_point = steer(start,end,i*step)
            yield next_point

def steer(start,end,dist):
    """ Generate a random new point by using step size from the diff between start and goal state.

    Args:
        start (tuple): start state.
        end (tuple): end goal state.
        dist (integer): distance to the goal state.

    Returns:
        movedPoint(Tuple): _description_
    """
    start,end = np.array(start),np.array(end)
    diff = end-start
    step = diff / (np.sqrt(np.sum(diff ** 2)))
    moved_point = start + step*dist
    return tuple(moved_point)


class RRT(object):
    def __init__(self, s_space, edge_list, x_init, x_goal, max_samples, res, prc=0.01) -> None:
        self.s_space = s_space
        self.edge_list = edge_list
        self.samples_taken = 0
        self.max_samples = max_samples
        self.resolution = res
        self.prc = prc
        self.x_init = x_init
        self.x_goal = x_goal
        self.trees = []  # list of all trees
        self.add_tree()


    def search(self):
        """ RRT Search Function.
        Returns:
            list : path to reach the goal.
        """
        self.add_vertex(0,self.x_init)
        self.add_edge(0,self.x_init,None)
        while True:
            for edge in self.edge_list:
                for i in range(edge[1]):
                    x_new,x_nearest = self.get_new_and_near(0,edge)

                    if x_new is None:
                        continue

                    self.connect_to_point(0, x_nearest, x_new)

                    solution = self.check_solution()
                    if solution[0]:
                        return solution[1]
    
    def add_tree(self):
        self.trees.append(Tree(self.s_space))

    def add_vertex(self, tree, v):
        self.trees[tree].vertex.insert(0, v + v, v)
        self.trees[tree].vertex_count += 1  
        self.samples_taken += 1
    
    def add_edge(self,tree,child,parent):
        self.trees[tree].edges[child] = parent

    def get_nearest(self,tree,x):
        return next(self.trees[tree].vertex.nearest(x,num_results=1,objects='raw'))

    def get_new_and_near(self,tree,edge):
        """ get nearest point from the search space and generate a new point in the search space 
            to connect to the goal state.

        Args:
            tree (Tree Object): random trees formed from the search space.
            edge (list): list of explored edges.  

        Returns:
            x_new,x_nearest: new point and nearest point to the goal state
        """
        x_rand = self.s_space.sample_free()
        x_nearest = self.get_nearest(tree,x_rand)
        x_new = self.bounded(steer(x_nearest,x_rand,edge[0]))
        # Check whether the new point does not belong to already formed vertices and 
        # it is in the collision free space.
        if((self.trees[0].vertex.count(x_new)!=0) or (not self.s_space.obstacle_free(x_new))):
            return None,None
        self.samples_taken+=1
        return x_new,x_nearest
    
    def bounded(self,point):
        """ check whether the given point is within the search space.

        Args:
            point (tuple): point to be checked

        Returns:
            tuple: bounded point.
        """
        point = np.maximum(point,self.s_space.dimension_lengths[:,0])
        point = np.minimum(point,self.s_space.dimension_lengths[:,1])
        return tuple(point) # check whether tuple is within the boundary limit.

    def connect_to_point(self,tree,x_a,x_b):
        if(self.trees[tree].vertex.count(x_b) == 0 and self.s_space.collision_free(x_a, x_b, self.resolution)):
                self.add_vertex(tree, x_b)
                self.add_edge(tree, x_b, x_a)
                return True
        return False
    
    def can_connect_to_goal(self,tree):
        """ get the nearest point and check if it can be connected to the goal.

        Args:
            tree (index): index of the tree to be explored.

        Returns:
            boolean: whether goal can be reached or not.
        """
        x_nearest = self.get_nearest(tree,self.x_goal)
        if(self.x_goal in self.trees[tree].edges and x_nearest == self.trees[tree].edges[self.x_goal]):
            return True
        if(self.s_space.collision_free(x_nearest,self.x_goal,self.resolution)):
            return True
        return False

    def get_path(self):
        """ Find path from the search space 

        Returns:
            path(list): path from start to end state. 
        """
        if(self.can_connect_to_goal(0)):
            print("Can connect to goal")
            x_nearest = self.get_nearest(0,self.x_goal)
            self.trees[0].edges[self.x_goal] = x_nearest
            path = [self.x_goal]
            current = self.x_goal
            if(self.x_init==self.x_goal):
                return path

            while(self.trees[0].edges[current]!=self.x_init):
                path.append(self.trees[0].edges[current])
                current = self.trees[0].edges[current]
            path.append(self.x_init)
            path.reverse()
            return path
        return None
        

    def check_solution(self):
        """ To check if solution to the goal state exists.

        Returns:
            is_Path,path: whether path to the goal state exists and return the path.
        """
        if(self.prc and random.random() < self.prc):
            print("to check the solution:", str(self.samples_taken), "samples")
            path = self.get_path()
            if(path is not None):
                return True,path
        
        if(self.samples_taken >= self.max_samples):
            return True, self.get_path()

        return False, None



    


    

