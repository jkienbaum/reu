import h5py
import argparse
import numpy as np
import numpy
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import itertools
import copy

def plot_1d_binned_slices(truth, reco1, reco2=None,
					   xarray1=None,xarray2=None,truth2=None,\
					   plot_resolution=False, use_fraction = False,\
					   bins=10,xmin=-1.,xmax=1,style="contours",\
					   x_name = "Zenith", x_units = "",\
					   y_units=None,
					   reco1_name = "Reco 1", reco2_name = "Reco 2",\
					   reco1_weight = None, reco2_weight = None,
					   save=True,savefolder='.'):
	"""Plots different energy slices vs each other (systematic set arrays)
	Receives:
		truth = 1D array with truth values
		reco1 = 1D array that has reconstructed results
		reco2 = optional, 1D array that has an alternate reconstructed results
		xarray1 = optional, 1D array that the reco1 variable (or resolution) will be plotted against, if none is given, will automatically use truth1
		xarray2 = optional, 1D array that the reco2 variable (or resolution2) will be plotted against, if none is given, will automatically use xarray1
		truth2 = 1D array with truth values used to calculate resolution2
		plot_resolution = use resolution (reco - truth) instead of just reconstructed values
		use_fraction = bool, use fractional resolution instead of absolute, where (reco - truth)/truth
		style = "errorbars" is only string that would trigger change (to errorbar version), default is contour plot version
		bins = integer number of data points you want (range/bins = width)
		xmin = minimum truth value to start cut at (default = -1.)
		xmax = maximum truth value to end cut at (default = 1.)
		x_name = variable for x axis (what is the truth)
		x_units = units for truth/x-axis variable
		reco1_name = name for reconstruction 1
		reco2_name = name for reconstruction 2
		reco1_weight = 1D array for reco1 weights, if left None, will not use
		reco2_weight = 1D array for reco2 weights, if left None, will not use
	Returns:
		Scatter plot with truth bins on x axis (median of bin width)
		y axis has median of resolution or absolute reconstructed value with error bars containing given percentile
	"""

	percentile_in_peak = 68.27 #CAN CHANGE
	left_tail_percentile  = (100.-percentile_in_peak)/2
	right_tail_percentile = 100.-left_tail_percentile
	ranges  = numpy.linspace(xmin,xmax, num=bins)
	centers = (ranges[1:] + ranges[:-1])/2.
	
	# if no xarray given, automatically use truth
	if xarray1 is None:
		xarray1 = truth
	# Calculate resolution if plot_resolution flag == True
	if plot_resolution:
		if use_fraction:
			yvariable = ((reco1-truth)/truth) # in fraction
		else:
			yvariable = (reco1-truth)
	else: #use reco directly, not resolution
		y_variable = reco1
		assert use_fraction==False, "Flag for fractional resolution only, not doing resolution here"

	medians  = numpy.zeros(len(centers))
	err_from = numpy.zeros(len(centers))
	err_to   = numpy.zeros(len(centers))

	#Compare to second reconstruction if given    
	if reco2 is not None:
		#check if some variables exist, if not, set to match reco1's
		if truth2 is None:
			truth2 = truth
		if xarray2 is None:
			xarray2 = xarray1

		if plot_resolution:
			if use_fraction:
				yvariable2 = ((reco2-truth2)/truth2)
			else:
				yvariable2 = (reco2-truth2)
		else:
			yvariable2 = reco2
		medians2  = numpy.zeros(len(centers))
		err_from2 = numpy.zeros(len(centers))
		err_to2   = numpy.zeros(len(centers))

	# Find median and percentile bounds for data
	for i in range(len(ranges)-1):

		# Make a cut based on the truth (binned on truth)
		var_to   = ranges[i+1]
		var_from = ranges[i]
		cut = (xarray1 >= var_from) & (xarray1 < var_to)
		if not sum(cut)>0:
			print(i)
			continue
		assert sum(cut)>0, "No events in xbin from %s to %s for reco1, may need to change xmin, xmax, or number of bins or check truth/xarray inputs"%(var_from, var_to)
		if reco2 is not None:
			cut2 = (xarray2 >= var_from) & (xarray2 < var_to)
			assert sum(cut2)>0, "No events in xbin from %s to %s for reco2, may need to change xmin, xmax, or number of bins or check truth2/xarray2 inputs"%(var_from, var_to)
		
		#find number of reco1 (or resolution) in this bin
		if reco1_weight is None:
			lower_lim = numpy.percentile(yvariable[cut], left_tail_percentile)
			upper_lim = numpy.percentile(yvariable[cut], right_tail_percentile)
			median = numpy.percentile(yvariable[cut], 50.)
		else:
			import wquantiles as wq
			lower_lim = wq.quantile(yvariable[cut], reco1_weight[cut], left_tail_percentile)
			upper_lim = wq.quantile(yvariable[cut], reco1_weight[cut], right_tail_percentile)
			median = wq.median(yvariable[cut], reco1_weight[cut])

		medians[i] = median
		err_from[i] = lower_lim
		err_to[i] = upper_lim
 
		#find number of reco2 (or resolution2) in this bin
		if reco2 is not None:
			if reco2_weight is None:
				lower_lim2 = numpy.percentile(yvariable2[cut2], left_tail_percentile)
				upper_lim2 = numpy.percentile(yvariable2[cut2], right_tail_percentile)
				median2 = numpy.percentile(yvariable2[cut2], 50.)
			else:
				import wquantiles as wq
				lower_lim2 = wq.quantile(yvariable2[cut2], reco2_weight[cut2], left_tail_percentile)
				upper_lim2 = wq.quantile(yvariable2[cut2], reco2_weight[cut2], right_tail_percentile)
				median2 = wq.median(yvariable2[cut2], reco2_weight[cut2])

			medians2[i] = median2
			err_from2[i] = lower_lim2
			err_to2[i] = upper_lim2

	# Make plot
	plt.figure(figsize=(10,7))
	
	# Median as datapoint
	# Percentile as y error bars
	# Bin size as x error bars
	if style is "errorbars":
		plt.errorbar(centers, medians, yerr=[medians-err_from, err_to-medians], xerr=[ centers-ranges[:-1], ranges[1:]-centers ], capsize=5.0, fmt='o',label="%s"%reco1_name)
		#Compare to second reconstruction, if given
		if reco2 is not None:
			plt.errorbar(centers, medians2, yerr=[medians2-err_from2, err_to2-medians2], xerr=[ centers-ranges[:-1], ranges[1:]-centers ], capsize=5.0, fmt='o',label="%s"%reco2_name)
			plt.legend(loc="upper center")
	# Make contour plot
	# Center solid line is median
	# Shaded region is percentile
	# NOTE: plotted using centers, so 0th and last bins look like they stop short (by 1/2*bin_size)
	else:
		alpha=0.5
		lwid=3
		cmap = plt.get_cmap('Blues')
		colors = cmap(numpy.linspace(0, 1, 2 + 2))[2:]
		color=colors[0]
		cmap = plt.get_cmap('Oranges')
		rcolors = cmap(numpy.linspace(0, 1, 2 + 2))[2:]
		rcolor=rcolors[0]
		ax = plt.gca()
		ax.plot(centers, medians,linestyle='-',label="%s median"%(reco1_name), color=color, linewidth=lwid)
		ax.fill_between(centers,medians, err_from,color=color, alpha=alpha)
		ax.fill_between(centers,medians, err_to, color=color, alpha=alpha,label=reco1_name + " %i"%percentile_in_peak +'%' )
		if reco2 is not None:
			ax.plot(centers,medians2, color=rcolor, linestyle='-', label="%s median"%reco2_name, linewidth=lwid)
			ax.fill_between(centers,medians2,err_from, color=rcolor, alpha=alpha)
			ax.fill_between(centers,medians2,err_to2, color=rcolor,alpha=alpha,label=reco2_name + " %i"%percentile_in_peak +'%' )
	
	# Extra features to have a horizontal 0 line and trim the x axis
	plt.plot([xmin,xmax], [0,0], color='k')
	plt.xlim(xmin,xmax)
	
	#Make pretty labels
	plt.xlabel("%s %s"%(x_name,x_units))
	if plot_resolution:
		if use_fraction:
			plt.ylabel("Fractional Resolution: \n (reconstruction - truth)/truth")
		else:
			plt.ylabel("Resolution: \n reconstruction - truth %s"%x_units)
			if y_units is not None:
				plt.ylabel("Resolution: \n reconstruction - truth %s"%y_units)            	
	else:
		plt.ylabel("Reconstructed %s %s"(x_name,x_units)) 

	# Make a pretty title
	title = "%s Dependence for Electron Neutrinos %s"%(x_name,reco1_name)
	if reco2 is not None:
		title += " and %s"%(reco2_name)
	if plot_resolution:
		title += " Resolution"
	plt.title("%s"%(title))

	# Make a pretty filename
	savename = "%s"%(x_name.replace(" ",""))
	if use_fraction:
		savename += "Frac"
	if plot_resolution:
		savename += "Resolution"
	if reco2 is not None:
		savename += "_Compare%s"%(reco2_name.replace(" ",""))
	if save == True:
		plt.savefig("%s/%s.png"%(savefolder,savename))

