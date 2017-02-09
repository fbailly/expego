#!/usr/bin/env python
import rospy
import sys
import os
import math
import message_filters
from IPython import embed
import matplotlib.pyplot as plt
import numpy as np
from mocap_align import mocap_extract, mocap_align_abs
from read_results import mocap_intercept, get_PI, get_subject

global balls_centersy
global balls_centersx
global mes_bplume
global mes_brouge
global mes_bvide
mes_bplume = np.array([-3.6004087458,3.3680321189,1.5372971483])
mes_brouge = np.array([-3.6178109599,3.9675009516,1.5314543185])
mes_bvide = np.array([-3.6363492807,4.5560661391,1.5339595827])
balls_centersy = [3.3680321189,3.9675009516,4.5560661391]
balls_centersz = [1.5372971483,1.5314543185,1.5339595827]

def old_get_structure(dys,dzs,plotflag) :
	centerfeather = mes_bplume + np.array([0,dys[0],dzs[0]])	
	centerred = mes_brouge + np.array([0,dys[1],dzs[1]])
	centerempty = mes_bvide + np.array([0,dys[2],dzs[2]])
	vfeatherred =  centerred - centerfeather
	vfeatherempty = centerempty - centerfeather 
	alignment = np.arccos(np.dot(vfeatherred,vfeatherempty)/np.linalg.norm(vfeatherred)/np.linalg.norm(vfeatherempty))
	aligned_red = centerfeather + np.linalg.norm(vfeatherred)*np.cos(alignment)*vfeatherempty/np.linalg.norm(vfeatherempty)
	dfr = np.linalg.norm(aligned_red - centerfeather)
	dre = np.linalg.norm(centerempty - aligned_red)
	print(dfr,dre)
	if plotflag == 1 :
		plt.plot(balls_centersy[0],balls_centersz[0],'go',markersize=40)
		plt.plot(balls_centersy[1],balls_centersz[1],'ro',markersize=40)
		plt.plot(balls_centersy[2],balls_centersz[2],'ko',markersize=40)
		plt.plot(balls_centersy[0]+dys[0],balls_centersz[0]+dzs[0],'gx',markersize=45)
		plt.plot(balls_centersy[1]+dys[1],balls_centersz[1]+dzs[1],'rx',markersize=45)
		plt.plot(balls_centersy[2]+dys[2],balls_centersz[2]+dzs[2],'kx',markersize=45)
		plt.plot(aligned_red[1],aligned_red[2],'bx',markersize=45)
		plt.axis([2,6,0,3])	
		plt.show()
	alignment_grade = (np.pi/2-abs(alignment))/(np.pi/2)*100
	ecartement_grade = 1/(1+abs(dfr-dre))*100
	distanceg_grade = 0.6/(0.6+abs(dfr-0.6))*100
	distanced_grade = 0.6/(0.6+abs(dre-0.6))*100
	return alignment_grade,distanceg_grade,distanced_grade,ecartement_grade
	
def new_get_structure(pos_viseur,pos_PI) :
	vec_feather = pos_viseur[0,:]-pos_PI[0,:]	
	vec_red = pos_viseur[1,:]-pos_PI[1,:]	
	vec_empty = pos_viseur[2,:]-pos_PI[2,:]	
	ang_feather_red = math.atan2(np.linalg.norm(np.cross(vec_feather,vec_red)), np.dot(vec_feather,vec_red))
	ang_red_empty = math.atan2(np.linalg.norm(np.cross(vec_red,vec_empty)), np.dot(vec_red,vec_empty));
	score_sym = (np.pi/2-abs(ang_feather_red-ang_red_empty))/(np.pi/2)*100
	plane_normal = np.cross(vec_feather,vec_empty);
	ang_align = abs(np.pi/2 - math.acos(np.dot(vec_red,plane_normal)/np.linalg.norm(plane_normal)/np.linalg.norm(vec_red)));
	print(ang_align)
	score_align = abs(np.pi/2-ang_align)/(np.pi/2)*100
	print(score_align)
	print(score_sym)
	return score_align,score_sym

