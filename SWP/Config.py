"""
File containing parser functions for the config file.
"""

import configparser

def load_conf(filename):
	config=configparser.ConfigParser()
	config.read(filename)
	return config

def save_conf(filename,daq_dict,wvm_dict,cav_dict,las1_dict,las2_dict=None):
	config=configparser.ConfigParser()
	config.optionxform = str
	config['DAQ']=daq_dict
	config['WAVEMETER']=wvm_dict
	config['CAVITY']=cav_dict
	config['LASER1']=las1_dict
	if las2_dict is not None:
		config['LASER2']=las2_dict

	if filename[-4:]!=".ini":
		filename+='.ini'
	with open(filename,'w') as configfile:
		config.write(configfile)

