"""
The Ueber python script, the only one that needs to be edited to set up all 
simulation parameters.
Uses other python scripts to prime the simulation (interpolate raw data over chosen 
wavelengths etc.), then calls the fortran routine pcpv.exe for each wavelength giving 
it all the required details. It does this by spanning a new process for each wavelength,
keeping the total running instances to a maximum number (num_cores_to_use). Finally all 
results are collected in text files and the spectra are plotted. A log file is found in
python_log.txt
"""

import time
import datetime
import numpy as np
import subprocess
import sys
# import multiprocessing   as mp
sys.path.append("../PCPV/")

import clear_previous
import objects
import materials
import cat_n_clean
import plotting
import temporary_bullshit as bs
from stack import *

start = time.time()
label_nu = 0
################ Simulation parameters ################

simo_para  = objects.Controls(debug = 0,max_order_PWs = 5, num_cores = 7,
    PrintAll = 0, Checks = 0, PrintSolution = 0, PrintSupModes = 0)
# Remove results of previous simulations
clear_previous.clean('.txt')
clear_previous.clean('.pdf')
clear_previous.clean('.log')
clear_previous.clean('.npy')

################ Light parameters #####################
wl_1     = 900
wl_2     = 1200
no_wl_1  = 2#8
# Set up light objects
wavelengths = np.linspace(wl_1, wl_2, no_wl_1)
light_list  = [objects.Light(wl, pol = 'TM', bs_label = i+1)
        for i, wl in enumerate(wavelengths)]
# Single wavelength run
# wl_super = 1050
# wavelengths = np.array([wl_super])
# light_list  = [objects.Light(wl) for wl in wavelengths]


################ Scattering matrices (for distinct layers) ##############
""" Calculate scattering matrices for each distinct layer.
Calculated in the order listed below, however this does not influence final 
structure which is defined later
"""

# period must be consistent throughout simulation!!!
period = 120

cover  = objects.ThinFilm(period = period, height_1 = 'semi_inf',
    film_material = materials.Material(3.5 + 0.0j), superstrate = materials.Air, 
    substrate = materials.Air,loss = True, label_nu = 0)
# scat_mats(cover, light_list, simo_para)
sim_cover = [cover.calc_modes(li, simo_para) for li in light_list]
bs.save_k_perps(sim_cover, sim_cover[0].structure.nu_tot_ords)

homo_film  = objects.ThinFilm(period = period, height_1 = 5, num_h = 1,
    film_material = materials.Material(3.6 + 0.27j), superstrate = materials.Air, 
    substrate = materials.Air,loss = True, label_nu = 1)
# scat_mats(homo_film, light_list, simo_para)
sim_homo_film = [homo_film.calc_modes(li, simo_para) for li in light_list]
bs.save_k_perps(sim_homo_film, sim_homo_film[0].structure.nu_tot_ords)

bottom = objects.ThinFilm(period = period, height_1 = 'semi_inf',
    film_material = materials.Air, superstrate = materials.Air, 
    loss = False, label_nu = 2)
# scat_mats(bottom, light_list, simo_para)
sim_bot = [bottom.calc_modes(li, simo_para) for li in light_list]
bs.save_k_perps(sim_bot, sim_bot[0].structure.nu_tot_ords)

max_num_BMs = 120
grating_1 = objects.NanoStruct('1D_grating', period, 100, height_1 = 25, num_h = 1,
    inclusion_a = materials.Ag, background = materials.Material(1.5 + 0.0j), loss = True, nb_typ_el = 4, 
    make_mesh_now = True, force_mesh = True, lc_bkg = 0.1, lc2= 4.0,
    label_nu = 3)
# Find num_BM for each simulation in a somewhat arbitrary way
# Maybe roll this out into a Bjorn-specific function
max_n = max([grating_1.inclusion_a.n(wl).real for wl in wavelengths])
num_BM_list = [round(max_num_BMs * grating_1.inclusion_a.n(wl).real/max_n)
    for wl in wavelengths]

