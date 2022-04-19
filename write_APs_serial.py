""" Rescores model APs and writes AP files """

import sys
import os
import pandas as pd

from run_dclamp_simulation import run_ind_dclamp
from cell_recording import ExperimentalAPSet


def main(argv):
    if (len(argv) != 2):
        print('write_hof_APs.py hof_file NUM_MODELS')
        return
    elif (os.path.exists(argv[0]) is False):
        print('Cannot find hof_file.')
        print('write_hof_APs.py hof_file NUM_MODELS')
        return
    else:
        # Load Hall of Fame File
        hof_filename = argv[0]
        fout_prefix = hof_filename.split('.txt')[0]
        fout_suffix = '.scrs'
        hof = pd.read_csv(hof_filename, delimiter=' ')
        # Check number of requested Individuals
        if (hof.shape[0] < int(argv[1])):
            print('Too many individuals requested. Check inputs.')
            return
        if (hof.shape[1] != 14):
            print('Number of model paramters unequal to hof_file. Check inputs.')
            return

        NUM_MODELS = int(argv[1])

        # Load in experimental AP set
        # Example: Cell 1 recorded 12/24/20 Ishihara dynamic-clamp 0.75 pA/pF
        path_to_aps = '/home/drew/projects/iPSC-EA_Aug-Oct_2021/cell_6/AP_set'
        cell = ExperimentalAPSet(path=path_to_aps, file_prefix='cell_6_',
                                   file_suffix='_SAP.txt', cell_id=6, dc_ik1=1.25)

        # Score AP_set against cell
        hof_scores = []
        for i in range(NUM_MODELS):
            model = hof.iloc[i, ]
            mod_APSet, ap_failure = run_ind_dclamp(model, dc_ik1=cell.dc_ik1)
            hof_scores.append(cell.score((mod_APSet, ap_failure), i, write_data=True))

        # Order the dict: Format output file
        column_names = []
        scrs_list = []
        scrs_dict = {}
        for i in hof_scores[0].keys():
            column_names.append(i)
            tmp = []
            for j in range(len(hof_scores)):
                tmp.append(hof_scores[j][i])
            scrs_list.append(tmp)
        fout_name = fout_prefix + fout_suffix
        if (len(column_names) == len(scrs_list)):
            for i in range(len(column_names)):
                scrs_dict[column_names[i]] = scrs_list[i]
            fout_df = pd.DataFrame.from_dict(scrs_dict)
            fout_df.to_csv(fout_name, sep=' ', index=False)
        else:
            print("Format Error.")
            return


if __name__ == '__main__':
    main(sys.argv[1:])
