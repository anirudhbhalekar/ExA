import numpy as np
from ProcessCommandsImproved import processgcode  # This function edits the gcode

printcommands = np.load('objectdata/DimensionalAccuracy.npy')  # The hollow cube is chosen for processing

temperature_list = [215, 205, 195, 185,215, 205, 195, 185,215, 205, 195, 185,215, 205, 195, 185]
ext_amt_list =     [1.2, 1.2, 1.2, 1.2, 1.1, 1.1, 1.1, 1.1, 1, 1, 1, 1, 0.9, 0.9, 0.9, 0.9]
# See the instruction document for details of the following function's inputs
processgcode('OUTPUT_DimensionAccuracy_initalised', printcommands, nozzletemp=temperature_list, bedtemp= 65, speedfactor= 1, retraction=3, extrusionfactor=ext_amt_list, num_prints=16)

# The output file is saved as 'OUTPUT_HollowCube' in the outputgcode folder.
# The nozzle temperature starts at 200C, increases to 220 by the middle of the print, then returns to 200C.
# The bed temperature starts at 65C and linearly decreases to 50C.
# The retraction length is set to a constant value of 3mm.
# All other variables are kept as their constant defaults.

# If increasing speedfactor does not increase the print speed, the maximum motor feedrates may need editing.
# Google 'Marlin M203' for more information.

print('Data Processed')