def find_contours_2D(x_values,y_values,xbins,weights=None,c1=16,c2=84):   
	"""
	Find upper and lower contours and median
	x_values = array, input for hist2d for x axis (typically truth)
	y_values = array, input for hist2d for y axis (typically reconstruction)
	xbins = values for the starting edge of the x bins (output from hist2d)
	c1 = percentage for lower contour bound (16% - 84% means a 68% band, so c1 = 16)
	c2 = percentage for upper contour bound (16% - 84% means a 68% band, so c2=84)
	Returns:
		x = values for xbins, repeated for plotting (i.e. [0,0,1,1,2,2,...]
		y_median = values for y value medians per bin, repeated for plotting (i.e. [40,40,20,20,50,50,...]
		y_lower = values for y value lower limits per bin, repeated for plotting (i.e. [30,30,10,10,20,20,...]
		y_upper = values for y value upper limits per bin, repeated for plotting (i.e. [50,50,40,40,60,60,...]
	"""
	if weights is not None:
		import wquantiles as wq
	y_values = numpy.array(y_values)
	indices = numpy.digitize(x_values,xbins)
	r1_save = []
	r2_save = []
	median_save = []
	for i in range(1,len(xbins)):
		mask = indices==i
		if len(y_values[mask])>0:
			if weights is None:
				r1, m, r2 = numpy.percentile(y_values[mask],[c1,50,c2])
			else:
				r1 = wq.quantile(y_values[mask],weights[mask],c1/100.)
				r2 = wq.quantile(y_values[mask],weights[mask],c2/100.)
				m = wq.median(y_values[mask],weights[mask])
		else:
			#print(i,'empty bin')
			r1 = numpy.nan
			m = numpy.nan
			r2 = numpy.nan
		median_save.append(m)
		r1_save.append(r1)
		r2_save.append(r2)
	median = numpy.array(median_save)
	lower = numpy.array(r1_save)
	upper = numpy.array(r2_save)

	# this is a funny way of outputting the result
	# which was in the original code we borrowed from the oscnext folks
	# remove it for now
	# x = list(itertools.chain(*zip(xbins[:-1],xbins[1:])))
	# y_median = list(itertools.chain(*zip(median,median)))
	# y_lower = list(itertools.chain(*zip(lower,lower)))
	# y_upper = list(itertools.chain(*zip(upper,upper)))
	# return x, y_median, y_lower, y_upper

	# the first return with the [1:] and [:-1] is about locating the bin centers
	return (xbins[1:] + xbins[:-1])/2, median, lower, upper



