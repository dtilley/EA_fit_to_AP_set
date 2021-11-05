import pandas as pd
import os
import sys
import time
import datetime


def main(indir):
    filenames = os.listdir(indir)
    popfiles = list(filter(lambda k: 'fitness' not in k, filenames))
    popfiles = list(filter(lambda k: 'strategy' not in k, popfiles))
    popfiles = list(filter(lambda k: 'pop_' in k, popfiles))

    prms_prefix = 'pop_'
    suffix = '.txt'
    strtgy_prefix = 'pop_strategy_'
    ftnss_prefix = 'pop_fitness_'
    
    gens = []
    for i in popfiles:
        try:
            gens.append(int(i[(i.find('_')+1):i.find('.')]))
        except ValueError:
            print('File Parsing Error.')
            sys.exit()
    gens.sort()

    # Not fixed yet
    tstamp = time.ctime(os.path.getmtime(os.path.join(indir,'pop_1.txt')))
    dt = datetime.datetime.strptime(tstamp, "%a %b %d %H:%M:%S %Y")



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
