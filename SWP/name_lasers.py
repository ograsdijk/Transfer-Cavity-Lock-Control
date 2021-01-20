from Devices import *



las=connect_lasers()
# for l in las:
	# if l.get_name()=="Seed 1":
		# l.write_name('Seed 2')
for l in las:
	print(l)
