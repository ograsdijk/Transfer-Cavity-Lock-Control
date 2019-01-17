import math
import numpy as np
import matplotlib.pyplot as plt
from scipy import interpolate
from statistics import mean, stdev
from time import sleep, time
import random
import sys
import imageio



class Signal:

	def __init__(self,datax,datay,fltr):

		self.data_x=datax
		self.data_y=datay
		self.dx=datax[1]-datax[0]
		self.std=stdev(datay)
		self.smooth_y=fltr.apply(datay,0,datax[1]-datax[0])
		self.fltr=fltr
		self.der_y=[]
		self.smooth_der=[]
		self.peaks_x=[]
		self.peaks_y=[]

	def find_peaks(self,criterion=1,win_size=7,hs=10):

		C=self.smooth_y
		D=self.fltr.apply(C,1,self.dx)
		self.der_y=D
		D=self.fltr.apply(D,0,self.dx)
		D=self.fltr.moving_avg(D,half_size=hs)
		self.smooth_der=D

		points=[]
		skip=0
		for i in range(win_size,len(D)-win_size):

			if skip>0:
				skip-=1
				continue

			if D[i]<0 and D[i-1]>0:
				
				if mean(self.data_y[i-win_size:i+win_size])>criterion*self.std:

					a,b=np.polyfit(self.data_x[i-win_size:i+win_size],D[i-win_size:i+win_size],1)
					points.append(-b/a)
					skip=win_size


		self.peaks_x=np.array(points)
	
	def get_ypeaks(self):

		if len(self.peaks_x)==0:
			return

		f=interpolate.interp1d(self.data_x,self.smooth_y)

		self.peaks_y=f(self.peaks_x)

	def plot_signal(self):
	

		fig, (ax1,ax2)=plt.subplots(1,2,sharey=True)


		ax1.plot(self.data_x,self.smooth_y)
		ax1.plot(self.data_x,[self.std]*len(self.data_x),'k--')
		ax1.plot(self.peaks_x,self.peaks_y,'ro')
		ax2.plot(self.data_x,self.smooth_der,'g-')
		ax2.plot(self.peaks_x,[0]*len(self.peaks_x),'ro')


		plt.show()


class Filter:

	def __init__(self):

		self.coeffs=[[-2/21,3/21,6/21,7/21,6/21,3/21,-2/21],[-3/10,-1/5,-1/10,0,1/10,1/5,3/10],[5/42,0,-3/42,-4/42,-3/42,0,5/42],[-1/6,1/6,1/6,0,-1/6,-1/6,1/6]]

	def apply(self,signal,der,sp):

		C=self.coeffs[der][:]
		if der>0:
			C=[c/sp**der for c in C]


		aux=[x for x in signal]

		res=[0 for i in range(len(aux))]

		res[0]=aux[0]
		res[1]=aux[1]
		res[2]=aux[2]
		res[len(res)-3]=aux[len(res)-3]
		res[len(res)-2]=aux[len(res)-2]
		res[-1]=aux[-1]



		for i in range(3,len(res)-4):
			res[i]=C[0]*aux[i-3]+C[1]*aux[i-2]+C[2]*aux[i-1]+C[3]*aux[i]+C[4]*aux[i+1]+C[5]*aux[i+2]+C[6]*aux[i+3]

		return res

	def moving_avg(self,data,half_size=2):


		aux=[x for x in data]
		res=[0 for i in range(len(aux))]
		c=1/(half_size*2+1)
		
		avg=c*sum(aux[:2*half_size+1])
		res[half_size]=avg

		for i in range(half_size+1,len(aux)-half_size):
			avg=avg+c*(aux[i+half_size]-aux[i-half_size-1])
			res[i]=avg

		return res

