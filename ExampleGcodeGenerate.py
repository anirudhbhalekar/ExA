import numpy as np
from ProcessCommandsImproved import processgcode  # This function edits the gcode

NUM_PRINTS = 16 
printcommands = np.load('objectdata/DimensionalAccuracy.npy')  # The hollow cube is chosen for processing

def generate_temp_profiles(num_prints): 
    temp_tuple = []

    temp_init_h = 220
    temp_init_l = 200

    temp_end_h = 200
    temp_end_l = 180

    step_init = (temp_init_h - temp_init_l)/int(np.sqrt(num_prints))
    step_end = (temp_end_h - temp_end_l) /  int(np.sqrt(num_prints))

    for i in range(int(np.sqrt(num_prints))): 
        for e in range(int(np.sqrt(num_prints))): 

            temp_tuple.append(list((temp_init_h - i*step_init, temp_end_h - e*step_end)))

    return temp_tuple

temperature_list = generate_temp_profiles(NUM_PRINTS)
ext_amt_list =     [1.2, 1.2, 1.2, 1.2, 1.05, 1.05, 1.05, 1.05, 0.9, 0.9, 0.9, 0.9, 0.75, 0.75, 0.75, 0.75]



if __name__ == "__main__": 
    # See the instruction document for details of the following function's inputs
    processgcode('OUTPUT_DimensionAccuracy_Updated', printcommands, nozzletemp=temperature_list, bedtemp= 50, speedfactor= 1, retraction=3, extrusionfactor=ext_amt_list, num_prints=NUM_PRINTS)

    tt = generate_temp_profiles(NUM_PRINTS)
    print(tt)
    # The output file is saved as 'OUTPUT_HollowCube' in the outputgcode folder.
    # The nozzle temperature starts at 200C, increases to 220 by the middle of the print, then returns to 200C.
    # The bed temperature starts at 65C and linearly decreases to 50C.
    # The retraction length is set to a constant value of 3mm.
    # All other variables are kept as their constant defaults.

    # If increasing speedfactor does not increase the print speed, the maximum motor feedrates may need editing.
    # Google 'Marlin M203' for more information.

    print('Data Processed')