#!/usr/bin/env ipython3

##
# @file
# calculations for velocity dispersion
# disk version

# (c) 2013 Pascal Steger, psteger@phys.ethz.ch

import pdb
import numpy as np
import scipy.integrate as integrate
import scipy.constants as constants
import math
import gi_helper as gh

# New rho function:
def rho(zvec, kpar, rho0):
    logrho0 = math.log(rho0)
    logrho = np.array(logrho0 + integrate.cumtrapz(-kpar,zvec,initial=0.))
    rhovec = np.exp(logrho)
    return rhovec
# calculate density from k(z) = -d(ln(rho))/dz, rho at z=0, using trapezoidal rule
# @param kpar: kpar(z) vector, with kpar(0) as zeroth element
# @param rho0: density at z=0
# @param zvec: vector of z, at which k(z) is given (requirs z[0] != 0.)

# New function for calculating the surface density
def Sig(zvec, rhovec):
    Sigvec = 2.*np.array(integrate.cumtrapz(rhovec,zvec,initial=0.))
    return Sigvec
# calculate (total) surface density from the density, using trapezoidal rule
# @param Sigvec: surface density vector, Sigma[0] = 0.
# @param rhovec: rho(z) vector, with rho(0) as zeroth element.
# OBS: rho(z) is total density: rho = rho_DM + rho_bary (if return total Sig)
# @param zvec: z-vector, at which rho/Sig(z) is given (requires z[0] != 0.)

# New function for calculating the z-dir velocity dispersion
def sigz2(zvec,Sigvec,nuvec,C):
    G1 = 4.299e-6  # Newton's constant in (km)^2*kpc/(Msun*s^2)
    Kzvec = -2.*constants.pi*G1*Sigvec
    integral = integrate.cumtrapz(nuvec*Kzvec,zvec,initial=0.) + C
    sig2 = integral/nuvec
    if (any(sig2<0.)):
        gh.LOG(1,'Negative sig2 in phys.sigz')
        raise ValueError('negative value in sig2 array')
        return
    #sigvec = np.sqrt(sig2)
    return sig2
# calculate z velocity dispersion using eq. 5 in 'almost' paper
# @param sigvec: velocity dispersion vector at the locations of zvec
# @param zvec: z-vector, at which nu/Sig(z) is given (assuming z[0] = 0.)
# @param nuvec: tracer number density at the locations of zvec
# @param C: Integration constant C in eq (5) in the 'almost' paper
# all arrays (zvec,Sigvec,nuvec) are required to be numpy arrays.
# outputs sigvec at z = zvec[1:], eg diskards first z point


def tilt(zipol, param, gp):
    tilttmp = 0.
    for i in range(gp.nbeta):
        tilttmp += param[i]*(zipol/max(zipol))**i
    return tilttmp
## \fn tilt(zipol, param, gp)
# return sum of polynomials for tilt as fct of radius
# TODO: get tilt size from Garbari+2011
# @param zipol [pc]
# @param param n_beta parameters
# @param gp global parameters


def kappa(xipol, Kz):
    z0 = xipol
    kzpar = -np.hstack([Kz[0]/z0[0], (Kz[1:]-Kz[:-1])/(z0[1:]-z0[:-1])])
    return kzpar
## \fn kappa(xipol, Kz)
# calculate vertical force from Kz
# @param xipol height above midplane [pc]
# @param Kz acceleration in z direction


def sig_rz(z, zpars, tpars):
    # Mirror prior
    tparsu = abs(tpars)

    # dz = zpars[2]-zpars[1]
    # sig_Rz = np.zeros(gp.nipol)
    # sig_Rz[0] = tparsu[0] * dz / 2.
    # for i in range(1,gp.nipol):
    #   sig_Rz[i] = sig_Rz[i-1] + tparsu[i] * dz
    # f = gp.ipol(zpars,sig_Rz,z)

    # Alternative here --> don't assume monotonic!
    f = gh.ipol(zpars, tparsu, z)
    return f
## \fn sig_rz(z, zpars, tpars)
# General function to describe the tilt profile
# @param z [pc]
# @param zpars [pc] z, on which sig is defined
# @param tpars tilt parameters: Rsun, hr, hsig


def rho_baryon_simplenu(zvec, params):
    G1 = 4.299e-6 # Newton's constant in (km)^2*kpc/(Msun*s^2)
    K=params[0]
    D=params[1]
    return (1/(4*np.pi*G1)) * abs((K*(D**2)/((D**2 + zvec**2)**(1.5))))


## \fn rho_baryon_simplenu(zvec, K, D)
# Calculate baryon density from the model used to generate the simplenu mock data
# @param zvec [kpc]
# @param K [kpc s^-2], baryon force parameter
# @param D [kpc], baryon disk scale height
