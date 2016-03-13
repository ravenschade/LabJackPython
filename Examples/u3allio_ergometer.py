# Based on u3allio.c

import sys
import time
from datetime import datetime

import u3

numChannels = 4
quickSample = 0
longSettling = 0

latestAinValues = [0] * numChannels

numIterations = 100000000

d = u3.U3()

try:
    #Configure the IOs before the test starts
    
    FIOEIOAnalog = ( 2 ** numChannels ) - 1;
    fios = FIOEIOAnalog & (0xFF)
    eios = FIOEIOAnalog/256
    
    d.configIO( FIOAnalog = fios, EIOAnalog = eios )
    
    d.getFeedback(u3.PortDirWrite(Direction = [0, 0, 0], WriteMask = [0, 0, 15]))
    
    
    feedbackArguments = []
    
    feedbackArguments.append(u3.DAC0_8(Value = 125))
    feedbackArguments.append(u3.PortStateRead())
    
    #Check if the U3 is an HV
    if d.configU3()['VersionInfo']&18 == 18:
        isHV = True
    else:
        isHV = False

    for i in range(numChannels):
        feedbackArguments.append( u3.AIN(i, 31, QuickSample = quickSample, LongSettling = longSettling ) )
    
    #print feedbackArguments

    rotation = False
    lastrotation = datetime.now()
    sum=0
    sumi=0

    myfile=open(sys.argv[1], "a")
    
    start = datetime.now()
    # Call Feedback 1000 times
    i = 0
    while i < numIterations:
        results = d.getFeedback( feedbackArguments )
        #print results
        for j in range(numChannels):
            #Figure out if the channel is low or high voltage to use the correct calibration
            if isHV == True and j < 4:
                lowVoltage = False
            else:
                lowVoltage = True
            latestAinValues[j] = d.binaryToCalibratedAnalogVoltage(results[ 2 + j ], isLowVoltage = lowVoltage, isSingleEnded = True)
        i += 1
        if latestAinValues[1]-latestAinValues[0] < 2.0:
#        if i%80== 2:
            if not rotation:
                sum=abs(sum/sumi)
                delta = datetime.now()-lastrotation
                print >> sys.stderr,"rotation",1.0/(delta.seconds+delta.microseconds/1000000.0)*60.0,sumi,sum
                delta1 = datetime.now()-start
                line=str(time.time())+" "+str(delta1.microseconds/1000000.0+delta1.seconds)+" "+str(1.0/(delta.seconds+delta.microseconds/1000000.0)*60.0)+" "+str(sum)+"\n"
                myfile.write(line)
                myfile.flush()
                lastrotation = datetime.now()
                sum=0
                sumi=0
            rotation = True
        else:
            rotation = False
        delta1 = datetime.now()-start
        sum=sum+latestAinValues[3]-latestAinValues[2]
        sumi=sumi+1
#    	print latestAinValues
	time.sleep(0.01)

finally:
    d.close()
