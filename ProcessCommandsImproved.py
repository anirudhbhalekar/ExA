import numpy as np
from scipy import interpolate



def interpolate_variable(variable, length):
    # Interpolation functions map length of input variable to length of gcode file
    if np.isscalar(variable):  # Variable is constant throughout print
        f = interpolate.interp1d([0, length-1], [variable, variable])
    else:  # Interpolate variable over print
        f = interpolate.interp1d(np.linspace(0, length-1, len(variable)), variable)
    return f


def addvariable(command, index, string):
    # Returns gcode string if the variable value is defined in command
    if np.isnan(command[index]):
        return ''
    else:
        return ' ' + string + str(command[index])

def checklimits(printparameter, value, lessthan=True):
    # Safety limit assertions: check printparameter is within desired values
    # Handle integer & float arguments
    if isinstance(printparameter, int) or isinstance(printparameter, float):
        if lessthan:
            assert printparameter <= value
        else:
            assert printparameter >= value
    # Handle list arguments
    elif isinstance(printparameter, list):
        if lessthan:
            assert all(param <= value for param in printparameter)
        else:
            assert all(param >= value for param in printparameter)
    # Handle other arguments
    else:
        raise Exception("Unexpected parameter type")


def create_list_from_val(val, num_prints):

    mt_list = np.zeros(num_prints)

    if type(val) != list: 
        mt_list[:] = val

    elif len(val) < num_prints: 
        while len(val) < num_prints: 
            val.append(val[-1])

        mt_list = val
    else: 
        mt_list = val
    
    return mt_list

def return_grid_size(num_prints): 

    tolerance = 0.01
    
    size = np.ceil(np.sqrt(num_prints - tolerance)) 

    return int(size)

