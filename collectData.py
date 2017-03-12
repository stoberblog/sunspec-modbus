# -*- coding: utf-8 -*-
"""
@author:         stoberblog
@detail:         This is the main script for the Fronius
                 MODbus project. It calls the read functions,
                 and then sends them to a database
                
@created:     Thurs 16th Feburary 2017
@modified:    Saturday 25th Feburary 2017
@version:     0.1

@change:      

@license:     MIT License

                Copyright (c) 2017 stoberblog
                
                Permission is hereby granted, free of charge, to any person obtaining a copy
                of this software and associated documentation files (the "Software"), to deal
                in the Software without restriction, including without limitation the rights
                to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
                copies of the Software, and to permit persons to whom the Software is
                furnished to do so, subject to the following conditions:
                
                The above copyright notice and this permission notice shall be included in all
                copies or substantial portions of the Software.
                
                THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
                IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
                FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
                AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
                LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
                OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
                SOFTWARE.
                
@todo:        Database Library?
              Abort on not being able to connect to database
              Use Configuartion log level
              Give more logging output
              Viewer session cleaner (viewerFunctions.py)
              
                
"""

import database
import sunspecModbus
import configuration



# Multithreading support so can stop acquistion softly
import threading
import signal
import math
import datetime
import sys
import time # For sleep

from enum import Enum

class ErrorLevels(Enum):
    FATAL   = 1
    ERROR   = 2
    NOTICE  = 3
    DEBUG   = 4

class Device(Enum):
    INVERTER     = 1
    METER        = 2


stopAcquistion = False # Variable used to gracefully shutdown script
sleeping = False # Variable used to gracefully shutdown script

"""
@brief:        When program told to terminate, do so gracefully
@created:      25th Feb 2017
@return:       none 
"""
def sigterm_handler(_signo, _stack_frame):
    print("Termination signal recieved. Shutting down")
    global stopAcquistion
    global sleeping

    stopAcquistion = True
    while progThread.is_alive(): # Wait until thread has closed
        if sleeping == True:
            break
        pass
    sys.exit()

"""
@brief:        Check the config has valid values
@created:      25th Feb 2017
@return:       none 
"""
def configCheck():
    #First check interval
    if not (configuration.SCHED_INTERVAL >= 1):
        print("Invalid Sampling (scheduler) interval")
        sys.exit()
    if not (configuration.POW_THERESHOLD >= 1):
        print("Invalid Power Threshold")
        sys.exit()
    '''
    if isinstance(configuration.MODBUS_PORT, int ):
        print("Invalid Modbus Port")
        sys.exit()
    if isinstance(configuration.METER_INSTALLED, bool ):
        print("Meter Instalation config not stated")
        sys.exit()
    if configuration.METER_INSTALLED == True:
        if isinstance(configuration.METER_ADDR, int ):
            print("Invalid Modbus Port")
            sys.exit()
        if isinstance(configuration.METER_ADDR, int ):
            print("Invalid Modbus meter Address")
            sys.exit()
    '''
"""
@brief:        Main loop that fires of capture at predefined intervals
@created:      18th Feb 2017
@return:       none 
"""
def scheduler():
    global sleeping
    while stopAcquistion == False:
        capture()
        # The scheduler uses local time regardless of settings currently
        sleeping = True
        time.sleep(((configuration.SCHED_INTERVAL-1)- datetime.datetime.now().minute % configuration.SCHED_INTERVAL)*60+(60-datetime.datetime.now().second))
        sleeping = False
        
"""
 @brief:     Structure to store captured data in
"""
captureData=database.interval_struct()


