#!/usr/bin/env python
import rospy
import sys
import os
import message_filters
from IPython import embed
import matplotlib.pyplot as plt
import numpy as np
from mocap_align import mocap_extract, mocap_align_abs
from read_results import mocap_intercept, get_PI, get_subject

def check_distances(directory) :
	for filename in os.listdir(directory):
		PI_directory = directory+filename
		if os.path.isdir(PI_directory) :
			for balltype in os.listdir(PI_directory) :
				for session in ['1','2','3','4'] :
					try :
						body_PI = mocap_extract(PI_directory+'/'+balltype+'/'+session+'/'+'PI'+'.csv')
						body_viseur = mocap_extract(PI_directory+'/'+balltype+'/'+session+'/'+'viseur'+'.csv')
						pos_PI = np.array([np.mean(body_PI[:,0]),np.mean(body_PI[:,1]),np.mean(body_PI[:,2])])
						pos_viseur = np.array([np.mean(body_viseur[:,0]),np.mean(body_viseur[:,1]),np.mean(body_viseur[:,2])])
						distance_PI_viseur = np.linalg.norm(pos_PI-pos_viseur)
						print(filename,balltype,session)
						print(distance_PI_viseur)
					except :
						pass


def main(argv) :
	subject_id = get_subject()
	directory = '~/expego/data/'+subject_id+'/'
	directory = os.path.expanduser(directory)
	check_distances(directory)
				
if __name__ == '__main__':
	main(sys.argv)
