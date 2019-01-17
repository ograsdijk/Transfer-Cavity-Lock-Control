from tkinter import *
from tkinter import messagebox, filedialog
from tkinter import ttk
from Sweep import *
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from lock import *

def callback():
	root.destroy()
	if len(ld.laser_tabs)>0:
		for obj in ld.laser_tabs:
			if obj.laser.is_on():
				obj.laser.emission_off()
			
class LaserControl:

	def __init__(self,parent,stat,laser):

		c=299792.458 

		if laser.is_on():
			laser.emission_off()

		self.parent=parent
		self.status=stat
		self.laser=laser

		self.max_wv=self.laser.get_central_wavelength()+0.37
		self.min_wv=self.laser.get_central_wavelength()-0.4

		
		parent.grid_columnconfigure(0,minsize=30)
		parent.grid_columnconfigure(3,minsize=80)
		parent.grid_columnconfigure(6,minsize=80)
		parent.grid_columnconfigure(9,minsize=30)
		parent.grid_rowconfigure(0,minsize=30)
		parent.grid_rowconfigure(4,minsize=40)
		parent.grid_rowconfigure(8,minsize=40)
		parent.grid_rowconfigure(11,minsize=40)
		parent.grid_rowconfigure(15,minsize=70)
		parent.grid_rowconfigure(17,minsize=30)


		Label(parent,text="IR",font="Arial 14 bold").grid(row=1,column=2,sticky=W)
		Label(parent,text="\u03bb:",font="Arial 12 bold").grid(row=2,column=1,sticky=W)
		Label(parent,text="f:",font="Arial 12 bold").grid(row=3,column=1,sticky=W)
		Label(parent,text="UV",font="Arial 14 bold").grid(row=5,column=2,sticky=W)
		Label(parent,text="\u03bb:",font="Arial 12 bold").grid(row=6,column=1,sticky=W)
		Label(parent,text="f:",font="Arial 12 bold").grid(row=7,column=1,sticky=W)
		Label(parent,text="Output:",font="Arial 12 bold").grid(row=9,column=1,sticky=W)
		Label(parent,text="Temperature:",font="Arial 12 bold").grid(row=10,column=1,sticky=W)

		self.lam=Label(parent,text="",font="Arial 12 bold")
		self.lam.grid(row=2,column=2,sticky=E)
		self.freq=Label(parent,text="",font="Arial 12 bold")
		self.freq.grid(row=3,column=2,sticky=E)
		self.lamu=Label(parent,text="",font="Arial 12 bold")
		self.lamu.grid(row=6,column=2,sticky=E)
		self.frequ=Label(parent,text="",font="Arial 12 bold")
		self.frequ.grid(row=7,column=2,sticky=E)
		self.pow=Label(parent,text="",font="Arial 12 bold")
		self.pow.grid(row=9,column=2,sticky=E)
		self.temp=Label(parent,text="",font="Arial 12 bold")
		self.temp.grid(row=10,column=2,sticky=E)


		Label(parent,text="Set wavelength [nm]:",font="Arial 14 bold").grid(row=1,column=4,columnspan=2)

		self.set_wv=StringVar()
		self.set_wv_field=Entry(parent,textvariable=self.set_wv,width=15)
		self.set_wv_field.grid(row=2,column=4)
		self.set_wv_button=Button(parent,width=5,command=self.set_wvl,text="Set",font="Arial 12 bold")
		self.set_wv_button.grid(row=2,column=5)


		Label(parent,text="Settings:",font="Arial 14 bold").grid(row=1,column=7,columnspan=2)
		Label(parent,text="Modulation",font="Arial 12 bold").grid(row=2,column=7,sticky=W)

		self.mod_var=StringVar()
		self.mod_var_opt=OptionMenu(parent,self.mod_var,"Wide","Narrow")
		self.mod_var_opt.grid(row=2,column=8,sticky=E)
		self.mod_var.set("Narrow")
		self.mod_var.trace('w',self.change_mod)


		Label(parent,text="Minimum \u03bb:",font="Arial 12 bold").grid(row=4,column=7,sticky=W)
		Label(parent,text="Maximum \u03bb:",font="Arial 12 bold").grid(row=5,column=7,sticky=W)
		Label(parent,text="{0:.4f}".format(self.min_wv)+" nm",font="Arial 12 bold").grid(row=4,column=8,sticky=E)
		Label(parent,text="{0:.4f}".format(self.max_wv)+" nm",font="Arial 12 bold").grid(row=5,column=8,sticky=E)
		Label(parent,text="Minimum f:",font="Arial 12 bold").grid(row=7,column=7,sticky=W)
		Label(parent,text="Maximum f:",font="Arial 12 bold").grid(row=8,column=7,sticky=W)
		Label(parent,text="{0:.5f}".format(c/self.max_wv)+" THz",font="Arial 12 bold").grid(row=7,column=8,sticky=E)
		Label(parent,text="{0:.5f}".format(c/self.min_wv)+" THz",font="Arial 12 bold").grid(row=8,column=8,sticky=E)
		
		Label(parent,text="Sweep frequency settings:",font="Arial 14 bold").grid(row=4,column=4,columnspan=2)
		Label(parent,text="Start [THz]",font="Arial 12 bold").grid(row=6,column=4)
		Label(parent,text="Stop [THz]",font="Arial 12 bold").grid(row=6,column=5)
		Label(parent,text="Step [GHz]",font="Arial 12 bold").grid(row=8,column=4)
		Label(parent,text="Delay [s]",font="Arial 12 bold").grid(row=8,column=5)

		self.start_freq=StringVar()
		self.stop_freq=StringVar()
		self.step=StringVar()
		self.delay=IntVar()
		self.start_freq_entry=Entry(parent,textvariable=self.start_freq,width=10)
		self.start_freq_entry.grid(row=7,column=4)
		self.stop_freq_entry=Entry(parent,textvariable=self.stop_freq,width=10)
		self.stop_freq_entry.grid(row=7,column=5)
		self.step_entry=Entry(parent,textvariable=self.step,width=10)
		self.step_entry.grid(row=9,column=4)
		self.delay_entry=OptionMenu(parent,self.delay,1,2,3,4,5,6,7,8,9,10,12,14,16,18,20,25,30,40,50,60)
		self.delay_entry.grid(row=9,column=5)

		self.delay.set(1)

		self.swp_but=Button(parent,text="Sweep",font="Arial 12 bold",command=self.sweep_fs,width=10)
		self.swp_but.grid(row=15,column=4,columnspan=2)
		
		self.lam_start=Label(parent,text="")
		self.lam_start.grid(row=12,column=1,sticky=W)
		self.freq_start=Label(parent,text="")
		self.freq_start.grid(row=14,column=1,sticky=W)
		self.lam_stop=Label(parent,text="")
		self.lam_stop.grid(row=12,column=8,sticky=E)
		self.freq_stop=Label(parent,text="")
		self.freq_stop.grid(row=14,column=8,sticky=E)
		self.lam_now=Label(parent,text="")
		self.lam_now.grid(row=12,column=4,columnspan=2)
		self.freq_now=Label(parent,text="")
		self.freq_now.grid(row=14,column=4,columnspan=2)


		self.pr_var=DoubleVar()

		self.progress=ttk.Progressbar(parent,orient=HORIZONTAL,length=800,maximum=100,mode='determinate',variable=self.pr_var)
		self.progress.grid(row=13,column=1,columnspan=8)


		self.emission_on_button=Button(parent,text="Off",width=10,command=self.turn_on,font="Arial 12 bold",fg="red",relief=RAISED)
		self.emission_on_button.grid(row=16,column=8)



		wavelength=self.laser.get_wavelength()
		frequency=self.laser.get_frequency()
		power=self.laser.get_power()
		temperature=self.laser.get_temperature()

		self.lam.configure(text="{0:.4f}".format(wavelength)+" nm")
		self.freq.configure(text="{0:.5f}".format(frequency)+" THz")
		self.lamu.configure(text="{0:.5f}".format(wavelength/4)+" nm")
		self.frequ.configure(text="{0:.5f}".format(frequency*4)+" THz")
		self.pow.configure(text="{0:.2f}".format(power)+" mW")
		self.temp.configure(text="{0:.2f}".format(temperature)+" C")


		self.fig=plt.figure()
		self.ax=self.fig.add_subplot(111)

		self.frame=Frame(parent,width=500)
		self.frame.grid(row=1,column=10,rowspan=20)

		self.canvas=FigureCanvasTkAgg(self.fig,self.frame)
		self.canvas.draw()
		self.canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=True)

		# toolbar = NavigationToolbar2TkAgg(self.canvas,self.frame)
		# toolbar.update()
		# toolbar.pack(side=BOTTOM)
		# self.canvas._tkcanvas.pack(side=BOTTOM, fill=BOTH, expand=True)


		# self.parent.after(500,self.update_params)

		self.simlock=Button(parent,text="Sim",width=10,command=self.simulate,font="Arial 12 bold")
		self.simlock.grid(row=18,column=8)

	def simulate(self):
		L=Lock(11,[0.5,0.7])
		L.adjust_gains(60,8)
		# plt.ion()
		simulate_lock(L,0.01,150,15,self.ax)


	def update_params(self):

		wavelength=self.laser.get_wavelength()
		frequency=self.laser.get_frequency()
		power=self.laser.get_power()
		temperature=self.laser.get_temperature()

		self.lam.configure(text="{0:.4f}".format(wavelength)+" nm")
		if power>1:
			self.status[2].configure(text="{0:.2f}".format(wavelength)+" nm")
		self.freq.configure(text="{0:.5f}".format(frequency)+" THz")
		self.lamu.configure(text="{0:.5f}".format(wavelength/4)+" nm")
		self.frequ.configure(text="{0:.5f}".format(frequency*4)+" THz")
		self.pow.configure(text="{0:.2f}".format(power)+" mW")
		self.temp.configure(text="{0:.2f}".format(temperature)+" C")

		self.parent.after(500,self.update_params)

	def set_wvl(self):
		try:
			wvl=float(self.set_wv.get())
		except ValueError:
			return	
		if wvl<self.min_wv:
			wvl=self.min_wv
			self.set_wv.set(wvl)
		elif wvl>self.max_wv:
			wvl=self.max_wv
			self.set_wv.set(wvl)
		self.laser.set_wavelength(wvl)

	def sweep_fs(self):
		

		c=299792.458

		if self.start_freq.get()=='' or self.stop_freq.get()=='' or self.step.get()=='':
			return
		
		try:
			st_fr=float(self.start_freq.get())
			sp_fr=float(self.stop_freq.get())
			stp=float(self.step.get())
		except ValueError:
			return

		dly=self.delay.get()

		if sp_fr<st_fr:
			st_fr,sp_fr=sp_fr,st_fr
		

		if st_fr<c/self.max_wv:
			st_fr=c/self.max_wv
		elif st_fr>c/self.min_wv:
			st_fr=c/self.min_wv
		
		if sp_fr>c/self.min_wv:
			sp_fr=c/self.min_wv
		elif sp_fr<c/self.max_wv:
			sp_fr=c/self.max_wv

		if sp_fr==st_fr:
			return


		if stp>(sp_fr-st_fr)*500 or stp<0.05:
			return

		self.swp_but.configure(state="disabled")
		self.emission_on_button.configure(state="disabled")
		self.set_wv_button.configure(state="disabled")
		self.delay_entry.configure(state="disabled")
		self.mod_var_opt.configure(state="disabled")

		self.lam_start.configure(text="{0:.4f}".format(c/st_fr)+" nm")
		self.lam_stop.configure(text="{0:.4f}".format(c/sp_fr)+" nm")
		self.freq_start.configure(text="{0:.5f}".format(st_fr)+" THz")
		self.freq_stop.configure(text="{0:.5f}".format(sp_fr)+" THz")

		self.laser.sweep(st_fr,sp_fr,stp,dly,self)

		self.swp_but.configure(state="normal")
		self.emission_on_button.configure(state="normal")
		self.set_wv_button.configure(state="normal")
		self.delay_entry.configure(state="normal")
		self.mod_var_opt.configure(state="normal")
		
	def change_mod(self,*args):

		new_mod=self.mod_var.get()
		if new_mod=="Wide":
			self.laser.modulation_type(1)
		elif new_mod=="Narrow":
			self.laser.modulation_type(0)

	def turn_on(self,event=None):

		self.laser.emission_on()

		cv=self.status[0]
		ov=self.status[1]
		wv=self.status[2]
		cv.itemconfig(ov,fill="#05FF2B")
		wvl=self.laser.get_wavelength()
		wv.configure(text="{0:.2f}".format(wvl)+" nm")
		self.emission_on_button.configure(text="On",fg="green",command=self.turn_off,relief=SUNKEN)


	def turn_off(self,event=None):

		self.laser.emission_off()

		cv=self.status[0]
		ov=self.status[1]
		wv=self.status[2]
		cv.itemconfig(ov,fill="red")
		wv.configure(text="")
		self.emission_on_button.configure(text="Off",fg="red",command=self.turn_on,relief=RAISED)

		