class Lock:
	def __init__(self,mlp,slps):
		self.master_lockpoint=mlp
		self.slave_lockpoints=slps
		self.master_err=0
		self.master_err_prev=0
		self.slave_errs=[0]*len(slps)
		self.slave_errs_prev=[0]*len(slps)
		self.master_ctrl=0
		self.slave_ctrls=[0]*len(slps)
		self.master_peaks=[]
		self.slave_peaks=[0]*len(slps)
		self.prop_gain=0
		self.int_gain=0
		self.interval=0

	def adjust_gains(self,prop,integral):
		self.prop_gain=prop
		self.int_gain=integral

	def print_info(self):
		print("Master Laser Lockpoint: {:.2f}".format(self.master_lockpoint))
		print("Slave Lasers Lockpoints:")
		for i in range(len(self.slave_lockpoints)):
			print("L{}: {:.4f}".format(i+1,self.slave_lockpoints[i]))
		print("Prop gain: Kp={:.2f}".format(self.prop_gain)+"; Integral gain: Ki={:.2f}".format(self.int_gain))
		print("Master laser error signal={:.4f}".format(self.master_err))
		print("Slave lasers error signals:")
		for i in range(len(self.slave_lockpoints)):
			print("L{}: {:.4f}".format(i+1,self.slave_errs[i]))
		print("Master control signal={:.4f}".format(self.master_ctrl))
		print("Slave lasers control signals:")
		for i in range(len(self.slave_lockpoints)):
			print("L{}: {:.4f}".format(i+1,self.slave_ctrls[i]))


	def acquire_master_signal(self,signal):
		if len(signal.peaks_x)!=2:
			raise ValueError('Exactly 2 peaks should be acquired.')
		else:
			self.master_peaks=sorted(signal.peaks_x)
			self.master_err_prev=self.master_err
			self.master_err=self.master_lockpoint-self.master_peaks[0]
			self.interval=(signal.data_x[-1]-signal.data_x[0])/1000

	def acquire_slave_signal(self,signal,ind):
		self.slave_errs_prev=self.slave_errs
		for x in signal.peaks_x:
			if x<self.master_peaks[1] and x>self.master_peaks[0]:
				self.slave_peaks[ind]=x
				var=(self.master_peaks[0]-x)/(self.master_peaks[0]-self.master_peaks[1])
				self.slave_errs[ind]=self.slave_lockpoints[ind]-var
				break
		

	def refresh_control(self):
		self.master_ctrl=self.master_ctrl+0.5*self.prop_gain*(self.master_err-self.master_err_prev)+self.int_gain*self.master_err*self.interval 
		for i in range(len(self.slave_lockpoints)):
			self.slave_ctrls[i]=0.9*self.slave_ctrls[i]+self.prop_gain*(self.slave_errs[i]-self.slave_errs_prev[i])+self.int_gain*self.slave_errs[i]*self.interval

def generate_data(A,B,G,N,start,end):

	X=np.linspace(start,end,num=N)

	Y=[lor(X[i],A,B,G) for i in range(len(X))]

	return X,Y

def add_noise(data,var):

	noise=var*np.random.randn(len(data))

	return data+noise

def lor(x,A,B,G):
	res=0
	for i in range(len(A)):
		res+=A[i]/(G[i]**2+(x-B[i])**2)
	return res

