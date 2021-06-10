#!/bin/sh /cvmfs/icecube.opensciencegrid.org/py3-v4.1.1/icetray-start
#METAPROJECT combo/V01-01-00

from icecube import icetray, dataio, dataclasses, hdfwriter
from I3Tray import I3Tray

# so this part uses the python "argument parser"
# you can read more about it e.g. here: https://realpython.com/command-line-interfaces-python-argparse/
# it allows us to run commands like "python -o something"
# and then "something" (whether it be a number, word, etc) can be used in our code!
# we have two somethings for this: an input file and output file
# so, we could run like:
#    python create_hdf5.py -i /mnt/research/IceCube/Level2_IC86.2016_NuMu.021217.000000.i3.zst -o test

import argparse, copy
parser = argparse.ArgumentParser()
parser.add_argument("-i", type=str,
	dest="input_file",required=True,
	help="full path to the input file",
	)
parser.add_argument("-o", type=str,
	dest="output_file",required=True,
	help='''full path to the output file, without file extention. 
			That is, provide "test" not "test.i3.bz2"''',
	)
args = parser.parse_args()



# start up icetray
tray = I3Tray()

# and tell icetray to read a file
tray.AddModule("I3Reader", filenamelist=[args.input_file])


# next, we are only going to look at events which have the "Portia" and "Ophelia" reconstructions
# so, we build a little function that checks if the frame has the portia information
# and if it doesn't, then we will get rid of the frame

def has_needed(frame):
	return frame.Has('EHEOpheliaParticleSRT_ImpLF')

# drop every frame that doesn't have the Portia information we need
tray.AddModule(has_needed, # 'something',
	Streams=[icetray.I3Frame.Physics],
	)


# now we write a little bit of code that will find the most energetic neutrino
# and saves it to the frame for us to look at later
def store_primary(frame, mctree_name):
	if frame.Has(mctree_name):
		p = dataclasses.get_most_energetic_neutrino(frame[mctree_name])
		frame['NuPrimary'] = copy.copy(p)

tray.AddModule(store_primary, 
	mctree_name='I3MCTree_preMuonProp',
	Streams=[icetray.I3Frame.DAQ]
	)


# next, we can use the IceCube HDF5 writer to save things to file
# in this case, we are going to save out a few variables, given by the "Keys" argument
# in particular, Homogenized_QTot, EHEPortiaEventSummarySRT, etc.
# here is where you could add a new variable, for example, LineFit!
# because this is monte carlo, we know the right answer, and so we save it too (that is)
tray.AddSegment(hdfwriter.I3HDFWriter, 'hdf', 
	Output=f'{args.output_file}.hdf5', 
	Keys=[ 'I3EventHeader', 'Homogenized_QTot', 'EHEPortiaEventSummarySRT', 
	'EHEOpheliaParticleSRT_ImpLF', 'LineFit', 'NuPrimary' ],
	SubEventStreams=['InIceSplit']
	)

# sometimes it is also useful to write our results out in i3 format so we can look at them
# tray.AddModule("I3Writer", "write",
# 	filename=f'{args.output_file}.i3.zst',
# 	Streams=[icetray.I3Frame.DAQ, icetray.I3Frame.Physics],
# 	DropOrphanStreams=[icetray.I3Frame.Calibration, icetray.I3Frame.DAQ]
# 	)

tray.Execute()
