import pandas as pd
import numpy as np
import os
import sys
from scipy.interpolate import interp1d
from cell_models import protocols
from cell_models.kernik import KernikModel


def run_vcp(ind_params, mvc_data, dt, ljp, filename):
    # Check data structure
    column_names = vc_data.columns.to_list()
    try:
        column_names.index('mV')
    except ValueError:
        print("voltage-clamp data file columns must have a column named 'mV'.")
        sys.exit()

    # Build voltage-clamp protocol
    vcmd = vc_data.mV + ljp
    t = np.arange(len(vc_data.mV)) * dt

    steps = list()
    for i in range(len(vcmd)):
        steps.append(protocols.VoltageClampStep(voltage=vcmd[i], duration=dt))
    # Add holding potential steps
    steps = [protocols.VoltageClampStep(voltage=-80.0, duration=10000)] + steps
    steps.append(protocols.VoltageClampStep(voltage=-80.0, duration=100))
    vcp = protocols.VoltageClampProtocol(steps)

    print('Model internal: [Na+]=10.0 mM and [K+]=130.0 mM')
    kci = KernikModel()
    kci.nai_millimolar = 10.0
    kci.ki_millimolar = 130.0

    vcp_response = kci.generate_response(vcp, is_no_ion_selective=False)
    # Remove v_hold segments
    t_bounds = [np.abs(vcp_response.t - 10000).argmin(),
                np.abs(vcp_response.t - (10000 + t[-1])).argmin()+1]
    t_simu = vcp_response.t[t_bounds[0]:t_bounds[1]] - vcp_response.t[t_bounds[0]]
    # Check bounds
    if (t_simu[0] <= t[0] and t_simu[-1] >= t[-1]):
        # Get simulated currents
        currents = list()
        I_total = vcp_response.current_response_info.get_current_summed()[t_bounds[0]:t_bounds[1]]
        f = interp1d(t_simu, I_total)
        currents.append(f(t))
        # Current Dictionary
        current_names = ['I_K1', 'I_To', 'I_Kr', 'I_Ks', 'I_CaL', 'I_NaK', 'I_Na',
                         'I_NaCa', 'I_pCa', 'I_F', 'I_bNa', 'I_bCa', 'I_CaT']
        for i in current_names:
            f = interp1d(t_simu, vcp_response.current_response_info.get_current(i)[t_bounds[0]:t_bounds[1]])
            currents.append(f(t))
        current_names = ['I_total'] + current_names
        return((current_names, currents))
    else:
        print('Interpolation bounds error.')
        return

"""if __name__ == '__main__':
    if (len(sys.argv) != 4):
        outstr = 'python '+sys.argv[0]+' vc_file dt ljp(~ 2.8 mV)'
        print(outstr)
        sys.exit()
    elif (len(sys.argv) == 4):
        if os.path.exists(sys.argv[1]):
            vc_data = pd.read_csv(sys.argv[1], delimiter=' ')
            dt = float(sys.argv[2])
            ljp = float(sys.argv[3])
            main(vc_data, dt, ljp, sys.argv[1])
        else:
            print('Cannot find voltage-clamp file: '+sys.argv[1])
            sys.exit()
"""
