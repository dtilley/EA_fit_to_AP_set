import pandas as pd
import numpy as np
import os
import sys
import time
import datetime
from shutil import copy2


def main(indir):
    filenames = os.listdir(indir)
    popfiles = list(filter(lambda k: 'fitness' not in k, filenames))
    popfiles = list(filter(lambda k: 'strategy' not in k, popfiles))
    popfiles = list(filter(lambda k: 'pop_' in k, popfiles))

    prms_prefix = 'pop_'
    suffix = '.txt'
    strtgy_prefix = 'pop_strategy_'
    ftnss_prefix = 'pop_fitness_'

    PARAM_NAMES = ['phi', 'G_K1', 'G_Kr', 'G_Ks', 'G_to', 'P_CaL',
                   'G_CaT', 'G_Na', 'G_F', 'K_NaCa', 'P_NaK',
                   'G_b_Na', 'G_b_Ca', 'G_PCa']

    gens = []
    for i in popfiles:
        try:
            gens.append(int(i[(i.find('_')+1):i.find('.')]))
        except ValueError:
            print('File Parsing Error.')
            sys.exit()
    gens.sort()

    # Get Time Stamp
    final_ndx = max(gens)
    filename = prms_prefix + str(final_ndx) + suffix
    tstamp = time.ctime(os.path.getmtime(os.path.join(indir, filename)))
    dt = datetime.datetime.strptime(tstamp, "%a %b %d %H:%M:%S %Y")
    dt = dt.strftime("%m%d%y_%H%M%S")

    # Copy final generation data
    fout = 'pop_final_' + dt + suffix
    fin_df = pd.read_csv(filename, delimiter=' ')
    fin_df.columns = PARAM_NAMES
    fin_df.to_csv(fout, sep=' ', index=False)
    filename = strtgy_prefix + str(final_ndx) + suffix
    fout = strtgy_prefix + dt + suffix
    fin_df = pd.read_csv(filename, delimiter=' ')
    fin_df.columns = PARAM_NAMES
    fin_df.to_csv(fout, sep=' ', index=False)
    filename = ftnss_prefix + str(final_ndx) + suffix
    fout = ftnss_prefix + dt + suffix
    copy2(os.path.join(indir, filename), fout)

    # Create log file
    fitnesses = []
    pops = []
    for i in gens:
        filename = ftnss_prefix + str(i) + suffix
        ftnss = pd.read_csv(filename, delimiter=' ')
        fitnesses.append(ftnss)
        filename = prms_prefix + str(i) + suffix
        pop = pd.read_csv(filename, delimiter=' ')
        pop['fitness'] = ftnss
        pops.append(pop)

    log = pd.DataFrame.from_dict(
        {'gen': np.array(gens),
         'nevals': np.array(np.repeat('NA', len(gens))),
         'avg': np.fromiter(map(np.mean, fitnesses), dtype=np.double),
         'std': np.fromiter(map(np.std, fitnesses), dtype=np.double),
         'min': np.fromiter(map(np.min, fitnesses), dtype=np.double),
         'max': np.fromiter(map(np.max, fitnesses), dtype=np.double)}
        )
    filename = 'logbook_' + dt + suffix
    log.to_csv(filename, sep=' ', index=False)

    # Create halloffame file of top 20% fitness score
    pops = pd.concat(pops)
    pops = pops.sort_values('fitness')
    NHOF = int(0.2 * pops.shape[0])
    hof = pops.iloc[0:NHOF, 0:len(PARAM_NAMES)]
    hof.columns = PARAM_NAMES
    hof_fitness = pops['fitness'][0:NHOF]
    filename = 'hof_' + dt + suffix
    hof.to_csv(filename, sep=' ', index=False)
    filename = 'hof_fitness_' + dt + suffix
    hof_fitness.to_csv(filename, sep=' ', index=False)


if __name__ == '__main__':
    if (len(sys.argv) == 2):
        if (os.path.exists(sys.argv[1])):
            main(sys.argv[1])
        else:
            print('Cannot find directory: '+sys.argv[1])
            sys.exit()
    else:
        outstr = 'python '+sys.argv[0]+' indir'
        print(outstr)
        sys.exit()
