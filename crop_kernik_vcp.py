import pandas as pd
import numpy as np
from scipy.signal import argrelextrema
from scipy.signal import correlate


def read_model_data(model_indices, file_prefix='model_', file_suffix='_kernik_vcp.txt'):
    model_data = list()
    file_names = list()
    for i in range(len(model_indices)):
        filename = file_prefix+str(model_indices[i])+file_suffix
        file_names.append(filename)
        model_data.append(pd.read_csv(filename, delimiter=' '))
    return((file_names, model_data))


def crop_third_AP(model_data, file_names):
    # Check if extrema are identical this is hard coded
    model_extrema = list()
    for i in range(len(model_data)):
        extrema = argrelextrema(np.array(model_data[i].vcmd), np.greater)[0]
        model_extrema.append(extrema)
    # Expected 5 local maxima, 4 APs and the final step down to -80 mV
    cl = int((model_extrema[0][3] - model_extrema[0][2]))
    t_bounds = [int(model_extrema[0][2] - 0.4*cl),
                int(model_extrema[0][2] + 0.6*cl)]
    for i in range(len(model_extrema)):
        if (np.array_equiv(model_extrema[0], model_extrema[i]) is False):
            print('All model extrema are not equal.')
            return(model_extrema)
    # Clip around AP
    file_suffix = '_SAP.txt'
    for i in range(len(file_names)):
        filename = file_names[i].split('.txt')[0] + file_suffix
        tmp_data = model_data[i].iloc[t_bounds[0]:t_bounds[1], :]
        tmp_data.to_csv(filename, sep=' ', index=False)
    return(t_bounds)


def calc_vc_rmse(vc_data, models_data, models_ndx, file_names):
    # Check data shape
    if (vc_data.shape[0] != models_data[0].shape[0]):
        print('Time series lengths differ.')
        return
    # Align curves
    offset = list()
    start_t = [vc_data.t_ms[0]]
    end_t = [vc_data.t_ms[(len(vc_data.t_ms)-1)]]
    for i in range(len(models_data)):
        # Shift models to align with vc_data
        dx = np.mean(np.diff(vc_data.t_ms))
        shift = (np.argmax(correlate(vc_data.i_sub_leak, models_data[i].I_total)) - len(models_data[i].I_total))
        shift = shift * dx
        offset.append(shift)
        models_data[i].t = models_data[i].t + shift
        start_t.append(models_data[i].t[0])
        end_t.append(models_data[i].t[(len(models_data[i].t)-1)])
    # Trim boundaries
    t_bounds = [max(start_t), min(end_t)]
    t_ndx = [(np.abs(vc_data.t_ms - t_bounds[0]).argmin()),
             (np.abs(vc_data.t_ms - t_bounds[1]).argmin())]
    vc_data = vc_data.iloc[t_ndx[0]:t_ndx[1], :]
    rmse = list()
    for i in range(len(models_data)):
        t_ndx = [(np.abs(models_data[i].t - t_bounds[0]).argmin()),
                 (np.abs(models_data[i].t - t_bounds[1]).argmin())]
        models_data[i] = models_data[i].iloc[t_ndx[0]:t_ndx[1], :]
        if (vc_data.shape[0] == models_data[i].shape[0]):
            err_sqrd = (vc_data.i_sub_leak - models_data[i].I_total)**2
            models_data[i]['err_sqrd'] = err_sqrd
            models_data[i]['i_sub_leak'] = vc_data.i_sub_leak
            rmse.append(np.sqrt(np.mean(err_sqrd)))
            filename = file_names[i].split('.txt')[0] + '_sqrd_err.txt'
            models_data[i].to_csv(filename, sep=' ', index=False)
        else:
            print('Model '+str(models_ndx[i])+' misaligned.')
            return
    out_df = pd.DataFrame()
    filename = 'model_ndx_rmse.txt'
    out_df['ndx'] = models_ndx
    out_df['t_offset'] = offset
    out_df['rmse'] = rmse
    out_df.to_csv(filename, sep=' ', index=False)
