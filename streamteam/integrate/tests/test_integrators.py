# coding: utf-8
"""
    Test the integrators.
"""

from __future__ import absolute_import, unicode_literals, division, print_function

__author__ = "adrn <adrn@astro.columbia.edu>"

# Standard library
import os

# Third-party
import pytest
import numpy as np
import astropy.units as u
from astropy.constants import G

# Project
from ..rk5 import RK5Integrator
from ..dopri853 import DOPRI853Integrator
from .helpers import plot

plot_path = "plots/tests/integrate"
if not os.path.exists(plot_path):
    os.makedirs(plot_path)

def sho(t,x,T):
    q,p = x.T
    return np.array([p, -(2*np.pi/T)**2*q]).T

@pytest.mark.parametrize(("name","Integrator"), [('rk5',RK5Integrator),
                                                 ('dopri853',DOPRI853Integrator)])
def test_forward(name, Integrator):
    dt = 0.1
    t1,t2 = 0, 2.5
    integrator = Integrator(sho, func_args=(10.,))
    ts, xs = integrator.run([0., 1.],
                            t1=t1, t2=t2, dt=dt)

    fig = plot(ts, xs)
    fig.savefig(os.path.join(plot_path,"forward_{0}.png".format(name)))

@pytest.mark.parametrize(("name","Integrator"), [('rk5',RK5Integrator),
                                                 ('dopri853',DOPRI853Integrator)])
def test_backward(name, Integrator):
    dt = -0.1
    t1,t2 = 2.5,0.
    integrator = Integrator(sho, func_args=(10.,))
    ts, xs = integrator.run([0., 1.],
                            t1=t1, t2=t2, dt=dt)

    fig = plot(ts, xs)
    fig.savefig(os.path.join(plot_path,"backward_{0}.png".format(name)))

@pytest.mark.parametrize(("name","Integrator"), [('rk5',RK5Integrator),
                                                 ('dopri853',DOPRI853Integrator)])
def test_harmonic_oscillator(name, Integrator):
    dt = 0.1
    integrator = Integrator(sho, func_args=(10.,))
    ts, xs = integrator.run([1., 0.],
                            dt=dt, nsteps=100)

    fig = plot(ts, xs)
    fig.savefig(os.path.join(plot_path,"harmonic_osc_{0}.png".format(name)))

@pytest.mark.parametrize(("name","Integrator"), [('rk5',RK5Integrator),
                                                 ('dopri853',DOPRI853Integrator)])
def test_point_mass(name, Integrator):
    GM = (G * (1.*u.M_sun)).decompose([u.au,u.M_sun,u.year,u.radian]).value

    def F(t,x):
        x,y,px,py = x.T
        a = -GM/(x*x+y*y)**1.5
        return np.array([px, py, x*a, y*a]).T

    q_i = np.array([1.0, 0.0]) # au
    p_i = np.array([0.0, 2*np.pi]) # au/yr

    integrator = Integrator(F)
    ts, xs = integrator.run(np.append(q_i,p_i),
                            t1=0., t2=10., dt=0.01)

    fig = plot(ts, xs)
    fig.savefig(os.path.join(plot_path,"point_mass_{0}.png".format(name)))

# KNOWN FAILURE FOR RK5
@pytest.mark.parametrize(("name","Integrator"), [('rk5',RK5Integrator),
                                                 ('dopri853',DOPRI853Integrator)])
def test_point_mass_multiple(name, Integrator):
    GM = (G * (1.*u.M_sun)).decompose([u.au,u.M_sun,u.year,u.radian]).value

    def F(t,x):
        x,y,px,py = x.T
        a = -GM/(x*x+y*y)**1.5
        return np.array([px, py, x*a, y*a]).T

    x_i = np.array([[1.0, 0.0, 0.0, 2*np.pi],
                    [0.8, 0.0, 0.0, 2.1*np.pi]])

    integrator = Integrator(F)
    ts, xs = integrator.run(x_i,
                            t1=0., t2=10., dt=0.01)

    fig = plot(ts, xs)
    fig = plot(ts, xs, fig=fig)
    fig.savefig(os.path.join(plot_path,"multi_point_mass_{0}.png".format(name)))

@pytest.mark.parametrize(("name","Integrator"), [('rk5',RK5Integrator),
                                                 ('dopri853',DOPRI853Integrator)])
def test_driven_pendulum(name, Integrator):

    def F(t,x,A,omega_d):
        q,p = x.T
        return np.array([p,-np.sin(q) + A*np.cos(omega_d*t)]).T

    integrator = Integrator(F, func_args=(0.07, 0.75))
    ts, xs = integrator.run([3., 0.],
                            dt=0.1, nsteps=10000)

    fig = plot(ts, xs, marker=None, alpha=0.5)
    fig.savefig(os.path.join(plot_path,"driven_pendulum_{0}.png".format(name)))

@pytest.mark.parametrize(("name","Integrator"), [('rk5',RK5Integrator),
                                                 ('dopri853',DOPRI853Integrator)])
def test_lorenz(name, Integrator):

    def F(t,x,sigma,rho,beta):
        x,y,z = x.T
        return np.array([sigma*(y-x), x*(rho-z)-y, x*y-beta*z]).T

    sigma, rho, beta = 10., 28., 8/3.
    integrator = Integrator(F, func_args=(sigma, rho, beta))
    ts, xs = integrator.run([0.5,0.5,0.5],
                            dt=0.01, nsteps=10000)

    fig = plot(ts, xs, marker=None, alpha=0.5)
    fig.savefig(os.path.join(plot_path,"lorenz_{0}.png".format(name)))

@pytest.mark.parametrize(("name","Integrator"), [('rk5',RK5Integrator),
                                                 ('dopri853',DOPRI853Integrator)])
def test_loop_vs_run(name, Integrator):
    # If this breaks, need to specify t1 in .run()

    def F(t,x,A,omega_d):
        q,p = x.T
        return np.array([p,-np.sin(q) + A*np.cos(omega_d*t)]).T

    nsteps = 100
    dt = 0.1
    integrator1 = Integrator(F, func_args=(0.07, 0.75))
    integrator2 = Integrator(F, func_args=(0.07, 0.75))

    ts, xs = integrator1.run([3., 0.],
                             dt=dt, nsteps=nsteps)

    x0 = np.array([3.,0.])
    xs_loop = np.zeros((nsteps+1,1,2))
    xs_loop[0] = x0
    time = 0.
    for ii in range(nsteps):
        t,new_x = integrator2.run(x0, t1=time, dt=dt, nsteps=1)
        x0 = new_x[-1]
        xs_loop[ii+1] = x0
        time += dt

    fig = plot(ts, xs, marker=None, alpha=0.5)
    fig = plot(ts, xs_loop, marker=None, alpha=0.5, fig=fig)
    fig.savefig(os.path.join(plot_path,"loop_vs_run_{0}.png".format(name)))