class LaserConnect:
	def __init__(self,parent,pane):

		self.pane=pane
		self.parent=parent
		self.laser_tabs=[]
		self.status=[]

		parent.grid_columnconfigure(2,minsize=20)
		parent.grid_columnconfigure(0,minsize=20)
		parent.grid_rowconfigure(0,minsize=50)
		parent.grid_rowconfigure(2,minsize=50)
		parent.grid_rowconfigure(4,minsize=50)
		parent.grid_rowconfigure(5,minsize=50)
		parent.grid_rowconfigure(6,minsize=50)
		parent.grid_rowconfigure(7,minsize=50)
		parent.grid_rowconfigure(8,minsize=50)

		self.err=Label(parent,text="")
		self.err.grid(row=3,column=1)

		self.con_button=Button(parent, text="Connect Lasers",width=15,height=5,font="Arial 14 bold",command=self.initialize)
		self.con_button.grid(row=1,column=1,sticky=W)

		

	def initialize(self,event=None):
		L=connect_lasers()
		
		if len(L)==0:
			self.err.configure(text="Didn't find any devices \n connected to the computer")
		else:
			self.err.configure(text="")
			tab_ctrl=ttk.Notebook(self.pane)
			tabs=[]
			las=[]
			for i in range(len(L)):
				tabs.append(ttk.Frame(tab_ctrl))
				self.add_status(2*i+4,i+1)
			for i in range(len(L)):
				tab_ctrl.add(tabs[i], text="Laser "+str(i+1))
				las.append(LaserControl(tabs[i],self.status[i],L[i]))
			
			self.laser_tabs=las

			tab_ctrl.pack(expand=1,fill=BOTH)

			self.con_button.configure(state="disabled")

	def add_status(self,rw,ind):

		cl=Label(self.parent,text="Laser "+str(ind),font="Arial 12 bold")
		cl.grid(row=rw,column=1,sticky=W)
		cv=Canvas(self.parent,height=30,width=30)
		cv.grid(row=rw,column=1,sticky=E)
		ov=cv.create_oval(5,5,25,25,fill="red")
		wl=Label(self.parent,text="\u03bb:",font="Arial 10 bold")
		wl.grid(row=rw+1,column=1,sticky=W)
		wv=Label(self.parent,font="Arial 10 bold",text="")
		wv.grid(row=rw+1,column=1,sticky=E)
		self.status.append((cv,ov,wv))




root = Tk()

root.title("Laser control")

root.geometry("1800x800")

pane=PanedWindow(root,sashwidth=5,sashpad=2,sashrelief=GROOVE)
pane.pack(fill=BOTH, expand=1)

left=Frame(pane,width=200,bd=1)
pane.add(left)


right=Frame(pane,width=600,bd=4)
pane.add(right)

ld=LaserConnect(left,right)


root.protocol("WM_DELETE_WINDOW", callback)

mainloop()


