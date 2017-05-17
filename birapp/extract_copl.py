#!/usr/bin/env python
import sys
import os
import csv
import numpy as np
import scipy as sp
from IPython import embed
import matplotlib.pyplot as plt
import matplotlib as mpl


def extract_coplanarity_ls(viseur_array,PI_array):
	pos_vec = np.vstack((viseur_array,PI_array))
	A = pos_vec.copy()
	A[:,2] = 1
	z = pos_vec[:,2]
	plane_pars,res,rank,s = sp.linalg.lstsq(A,z)
	return res
