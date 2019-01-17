from NKTP_DLL import *
from Registry import REG
from time import sleep, time
import sys
from math import ceil


class Laser:

	def __init__(self, port, dev_address):

		self.port=port
		self.devID=dev_address

	def get_central_wavelength(self):
		resc,center=registerReadU32(self.port,self.devID,REG['Wavelength_center'],-1)
		return center*0.0001

	def get_wavelength(self):

		resc,center=registerReadU32(self.port,self.devID,REG['Wavelength_center'],-1)
		reso,offset=registerReadS16(self.port,self.devID,REG['Wavelength_offset'],-1)

		return (center+offset)*0.0001

	def get_frequency(self):

		c=299792.458 

		resc,center=registerReadU32(self.port,self.devID,REG['Wavelength_center'],-1)
		reso,offset=registerReadS16(self.port,self.devID,REG['Wavelength_offset'],-1)

		return c/(0.0001*(center+offset))

	def set_wavelength(self,wavelength):
		c=299792.458 

		res,center=registerReadU32(self.port,self.devID,REG['Wavelength_center'],-1)
		center*=0.0001

		offset=int(round((wavelength-center)*10000))
		
		if offset>3700:
			offset=3700
		elif offset<-4000:
			offset=-4000


		wrRes=registerWriteS16(self.port,self.devID,REG['Wavelength_offset'],offset,-1)


	def sweep(self,f_start,f_stop,step,delay,window):

		c=299792.458 

		step/=1000

		step_nums=ceil((f_stop-f_start)/step)
		step_c=0

		curr_freq=f_start
		self.set_wavelength(c/curr_freq)

		wv=self.get_wavelength()
		fr=self.get_frequency()

		window.pr_var.set(step_c/step_nums*100)
		window.lam_now.configure(text="{0:.4f}".format(wv)+" nm")
		window.freq_now.configure(text="{0:.5f}".format(fr)+" THz")
		window.parent.update()

		sleep(delay)

		t_start=time()

		while curr_freq<f_stop:
			prev_freq=curr_freq
			curr_freq=prev_freq+step
			if curr_freq>f_stop or abs(curr_freq-f_stop)<0.000001:
				curr_freq=f_stop


			step_c+=1
			

			self.set_wavelength(c/curr_freq)

			wv=self.get_wavelength()
			fr=self.get_frequency()

			window.pr_var.set(step_c/step_nums*100)
			window.lam_now.configure(text="{0:.4f}".format(wv)+" nm")
			window.freq_now.configure(text="{0:.5f}".format(fr)+" THz")
			window.parent.update()

			sleep(delay-((time()-t_start) % delay))


	def get_temperature(self):

		res,tp=registerReadS16(self.port,self.devID,REG['Temperature'],-1)

		return tp*0.1

	def get_power(self):

		res,pw=registerReadU16(self.port,self.devID,REG['Output_power'],-1)
		
		return pw*0.01

	def emission_on(self):

		emR = registerWriteU8(self.port,self.devID, REG['Emission'], 1, -1) 

	def emission_off(self):

		emR = registerWriteU8(self.port,self.devID, REG['Emission'], 0, -1) 

	def is_on(self):

		res,val=registerReadU8(self.port,self.devID,REG['Emission'],-1)
		return val

	def modulation_type(self,setting):

		rd,val=registerReadU16(self.port,self.devID,REG['Setup'],-1)
		val=list('{0:010b}'.format(val))
		if val[8]!=str(setting):
			val[8]=str(setting)
			val=''.join(val)
			val=int(val,2)
			wr=registerWriteU16(self.port,self.devID,REG['Setup'],val,-1)


	def status_readout(self):
		rd,val=registerReadU16(self.port,self.devID,REG['Status'],-1)
		print('{0:016b}'.format(val)[::-1])



class Device:

	def __init__(self,dvType,dvID,prt):
		self.devType=dvType
		self.devID=dvID
		self.port=prt
		self.laser=0

	def make_laser(self):

		if self.devType=="0x33" and self.laser==0:
			self.laser=Laser(self.port,self.devID)
			return self.laser



class Port:

	def __init__(self,portname):

		self.name=portname
		self.devices=[]

	def create_devices(self):

		res,deviceList=deviceGetAllTypes(self.name)

		for devID in range(0,len(deviceList)):
			if (deviceList[devID]!=0):
				d=Device(hex(deviceList[devID]),devID,self.name)
				self.devices.append(d)

	def close_port(self):
		clR=closePorts(self.name)



def create_ports():
	roP=openPorts(getAllPorts(), 1, 1)
	P=[]
	for portname in getOpenPorts().split(','):
		P.append(Port(portname))

	return P

def connect_lasers():

	openports=create_ports()
	
	L=[]

	for port in openports:
		port.create_devices()
		for device in port.devices:
			las=device.make_laser()
			if las!=0 and las!=None:
				L.append(las)
				
	return L

