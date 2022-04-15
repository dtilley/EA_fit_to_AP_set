import pandas as pd
import numpy as np
from scipy.interpolate import interp1d
from cell_models import protocols
from cell_models.kernik import KernikModel
import sys
import os


def main(args):


if __name__ == '__main__':
    if (len(sys.argv) == 1):
        outstr = 'python '+sys.argv[0]+' models_file vcp_file'
        print(outstr)
        sys.exit()
    elif (len(sys.argv) == 3):