parser = argparse.ArgumentParser()
parser.add_argument("-f", type=str, nargs='+',
	dest="input_files", required=True,
	help="paths to input files (absolute or relative)")
args = parser.parse_args()
files = args.input_files

ophelia_zenith = np.asarray([])
linefit_zenith = np.asarray([])
true_zenith = np.asarray([])
true_energy = np.asarray([])
hqtot = np.asarray([])
current_type = np.asarray([])

for file in files:

	file_in = h5py.File(file, "r")
	# print(file_in['NuPrimary'].dtype.names)

	try:
		ophelia_zenith = np.concatenate((ophelia_zenith, 
			file_in['EHEOpheliaParticleSRT_ImpLF']['zenith']))
		linefit_zenith = np.concatenate((linefit_zenith, 
			file_in['LineFit']['zenith']))
		true_zenith = np.concatenate((true_zenith,
			file_in['NuPrimary']['zenith']))
		true_energy = np.concatenate((true_energy,
			file_in['NuPrimary']['energy']))
		hqtot = np.concatenate((hqtot,
			file_in['Homogenized_QTot']['value']))
		current_type = np.concatenate((current_type,
			file_in['I3MCWeightDict']['InteractionType']))
		print("Finished all {}".format(file))
	except:
		print('Skipping {}'.format(file))

	file_in.close()


