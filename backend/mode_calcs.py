"""
    mode_calcs.py is a subroutine of EMUstack that contains methods to 
    calculate the modes of a given layer, either analytically 
    (class 'Anallo') or from the FEM routine (class 'Simmo').

    Copyright (C) 2013  Bjorn Sturmberg, Kokou Dossou, Felix Lawrence

    EMUstack is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import numpy as np
import sys
from scipy import sqrt
sys.path.append("../backend/")

import materials
import objects
from Fortran import EMUstack

_interfaces_i_have_known = {}
pi = np.pi

class Modes(object):
    """ Super-class from which Simmo and Anallo inherit common functionality"""
    def k_pll_norm(self):
        return self.light.k_pll * self.structure.period

    def wl_norm(self):
        wl = float(self.light.wl_nm) / self.structure.period
        if self.light.wl_nm % self.structure.period == 0:
            wl += 1e-15
        return wl

    def air_ref(self):
        """ Return an :Anallo: for air for the same :Light: as this."""
        return self.light._air_ref(self.structure.period)

    def calc_grating_orders(self, max_order):
        """ Return the grating order indices px and py, unsorted."""
        # Create arrays of grating order indexes (-p, ..., p)
        pxs = pys = np.arange(-max_order, max_order + 1)
        # The inner loop in the fortran is over y, not x
        # So we call meshgrid with y first
        pys_mesh, pxs_mesh = np.meshgrid(pys, pxs)
        # Which elements of pys_mesh and pxs_mesh correspond to
        # orders low enough that we're interested in?
        low_ord = (pxs_mesh**2 + pys_mesh**2 <= max_order**2)

        return pxs_mesh[low_ord], pys_mesh[low_ord]

    def prop_fwd(self, height_norm):
        """ Return the matrix P corresponding to forward propagation/decay"""
        return np.mat(np.diag(np.exp(1j * self.k_z * height_norm)))

    def __del__(self):
        # Clean up _interfaces_i_have_known to avoid memory leak
        if _interfaces_i_have_known != None:
            for key in _interfaces_i_have_known.keys():
                if id(self) in key:
                    _interfaces_i_have_known.pop(key)










class Anallo(Modes):
    """ Like a :Simmo:, but for a thin film, and calculated analytically."""
    def __init__(self, thin_film, light):
        self.structure     = thin_film
        self.light         = light
        self.max_order_PWs = light.max_order_PWs
        self.is_air_ref    = False

    def calc_modes(self):
        #TODO: switch to just using calc_kz()?

        kzs = self.calc_kz()

        self.k_z = np.append(kzs, kzs) # add 2nd polarisation
        self.structure.num_pw_per_pol = len(kzs)

    def calc_kz(self):
        """ Return a sorted 1D array of grating orders' kz."""
        d = 1 #TODO: are lx, ly relevant here??

        # Calculate vectors of pxs and pys of all orders
        # with px^2 + py^2 <= self.max_order_PWs
        pxs, pys = self.calc_grating_orders(self.max_order_PWs)

        # Calculate k_x and k_y components of scattered PWs
        # (using the grating equation)
        alpha0, beta0 = self.k_pll_norm()
        alphas = alpha0 + pxs * 2 * pi / d
        betas  = beta0 + pys * 2 * pi / d

        k_z_unsrt = sqrt(self.k()**2 - alphas**2 - betas**2)

        if self.is_air_ref:
            assert not hasattr(self, 'sort_order'), \
                "Are you sure you want to reset the sort_order?"
            # Sort the modes from propagating to fastest decaying
            # k_z is real for propagating waves
            # This must be done consistently
            s = np.argsort(-1*k_z_unsrt.real + k_z_unsrt.imag)
            self.sort_order = s
        else:
            s = self.air_ref().sort_order
            assert s.shape == k_z_unsrt.shape, (s.shape, 
                k_z_unsrt.shape)

        # Find element of k_z_unsrt corresponding to zeroth order
        self.specular_order = np.nonzero((pxs[s] == 0) * (pys[s] == 0))[0][0]

        # Calculate number of propagating plane waves in thin film
        self.num_prop_pw_per_pol = (k_z_unsrt.imag == 0).sum()

        return k_z_unsrt[s]

    def n(self):
        if self.structure.loss:
            return self.structure.material.n(self.light.wl_nm)
        else:
            return self.structure.material.n(self.light.wl_nm).real


    def k(self):
        """ Return the normalised wavenumber in the background material"""
        return 2 * pi * self.n() / self.wl_norm()

    def Z(self):
        """ Return the wave impedance as a 1D array."""
        # Zcr is relative characteristic impedance Zc / Z0
        # Zcr = 1/n assumes that relative permeability is 1
        # Otherwise, use Zcr = \sqrt(epsilon_r / mu_r)
        Zcr = 1./self.n()

        # self.k_z repeats itself halfway through
        # First half is for TE pol, second is for TM
        num_pw2 = len(self.k_z) / 2
        k_z = self.k_z[:num_pw2]
        assert (k_z == self.k_z[num_pw2:]).all()

        # Calculate the (relative) wave impedances Z
        # TE (E in interface plane): Z = Zcr * k/k_z
        # TM (H in interface plane): Z = Zcr / (k/k_z)
        k_on_kz = self.k() / k_z

        # TE is always represented first
        return np.concatenate((Zcr * k_on_kz, Zcr / k_on_kz))

    def specular_incidence(self, pol = 'TE'):
        """ Return a vector of plane wave amplitudes corresponding
            to specular incidence in the specified polarisation.

            i.e. all elements are 0 except the zeroth order.
        """
        # Element corresponding to 0th order, TE
        spec_TE = self.specular_order
        # Element corresponding to 0th order, TM
        spec_TM = self.specular_order + self.structure.num_pw_per_pol
        tot_num_pw = self.structure.num_pw_per_pol * 2

        inc_amp = np.mat(np.zeros(tot_num_pw, dtype='complex128')).T
        if   'TE' == pol:
            inc_amp[spec_TE] = 1
        elif 'TM' == pol:
            inc_amp[spec_TM] = 1
        elif 'R Circ' == pol:
            inc_amp[spec_TE] = 1/sqrt(2.)
            inc_amp[spec_TM] = +1j/sqrt(2.)
        elif 'L Circ' == pol:
            inc_amp[spec_TE] = 1/sqrt(2.)
            inc_amp[spec_TM] = -1j/sqrt(2.)
        else:
            raise NotImplementedError, \
            "Must select from the currently implemented polarisations; \
             TE, TM, R Circ, L Circ."

        return inc_amp