def processgcode(filestub, commands, kp=15.5, ki=0.13, kd=6.0, nozzletemp=210, bedtemp=55, speedfactor=1,
                 extrusionfactor=1, retraction=2.5, fanspeed=255, num_prints=9):

    # Safety limits: to prevent damage to the printer. Check with your demonstrator before exceeding these.
    checklimits(nozzletemp, 180, False)
    checklimits(nozzletemp, 260)
    checklimits(bedtemp, 75)
    checklimits(extrusionfactor, 2)
    checklimits(retraction, 15)

    offsets = []
    grid_size = return_grid_size(num_prints)
    step = (100/grid_size)
    for i in range(num_prints):
        if ((i // grid_size) + 1) % 2 == 0:
            x = int((grid_size - (i % grid_size) - 0.5) * step)
        else:
            x = int(((i % grid_size) + 0.5) * step)
        y = int(((i // grid_size) + 0.5) * step)
        offsets.append((x, y))
    
    for o in offsets:
        print(o)

    output = ''

    kp_list = create_list_from_val(kp, num_prints)
    ki_list = create_list_from_val(ki, num_prints)
    kd_list = create_list_from_val(kd, num_prints)

    nozzletemp_list = create_list_from_val(nozzletemp, num_prints)
    bedtemp_list = create_list_from_val(bedtemp, num_prints)

    speedfactor_list = create_list_from_val(speedfactor, num_prints)
    extrusionfactor_list = create_list_from_val(extrusionfactor, num_prints)

    retraction_list = create_list_from_val(retraction, num_prints)
    fanspeed_list = create_list_from_val(fanspeed, num_prints)

    for n in range(num_prints):

        # Create interpolation functions
        fkp = interpolate_variable(kp_list[n], len(commands))
        fki = interpolate_variable(ki_list[n], len(commands))
        fkd = interpolate_variable(kd_list[n], len(commands))
        fnozzletemp = interpolate_variable(nozzletemp_list[n], len(commands))
        fbedtemp = interpolate_variable(bedtemp_list[n], len(commands))
        fspeedfactor = interpolate_variable(speedfactor_list[n], len(commands))
        fextrusionfactor = interpolate_variable(extrusionfactor_list[n], len(commands))
        fretraction = interpolate_variable(retraction_list[n], len(commands))
        ffanspeed = interpolate_variable(fanspeed_list[n], len(commands))

        # All gcode is saved in output variable, which is saved to file at the end
        output += 'M301 P' + str(fkp(0)) + ' I' + str(fki(0)) + ' D' + str(fkd(0)) + '\n'  # Set initial PID parameters
        output += 'M140 S' + str(fbedtemp(0)) + '\n' + 'M190 S' + str(fbedtemp(0)) + '\n'  # Set initial bed temperature
        output += 'M104 S' + str(fnozzletemp(0)) + '\n' + 'M109 S' \
                  + str(fnozzletemp(0)) + '\n'  # Set initial hotend temperature
        output += 'M83\nG21\nG90\nM107\nG28\nG0 Z5 E5 F500\nG0 X-1 Z0\nG1' \
                  ' Y60 E3 F500\nG1 Y10 E8 F500\nG1 E-1 F250\n'  # Initialise printer

        # Retract, move to starting position, and begin extrusion
        output += 'G1 F2400 E-2.5\nG0'
        output += addvariable(commands[0], 2, 'X')  # Add X command if it exists
        output += addvariable(commands[0], 3, 'Y')  # Add Y command if it exists
        output += addvariable(commands[0], 4, 'Z')  # Add Z command if it exists
        output += addvariable(commands[0], 5, 'E')  # Add E command if it exists
        output += '\nG1 F2400 E2.5\n'
        output += 'G0 F'+str(2400*speedfactor)+'\n'

        output += 'M106 S' + str(ffanspeed(0)) + '\n'  # Set initial fan speed

        # Walk through all remaining commands
        retractflag = False
        for i in range(2, len(commands)):
            if i % 1000 == 0:
                print(str(i) + '/' + str(len(commands)) + ' commands')
            commands[i][1] *= fspeedfactor(i) # Apply speed factor
            if commands[i][5] < 0:
                commands[i][5]= -fretraction(i) # Apply retraction
                retractflag = True
            elif retractflag and commands[i][5] > 0:
                commands[i][5] = fretraction(i) # Apply retraction
                retractflag = False
            else:
                commands[i][5] *= fextrusionfactor(i) # Apply extrusion factor

            # Change PID controls when necessary
            if float(fkp(i)) != float(fkp(i-1)) or float(fki(i)) != float(fki(i-1)) or float(fkd(i)) != float(fkd(i-1)):
                output += 'M301 P' + str(fkp(i)) + ' I' + str(fki(i)) + ' D' + str(fkd(i)) +'\n'
            # Change hotend temperature when necessary
            if float(fnozzletemp(i)) != float(fnozzletemp(i-1)):
                output += 'M104 S' + str(fnozzletemp(i)) + '\n'
            # Change bed temperature when necessary
            if float(fbedtemp(i)) != float(fbedtemp(i-1)):
                output += 'M140 S' + str(fbedtemp(i)) + '\n'
            # Change fan speed when necessary
            if float(ffanspeed(i)) != float(ffanspeed(i-1)):
                output += 'M106 S' + str(ffanspeed(i)) + '\n'

            output += 'G' + str(int(commands[i][0]))
            output += addvariable(commands[i], 2, 'X')  # Add X command if it exists
            output += addvariable(commands[i], 3, 'Y')  # Add Y command if it exists
            output += addvariable(commands[i], 4, 'Z')  # Add Z command if it exists
            output += addvariable(commands[i], 5, 'E')  # Add E command if it exists
            output += '\n'

    # Closing code
    output += 'M107\nG0 X0 Y120\nM190 S0\nG1 E-3 F200\nM104 S0\nG4 S300\nM107\nM84'

    # Write output to file
    filename = 'outputgcode/' + filestub + '.gcode'
    file = open(filename, 'w')
    file.write(output)
    file.close()


if __name__ == "__main__": 

    pass
