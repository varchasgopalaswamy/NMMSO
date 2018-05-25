import numpy as np
from .insect import Insect
from .utilities import out_of_bounds


class Swarm(object):

    def __init__(self, objective, bounds, tolerance, max_insects=100):
        self.flagged = True
        self.best_insect = None
        self.best_insect_index = None
        self.objective = objective
        self.max_insects = max_insects
        self.tolerance=tolerance
        self.size = 0
        self.insects = np.empty(shape=max_insects, dtype=Insect)

        self._iterator = 0
        self.bounds = bounds

    @property
    def full(self):
        if self.size < self.max_insects:
            return False
        else:
            return True

    def __iter__(self):

        if self.size < 0:
            return [].__iter__()
        elif self.size == 0:
            return np.atleast_1d(self.insects[0]).__iter__()
        else:
            return self.insects[0:self.size].__iter__()

    def __getitem__(self, item: int):
        if item > self.size:
            raise IndexError
        if item < 0:
            return self.insects[self.size + item]
        else:
            return self.insects[item]

    def add(self, insect:Insect=None,position=None,velocity=None):
        if self.size >= self.max_insects:
            raise IndexError
        if insect is not None:
            self.insects[self.size] = insect
            self.size += 1
        elif position is not None and velocity is not None:
            self.insects[self.size] = Insect(position,velocity,
                      objective=self.objective,bounds=self.bounds)
            self.size += 1
        else:
            raise ValueError
        self.evaluate(self.size - 1)
    def remove(self,insect_index):
        self.insects = np.delete(self.insects,insect_index)
        self.insects.resize((self.max_insects,))
        self.size -= 1
        self.insects[self.size:] = None

    def distance(self,other_swarm):
        return np.sqrt(np.sum((self.best_insect.position - other_swarm.best_insect.position)**2))

    def nearest_neighbour(self,other_swarms):
        distance = np.inf
        nearest_swarm = None
        for swarm in other_swarms:
            this_distance = self.distance(swarm)
            if this_distance < distance:
                distance = this_distance
                nearest_swarm = swarm
        return nearest_swarm
    def increment(self, nearest_swarm=None):
        if not self.full:
            oob = True
            while oob:
                if nearest_swarm is None:
                    position = np.random.uniform(low=self.bounds[:, 0], high=self.bounds[:, 1])
                else:
                    hypersphere_radius = (self.best_insect.position - nearest_swarm.best_insect.position) / 2
                    delta = np.random.uniform(low=-hypersphere_radius, high=hypersphere_radius)
                    position = self.best_insect.position + delta
                oob = out_of_bounds(position, self.bounds)

            if nearest_swarm is None:
                velocity = np.random.uniform(low=self.bounds[:, 0], high=self.bounds[:, 1])
            else:
                hypersphere_radius = (self.best_insect.position - nearest_swarm.best_insect.position) / 2
                delta = np.random.uniform(low=-hypersphere_radius, high=hypersphere_radius)
                velocity = self.best_insect.position + delta

            self.add(position=position, velocity=velocity)

        else:
            random_insect = np.random.randint(low=0, high=self.max_insects)
            self[random_insect].update(self.best_insect)
            self.evaluate(random_insect)

    def evaluate(self, insect_number):
        import copy
        insect = self[insect_number]
        fitness = insect.fitness
        if self.best_insect is None:
            #print('Initializing best')
            self.best_insect = copy.copy(insect)
            self.flagged = True
        elif fitness > self.best_insect.fitness:
            #print('Updating {prev} to {next}'.format(prev=self.best_insect,next=insect))
            self.best_insect = copy.copy(insect)
            self.flagged = True

    def split(self,nearest_swarm=None):
        from .utilities import separated_peaks
        random_insect_idx = np.random.randint(low=0, high=self.size)
        random_insect = self.insects[random_insect_idx]

        midpoint = random_insect.midpoint(self.best_insect)
        if nearest_swarm is None:
            velocity = np.random.uniform(low=self.bounds[:, 0], high=self.bounds[:, 1])
        else:
            hypersphere_radius = (self.best_insect.position - nearest_swarm.best_insect.position) / 2
            delta = np.random.uniform(low=-hypersphere_radius, high=hypersphere_radius)
            velocity = self.best_insect.position + delta
        midpoint.velocity = velocity

        if np.sum((midpoint.position  - random_insect.position)**2)**0.5 < self.tolerance:
            new_swarm = None
        else:
            if separated_peaks(left=random_insect,right=self.best_insect,objective=self.objective,nmax=5):
                new_swarm = Swarm(objective=self.objective,max_insects=self.max_insects,bounds=self.bounds,tolerance=self.tolerance)
                new_swarm.add(random_insect)
                self.remove(random_insect_idx)
                self.add(midpoint)
            else:
                if self.best_insect.fitness < midpoint.fitness:
                    #self.insects[self.best_insect_index] = midpoint
                    self.best_insect = midpoint
                new_swarm = None
        return new_swarm

    def merge(self,other):
        if self.size + other.size < self.max_insects:
            for insect in self:
                other.add(insect)
        else:
            all_insects = np.concatenate((self.insects[0:self.size],other.insects[0:other.size]))
            fitnesses = np.zeros_like(all_insects,dtype=np.float64)
            for idx, swarm in enumerate(all_insects):
                fitnesses[idx] = swarm.fitness
            best_fitness = np.argsort(fitnesses)

            other.insects = all_insects[best_fitness][0:self.max_insects]
            other.size = self.max_insects
            other.flagged = False


    def plot(self,ax=None,levels=30):
        import matplotlib.pyplot as plt
        if ax is None:

            fig,ax = plt.subplots()
        x_grid = np.linspace(start=self.bounds[0,0],stop=self.bounds[0,1],num=100)
        y_grid = np.linspace(start=self.bounds[1,0],stop=self.bounds[1,1],num=100)
        x_grid,y_grid = np.meshgrid(x_grid,y_grid)
        fvals = self.objective(np.stack((x_grid,y_grid)))
        ax.contour(x_grid,y_grid,fvals,levels)

        for insect in self:
            ax.scatter(insect.position[0],insect.position[1],color='k',s=100)
            ax.quiver(insect.position[0],insect.position[1],insect.velocity[0],insect.velocity[1],color='k',units='xy',angles='xy')
        ax.scatter(self.best_insect.position[0],self.best_insect.position[1],color='r',marker='s',s=100)