"""
@brief:        Aquires modbus data, and sends to database
@created:      18th Feb 2017
@return:       none 
"""
def capture():
    database.openConnection()
    #database.logMsg(ErrorLevels.NOTICE.value,"Woken up at "+str(datetime.datetime.now().strftime('%H:%M:%S on %d/%m/%Y')))
    #print("Woken up at "+datetime.datetime.now().strftime('%H:%M:%S on %d/%m/%Y')+", current epoch "+str(int(time.time())))
    if configuration.EPOCH_INVERTER == False:
        captureData.epoch = int(time.time()) # epoch Time in UTC. Based off computer time
    else:
        captureData.epoch = sunspecModbus.inv_Time_s() # epoch Time in UTC. Based off inverter time
        errorModbus(Device.INVERTER, "inv_Time_s()")
    captureData.DC_s1_v = sunspecModbus.inv_DCs1Voltage_V() # (int32)
    if errorModbus(Device.INVERTER, "inv_DCs1Voltage_V()"):
        captureData.DC_s1_v = 0
    captureData.DC_s2_v = sunspecModbus.inv_DCs2Voltage_V() # (int32)
    if errorModbus(Device.INVERTER, "inv_DCs2Voltage_V()"):
        captureData.DC_s2_v = 0
    captureData.pf_inv = sunspecModbus.inv_ACPF_percent()/100 # (float)
    if errorModbus(Device.INVERTER, "inv_ACPF_percent()") or math.isnan(captureData.pf_inv):
        captureData.pf_inv = 0.0
    captureData.pow_prod = sunspecModbus.inv_ACPower_W() # (float)
    if errorModbus(Device.INVERTER, "inv_ACPower_W()") or math.isnan(captureData.pow_prod):
        captureData.pow_prod = 0.0    
    captureData.eng_tot_prod = sunspecModbus.inv_SiteEnergyTotal_Wh() # (uint64)
    if errorModbus(Device.INVERTER, "inv_SiteEnergyTotal_Wh()"):
        captureData.eng_tot_prod = 0
    captureData.cur_inv = sunspecModbus.inv_ACCurrentTotal_A() # (float)
    if errorModbus(Device.INVERTER, "inv_ACCurrentTotal_A()") or math.isnan(captureData.cur_inv):
        captureData.cur_inv = 0.0
        
    if configuration.METER_INSTALLED == True:
        captureData.pf_feed = sunspecModbus.mtr_ACPFAverage_cos() # (float)
        if errorModbus(Device.METER, "mtr_ACPFAverage_cos()") or math.isnan(captureData.pf_feed):
            captureData.pf_feed = 0.0
        captureData.pow_feed = sunspecModbus.mtr_ACPowerTotal_W() # (float)
        if errorModbus(Device.METER, "mtr_ACPowerTotal_W()") or math.isnan(captureData.pow_feed):
            captureData.pow_feed = 0.0
        captureData.eng_tot_out = sunspecModbus.mtr_ACTotalWattHoursExp_Wh() # (uint32)
        if errorModbus(Device.METER, "mtr_ACTotalWattHoursExp_Wh()"):
            captureData.eng_tot_out = 0
        captureData.eng_tot_in = sunspecModbus.mtr_ACTotalWattHoursImp_Wh() # (uint32)
        if errorModbus(Device.METER, "mtr_ACTotalWattHoursImp_Wh()"):
            captureData.eng_tot_in = 0
        captureData.volt_feed = sunspecModbus.mtr_ACVoltageAverage_V() # (float)
        if errorModbus(Device.METER, "mtr_ACVoltageAverage_V()") or math.isnan(captureData.volt_feed):
            captureData.volt_feed = 0.0
    else:
        captureData.pf_feed = 0.0
        captureData.pow_feed = 0.0
        captureData.eng_tot_out = 0
        captureData.eng_tot_in = 0
        captureData.volt_feed = 0.0
        
    
    database.storeInterval(captureData)
    
    
    
    if configuration.EPOCH_INVERTER == False:
        testTime = captureData.epoch
    else:
        testTime =time.time()
    
    # Check to see if should sample/calculate Daily data
    # Maybe use an if statement to select if use computer time or inverter
    if (time.localtime(testTime).tm_wday) != (time.localtime(testTime+configuration.SCHED_INTERVAL*60+1).tm_wday):
        # We will be changing day soon, collect daily stats here!
        database.logMsg(ErrorLevels.NOTICE.value,"Running Daily Sample")
        dailyData()
    
    #print("\t\tSeconds to next capture: "+str(((configuration.SCHED_INTERVAL-1)- datetime.datetime.now().minute % configuration.SCHED_INTERVAL)*60+(60-datetime.datetime.now().second) ))

    database.closeConnection()
    #print()
    