def simulate_lock(lck,fbk,scan_time,sim_time,ax1):

	peak_m1=25+2*random.random()
	peak_m2=peak_m1+100

	peak_s1=35+2*random.random()
	peak_s2=65+2*random.random()

	# Mst=[peak_m1-lck.master_lockpoint]
	# Slv=[peak_s1-(lck.slave_lockpoints[0]*100+lck.master_lockpoint)]
	# IM=[]

	T,M=generate_data([1,1],[peak_m1,peak_m2],[1,1],1000,0,scan_time)
	M=add_noise(M,0.005)
	T,S1=generate_data([0.9],[peak_s1],[1.2],1000,0,scan_time)
	S1=add_noise(S1,0.006)
	T,S2=generate_data([0.85],[peak_s2],[1.1],1000,0,scan_time)
	S2=add_noise(S2,0.005)

	fl=Filter()

	sgm=Signal(T,M,fl)
	sgm.find_peaks()

	sgs1=Signal(T,S1,fl)
	sgs1.find_peaks()

	sgs2=Signal(T,S2,fl)
	sgs2.find_peaks()



	lck.acquire_master_signal(sgm)
	lck.acquire_slave_signal(sgs1,0)
	lck.acquire_slave_signal(sgs2,1)

	lck.refresh_control()

	r_s1=lck.slave_lockpoints[0]-lck.slave_errs[0]
	r_s2=lck.slave_lockpoints[1]-lck.slave_errs[1]

	plt.ion()
	# fig = plt.figure() # Initialize figure
	# ax1 = fig.add_subplot(111) # Create a subplot
	# ax1.set_autoscalex_on(True)
	# ax1.set_autoscaley_on(True)
	# ax1.set_autoscale_on(False)
	ax1.autoscale(False)
	ax1.set_xlim(0,scan_time)
	ax1.set_ylim(0,1.1)
	# ax1.autoscale_view(False, True, True)
	ax1.plot(T,M,'b-')
	ax1.plot(T,S1,'r-')
	ax1.plot(T,S2,'g-')
	sleep(0.001)

	t_start=time()

	while time()<t_start+sim_time:
		# print(lck.slave_errs[0])
		# print(lck.slave_ctrls[0])

		peak_m1+=fbk*lck.master_ctrl
		ra=random.random()
		if ra<0.01 and ra>0.001:
			peak_m1+=random.random()-0.5
		elif ra<0.001:
			peak_m1+=5*(random.random()-0.5)
		peak_m2=peak_m1+100

		r_s1+=fbk*lck.slave_ctrls[0]
		r_s2+=fbk*lck.slave_ctrls[1]


		peak_s1=r_s1*100+peak_m1
		peak_s2=r_s2*100+peak_m1

		ra=random.random()
		if ra<0.01 and ra>0.001:
			peak_s1+=random.random()-0.5
		elif ra<0.001:
			peak_s1+=5*(random.random()-0.5)

		ra=random.random()
		if ra<0.01 and ra>0.001:
			peak_s2+=random.random()-0.5
		elif ra<0.001:
			peak_s2+=5*(random.random()-0.5)

		# Mst.append(peak_m1-lck.master_lockpoint)
		# Slv.append(peak_s1-(lck.slave_lockpoints[0]*100+lck.master_lockpoint))

		T,M=generate_data([1,1],[peak_m1,peak_m2],[1,1],1000,0,scan_time)
		M=add_noise(M,0.005)
		T,S1=generate_data([0.9],[peak_s1],[1.2],1000,0,scan_time)
		S1=add_noise(S1,0.006)
		T,S2=generate_data([0.85],[peak_s2],[1.1],1000,0,scan_time)
		S2=add_noise(S2,0.0055)


		sgm=Signal(T,M,fl)
		sgm.find_peaks()

		sgs1=Signal(T,S1,fl)
		sgs1.find_peaks()

		sgs2=Signal(T,S2,fl)
		sgs2.find_peaks()

		lck.acquire_master_signal(sgm)
		lck.acquire_slave_signal(sgs1,0)
		lck.acquire_slave_signal(sgs2,1)

		lck.refresh_control()

		# lck.print_info()


		ax1.clear()
		ax1.autoscale(False)
		ax1.set_xlim(0,scan_time)
		ax1.set_ylim(0,1.1)
		ax1.plot(T,M,'b-')
		ax1.plot(T,S1,'r-')
		ax1.plot(T,S2,'g-')
		ax1.axvline(x=lck.master_lockpoint,color='c', linestyle='--')
		ax1.axvline(x=lck.slave_lockpoints[0]*100+lck.master_lockpoint,color='k', linestyle='--')
		ax1.axvline(x=lck.slave_lockpoints[1]*100+lck.master_lockpoint,color='k', linestyle='--')

		# fig.canvas.draw()
		# image=np.frombuffer(fig.canvas.tostring_rgb(),dtype='uint8')
		# image  = image.reshape(fig.canvas.get_width_height()[::-1] + (3,))

		# IM.append(image)
		sleep(0.001)


	# plt.show()






# fl=Filter()

# sgm=Signal(T,M,fl)
# sgm.find_peaks()
# # sgm.get_ypeaks()
# # sgm.plot_signal()

# sgs=Signal(Ts,S,fl)
# sgs.find_peaks()
# # sgs.get_ypeaks()
# # sgs.plot_signal()




# L=Lock(11,[0.5,0.7])
# L.adjust_gains(60,8)

# ims=simulate_lock(L,0.01,150,30)

# plt.close()
# plt.ioff()



# imageio.mimwrite('./anim.gif',ims,fps=10)
# fig1,(ax1,ax2)=plt.subplots(1,2)
# ax1.plot(mast)
# ax2.plot(slav)

# plt.show()


# L.acquire_master_signal(sgm)
# L.acquire_slave_signal(sgs,0)

# L.refresh_control()
# L.print_info()

