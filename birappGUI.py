#!/usr/bin/env python
# -*- coding: utf-8 -*-

import rospy
import sys
import select
import os
import message_filters
from optitrack.msg import or_pose_estimator_state
from std_msgs.msg import String
from IPython import embed
from mocap_align import mocap_extract, mocap_align_abs
from Tkinter import * 

class GuiBirapp :
	
	def __init__(self,nom):
		self.nom=nom
		self.l1=[]
		self.l2=[]
		self.l1tmp=[]
		self.l2tmp=[]
		self.counter=0
		self.sync = 1
			
	def display_GUI(self,sub_name='Entrer sujet',session_nb='1') :
		
		self.fenetre = Tk()
		self.fenetre['bg']='white'
		# Frames
		f1 = Frame(self.fenetre, bg="white",width=300,height=75)
		f1.pack(side=TOP, fill=BOTH)
		#~ f2 = Frame(self.fenetre, bg="white",width=100,height=150,padx=5,pady=5)
		#~ f2.pack(side=RIGHT,expand=1,fill=BOTH)
		f3 = Frame(self.fenetre, bg="white",width=100,height=150,padx=5,pady=5)
		f3.pack(side=LEFT, expand=1,fill=BOTH)
		#~ f4 = Frame(f2, bg="grey",width=150,height=25,)
		#~ f4.pack(side=TOP,fill=X)
		f5 = Frame(f3, bg="grey",width=150,height=25)
		f5.pack(side=TOP,fill=X)
		f6 = Frame(self.fenetre, bg="white",width=300,height=75)
		f6.pack(side=BOTTOM, fill=BOTH)
		f7 = Frame(self.fenetre, bg="white",width=100,height=150,padx=5,pady=5)
		f7.pack(side=LEFT, expand=1,fill=BOTH)
		f8 = Frame(f7, bg="grey",width=150,height=25)
		f8.pack(side=TOP,fill=X)
		
		# liste des points du corps
		self.listePI = Listbox(f3,exportselection=1)
		self.listePI.insert(1, "Tete")
		self.listePI.insert(2, "EpauleG")
		self.listePI.insert(3, "EpauleD")
		self.listePI.insert(4, "CoudeG")
		self.listePI.insert(5, "CoudeD")
		self.listePI.insert(6, "PoignetG")
		self.listePI.insert(7, "PoignetD")
		self.listePI.insert(8, "GenouxG")
		self.listePI.insert(9, "GenouxD")
		self.listePI.insert(10, "ChevilleG")
		self.listePI.insert(11, "ChevilleD")
		self.listePI.insert(12, "Bassin")
		self.listePI.pack()
		
		# numero de session
		var = StringVar(f7)
		var.set(str(session_nb))
		self.session_num = Spinbox(f7, from_=1, to=10, textvariable=var)
		self.session_num.pack()
		
		
		# titres
		self.labelPI = Label(f5, text="Sélectionner PI",bg="grey")
		self.labelPI.pack()
		self.labelsession = Label(f8, text="Sélectionner numéro de session",bg="grey")
		self.labelsession.pack()


		#~ # subject id
		self.sub_frame = Entry(f1)
		self.sub_frame.pack(side = LEFT)
		self.sub_frame.delete(0, END)
		self.sub_frame.insert(0, sub_name)
		
		# bouton de sortie
		bouton=Button(f6, text="Fermer", anchor="s", command=self.fenetre.destroy)
		bouton.pack(side=RIGHT)

		# bouton de selection
		bouton2=Button(f6, text="Ok", anchor="se", command=self.get_select)
		bouton2.pack(side=RIGHT)
		self.fenetre.mainloop()
		
	def get_select(self) :
		self.PI_id = self.listePI.get(self.listePI.curselection())
		#~ self.target_id = self.listeball.get(self.listeball.curselection())
		self.subject_id = self.sub_frame.get()
		self.session_nb = self.session_num.get()
		print(self.subject_id,self.PI_id,self.session_nb)
		self.set_directory(self.subject_id,self.PI_id,self.session_nb)
		print('Directory created')
		self.listener()
		self.fenetre.destroy()
			
	def mocap_callback(self,data1,data2):
		coord = ['x','y','z','qw','qx','qy','qz']
		self.ts1 = data1.ts # timestamps
		self.ts2 = data2.ts
		self.pos1 = data1.pos # positions
		self.pos2 = data2.pos
		self.tmpsync = (self.ts1==self.ts2) # synchro flag
		self.sync = self.tmpsync and self.sync
		for i in range(7) :
			self.l1.append(str(str(eval('self.pos1[0].'+coord[i])) + ','))
			self.l2.append(str(str(eval('self.pos2[0].'+coord[i])) + ','))
			if i==6 :
				self.l1.append(str('\n'))
				self.l2.append(str('\n'))
		self.counter +=1
		if self.counter == 1 :
			self.duration1 = self.ts1
			self.duration2 = self.ts2
			
		if (select.select([sys.stdin], [], [], 0)[0] == [sys.stdin])  :
			print('\nFrames : '+ str(self.counter))
			print('Synchro : ' + str(self.sync) )
			self.duration1 = self.ts1.sec-self.duration1.sec + pow(10,-9)*(self.ts1.sec-self.duration1.nsec)
			self.duration2 = self.ts2.sec-self.duration2.sec + pow(10,-9)*(self.ts2.sec-self.duration2.nsec)
			# gather lists
			self.l1tmp.append('Frames : ' + str(self.counter) + '\n')
			self.l1tmp.append('Synchro : ' + str(self.sync) + '\n' )
			self.l1tmp.append('Duration : ' + str(self.duration1) + '\n' )
			self.l2tmp.append('Frames : ' + str(self.counter) + '\n')
			self.l2tmp.append('Synchro : ' + str(self.sync) + '\n')
			self.l2tmp.append('Duration : ' + str(self.duration2) + '\n' )
			self.l1tmp.extend(self.l1)
			self.l2tmp.extend(self.l2)
			self.finalize()

	def test_callback(self,dat1,dat2):
		if select.select([sys.stdin], [], [], 0)[0] == [sys.stdin]:
			print(sys.stdin.read(1))

	def finalize(self):
        #~ Kill the rosnode
		rospy.signal_shutdown("ROSPy Shutdown")
 
	def listener(self):

		rospy.init_node('listener', anonymous=True)
		chat1_sub = message_filters.Subscriber('/optitrack/bodies/'+'PI', or_pose_estimator_state)
		chat2_sub = message_filters.Subscriber('/optitrack/bodies/'+'viseur', or_pose_estimator_state)
		self.ts = message_filters.ApproximateTimeSynchronizer([chat1_sub, chat2_sub], 51,1, allow_headerless=True)
		self.ts.registerCallback(self.mocap_callback)
		rospy.spin()
		

	def set_directory(self,subject_id,PI_id,session_nb) :
		self.directory = '~/expego/databirapp/'+self.subject_id+'/'+self.PI_id+'/'+self.session_nb+'/'
		self.os_directory = os.path.expanduser(self.directory)
		print('______\n\nPerforming motion capture for :\nSubject : {0}\nPI : {1}\nSession : {2}\n______'.format(subject_id,PI_id,session_nb))
		print('\n'+self.os_directory+'\n')
		if os.path.exists(self.os_directory):
			print('session already created, erase it ? ([y], n)')
			ans = raw_input()
			if ans == 'n' :
				session_nb = str(max((list(map(int,os.listdir(os.path.expanduser('~/expego/databirapp/'+subject_id+'/'+PI_id))))))+1)
				self.directory = '~/expego/databirapp/'+subject_id+'/'+PI_id+'/'+'/'+session_nb+'/'
				self.os_directory = os.path.expanduser(self.directory)
				os.makedirs(self.os_directory)
			else :
				pass
		elif not os.path.exists(self.os_directory):
			os.makedirs(self.os_directory)