class Simmo(Modes):
    """docstring for Simmo"""
    def __init__(self, structure, light):
        self.structure      = structure
        self.light          = light
        self.max_order_PWs  = light.max_order_PWs
        self.prop_consts    = None
        self.mode_pol       = None

    def calc_modes(self, num_BM, delete_working = True):
        """ Run the FEM in Fortran """
        st = self.structure
        wl = self.light.wl_nm
        if self.structure.diameter2 == 0:
            nb_typ_el = 2
        else:
            nb_typ_el = 3
        n_effs = np.array([st.background.n(wl), st.inclusion_a.n(wl), 
            st.inclusion_b.n(wl)])
        n_effs = n_effs[:nb_typ_el]

        if self.structure.loss == False:
            n_effs = n_effs.real

        pxs, pys = self.calc_grating_orders(self.max_order_PWs)
        num_pw_per_pol = pxs.size
        self.num_BM = num_BM
        assert num_BM > num_pw_per_pol * 2, "You must include at least as many BMs as PWs. \n" + \
        "Currently you have %(bm)i BMs < %(np)i PWs." % {
            'bm': num_BM, 'np': num_pw_per_pol * 2} 

        d = self.structure.period

        # Prepare for the mesh
        with open("../backend/Data/"+self.structure.mesh_file) as f:
            n_msh_pts, n_msh_el = [int(i) for i in f.readline().split()]

        # Size of Fortran's complex superarray (scales with mesh)
        # In theory could do some python-based preprocessing
        # on the mesh file to work out RAM requirements
        cmplx_max = 2**27#30

        # Parameters that control how FEM routine runs
        FEM_debug = 0   # Fortran routine will print info to screen and save additional into to file
        E_H_field = 1   # Selected formulation (1=E-Field, 2=H-Field)
        i_cond    = 2   # Boundary conditions (0=Dirichlet,1=Neumann,2=Periodic)
        itermax   = 30  # Maximum number of iterations for convergence

        resm = EMUstack.calc_modes(
            self.wl_norm(), self.num_BM, self.max_order_PWs, 
            self.structure.period, FEM_debug, 
            self.structure.mesh_file, n_msh_pts, n_msh_el,
            n_effs, self.k_pll_norm(),
            E_H_field, i_cond, itermax, 
            self.structure.plot_modes, self.structure.plot_real, 
            self.structure.plot_imag, self.structure.plot_abs,
            num_pw_per_pol, cmplx_max, nb_typ_el)

        self.k_z, J, J_dag, self.sol1, self.sol2, self.mode_pol = resm

        self.J, self.J_dag = np.mat(J), np.mat(J_dag)

        if delete_working:
            self.sol1 = None
            self.sol2 = None
            # self.mode_pol = None

