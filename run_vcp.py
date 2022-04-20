import pandas as pd
import numpy as np
import sys
from scipy.interpolate import interp1d
from cell_models import protocols
from cell_models.kernik import KernikModel


def run_vcp(ind_params, model_ndx, vc_data, dt=0.1, protocol_name='vcp', rtrn=False):
    # Check data structure
    column_names = vc_data.columns.to_list()
    try:
        column_names.index('mV_cell')
    except ValueError:
        print("voltage-clamp data file columns must have a column named 'mV_cell'.")
        sys.exit()

    # Create KC-model
    print('Model internal: [Na+]=10.0 mM and [K+]=130.0 mM')
    kc = KernikModel()
    kc.nai_millimolar = 10.0
    kc.ki_millimolar = 130.0

    # Set model parameters
    try:
        kc.default_parameters['G_K1'] = ind_params.G_K1
        kc.default_parameters['G_Kr'] = ind_params.G_Kr
        kc.default_parameters['G_Ks'] = ind_params.G_Ks
        kc.default_parameters['G_to'] = ind_params.G_to
        kc.default_parameters['P_CaL'] = ind_params.P_CaL
        kc.default_parameters['G_CaT'] = ind_params.G_CaT
        kc.default_parameters['G_Na'] = ind_params.G_Na
        kc.default_parameters['G_F'] = ind_params.G_F
        kc.default_parameters['K_NaCa'] = ind_params.K_NaCa
        kc.default_parameters['P_NaK'] = ind_params.P_NaK
        kc.default_parameters['G_b_Na'] = ind_params.G_b_Na
        kc.default_parameters['G_b_Ca'] = ind_params.G_b_Ca
        kc.default_parameters['G_PCa'] = ind_params.G_PCa
    except AttributeError:
        print('Individual model parameters could not be set.')
        sys.exit()

    # Build voltage-clamp protocol
    vcmd = vc_data.mV_cell
    t = np.arange(len(vcmd)) * dt

    steps = list()
    for i in range(len(vcmd)):
        steps.append(protocols.VoltageClampStep(voltage=vcmd[i], duration=dt))
    # Add holding potential steps
    steps = [protocols.VoltageClampStep(voltage=-80.0, duration=10000)] + steps
    steps.append(protocols.VoltageClampStep(voltage=-80.0, duration=100))
    vcp = protocols.VoltageClampProtocol(steps)

    # Simulate VCP
    vcp_response = kc.generate_response(vcp, is_no_ion_selective=False)
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
            current = vcp_response.current_response_info.get_current(i)
            f = interp1d(t_simu, current[t_bounds[0]:t_bounds[1]])
            currents.append(f(t))
        current_names = ['I_total'] + current_names
        current_names.append('t')
        current_names.append('vcmd')
        currents.append(t)
        currents.append(vcmd)

        # Write Data
        filename = 'model_' + str(model_ndx) + '_' + protocol_name + '.txt'
        data = pd.DataFrame(np.column_stack(currents), columns=current_names)
        data.to_csv(filename, sep=' ', index=False)

        if (rtrn):
            return((current_names, currents))
        else:
            return
    else:
        print('Interpolation bounds error with model: '+str(model_ndx))
        print('Retrying...')
        t_bounds[0] = t_bounds[0]-1
        t_bounds[1] = t_bounds[1]+1
        t_simu = vcp_response.t[t_bounds[0]:t_bounds[1]] - vcp_response.t[t_bounds[0]]
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
                current = vcp_response.current_response_info.get_current(i)
                f = interp1d(t_simu, current[t_bounds[0]:t_bounds[1]])
                currents.append(f(t))
        current_names = ['I_total'] + current_names
        current_names.append('t')
        current_names.append('vcmd')
        currents.append(t)
        currents.append(vcmd)

        # Write Data
        filename = 'model_' + str(model_ndx) + '_' + protocol_name + '.txt'
        data = pd.DataFrame(np.column_stack(currents), columns=current_names)
        data.to_csv(filename, sep=' ', index=False)

        if (rtrn):
            return((current_names, currents))
        else:
            return
