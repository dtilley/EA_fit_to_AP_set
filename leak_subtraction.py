import pandas as pd
import numpy as np
import os
import sys
import matplotlib.pyplot as plt


def main(vc_data, c_cell, ljp, filename):
    # Check data structure
    column_names = vc_data.columns.to_list()
    try:
        column_names.index('tms')
        column_names.index('mV')
        column_names.index('pApF')
    except ValueError:
        print("voltage-clamp columns must be named 'tms', 'mV', and 'pApF'")
        sys.exit()

    mV = vc_data.mV + ljp
    g_leak = (np.linspace(start=0.1, stop=5.0, num=50))**-1  # in nS
    g_leak_final = float()

    rmse_leak = list()
    for i in range(len(g_leak)):
        i_seal_leak = (g_leak[i] * mV)/c_cell
        rmse_leak.append(calc_rmse(vc_data.pApF, i_seal_leak))

    g_leak_crude = g_leak[rmse_leak.index(min(rmse_leak))]
    print('g_leak_crude: ' + str(g_leak_crude) + ' nS')

    if (rmse_leak.index(min(rmse_leak)) > 0):
        ndx = rmse_leak.index(min(rmse_leak))
        g_leak_fine = np.linspace(start=g_leak[(ndx-1)], stop=g_leak[(ndx+1)], num=50)
        rmse_fine = list()
        for i in range(len(g_leak_fine)):
            i_seal_leak = (g_leak_fine[i] * mV)/c_cell
            rmse_fine.append(calc_rmse(vc_data.pApF, i_seal_leak))
        g_leak_fine = g_leak_fine[rmse_fine.index(min(rmse_fine))]
        print('g_leak_fine: ' + str(g_leak_fine) + ' nS')
        g_leak_final = g_leak_fine
        x_ = np.array([g_leak_fine, g_leak_fine])
        y_ = np.array([min(rmse_leak), max(rmse_leak)])
        plt.plot(g_leak, rmse_leak)
        plt.plot(x_, y_)
        plt.show()
    else:
        g_leak_final = g_leak_crude
        plt.plot(g_leak, rmse_leak)
        plt.show()

    i_seal_leak = (g_leak_final * mV)/c_cell
    leak_subtracted = vc_data.pApF - i_seal_leak
    plt.plot(vc_data.tms, leak_subtracted)
    plt.show()

    # Write leak_subtracted
    file_suffix = '_leak_sub.txt'
    filename = filename.split('.txt')[0]+file_suffix
    vc_data['i_sub_leak'] = leak_subtracted
    vc_data['i_leak_pApF'] = i_seal_leak
    vc_data.to_csv(filename, sep=' ', index=False)


def calc_rmse(i_pApF, i_leak_pApF):
    n = float(len(i_pApF))
    rmse = (sum((i_pApF - i_leak_pApF)**2) / n)**0.5
    return(rmse)


if __name__ == '__main__':
    if (len(sys.argv) != 4):
        outstr = 'python '+sys.argv[0]+' vc_file Cm(pF) ljp(~ 2.8 mV)'
        print(outstr)
        sys.exit()
    elif (len(sys.argv) == 4):
        if os.path.exists(sys.argv[1]):
            vc_data = pd.read_csv(sys.argv[1], delimiter=' ')
            cm = float(sys.argv[2])
            ljp = float(sys.argv[3])
            main(vc_data, cm, ljp, sys.argv[1])
        else:
            print('Cannot find voltage-clamp file: '+sys.argv[1])
            sys.exit()
