import numpy as np
from .utilities import out_of_bounds

class Insect(object):

    def __repr__(self):

#        print(self.position,self.velocity,self.fitness)
        return 'Position = {pos}, Fitness = {fit}, Previous Best = {prev}'.format(pos=self.position,fit=self.fitness,prev=self.previous_best)
    def __init__(self, position, velocity, objective, bounds=None, inertia=0.1, velocity_constraint=1.0,
                 cognitive_lf=2.0, social_lf=2.0):

        self.objective = objective
        self.position = np.asarray(position)
        self.velocity = np.asarray(velocity)
        self.inertia = inertia
        self.velocity_constraint = velocity_constraint
        self.cognitive_lf = cognitive_lf
        self.social_lf = social_lf
        if bounds is not None:
            self.bounds = bounds
            if out_of_bounds(self.position, self.bounds):
                raise ValueError
        else:
            self.bounds = np.zeros(shape=(self.position.shape[0], 2))
            self.bounds[:, 0] = -np.inf
            self.bounds[:, 1] = np.inf
        self.previous_best = position

    @property
    def fitness(self):
        return self.objective(self.position)

    def update(self, swarm_best):

        oob = True
        iterations = 0
        inertia_factor = 1.0
        previous_fitness = self.fitness
        while oob:
            r1, r2 = tuple(np.random.uniform(size=2))
            new_velocity = inertia_factor*self.inertia * self.velocity + self.cognitive_lf * r1 * (
                    self.previous_best - self.position) + self.social_lf * r1 * (swarm_best.position - self.position)
            new_position = self.position + self.velocity_constraint * new_velocity
            oob = out_of_bounds(new_position, self.bounds)
            iterations += 1
            if iterations > 100:
                inertia_factor -= 0.01
        self.position = new_position
        self.velocity = new_velocity
        if self.fitness > previous_fitness:
            self.previous_best = self.position

    def midpoint(self,best_insect):

        return Insect((self.position + best_insect.position)/2,(self.velocity + best_insect.velocity)/2,
                      objective=self.objective,bounds=self.bounds,inertia=self.inertia,
                      velocity_constraint=self.velocity_constraint,cognitive_lf=self.cognitive_lf,social_lf=self.social_lf)

