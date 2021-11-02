import array as arr
import pandas as pd
import numpy as np
import random

from run_dclamp_simulation import run_ind_dclamp
from cell_recording import ExperimentalAPSet
from multiprocessing import Pool
from scipy.stats import lognorm

from deap import algorithms
from deap import base
from deap import creator
from deap import tools


indir = '/home/drew/projects/iPSC_EA_Fitting_Sep2021/cell_2/EA_fit_092421/EA_output/run_1_092921/'

filename = indir + 'pop_final_093021_020021_mini.txt'
pop_params = pd.read_csv(filename, delimiter=' ')
filename = indir + 'pop_strategy_093021_020021_mini.txt'
pop_strategy = pd.read_csv(filename, delimiter=' ')
filename = indir + 'pop_fitness_093021_020021_mini.txt'
pop_fitness = pd.read_csv(filename, delimiter=' ')
filename = indir + 'hof_093021_020021_mini.txt'
hof_params = pd.read_csv(filename, delimiter=' ')
filename = indir + 'hof_fitness_093021_020021_mini.txt'
hof_fitness = pd.read_csv(filename, delimiter=' ')

pop_ = (pop_params, pop_strategy, pop_fitness)
hof_ = (hof_params, hof_fitness)

creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", arr.array, typecode="d",
               fitness=creator.FitnessMin, strategy=None)
creator.create("Strategy", arr.array, typecode="d")


def rstrtES(ind_clss, strategy_clss, fit_clss, data):
    """This function constructs an individual from a prior EA population."""
    # Pass parameter to individual class
    ind = ind_clss(data[0])
    ind.strategy = strategy_clss(data[1])
    ind.fitness = fit_clss(data[2])

    return ind


def rstrtHOF(hof, ind_clss, fit_clss, data):
    """This function constructs a HallOfFame from a prior EA optimization."""
    if (data[0].shape[0] == len(data[1])):
        for i in range(data[0].shape[0]):
            ind = ind_clss(data[0].iloc[i, :])
            ind.fitness = fit_clss(data[1].iloc[i])
            hof.insert(ind)
        return hof
    else:
        print('\tHallofFame did not load successfully.')
        return(hof)


def initRstrtPop(container, rstInd, pop_data):
    pop = []
    N = pop_data[0].shape[0]
    for i in range(N):
        ind_data = (list(pop_data[0].iloc[0, :]), list(pop_data[1].iloc[0, :]),
                    tuple(pop_data[2].iloc[0, :]))
        pop.append(rstInd(data=ind_data))
    return container(pop)


def fitness(ind, ExperAPSet):
    model_APSet = run_ind_dclamp(ind, dc_ik1=ExperAPSet.dc_ik1, printIND=True)
    rmsd_total = (sum(ExperAPSet.score(model_APSet).values()),)
    return rmsd_total


def mutateES(ind, indpb=0.3):
    for i in range(len(ind)):
        if (indpb > random.random()):
            # Mutate
            ind[i] *= lognorm.rvs(s=ind.strategy[i], size=1)
            ind.strategy[i] *= lognorm.rvs(s=ind.strategy[i], size=1)
    # Check that Phi is
    if (ind[0] > 1.0):
        # Reset
        ind[0] = random.random()
        ind.strategy[0] = random.random()
    return ind,


def cxESBlend(ind1, ind2, alpha):
    for i, (x1, s1, x2, s2) in enumerate(zip(ind1, ind1.strategy,
                                             ind2, ind2.strategy)):
        # Blend the values
        gamma = 1.0 - random.random() * alpha
        ind1[i] = gamma * x1 + (1.0 - gamma) * x2
        ind2[i] = gamma * x2 + (1.0 - gamma) * x1
        # Blend the strategies
        gamma = 1.0 - random.random() * alpha
        ind1.strategy[i] = (1. - gamma) * s1 + gamma * s2
        ind2.strategy[i] = gamma * s1 + (1. - gamma) * s2

    return ind1, ind2


# Load in experimental AP set
# Cell 2 recorded 12/24/20 Ishihara dynamic-clamp 1.0 pA/pF
path_to_aps = '/home/drew/projects/iPSC_EA_Fitting_Sep2021/cell_2/AP_set'
cell_2 = ExperimentalAPSet(path=path_to_aps, file_prefix='cell_2_',
                           file_suffix='_SAP.txt', cell_id=2, dc_ik1=1.0)

toolbox = base.Toolbox()

toolbox.register("individual", rstrtES, creator.Individual, creator.Strategy,
                 creator.FitnessMin, data=None)
toolbox.register("population", initRstrtPop, list, toolbox.individual, pop_)

pop = toolbox.population()
NGEN = 2

MU = len(pop)
LAMBDA = 2 * MU
NHOF = int((0.1) * LAMBDA * NGEN)

hof = rstrtHOF(tools.HallOfFame(NHOF), creator.Individual, creator.FitnessMin, hof_)


# These functions allow the population to evolve.
toolbox.register("mate", cxESBlend, alpha=0.3)
toolbox.register("mutate", mutateES)

# Selection
toolbox.register("evaluate", fitness, ExperAPSet=cell_2)
toolbox.register("select", tools.selTournament, tournsize=3)

# Register some statistical functions to the toolbox.
stats = tools.Statistics(lambda ind: ind.fitness.values)
stats.register("avg", np.mean)
stats.register("std", np.std)
stats.register("min", np.min)
stats.register("max", np.max)

# To speed things up with multi-threading
p = Pool()
toolbox.register("map", p.map)

print('(mu,lambda): ('+str(MU)+','+str(LAMBDA)+')')

pop, logbook = algorithms.eaMuCommaLambda(pop, toolbox, mu=MU, lambda_=LAMBDA,
                                          cxpb=0.6, mutpb=0.3, ngen=NGEN, stats=stats,
                                          halloffame=hof, verbose=False)
