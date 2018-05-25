def out_of_bounds(position,bounds):
    out_of_bounds = False
    for idx,dim in enumerate(position):
        if not (bounds[idx,0] <= dim <= bounds[idx,1]):
            out_of_bounds = True
            break
    return out_of_bounds


def separated_peaks(left,right,objective,nmax=5):
    import numpy as np
    n = np.random.randint(low=1,high=nmax) + 2
    min_fitness = np.min([left.fitness,right.fitness])
    centers = np.linspace(start=0,stop=1.0,num=n)
    centers = centers[1:-1]
    partitions = np.random.normal(loc=centers,scale=0.05)
    has_valley = False
    for idx,fraction in enumerate(partitions):
        if fraction > 0 and fraction < 1:
            midpoint = fraction*left.position + (1-fraction)*right.position
            fitness = objective(midpoint)
            if fitness < min_fitness:
                has_valley = True
                break

    return has_valley

