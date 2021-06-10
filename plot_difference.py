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

# let's start by making a histogram of the true and reconstructed directions
# so, we make an empty array for each

reco_azimuth = np.asarray([])
true_azimuth = np.asarray([])


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
		reco_azimuth = np.concatenate((reco_azimuth, 
			file_in['EHEOpheliaParticleSRT_ImpLF']['azimuth']))
		true_azimuth = np.concatenate((true_azimuth,
			file_in['NuPrimary']['azimuth']))
	except:
		print('Skipping {}'.format(file))

	# close the file
	file_in.close()


# we are going to convert the radians to degrees
reco_azimuth = np.rad2deg(reco_azimuth)
true_azimuth = np.rad2deg(true_azimuth)

# my attempt
difference_azimuth = reco_aziumuth-true_azimuth

# now that we've loaded the data, we can make a plot!
fig = plt.figure(figsize=(5,5))
ax = fig.add_subplot(111)
bins = np.linspace(0,360,37) # let's do uniform binning from 0 -> 360 in 10 degree bins
ax.hist(difference_azimuth,bins=bins, alpha=0.5, label='Reco-True')

ax.set_ylabel('Number of Events')
ax.set_xlabel('Azimuth [deg]')
ax.legend()
plt.tight_layout()
fig.savefig('distribution_of_azimuth.png', dpi=300)
del fig, ax
