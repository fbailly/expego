#!/usr/bin/env python
import sys
import os
import csv
import numpy as np
import scipy as sp
from IPython import embed
import matplotlib.pyplot as plt
import matplotlib as mpl


def extract_colinearity_ls(viseur_array,PI_array):
	
	
	col1 = np.dot(np.cross((vis2-vis1),(PI_array-vis3)),(vis3-vis1))
	col2 = np.dot(np.cross((vis2-vis1),(PI_array-vis4)),(vis4-vis1))
	tot_col = 1./np.sqrt(col1*col1+col2*col2)
	return tot_col
