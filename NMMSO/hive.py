import numpy as np
from .swarm import Swarm
class Hive(object):

    def __init__(self,objective, bounds,max_insects=100,max_increment=100, max_swarms = 1000,tolerance=1e-7):


        self.objective = objective
        self.max_insects = max_insects
        self.max_increment = max_increment
        self.max_swarms = max_swarms


        self.bounds = np.asarray(bounds)
        self.tolerance = tolerance
        self.size = 0
        self.swarms = np.empty(shape=max_swarms, dtype=Swarm)

    def __iter__(self):

        if self.size < 0:
            return [].__iter__()
        elif self.size == 0:
            return np.atleast_1d(self.swarms[0]).__iter__()
        else:
            return self.swarms[0:self.size].__iter__()

    def __getitem__(self, item: int):
        if item > self.size:
            raise IndexError
        if item < 0:
            return self.swarms[self.size + item]
        else:
            return self.swarms[item]


    def add(self, swarm:Swarm):
        if self.size >= self.max_swarms:
            self.swarms.resize((self.max_swarms+50,))
            self.max_swarms += 50

        self.swarms[self.size] = swarm
        self.size += 1

    def remove(self, swarm_index):
        self.swarms = np.delete(self.swarms, swarm_index)
        self.swarms.resize((self.max_swarms,))
        self.size -= 1
        self.swarms[self.size:] = None
    def increment(self):

        if self.size > self.max_increment:
            fitnesses = np.zeros_like(self.swarms[0:self.size])
            for idx, swarm in enumerate(self.swarms[0:self.size]):
                fitnesses[idx] = swarm.best_insect.fitness
            best_fit = np.argsort(fitnesses)

            for swarm_idx in best_fit[0:int(self.max_increment/2)]:
                this_swarm = self[swarm_idx]
                nearest_swarm = this_swarm.nearest_neighbour(np.delete(self.swarms[0:self.size],swarm_idx))
                self[swarm_idx].increment(nearest_swarm)

            for swarm_idx in np.random.permutation(best_fit)[0:int(self.max_increment/2)]:
                this_swarm = self[swarm_idx]
                nearest_swarm = this_swarm.nearest_neighbour(np.delete(self.swarms[0:self.size], swarm_idx))
                self[swarm_idx].increment(nearest_swarm)

        elif self.size == 0:
            self.swarms[0] = Swarm(objective=self.objective, max_insects=self.max_insects, bounds=self.bounds,tolerance=self.tolerance)
            self.swarms[0].increment()
            self.size += 1
        else:
            for swarm in self:
                swarm.increment()


    def split(self):
        def full(a):
            return a.full
        full = np.vectorize(full)
        full_swarm_idxs = np.where(full(self.swarms[0:self.size]))[0]
        if full_swarm_idxs.size == 0:
            pass
        else:
            random_swarm_idx = np.random.choice(full_swarm_idxs)
            random_full_swarm = self.swarms[random_swarm_idx]
            new_swarm = random_full_swarm.split()
            if new_swarm is not None:
                #print('Splitting from {s}'.format(s=random_swarm_idx))
                self.add(new_swarm)

    def crossover_add(self):
        from .insect import Insect
        new_swarm = Swarm(objective=self.objective, max_insects=self.max_insects, bounds=self.bounds,tolerance=self.tolerance)
        if np.random.uniform() < 0.5:
            new_swarm.increment()
        else:
            #print('Adding new swarm')
            new_position = []
            new_velocity = []
            parent_idx = np.random.randint(low=0,high=self.size,size=2)
            parents = np.zeros_like(parent_idx,dtype=Insect)
            parents[0] = self.swarms[parent_idx[0]].best_insect
            parents[1] = self.swarms[parent_idx[1]].best_insect
            for idx,pos in enumerate(parents[0].position):
                if np.random.uniform() < 0.5:
                    new_position.append(pos)
                else:
                    new_position.append(parents[1].position[idx])
                if np.random.uniform() < 0.5:
                    new_velocity.append(parents[0].velocity[idx])
                else:
                    new_velocity.append(parents[1].velocity[idx])
            new_swarm.add(position=new_position,velocity=new_velocity)
        self.add(new_swarm)

    def merge(self):
        from .utilities import separated_peaks
        def flagged(a):
            return a.flagged
        flagged = np.vectorize(flagged)
        if self.size > 2:
            flagged_swarm_idxs = np.where(flagged(self.swarms[0:self.size]))[0]
            #print(flagged_swarm_idxs)
            while flagged_swarm_idxs.size > 1:
                for swarm_idx in flagged_swarm_idxs:

                    this_swarm = self.swarms[swarm_idx]
                    nearest = this_swarm.nearest_neighbour(np.delete(self.swarms[0:self.size],swarm_idx))

                    if np.sum((nearest.best_insect.position - this_swarm.best_insect.position)**2)**0.5 < self.tolerance:
                        #print("merging {i} due to closeness".format(i=swarm_idx))
                        this_swarm.merge(nearest)
                        self.remove(swarm_idx)
                        break
                    else:

                        if not separated_peaks(left=this_swarm.best_insect,right=nearest.best_insect,objective=self.objective,nmax=10):
                            #print("merging {i} due to no valley".format(i=swarm_idx))
                            this_swarm.merge(nearest)
                            self.remove(swarm_idx)
                            break
                        else:
                            this_swarm.flagged = False
                flagged_swarm_idxs = np.where(flagged(self.swarms[0:self.size]))[0]



