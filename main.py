#Commands for controlling MonoPrice Blackbird HDMI Matrix
#Product number 21905. Commands pulled from:
#http://downloads.monoprice.com/files/manuals/21905_RS232_Control_180103.pdf
#Author: Cody Johnson
#Email: cody994@gmail.com


import serial
#Be sure to set your correct serial port!
ser = serial.Serial("COM2", 115200)

#------------------------------------------------------------------------------#
#Change Commands

#changeInput: Takes one input and n outputs and sets outputs with new inputs
#pass as integers, function will conver them to string
def changeInput(vidIn,*args):
    header = "5056540203" + str(vidIn).zfill(2) + "00"
    for vidOut in args:
        sendCommand(header + str(vidOut).zfill(2))

#pass as integers, function will conver them to string
def changeInputAll(vidIn):
    vidIn = str(vidIn).zfill(2)
    changeInput(vidIn,1,2,3,4)

#pass as integers, function will conver them to string
#EDID index list:
#01 = 1080p Stereo Audio 2.0| 02 = 1080p Dolby/DTS 5.1| 03 = 1080p HD Audio 7.1
#04 = 1080i Stereo Audio 2.0| 05 = 1080i Dolby/DTS 5.1| 06 = 1080i HD Audio 7.1
#07 = 3D Stereo Audio 2.0   | 08 = 3D Dolby/DTS 5.1   | 09 = 3D HD Audio 7.1
#10= 4K2K30 Stereo Audio 2.0| 11= 4K2K30 Dolby/DTS 5.1| 12= 4K2K30 HD Audio7.1
#13= DVI 1024x768           | 14= DVI 1920x1080       | 15= DVI 1920x1200
def changeEDID(edid,vidIn):
    sendCommand("5056540201" + str(edid).zfill(2) + "00" + str(vidIn).zfill(2))

#copyEDID: Takes one output and n inputs and sets input's EDID to match output
#sending 0 for input will set it for all inputs
def copyEDID(vidOut,*args):
    header = "5056540304" + str(vidOut).zfill(2) + "00"
    for vidIn in args:
        sendCommand(header + str(vidIn).zfill(2))

#beepOn: Turns on main unit beep when making changes
def beepOn():
    sendCommand("50565406010F00DD")

#beepOff: Turns off main unit beep when making changes
def beepOff():
    sendCommand("5056540601F")    

#powerOn: Turns the main unit on (takes it out of standby mode)
def powerOn():
    sendCommand("505654080B0F000F")

#powerOff: Turns the main unit off (puts it into standby mode)
def powerOff():
    sendCommand("505654080BF000F0")

#rebootMatrix: Reboots the main unit
def rebootMatrix():
    sendCommand("505654080D")

#factoryReset: Factory resets the main unit
def factoryReset():
    sendCommand("505654080A")

#------------------------------------------------------------------------------#
#Query Commands

#queryOutput: Takes given output and returns the input it is displaying
#pass as integers, function will conver them to string
#returned as int
def queryOutput(vidOut):
    response = sendCommand("5056540201" + str(vidOut).zfill(2))
    return(int(response[23:25]))

#queryOutputAll: Returns input set for all four outputs
#returned as int list
def queryOutputAll():
    l = []
    for vidOut in range(1,5):
        l.append(queryOutput(vidOut))
    return(l)

#queryEdid: Returns status of EDID on specified input port
#pass as integers, function will conver them to string
#returned outputs mean as follows
#01 = 1080p Stereo Audio 2.0| 02 = 1080p Dolby/DTS 5.1| 03 = 1080p HD Audio 7.1
#04 = 1080i Stereo Audio 2.0| 05 = 1080i Dolby/DTS 5.1| 06 = 1080i HD Audio 7.1
#07 = 3D Stereo Audio 2.0   | 08 = 3D Dolby/DTS 5.1   | 09 = 3D HD Audio 7.1
#10= 4K2K30 Stereo Audio 2.0| 11= 4K2K30 Dolby/DTS 5.1| 12= 4K2K30 HD Audio7.1
#13= DVI 1024x768           | 14= DVI 1920x1080       | 15= DVI 1920x1200
def queryEdid(vidIn):
    status = sendCommand("505654010C" + str(vidIn).zfill(2))
    return(int(status[23:25]))

#queryBeep: Returns status if beep is on or off
#FF means Off, 00 means On
def queryBeep():
    status = sendCommand("505654010B")
    return(status[23:25]) 

#queryPower: Returns status if main unit is on or off
#0F means on, F0 means off
def queryPower():
    status = sendCommand("505654080C")
    return(status[15:17]) 

#queryHPD: Returns if unit has HDMI cable connected (I think?)
#pass as integers, function will conver them to string
#FF means LOW, 00 means HIGH
def queryHPD(vidOut):
    status = sendCommand("5056540105" + str(vidOut).zfill(2))
    return(status[23:25]) 

#queryInputStatus: Returns if input port has cable connected or not
#pass as integers, function will conver them to string
def queryInputStatus(vidIn):
    base = "5056540104" + str(vidIn).zfill(2)
    status = sendCommand(base)
    return(status[23:25])

def queryDeviceType():
    status = sendCommand("5056540101000000000000CC")
    return(status[15:17])


#------------------------------------------------------------------------------#
#Helper Functions

#sendCommand: Sends the command to the unit, and returns any responses
def sendCommand(base):
    command = generateCommand(base.upper())
    ser.write(command)
    s = str(ser.read(18))
    return(s.upper())

#generateCommand: takes hex string and inserts '\x' where needed
def generateCommand(base):
    command = attachChecksum(base)
    return(bytes.fromhex(command))

#attachChecksum: takes hex string and appends the checksum, returning the result
#a needs to be a string of just the numbers
#Example: "5056540203030004"
def attachChecksum(base):
    #break string into 2 byte objects in list
    l = [base[i:i+2] for i in range(0, len(base), 2)]
    #convert values from hex to decimal
    c = [int(i, 16) for i in l]
    #sum decimal list, then modulus 256
    d = sum(c) % 256
    #convert output to hex and force format to include leading zero if needed
    checksum = format(d, '02X')
    #append base with correct number of "0"s before attaching checksum.
    base = base + ("0"*(34-len(base)))
    return(base+checksum)