sim_grat1 = [ grating_1.calc_modes(li, simo_para, num_BM = num_BM)
    for num_BM, li in zip(num_BM_list, light_list)]
bs.save_omegas(sim_grat1)


mirror = objects.ThinFilm(period = period, height_1 = 100,
    film_material = materials.Ag, superstrate = materials.Air, 
    loss = True, label_nu = 4)
# scat_mats(mirror, light_list, simo_para)
sim_mirror = [mirror.calc_modes(li, simo_para) for li in light_list]
bs.save_k_perps(sim_mirror, sim_mirror[0].structure.nu_tot_ords)


################ Construct & solve for full solar cell structure ##############
""" Now when defining full structure order is critical and
solar_cell list MUST be ordered from bottom to top!
"""
stack_list = [Stack(st) for st in 
    zip(sim_bot, sim_mirror, sim_grat1, sim_homo_film, sim_cover)]
for stack in stack_list:
    stack.calc_scat()
t_r_a_plots(stack_list)


# solar_cell = [bottom, mirror, grating_1, homo_film, cover]
# specify which layer is the active one (where absorption generates charge carriers)
active_layer = homo_film
act_lay_nu   = active_layer.label_nu - 1
# specify which layer for which the parameters should be printed on figures
lay_print_params = grating_1


# net_scat_mats(solar_cell, wavelengths, simo_para)

################# Efficiency & weighted spectra for active layer ################
plotting.average_spec('Lay_Absorb_%d' % act_lay_nu, 'Av_Absorb',  
    len(wavelengths), lay_print_params.num_h)
plotting.average_spec('Lay_Trans_%d'  % act_lay_nu, 'Av_Trans',   
    len(wavelengths), lay_print_params.num_h)
plotting.average_spec('Reflectance', 'Av_Reflec',  
    len(wavelengths), lay_print_params.num_h)
# Interpolate solar spectrum and calculate efficiency
Efficiency = plotting.irradiance('Av_Absorb', 'Weighted_Absorb', 'Av_Trans', 'Weighted_Trans',
 'Av_Reflec', 'Weighted_Reflec', lay_print_params.radius1, period, ff = lay_print_params.ff)
# Plot averaged sprectra
last_light_object = light_list.pop()
spec_list = ['Av_Absorb', 'Av_Trans', 'Av_Reflec']
plotting.tra_plot('Spectra', spec_list, lay_print_params, last_light_object,
    max_num_BMs, simo_para.max_order_PWs, Efficiency)
# Plot weighted averaged sprectra
spec_list = ['Weighted_Absorb', 'Weighted_Trans', 'Weighted_Reflec']
plotting.tra_plot('Spectra_weighted', spec_list, lay_print_params, last_light_object, 
    max_num_BMs, simo_para.max_order_PWs, Efficiency)
# # Plot dispersion diagrams for each layer
# plotting.omega_plot(solar_cell, lay_print_params, last_light_object, 
#     max_num_BMs, simo_para.max_order_PWs, Efficiency)


#---------------OLD plotting routines--------------#
# if simo_para.PropModes  == 1:
#     cat_n_clean.c_c_detA()
#     if solar_cell.loss   == False:
#         cat_n_clean.c_c_prop_modes()

# if solar_cell.num_h != 1:
# # Calculate and plot efficiency as a function of height
#     plotting.efficiency_h('Absorptance','Efficiency_h',wavelengths,len(wavelengths),
#     solar_cell.num_h, simo_para.Animate)
# # Plot absorptance as funtion of height
#     plotting.height_plot('Spectra_height', 'Absorptance', solar_cell, last_light_object,
#     max_num_BMs, max_order_PWs, 'Efficiency_h', Efficiency, solar_cell.num_h)


# Wraping up simulation by printing to screen and log file
print '\n*******************************************'
print 'The ultimate efficiency is %12.8f' % Efficiency
print '-------------------------------------------'