ophelia_zenith = np.rad2deg(ophelia_zenith)
linefit_zenith = np.rad2deg(linefit_zenith)
true_zenith = np.rad2deg(true_zenith)
bins = [np.linspace(0,180,91), np.linspace(0,180,91)]

log_hqtot = np.log10(hqtot)
qtot_mask = log_hqtot > 4
print(qtot_mask)

interaction_mask = current_type >= 1
print(interaction_mask)


# 2D histogram
fig = plt.figure(figsize=(6,5))
ax = fig.add_subplot(111)
counts, xedges, yedges, im = ax.hist2d(
	true_zenith[qtot_mask & interaction_mask],
	ophelia_zenith[qtot_mask & interaction_mask],
	bins=bins,
	cmin=1,
	norm=colors.LogNorm()
	)

# get the contours, using a function from Jessie and the oscNext team
x, y_med, y_lo, y_hi = find_contours_2D(
	x_values=true_zenith[qtot_mask & interaction_mask],
	y_values=linefit_zenith[qtot_mask & interaction_mask],
	xbins=xedges
	)
y_med = np.asarray(y_med)
y_lo = np.asarray(y_lo)
y_hi = np.asarray(y_hi)
# plot them
ax.plot(x, y_med, 'r-', label='Median')
ax.plot(x, y_lo, 'r-.', label='68% contour')
ax.plot(x, y_hi, 'r-.')

cbar = plt.colorbar(im, ax=ax)
cbar.set_label('Number of Events')#, fontsize=sizer)
ax.set_ylabel('Reco Zenith')
ax.set_xlabel('True Zenith')
ax.legend()
plt.tight_layout()
plt.title('Muon Neutrino (LineFit Recon)')
fig.savefig('test_charge_electron_linefit.png', dpi=300)
del fig, ax

# we can also plot the size of the error bar in 1D to make visualization easier
fig = plt.figure(figsize=(6,5))
ax = fig.add_subplot(111)
ax.errorbar(x, y_med - x, yerr=[y_hi-y_med, y_med-y_lo], capsize=0.0, fmt='o')
ax.plot(x, y_med - x, 'o')
ax.set_xlabel('True Zenith')
ax.set_ylabel('Error (True - Reco)')
plt.tight_layout()
fig.savefig('test_error_electron.png')
del fig, ax

true_energy = np.log10(true_energy)
# finally, we can also plot our resolution as a function of energy
# for that, we're going to borrow a function from Jessie
plot_1d_binned_slices(truth=true_zenith[qtot_mask],
	reco1=linefit_zenith[qtot_mask & interaction_mask],
	reco2=ophelia_zenith[qtot_mask & interaction_mask],
	xarray1=true_energy[qtot_mask & interaction_mask],
	plot_resolution=True,
	xmin=np.min(true_energy[qtot_mask & interaction_mask]),
	xmax=np.max(true_energy[qtot_mask & interaction_mask]),
	x_name='True_Energy',
	x_units='log10(GeV)',
	y_units='Degrees',
	reco1_name='Ophelia',
	reco2_name='LineFit'
	)
