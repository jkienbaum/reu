import h5py
import argparse
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors

# again, we are going to use argparser to read in files!
# this time we are going to use nargs='+' to say "allow more than one argument"

parser = argparse.ArgumentParser()
parser.add_argument("-f", type=str, nargs='+',
	dest="input_files", required=True,
	help="paths to input files (absolute or relative)")
args = parser.parse_args()
files = args.input_files

# we make an empty array for each
ophelia_azimuth = np.asarray([])
linefit_azimuth = np.asarray([])
true_azimuth = np.asarray([])
ophelia_zenith = np.asarray([])
linefit_zenith = np.asarray([])
true_zenith = np.asarray([])


# now, we loop over every file
for file in files:

	# we open the hdf5 file for reading
	file_in = h5py.File(file, "r")

	# and now we "concatenate" our existing list and the new list!

	# note, if you want to see what variable names are available, 
	# you can try something like the following
	# print(file_in['EHEOpheliaParticleSRT_ImpLF'].dtype.names)

	# try/except statements are way of preventing the program from crashing 
	# if something is horribly wrong
	try:
		ophelia_azimuth = np.concatenate((ophelia_azimuth, 
			file_in['EHEOpheliaParticleSRT_ImpLF']['azimuth']))
		linefit_azimuth = np.concatenate((linefit_azimuth,
			file_in['LineFit']['azimuth']))
		true_azimuth = np.concatenate((true_azimuth,
			file_in['NuPrimary']['azimuth']))
		ophelia_zenith = np.concatenate((ophelia_zenith, 
			file_in['EHEOpheliaParticleSRT_ImpLF']['zenith']))
		linefit_zenith = np.concatenate((linefit_zenith,
			file_in['LineFit']['zenith']))
		true_zenith = np.concatenate((true_zenith,
			file_in['NuPrimary']['zenith']))
	except:
		print('Skipping {}'.format(file))

	# close the file
	file_in.close()


# we are going to convert the radians to degrees
ophelia_azimuth = np.rad2deg(ophelia_azimuth)
linefit_azimuth = np.rad2deg(linefit_azimuth)
true_azimuth = np.rad2deg(true_azimuth)
ophelia_zenith = np.rad2deg(ophelia_zenith)
linefit_zenith = np.rad2deg(linefit_zenith)
true_zenith = np.rad2deg(true_zenith)

# subtract true-recon
ophelia_diff_azimuth = np.subtract(true_azimuth,ophelia_azimuth)
linefit_diff_azimuth = np.subtract(true_azimuth,linefit_azimuth)
ophelia_diff_zenith = np.subtract(true_zenith,ophelia_zenith)
linefit_diff_zenith = np.subtract(true_zenith,linefit_zenith)

# absolute value true-recon
ophelia_abs_azi = np.abs(ophelia_diff_azimuth)
linefit_abs_azi = np.abs(linefit_diff_azimuth)
ophelia_abs_zen = np.abs(ophelia_diff_zenith)
linefit_abs_zen = np.abs(linefit_diff_zenith)

# now that we've loaded the data, we can make a plot!
fig = plt.figure(figsize=(5,5))
ax = fig.add_subplot(111)
bins = np.linspace(0,180,181) # let's do uniform binning
ax.hist(ophelia_abs_azi,bins=bins, alpha=0.5, label='Ophelia Azimuth')
ax.hist(linefit_abs_azi,bins=bins, alpha=0.5, label='LineFit Azimuth')
ax.hist(ophelia_abs_zen,bins=bins, alpha=0.5, label='Ophelia Zenith')
ax.hist(linefit_abs_zen,bins=bins, alpha=0.5, label='LineFit Zenith')
ax.set_yscale('log')
ax.set_ylabel('Number of Events')
ax.set_xlabel('Absolute(True-Recon) [deg]')
ax.legend()
plt.tight_layout()
fig.savefig('fig_abs_truerecon.png', dpi=300)
del fig, ax

figg = plt.figure(figsize=(5,5))
bx = figg.add_subplot(111)
bbins = np.linspace(-360,360,73) # let's do uniform binning
bx.hist(ophelia_diff_azimuth,bins=bins, alpha=0.5, label='Ophelia-True')
bx.hist(linefit_diff_azimuth,bins=bins, alpha=0.5, label='LineFit-True')
bx.hist(ophelia_diff_zenith,bins=bins, alpha=0.5, label='Ophelia-True')
bx.hist(linefit_diff_zenith,bins=bins, alpha=0.5, label='LineFit-True')
bx.set_yscale('log')
bx.set_ylabel('Number of Events')
bx.set_xlabel('[deg]')
bx.legend()
plt.tight_layout()
figg.savefig('fig_diff_truerecon.png', dpi=300)
del figg, bx
