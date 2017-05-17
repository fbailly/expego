#!/usr/bin/env python
import sys
import os
import csv
import numpy as np
import scipy as sp
from IPython import embed
import matplotlib.pyplot as plt
import matplotlib as mpl

def export_stats(birapp_table_1,birapp_table_2,subjects_list,PI_list,nb_sb,nb_PI) :
	
	directory = '~/expego/birapp/resultbirapp/'
	directory = os.path.expanduser(directory)
	stats_birapp1 = open(directory+'stats_birapp1.csv','w')
	stats_birapp2 = open(directory+'stats_birapp2.csv','w')
	#~ stats_birapp3 = open(directory+'stats_birapp3.csv','w')
	stats_birapp1.write('Sujet;Condition;Resultat\n')
	stats_birapp2.write('Sujet;Condition;Resultat\n')
	#~ stats_birapp3.write('Sujet;Condition;Resultat\n')
	exclude_subject = ['celine','kevin','dinesh','flo']
	exclude_subject = ['kevin','dinesh']
	subject_idx = range(nb_sb)
	for i in range(len(exclude_subject)) :
		subject_idx.remove(subjects_list.index(exclude_subject[i]))
	nb_sb_exc = len(subject_idx) 		
	birapp_table_exc_1 = np.zeros([nb_sb_exc,nb_PI])
	birapp_table_exc_2 = np.zeros([nb_sb_exc,nb_PI])
	k = 0
	for i in subject_idx :
		for j in range(nb_PI) :
			line_to_write1 = '{0};{1};{2}\n'.format(i+1,PI_list[j],birapp_table_1[i,j])
			line_to_write2 = '{0};{1};{2}\n'.format(i+1,PI_list[j],birapp_table_2[i,j])
			birapp_table_exc_1[k,j] = birapp_table_1[i,j]
			birapp_table_exc_2[k,j] = birapp_table_2[i,j]
			#~ line_to_write3 = '{0};{1};{2}\n'.format(i+1,PI_list[j],birapp_table_3[i,j])
			stats_birapp1.write(line_to_write1)
			stats_birapp2.write(line_to_write2)
			#~ stats_birapp3.write(line_to_write3)
		k+=1
	stats_birapp1.close
	stats_birapp2.close
	#~ stats_birapp3.close
	return birapp_table_exc_1,birapp_table_exc_2
	
