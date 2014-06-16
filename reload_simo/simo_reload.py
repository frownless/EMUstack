"""
Reload simulation results for further manipulation.

Sample script illustrating how to reload simulation objects from .npz files.
Once you have access to the objects you can do everything you forgot to at runtime,
eg. plot different spectra, plot using routines you didn't have at runtime,
view/print/export particular quantities.
"""

import numpy as np
import sys
sys.path.append("../backend/")

import objects
import materials
import plotting
from stack import *

directory = '/home/bjorn/Results/14_06-Ev_FoMs/day3/fig_of_merit-900-1100-single_large_grating-higher_grating'
npz_file  = 'Simo_results20140610191336'
data = np.load(directory+'/'+npz_file+'.npz')
stacks_list = data['stacks_list']

#### stacks_list is now just like in the original simo.py ####

# plotting.t_r_a_plots(stacks_list) 

plotting.evanescent_merit(stacks_list, lay_interest=0)
plotting.evanescent_merit(stacks_list, lay_interest=1)