"""
@brief:        Aquire or calculate data, and sends to database
@created:      19th Feb 2017
@return:       none 
"""
def dailyData():
    captureDay=database.daily_struct()
    
    captureDay.error_flag          = 0
    if configuration.EPOCH_INVERTER == False:
        captureDay.epoch = int(time.time()) # epoch Time in UTC. Based off computer time
    else:
        captureDay.epoch = sunspecModbus.inv_Time_s() # epoch Time in UTC. Based off inverter time
        errorModbus(Device.INVERTER, "inv_Time_s()")
    
    captureDay.eng_day = sunspecModbus.inv_SiteEnergyDay_Wh() # (float)
    if errorModbus(Device.INVERTER, "inv_SiteEnergyDay_Wh()") or math.isnan(captureDay.eng_day):
        captureDay.eng_day = 0.0
        captureDay.error_flag = 1
    captureDay.eng_tot_prod = sunspecModbus.inv_SiteEnergyTotal_Wh() # (uint32)
    if errorModbus(Device.METER, "inv_SiteEnergyTotal_Wh()"):
        captureDay.eng_tot_prod = 0
        captureDay.error_flag = 1
    if configuration.METER_INSTALLED == True:
        captureDay.eng_tot_out = sunspecModbus.mtr_ACTotalWattHoursExp_Wh() # (uint32)
        if errorModbus(Device.METER, "mtr_ACTotalWattHoursExp_Wh()"):
            captureDay.eng_tot_out = 0
            captureDay.error_flag = 1
        captureDay.eng_tot_in = sunspecModbus.mtr_ACTotalWattHoursImp_Wh() # (uint32)
        if errorModbus(Device.METER, "mtr_ACTotalWattHoursImp_Wh()"):
            captureDay.eng_tot_in = 0
            captureDay.error_flag = 1
    
        powFeedArray = database.getPowEpoch(time.time()-86400, time.time())
        thresholdIDrise=-1
        thresholdIDfall=-1
        captureDay.thres_rise_epoch=0
        for i in range (0,len(powFeedArray)-1):
            if (powFeedArray[i][3] >= configuration.POW_THERESHOLD):
                captureDay.thres_rise_epoch=powFeedArray[i][1]
                thresholdIDrise=i
                break
        captureDay.thres_fall_epoch=0
        for i in range (0,len(powFeedArray)-1):
            if (powFeedArray[len(powFeedArray)-1-i][3] >= configuration.POW_THERESHOLD):
                captureDay.thres_fall_epoch=powFeedArray[len(powFeedArray)-1-i][1]
                thresholdIDfall=len(powFeedArray)-1-i
                break
        
        powFeedOutCount = 0
        if thresholdIDrise >= 0 and thresholdIDfall >= 0:
            for i in range(thresholdIDrise,thresholdIDfall):
                if powFeedArray[i][2] < 0:
                    powFeedOutCount = powFeedOutCount+1
            captureDay.thres_perc_exp = float(powFeedOutCount/(thresholdIDfall-thresholdIDrise))
    
        captureDay.pow_max = database.maria_getMaxProduced(captureDay.thres_rise_epoch, captureDay.thres_fall_epoch) [0][0]
    
    else: # Not using smart meter, so set values to zero
            captureDay.eng_tot_out = 0
            captureDay.eng_tot_in = 0
            captureDay.pow_max = 0
            captureDay.thres_perc_exp = 0
            captureDay.thres_fall_epoch=0
            captureDay.thres_fall_epoch=0
    
    database.storeDaily(captureDay) #send to database
    

"""
@brief:        Checks if there was an error during datacollection
@detail:        Checks if there was an error during data collection,
                and if there was an error, log it.
@created:      18th Feb 2017
@param:        Device 
@param:        String containing called function
@return:        Flase when no error
                True when error
"""
def errorModbus(modbusDevice, function):
    if modbusDevice == Device.INVERTER:
        errorNo=sunspecModbus.inv_lastError()
    elif modbusDevice == Device.METER:
        errorNo=sunspecModbus.mtr_lastError()
    else:
        return(-1)
    if errorNo != 0:
        database.logMsg(ErrorLevels.ERROR.value,str(function)+" failure")
        #print("** There was an error when using function "+str(function))
        return True
    else:
        return False
        
        
        
        
"""
@brief:        This is where the script body starts
"""        
print("Sunspec Modbus Script")
configCheck()
progThread = threading.Thread(target=scheduler)
signal.signal(signal.SIGTERM, sigterm_handler)
signal.signal(signal.SIGINT, sigterm_handler)

progThread.deamon = False
progThread.start()
    