# Calculate and record the (real) time taken for simulation
elapsed = (time.time() - start)
hms     = str(datetime.timedelta(seconds=elapsed))
hms_string = 'Total time for simulation was \n \
    %(hms)s (%(elapsed)12.3f seconds)'% {
            'hms'       : hms,
            'elapsed'   : elapsed, }

python_log = open("python_log.log", "w")
python_log.write(hms_string)
python_log.close()

print hms_string
print '*******************************************'


def results_match_reference(filename):
    reference = np.loadtxt("ref/case_2/" + filename)
    result    = np.loadtxt(filename)
    np.testing.assert_allclose(result, reference, 1e-6, 1e-6, filename)

def results_match_reference_npy(filename):
    reference = np.load("ref/case_2/" + filename)
    result    = np.load(filename)
    np.testing.assert_allclose(result, reference, 1e-6, 1e-6, filename)

def test_txt_results():
    result_files = (
        "Absorptance.txt",      "beta_st0002.txt",
        "Lay_Trans_0.txt",      "omega_st0003.txt",
        "Av_Absorb.txt",        "beta_st0004.txt",
        "Lay_Trans_1.txt",      "Reflectance.txt",
        "Av_Reflec.txt",        "Efficiency.txt",
        "Lay_Trans_2.txt",      "Transmittance.txt",
        "Av_Trans.txt",         "Lay_Absorb_0.txt",
        "omega_Ft_st0003.txt",  "Weighted_Absorb.txt",
        "beta_st0000.txt",      "Lay_Absorb_1.txt",
        "omega_Fz_st0003.txt",  "Weighted_Reflec.txt",
        "beta_st0001.txt",      "Lay_Absorb_2.txt",
        "omega_pol_st0003.txt", "Weighted_Trans.txt",
    )
    for f in result_files:
        yield results_match_reference, f


def test_npy_results():
    result_files = (
        "st0000_wl0001_R12.npy",  "st0002_wl0002_R21.npy",
        "st0000_wl0001_R21.npy",  "st0002_wl0002_T12.npy",
        "st0000_wl0001_T12.npy",  "st0002_wl0002_T21.npy",
        "st0000_wl0001_T21.npy",  "st0003_wl0001_P.npy",
        "st0000_wl0002_R12.npy",  "st0003_wl0001_R12.npy",
        "st0000_wl0002_R21.npy",  "st0003_wl0001_R21.npy",
        "st0000_wl0002_T12.npy",  "st0003_wl0001_T12.npy",
        "st0000_wl0002_T21.npy",  "st0003_wl0001_T21.npy",
        "st0001_wl0001_P.npy",    "st0003_wl0002_P.npy",
        "st0001_wl0001_R12.npy",  "st0003_wl0002_R12.npy",
        "st0001_wl0001_R21.npy",  "st0003_wl0002_R21.npy",
        "st0001_wl0001_T12.npy",  "st0003_wl0002_T12.npy",
        "st0001_wl0001_T21.npy",  "st0003_wl0002_T21.npy",
        "st0001_wl0002_P.npy",    "st0004_wl0001_P.npy",
        "st0001_wl0002_R12.npy",  "st0004_wl0001_R12.npy",
        "st0001_wl0002_R21.npy",  "st0004_wl0001_R21.npy",
        "st0001_wl0002_T12.npy",  "st0004_wl0001_T12.npy",
        "st0001_wl0002_T21.npy",  "st0004_wl0001_T21.npy",
        "st0002_wl0001_R12.npy",  "st0004_wl0002_P.npy",
        "st0002_wl0001_R21.npy",  "st0004_wl0002_R12.npy",
        "st0002_wl0001_T12.npy",  "st0004_wl0002_R21.npy",
        "st0002_wl0001_T21.npy",  "st0004_wl0002_T12.npy",
        "st0002_wl0002_R12.npy",  "st0004_wl0002_T21.npy",
    )
    for f in result_files:
        yield results_match_reference_npy, f
