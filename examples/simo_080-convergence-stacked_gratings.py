"""
    Replicate Fig 2a from Handmer Opt Lett 2010
"""


import time
import datetime
import numpy as np
import sys
from multiprocessing import Pool
sys.path.append("../backend/")

import objects
import materials
import plotting
from stack import *

start = time.time()
################ Simulation parameters ################

# Number of CPUs to use im simulation
num_cores = 8

# Remove results of previous simulations
plotting.clear_previous('.log')
plotting.clear_previous('.txt')
plotting.clear_previous('.pdf')
plotting.clear_previous('.gif')

################ Light parameters #####################
wavelengths = np.linspace(1600,900,1)

BMs = [11,27,59,99,163,227,299,395,507,635,755,883,1059,1227,1419]
B = 0

for PWs in np.linspace(1,10,10):
    light_list  = [objects.Light(wl, max_order_PWs = PWs, theta = 28.0, phi = 0.0) for wl in wavelengths]

    ################ Grating parameters #####################
    period = 760

    superstrate = objects.ThinFilm(period, height_nm = 'semi_inf',
        material = materials.Air, loss = False)

    substrate  = objects.ThinFilm(period, height_nm = 'semi_inf',
        material = materials.Air, loss = False)

    grating_1 = objects.NanoStruct('1D_array', period, small_d=period/2,
        diameter1=int(round(0.25*period)), diameter2=int(round(0.25*period)), height_nm = 150, 
        inclusion_a = materials.Material(3.61 + 0.0j), inclusion_b = materials.Material(3.61 + 0.0j),
        background = materials.Material(1.46 + 0.0j), 
        loss = True, make_mesh_now = True, force_mesh = True, lc_bkg = 0.1, lc2= 3.0)

    grating_2 = objects.NanoStruct('1D_array', period, int(round(0.75*period)), height_nm = 2900, 
        background = materials.Material(1.46 + 0.0j), inclusion_a = materials.Material(3.61 + 0.0j), 
        loss = True, make_mesh_now = True, force_mesh = True, lc_bkg = 0.1, lc2= 3.0)

    num_BM = BMs[B]+30
    B += 1


    def simulate_stack(light):
       
        ################ Evaluate each layer individually ##############
        sim_superstrate = superstrate.calc_modes(light)
        sim_substrate   = substrate.calc_modes(light)
        sim_grating_1   = grating_1.calc_modes(light, num_BM = num_BM)
        sim_grating_2   = grating_2.calc_modes(light, num_BM = num_BM)

        ################ Evaluate full solar cell structure ##############
        """ Now when defining full structure order is critical and
        solar_cell list MUST be ordered from bottom to top!
        """

        stack = Stack((sim_substrate, sim_grating_1, sim_grating_2, sim_superstrate))
        # stack = Stack((sim_substrate, sim_grating_2, sim_superstrate))
        stack.calc_scat(pol = 'TE')
        return stack



    # Run in parallel across wavelengths.
    pool = Pool(num_cores)
    stacks_list = pool.map(simulate_stack, light_list)


    additional_name = str(int(PWs))
    stack_hs_wl_list = []
    for i in range(len(wavelengths)):
        stack_hs_wl_list.append(stacks_list[i])
    Efficiency = plotting.t_r_a_plots(stack_hs_wl_list, wavelengths, 
        add_name = additional_name)



######################## Wrapping up ########################
# Calculate and record the (real) time taken for simulation
elapsed = (time.time() - start)
hms     = str(datetime.timedelta(seconds=elapsed))
hms_string = 'Total time for simulation was \n \
    %(hms)s (%(elapsed)12.3f seconds)'% {
            'hms'       : hms,
            'elapsed'   : elapsed, }

# python_log = open("python_log.log", "w")
# python_log.write(hms_string)
# python_log.close()

print hms_string
print '*******************************************'
print ''