def get_deviations(directory,session) :
	dys =  np.array([0.,0.,0.])
	dzs =  np.array([0.,0.,0.])
	pos_viseur = np.zeros((3,3))
	pos_PI = np.zeros((3,3))
	for balltype in os.listdir(directory) :
		body_PI = mocap_extract(directory+'/'+balltype+'/'+session+'/'+'PI'+'.csv')
		body_viseur = mocap_extract(directory+'/'+balltype+'/'+session+'/'+'viseur'+'.csv')
		dy,dz = mocap_intercept(body_PI,body_viseur,balltype)
		if balltype == 'Feather' :
			dys[0] = dy
			dzs[0] = dz
			pos_viseur[0,:] = np.array([np.mean(body_viseur[:,0]),np.mean(body_viseur[:,1]),np.mean(body_viseur[:,2])])
			pos_PI[0,:] = np.array([np.mean(body_PI[:,0]),np.mean(body_PI[:,1]),np.mean(body_PI[:,2])])
		elif balltype == 'Red' :
			dys[1] = dy
			dzs[1] = dz
			pos_viseur[1,:] = np.array([np.mean(body_viseur[:,0]),np.mean(body_viseur[:,1]),np.mean(body_viseur[:,2])])
			pos_PI[1,:] = np.array([np.mean(body_PI[:,0]),np.mean(body_PI[:,1]),np.mean(body_PI[:,2])])
		elif balltype == 'Empty' :
			dys[2] = dy
			dzs[2] = dz
			pos_viseur[2,:] = np.array([np.mean(body_viseur[:,0]),np.mean(body_viseur[:,1]),np.mean(body_viseur[:,2])])
			pos_PI[2,:] = np.array([np.mean(body_PI[:,0]),np.mean(body_PI[:,1]),np.mean(body_PI[:,2])])
	return dys,dzs,pos_viseur,pos_PI

	
def save_grades(subject_id,directory,later_id) :
	cd_directory = os.path.expanduser('~/expego/data/')
	os.chdir(cd_directory)
	filename = 'results.csv'
	filename2 = 'results_dbg.csv'
	if os.path.exists(filename):
		results = open(cd_directory+filename,'a')
	else: 
		results = open(cd_directory+filename,'w')
		results.write('Sujets,Condition,Resultat\n')
	if os.path.exists(filename2):
		results_dbg = open(cd_directory+filename2,'a')
	else: 
		results_dbg = open(cd_directory+filename2,'w')
		results_dbg.write('Sujets,Condition,Score alignement,Score ecartement\n')
	plotflag = 0
	directory = cd_directory+subject_id+'/'
	for filename in os.listdir(directory):
			PI_directory = directory+filename
			if os.path.isdir(PI_directory) :
				for session in ['1','2','3','4'] :
					try :
						dys,dzs,pos_viseur,pos_PI = get_deviations(PI_directory,session)
						print(PI_directory,session)
						#~ alignment_grade,distanceg_grade,distanced_grade,ecartement_grade = get_structure(dys,dzs,plotflag)
						score_align,score_sym = new_get_structure(pos_viseur,pos_PI)
						if later_id == 'D' :
							filename = filename[:-1]+filename[-1].replace('D','Dom')
							filename = filename[:-1]+filename[-1].replace('G','Opp')
						if later_id == 'G' :
							filename = filename[:-1]+filename[-1].replace('D','Opp')
							filename = filename[:-1]+filename[-1].replace('G','Dom')
						results.write(subject_id+','+filename+','+str(score_align)+'\n')
						results_dbg.write(subject_id+','+filename+','+str(score_align)+','+str(score_sym)+'\n')
					except :
						pass
	results.close
	
	
		
def display_grades(directory) :
	plotflag = 0
	for filename in os.listdir(directory):
			PI_directory = directory+filename
			if os.path.isdir(PI_directory) :
				for session in ['1','2','3','4'] :
					try :
						dys,dzs = get_deviations(PI_directory,session)
						dys,dzs = get_deviations(PI_directory,session)
						alignment_grade,distanceg_grade,distanced_grade	= get_structure(dys,dzs,plotflag)
						print(alignment_grade,distanceg_grade,distanced_grade,alignment_grade+distanceg_grade+distanced_grade)
						print(filename,session)
						
					except :
						pass
						
						
def get_later() :
	print('______\n\nlateralisation : G/D ?')
	later_id = raw_input()
	while later_id != 'G' and later_id != 'D' :
		print('______\n\nlateralisation : G/D ?')
		later_id = raw_input()
		print(later_id)
	return later_id			

def main(argv) :
	subject_id = get_subject()
	later_id = get_later()
	directory = '~/expego/data/'+subject_id+'/'
	directory = os.path.expanduser(directory)
	#~ display_grades(directory)
	save_grades(subject_id,directory,later_id)
				
if __name__ == '__main__':
	main(sys.argv)
