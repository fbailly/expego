#!/usr/bin/env python
import sys
import os
import csv
import numpy as np
import scipy as sp
import pickle
from scipy import signal
from IPython import embed
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib as mpl
from mpl_toolkits.mplot3d import Axes3D
from sklearn.cluster import KMeans


def points_extract_pos_s(viseur_filt,viseur_speed,Nkmean,plt_flag) :
	# cluster 3D position
	est = KMeans(n_clusters=Nkmean)
	est.fit(viseur_filt)
	labels = est.labels_
	fig = plt.figure(1,figsize=(4,3))
	ax = Axes3D(fig, rect=[0, 0, .95, 1], elev=48, azim=134)
	if plt_flag == True :
		ax.scatter(viseur_filt[:, 0], viseur_filt[:, 1], viseur_filt[:, 2], c=labels.astype(np.float))
		ax.w_xaxis.set_ticklabels([])
		ax.w_yaxis.set_ticklabels([])
		ax.w_zaxis.set_ticklabels([])
		ax.set_xlabel('X')
		ax.set_ylabel('Y')
		ax.set_zlabel('Z')
	cnt_labels = np.zeros((Nkmean))
	for i in range(Nkmean) :
		nb_labels_i = sum(labels == i)
		cnt_labels[i] = nb_labels_i
	idx_labels_sorted = np.argsort(cnt_labels)
	idx_labels_sorted = idx_labels_sorted[::-1]
	idx_pos_unsorted = idx_labels_sorted[0:4]
	# reorganizing idx_pos so that it is in order of pointing
	idx_order = np.zeros(4)
	for i in range(4) :
		list_i = np.where(labels==idx_pos_unsorted[i])
		idx_order[i] = list_i[0][len(list_i[0])//2]
	idx_order_sorted = np.argsort(idx_order)
	idx_pos = idx_pos_unsorted[idx_order_sorted]
	# extract the four viseur areas
	vis1 = viseur_filt[labels==idx_pos[0],:]
	vis2 = viseur_filt[labels==idx_pos[1],:]
	vis3 = viseur_filt[labels==idx_pos[2],:]
	vis4 = viseur_filt[labels==idx_pos[3],:]
	offset_derivative = viseur_filt.shape[0]-viseur_speed.shape[0]
	labels_truncated = labels[7:-7]
	vis1speed = viseur_speed[(labels_truncated==idx_pos[0]) ]
	vis2speed = viseur_speed[(labels_truncated==idx_pos[1]) ]
	vis3speed = viseur_speed[(labels_truncated==idx_pos[2]) ]
	vis4speed = viseur_speed[(labels_truncated==idx_pos[3]) ]
	med_vis = np.zeros((4,3))
	med_speed = np.zeros(4)
	i = 0
	speeds = [vis1speed,vis2speed,vis3speed,vis4speed]
	dots_colors = ['r','c','g','m']
	lowerspeed_idx = [0,0,0,0]
	for visspeed in [vis1speed,vis2speed,vis3speed,vis4speed] :
		visspeed_sorted = np.argsort(visspeed)
		lowerspeed_idx[i] = visspeed_sorted[0]
		i+=1
	i = 0
	for vis in [vis1,vis2,vis3,vis4] :
		med_vis[i,0] = vis[:,0][lowerspeed_idx[i]]
		med_vis[i,1] = vis[:,1][lowerspeed_idx[i]]
		med_vis[i,2] = vis[:,2][lowerspeed_idx[i]]
		med_speed[i] = speeds[i][lowerspeed_idx[i]]
		if plt_flag == True :
			ax.scatter(med_vis[i,0],med_vis[i,1],med_vis[i,2],color=dots_colors[i],s=200)
		i += 1
	if plt_flag == True :
		plt.figure()
		plt.subplot(411)
		plt.plot(vis1speed)
		plt.axhline(y=med_speed[0], color='red', linestyle='-')
		plt.subplot(412)
		plt.plot(vis2speed)
		plt.axhline(y=med_speed[1], color='red', linestyle='-')
		plt.subplot(413)
		plt.plot(vis3speed)
		plt.axhline(y=med_speed[2], color='red', linestyle='-')
		plt.subplot(414)
		plt.plot(vis4speed)
		plt.axhline(y=med_speed[3], color='red', linestyle='-')
	return ax, med_vis
