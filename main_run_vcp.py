import sys
import pandas as pd
from run_vcp import run_vcp


def main(params, vcmd, protocol_name):

    # Get model_ndx
    ndx = params.model_ndx
    num_models = params.shape[0]

    for i in range(num_models):
        run_vcp(params.iloc[i, 1:14], model_ndx=ndx[i], vc_data=vcmd, protocol_name=protocol_name)


if __name__ == '__main__':
    if (len(sys.argv) != 4):
        print('run_vcp_top_models.py params_file vc_cmd_file protocol_name')
        sys.exit()
    else:
        params = pd.read_csv(sys.argv[1], delimiter=' ')
        vcmd = pd.read_csv(sys.argv[2], delimiter=' ')
        protocol_name = sys.argv[3]
        main(params, vcmd, protocol_name)