def r_t_mat(lay1, lay2):
    """ Return R12, T12, R21, T21 at an interface between lay1
        and lay2.
    """
    assert lay1.structure.period == lay2.structure.period

    # We memorise to avoid extra calculations
    global _interfaces_i_have_known
    # Have we seen this interface before?
    try:
        return _interfaces_i_have_known[id(lay1), id(lay2)]
    except KeyError: pass
    # Or perhaps its reverse?
    try:
        R21, T21, R12, T12 = _interfaces_i_have_known[id(lay2), id(lay1)]
        return R12, T12, R21, T21
    except KeyError: pass

    # No? Then we'll have to calculate its properties.
    if isinstance(lay1, Anallo) and isinstance(lay2, Anallo):
        ref_trans = r_t_mat_anallo(lay1, lay2)
    elif isinstance(lay1, Anallo) and isinstance(lay2, Simmo):
        ref_trans = r_t_mat_tf_ns(lay1, lay2)
    elif isinstance(lay1, Simmo) and isinstance(lay2, Anallo):
        R21, T21, R12, T12 = r_t_mat_tf_ns(lay2, lay1)
        ref_trans = R12, T12, R21, T21 
    elif isinstance(lay1, Simmo) and isinstance(lay2, Simmo):
        raise NotImplementedError, \
            "Sorry! For, now you can put an extremely thin film between your \
            NanoStructs"
    
    # Store its R and T matrices for later use
    _interfaces_i_have_known[id(lay1), id(lay2)] = ref_trans
    return ref_trans

def r_t_mat_anallo(an1, an2):
    """ Returns R12, T12, R21, T21 at an interface between thin films.

        R12 is the reflection matrix from Anallo 1 off Anallo 2

        The sign of elements in T12 and T21 is fixed to be positive,
        in the eyes of `numpy.sign`
    """
    if len(an1.k_z) != len(an2.k_z):
        raise ValueError, "Need the same number of plane waves in \
        Anallos %(an1)s and %(an2)s" % {'an1' : an1, 'an2' : an2}

    Z1 = an1.Z()
    Z2 = an2.Z()

    R12 = np.mat(np.diag((Z2 - Z1)/(Z2 + Z1)))
    # N.B. there is potentially a branch choice problem here, stemming
    # from the normalisation to unit flux.
    # We normalise each field amplitude by
    # $chi^{\pm 1/2} = sqrt(k_z/k)^{\pm 1} = sqrt(Z/Zc)^{\pm 1}$
    # The choice of branch in those square roots must be the same as the
    # choice in the related square roots that we are about to take:
    T12 = np.mat(np.diag(2.*sqrt(Z2)*sqrt(Z1)/(Z2+Z1)))
    R21 = -R12
    T21 = T12

    return R12, T12, R21, T21

def r_t_mat_tf_ns(an1, sim2):
    """ Returns R12, T12, R21, T21 at an1-sim2 interface.

        Based on:
        Dossou et al., JOSA A, Vol. 29, Issue 5, pp. 817-831 (2012)
        http://dx.doi.org/10.1364/JOSAA.29.000817

        But we use Zw = 1/(Zcr X) instead of X, so that an1 does not 
        have to be free space.
    """
    Z1_sqrt_inv = sqrt(1/an1.Z()).reshape((1,-1))

    # In the paper, X is a diagonal matrix. Here it is a 1 x N array.
    # Same difference.
    A = np.mat(Z1_sqrt_inv.T * sim2.J.A)
    B = np.mat(sim2.J_dag.A * Z1_sqrt_inv)

    denominator = np.eye(len(B)) + B.dot(A)

    # R12 = -I + 2 A (I + BA)^-1 B
    # T12 = 2 (I + BA)^-1 B
    den_inv_times_B = np.linalg.solve(denominator, B)
    R12 = -np.eye(len(A)) + 2 * A * den_inv_times_B
    T12 = 2 * den_inv_times_B

    # R21 = (I - BA)(I + BA)^-1 = (I + BA)^-1 (I - BA)
    # T21 = 2 A (I + BA)^-1 = T12^T
    R21 = np.linalg.solve(denominator, (np.eye(len(B)) - B*A))
    T21 = 2 * A * denominator.I
    # T21 = T12.T

    return np.mat(R12), np.mat(T12), np.mat(R21), np.mat(T21)
