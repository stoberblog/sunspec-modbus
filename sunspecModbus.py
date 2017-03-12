# -*- coding: utf-8 -*-
"""
@author:         stoberblog
@detail:         This script captures data from a Fronius Primo Inverter.
                 To do this, ModBus was used.
                
@created:     Sun 29th January 2017
@modified:    Wednesday 15th Feburary 2017
@version:     0.2

@change:     
                 
@note:        This file is NOT endien safe!

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
"""

from pyModbusTCP.client import ModbusClient
import ctypes
#import time

import configuration

'''
 These classes/structures/unions, allow easy conversion between
 modbus 16bit registers and ctypes (a useful format)
'''

# Single register (16 bit) based types
class convert1(ctypes.Union):
    _fields_ = [("u16", ctypes.c_uint16),
                ("s16", ctypes.c_int16)]
    
# Two register (32 bit) based types
class x2u16Struct(ctypes.Structure):
    _fields_ = [("h", ctypes.c_uint16),
                ("l", ctypes.c_uint16)]
class convert2(ctypes.Union):
    _fields_ = [("float", ctypes.c_float),
                ("u16", x2u16Struct),
                ("sint32", ctypes.c_int32),
                ("uint32", ctypes.c_uint32)]
    
# Four register (64 bit) based types
class x4u16Struct(ctypes.Structure):
    _fields_ = [("hh", ctypes.c_uint16),
                ("hl", ctypes.c_uint16),
                ("lh", ctypes.c_uint16),
                ("ll", ctypes.c_uint16)]
class convert4(ctypes.Union):
    _fields_ = [("u16", x4u16Struct),
                ("sint64", ctypes.c_int64),
                ("uint64", ctypes.c_uint64)]


# Modbus instances
mb_inverter = ModbusClient(host=configuration.INVERTER_IP, port=configuration.MODBUS_PORT, auto_open=True, auto_close=True, timeout=configuration.MODBUS_TIMEOUT, unit_id=0) # As directly connecting to inverter, its addr is 0
mb_meter = ModbusClient(host=configuration.INVERTER_IP, port=configuration.MODBUS_PORT, auto_open=True, auto_close=True, timeout=configuration.MODBUS_TIMEOUT, unit_id=configuration.METER_ADDR) # Smart Meter unit ID (device addr) is 240




"""
#####################################################################

        Inverter Based Functions

#####################################################################
"""

"""
@brief:        Gets Sunspec ID of Inverter
@detail:       ID should be 111: Single Phase
                            112: Split Phase
                            113: Three Phase
@created:      13th Feb 2017
@return:       Sunspec ID (uint16) 
"""
def inv_SunspecID():
    regs = mb_inverter.read_holding_registers(40070-1, 1)
    return regs[0]
    #print("Inverter ID="+str(regs[0]))

"""
@brief:        Site Energy Produced so far in current day [Watt-hours] from Inverter
@created:      13th Feb 2017
@return:       Site Energy for the day (uint64) 
"""
def inv_SiteEnergyDay_Wh():
    regs = mb_inverter.read_holding_registers(502-1, 4)
    Translate=convert4()
    Translate.u16.hh = regs[3]
    Translate.u16.hl = regs[2]
    Translate.u16.lh = regs[1]
    Translate.u16.ll = regs[0]
    return Translate.uint64
    #print("Site Energy Day="+str(Translate.uint64))

"""
@brief:        Site Energy Produced so far in current year [Watt-hours] from Inverter
@created:      13th Feb 2017
@return:       Site Energy for the year (uint64) 
"""
def inv_SiteEnergyYear_Wh():
    regs = mb_inverter.read_holding_registers(506-1, 4)
    Translate=convert4()
    Translate.u16.hh = regs[3]
    Translate.u16.hl = regs[2]
    Translate.u16.lh = regs[1]
    Translate.u16.ll = regs[0]
    return Translate.uint64
    #print("Site Energy Year="+str(Translate.uint64))

"""
@brief:        Instantanious Site Energy Total Produced [Watt-hours] from Inverter
@created:      13th Feb 2017
@return:       Site Energy Total Produced (uint64) 
"""
def inv_SiteEnergyTotal_Wh():
    regs = mb_inverter.read_holding_registers(510-1, 4)
    Translate=convert4()
    Translate.u16.hh = regs[3]
    Translate.u16.hl = regs[2]
    Translate.u16.lh = regs[1]
    Translate.u16.ll = regs[0]
    return Translate.uint64
    #print("Site Energy Total="+str(Translate.uint64))

"""
@brief:        Instantanious Site Power [Watts] from Inverter
@created:      13th Feb 2017
@return:       Current Site Power (uint32) 
"""
def inv_SitePower_W():
    regs = mb_inverter.read_holding_registers(500-1, 2)
    Translate=convert2()
    Translate.u16.h = regs[1]
    Translate.u16.l = regs[0]
    return Translate.uint32
    #print("Site Power="+str(Translate.uint32))


"""
@brief:        Gets Max Power Factor of Inverter
@created:      14th Feb 2017
@return:       Max Power Factor (int16) 
"""
def inv_getMaxPowerFactor_cos():
    Translate=convert1()
    TranslateScale=convert1()
    regs = mb_inverter.read_holding_registers(40248-1, 1)
    scale = mb_inverter.read_holding_registers(40262-1, 1) # Sunssf Scale factor
    TranslateScale.u16 = scale[0]
    Translate.u16=regs[0]
    maxPF=Translate.s16*(10**(TranslateScale.s16))
    return maxPF
    #print("Inverter ID="+str(maxPf))


"""
@brief:        Min Power Factor in Quadrent 1 of Inverter
@created:      14th Feb 2017
@return:       Max Power Factor in Q1 (int16) 
"""
def inv_getMinPowerFactorQ1_cos():
    Translate=convert1()
    TranslateScale=convert1()
    regs = mb_inverter.read_holding_registers(40173-1, 1)
    scale = mb_inverter.read_holding_registers(40189-1, 1) # Sunssf Scale factor
    TranslateScale.u16 = scale[0]
    Translate.u16=regs[0]
    minPF=Translate.s16*(10**(TranslateScale.s16))
    return minPF
    #print("Min Power Factor in Quadrent 1="+str(regs[0]))
    
"""
@brief:        Min Power Factor in Quadrent 4 of Inverter
@created:      14th Feb 2017
@return:       Max Power Factor in Q4 (int16) 
"""
def inv_getMinPowerFactorQ4_cos():
    Translate=convert1()
    TranslateScale=convert1()
    regs = mb_inverter.read_holding_registers(40173-1, 1)
    scale = mb_inverter.read_holding_registers(40189-1, 1) # Sunssf Scale factor
    TranslateScale.u16 = scale[0]
    Translate.u16=regs[0]
    minPF=Translate.s16*(10**(TranslateScale.s16))
    return minPF
    #print("Min Power Factor in Quadrent 4="+str(regs[0]))


"""
@brief:        Instantanious Total AC Current being Produced [Amps] from Inverter
@created:      13th Feb 2017
@return:       Current Site Power (float32) 
"""
def inv_ACCurrentTotal_A():
    regs = mb_inverter.read_holding_registers(40072-1, 2)
    Translate=convert2()
    Translate.u16.h = regs[1]
    Translate.u16.l = regs[0]
    return Translate.float
    #print("AC Total Current="+str(Translate.float))


"""
@brief:        Instantanious AC Power being Produced [Amps] from Inverter
@details:      This will be the same as site equivilent when only one inverter
@created:      13th Feb 2017
@return:       Current AC Power (float32) 
"""
def inv_ACPower_W():
    regs = mb_inverter.read_holding_registers(40092-1, 2)
    Translate=convert2()
    Translate.u16.h = regs[1]
    Translate.u16.l = regs[0]
    return Translate.float
    #print("AC Power="+str(Translate.float))
    
"""
@brief:        Instantanious Frequency being producted for AC Output [Hz] at the Inverter
@detail:       Will be zero(0) when not producing
@created:      13th Feb 2017
@return:       Current AC Frequency (float32) 
"""
def inv_ACFreq_Hz():
    regs = mb_inverter.read_holding_registers(40094-1, 2)
    Translate=convert2()
    Translate.u16.h = regs[1]
    Translate.u16.l = regs[0]
    return Translate.float
    #print("AC Frequency="+str(Translate.float))
    
"""
@brief:        Instantanious AC Apparent Power being Produced [VA] from Inverter
@created:      13th Feb 2017
@return:       Current AC Power (float32)
"""
def inv_ACAppPwr_VA():
    regs = mb_inverter.read_holding_registers(40096-1, 2)
    Translate=convert2()
    Translate.u16.h = regs[1]
    Translate.u16.l = regs[0]
    return Translate.float
    #print("AC Apparent Power="+str(Translate.float))
    
"""
@brief:        Instantanious AC Reactive Power being Produced [VAr] from Inverter
@created:      13th Feb 2017
@return:       Current AC Power (float32)
"""
def inv_ACReacPwr_VAr():
    regs = mb_inverter.read_holding_registers(40098-1, 2)
    Translate=convert2()
    Translate.u16.h = regs[1]
    Translate.u16.l = regs[0]
    return Translate.float
    #print("AC Reactive Power="+str(Translate.float))

"""
@brief:        Instantanious AC Power Factor being Produced [%] from Inverter
@created:      13th Feb 2017
@return:       Current AC Power Factor (float32)
"""
def inv_ACPF_percent():
    regs = mb_inverter.read_holding_registers(40100-1, 2)
    Translate=convert2()
    Translate.u16.h = regs[1]
    Translate.u16.l = regs[0]
    return Translate.float
    #print("AC Power Factor="+str(Translate.float))

"""
@brief:        Instantanious DC Power Total being Produced [Watts] from Inverter
@detail:       This is a total, so it sums power from individual strings
@created:      13th Feb 2017
@return:       Current DC String Power Total (float32)
"""
def inv_DCPwr_W():
    regs = mb_inverter.read_holding_registers(40108-1, 2)
    Translate=convert2()
    Translate.u16.h = regs[1]
    Translate.u16.l = regs[0]
    return Translate.float
    #print("DC String Power Total="+str(Translate.float))

"""
@brief:        Gets the time which is set on the inverter [seconds] from Inverter
@detail:       The Inverter actually sends this as seconds since 1/1/2000 00:00UTC.
               This function, converts this to epoch time (unix time) for ease of use.
               
@todo:         This needs to checked if sent in UTC or local time
@created:      13th Feb 2017
@return:       Current Inverter Time (uint32) 
"""
def inv_Time_s():
    regs = mb_inverter.read_holding_registers(40233-1, 2)
    
    Translate=convert2()
    Translate.u16.h = regs[1]
    Translate.u16.l = regs[0]
    epoch = Translate.uint32+946684800 # Add seconds between 1/1/1970 and 1/1/2000 
    return epoch
    #SampleTime = time.gmtime(epoch)
    #print("Time: "+time.strftime('%d-%m-%Y %H:%M:%S',SampleTime))


"""
@brief:        String 1 DC Current
@created:      14th Feb 2017
@return:       DC Current for String 1 (uint16) 
"""
def inv_DCs1Current_A():
    Translate=convert1()
    TranslateScale=convert1()
    regs = mb_inverter.read_holding_registers(40283-1, 1)
    scale = mb_inverter.read_holding_registers(40266-1, 1) # Sunssf Scale factor
    TranslateScale.u16 = scale[0]
    Translate.u16=regs[0]
    DCcurrent=Translate.s16*(10**(TranslateScale.s16))
    return DCcurrent
    #print("DC Current for String 1="+str(regs[0]))
    
"""
@brief:        String 2 DC Current
@created:      14th Feb 2017
@return:       DC Current for String 2 (uint16) 
"""
def inv_DCs2Current_A():
    Translate=convert1()
    TranslateScale=convert1()
    regs = mb_inverter.read_holding_registers(40303-1, 1)
    scale = mb_inverter.read_holding_registers(40266-1, 1) # Sunssf Scale factor
    TranslateScale.u16 = scale[0]
    Translate.u16=regs[0]
    DCcurrent=Translate.s16*(10**(TranslateScale.s16))
    return DCcurrent
    #print("DC Current for String 2="+str(regs[0]))

"""
@brief:        String 1 DC Voltage
@created:      14th Feb 2017
@return:       DC Voltage for String 1 (uint16) 
"""
def inv_DCs1Voltage_V():
    Translate=convert1()
    TranslateScale=convert1()
    regs = mb_inverter.read_holding_registers(40284-1, 1)
    scale = mb_inverter.read_holding_registers(40267-1, 1) # Sunssf Scale factor
    TranslateScale.u16 = scale[0]
    Translate.u16=regs[0]
    DCcurrent=Translate.s16*(10**(TranslateScale.s16))
    return DCcurrent
    #print("DC Voltage for String 1="+str(regs[0]))

"""
@brief:        String 2 DC Voltage
@created:      14th Feb 2017
@return:       DC Voltage for String 2 (uint16) 
"""
def inv_DCs2Voltage_V():
    Translate=convert1()
    TranslateScale=convert1()
    regs = mb_inverter.read_holding_registers(40304-1, 1)
    scale = mb_inverter.read_holding_registers(40267-1, 1) # Sunssf Scale factor
    TranslateScale.u16 = scale[0]
    Translate.u16=regs[0]
    DCcurrent=Translate.s16*(10**(TranslateScale.s16))
    return DCcurrent
    #print("DC Voltage for String 2="+str(regs[0]))
    
"""
@brief:        String 1 DC Power
@created:      14th Feb 2017
@return:       DC Power for String 1 (uint16) 
"""
def inv_DCs1Power_W():
    Translate=convert1()
    TranslateScale=convert1()
    regs = mb_inverter.read_holding_registers(40285-1, 1)
    scale = mb_inverter.read_holding_registers(40268-1, 1) # Sunssf Scale factor
    TranslateScale.u16 = scale[0]
    Translate.u16=regs[0]
    DCcurrent=Translate.s16*(10**(TranslateScale.s16))
    return DCcurrent
    #print("DC Power for String 1="+str(regs[0]))
    
"""
@brief:        String 2 DC Power
@created:      14th Feb 2017
@return:       DC Power for String 2 (uint16) 
"""
def inv_DCs2Power_W():
    Translate=convert1()
    TranslateScale=convert1()
    regs = mb_inverter.read_holding_registers(40305-1, 1)
    scale = mb_inverter.read_holding_registers(40268-1, 1) # Sunssf Scale factor
    TranslateScale.u16 = scale[0]
    Translate.u16=regs[0]
    DCcurrent=Translate.s16*(10**(TranslateScale.s16))
    return DCcurrent
    #print("DC Power for String 2="+str(regs[0]))
    

"""
#####################################################################

        Smart Meter Measurements

#####################################################################
"""


"""
@brief:        Gets Sunspec ID of Smart Meter
@detail:       ID should be 211: Single Phase
                            212: Split Phase
                            213: Three Phase
@created:      14th Feb 2017
@return:       Sunspec ID (uint16) 
"""
def mtr_SunspecID():
    regs = mb_meter.read_holding_registers(40070-1, 1)
    return regs[0]
    #print("Inverter ID="+str(regs[0]))


"""
@brief:        Instantanious Total AC Current at Feed-in Point [Amps] via Smart Meter
@detail:       For three-phase, this is sum of all phases
               Positive is inwards (from grid), negative is outwards (to grid)
@created:      14th Feb 2017
@return:       Instantanious AC Current (float32) 
"""
def mtr_ACCurrentTotal_A():
    regs = mb_meter.read_holding_registers(40072-1, 2)
    Translate=convert2()
    Translate.u16.h = regs[1]
    Translate.u16.l = regs[0]
    return Translate.float
    #print("Feed-in AC Current="+str(Translate.float))

"""
@brief:        Instantanious AC Voltage at Feed-in Point [Volts] via Smart Meter
@detail:       For three-phase, this is average phase-to-neutral voltage
@created:      14th Feb 2017
@return:       Instantanious AC Voltage (float32) 
"""
def mtr_ACVoltageAverage_V():
    regs = mb_meter.read_holding_registers(40080-1, 2)
    Translate=convert2()
    Translate.u16.h = regs[1]
    Translate.u16.l = regs[0]
    return Translate.float
    #print("Feed-in AC Voltage="+str(Translate.float))

"""
@brief:        Instantanious AC Frequency at Feed-in Point [Volts] via Smart Meter
@created:      14th Feb 2017
@return:       Instantanious AC Frequency (float32) 
"""
def mtr_ACFreq_Hz():
    regs = mb_meter.read_holding_registers(40096-1, 2)
    Translate=convert2()
    Translate.u16.h = regs[1]
    Translate.u16.l = regs[0]
    return Translate.float
    #print("Feed-in AC Frequency="+str(Translate.float))

"""
@brief:        Instantanious Total AC Power at Feed-in Point [Watts] via Smart Meter
@detail:       For three-phase, this is sum of all phases
               Positive is inwards (from grid), negative is outwards (to grid)
@created:      14th Feb 2017
@return:       Instantanious AC Power (float32) 
"""
def mtr_ACPowerTotal_W():
    regs = mb_meter.read_holding_registers(40098-1, 2)
    Translate=convert2()
    Translate.u16.h = regs[1]
    Translate.u16.l = regs[0]
    return Translate.float
    #print("Feed-in AC Power="+str(Translate.float))

"""
@brief:        Instantanious Total AC Apparent Power at Feed-in Point [Volt-Amps] 
                via Smart Meter
@detail:       For three-phase, this is sum of all phases
               Positive is inwards (from grid), negative is outwards (to grid)
@created:      14th Feb 2017
@return:       Instantanious AC Apparent Power (float32) 
"""
def mtr_ACAppPowerTotal_VA():
    regs = mb_meter.read_holding_registers(40106-1, 2)
    Translate=convert2()
    Translate.u16.h = regs[1]
    Translate.u16.l = regs[0]
    return Translate.float
    #print("Feed-in AC Apparent Power="+str(Translate.float))
    
"""
@brief:        Instantanious Total AC Reactive Power at Feed-in Point 
                [Volt-Amps reactive] via Smart Meter
@detail:       For three-phase, this is sum of all phases
               Positive is inwards (from grid), negative is outwards (to grid)
@created:      14th Feb 2017
@return:       Instantanious AC reactive Power (float32) 
"""
def mtr_ACReacPowerTotal_VAr():
    regs = mb_meter.read_holding_registers(40114-1, 2)
    Translate=convert2()
    Translate.u16.h = regs[1]
    Translate.u16.l = regs[0]
    return Translate.float
    #print("Feed-in AC Reactive Power="+str(Translate.float))
    
"""
@brief:        Instantanious Average AC Power Factor at Feed-in Point [Percentage]
                via Smart Meter
@detail:       For three-phase, this is an average of all phases
               Positive is capacitive, negative is inductive
@created:      14th Feb 2017
@return:       Instantanious AC Power Factor (float32) 
"""
def mtr_ACPFAverage_cos():
    regs = mb_meter.read_holding_registers(40122-1, 2)
    Translate=convert2()
    Translate.u16.h = regs[1]
    Translate.u16.l = regs[0]
    return Translate.float
    #print("Feed-in AC Power Factor="+str(Translate.float))
    
"""
@brief:        Instantanious Total Watt-hours Exported [Watt-hours] via Smart Meter
@detail:       For three-phase, this is an average of all phases
                This is total over life of meter
                it may overflow however and start from zero if enough production
@created:      14th Feb 2017
@return:       Total Watt-hours Exported (uint32) 
"""
def mtr_ACTotalWattHoursExp_Wh():
    regs = mb_meter.read_holding_registers(40130-1, 2)
    Translate=convert2()
    Translate.u16.h = regs[1]
    Translate.u16.l = regs[0]
    return Translate.uint32
    #print("Total Watt-hours Exported="+str(Translate.uint32))

"""
@brief:        Instantanious Total Watt-hours Imported [Watt-hours] via Smart Meter
@detail:       For three-phase, this is an average of all phases
                This is total over life of meter
                it may overflow however and start from zero if enough production
@created:      14th Feb 2017
@return:       Total Watt-hours Imported (uint32) 
"""
def mtr_ACTotalWattHoursImp_Wh():
    regs = mb_meter.read_holding_registers(40138-1, 2)
    Translate=convert2()
    Translate.u16.h = regs[1]
    Translate.u16.l = regs[0]
    return Translate.uint32
    #print("Total Watt-hours Imported="+str(Translate.uint32))

"""
@brief:        Instantanious Total VA-hours Exported [VA-hours] via Smart Meter
@detail:       For three-phase, this is an average of all phases
                This is total over life of meter
                it may overflow however and start from zero if enough production
@created:      14th Feb 2017
@return:       Total VA-hours Exported (uint32) 
"""
def mtr_ACTotalVAHoursExp_Wh():
    regs = mb_meter.read_holding_registers(40146-1, 2)
    Translate=convert2()
    Translate.u16.h = regs[1]
    Translate.u16.l = regs[0]
    return Translate.uint32
    #print("Total VA-hours Exported="+str(Translate.uint32))

"""
@brief:        Instantanious Total VA-hours Imported [VA-hours] via Smart Meter
@detail:       For three-phase, this is an average of all phases
                This is total over life of meter
                it may overflow however and start from zero if enough production
@created:      14th Feb 2017
@return:       Total VA-hours Imported (uint32) 
"""
def mtr_ACTotalVAHoursImp_Wh():
    regs = mb_meter.read_holding_registers(40154-1, 2)
    Translate=convert2()
    Translate.u16.h = regs[1]
    Translate.u16.l = regs[0]
    return Translate.uint32
    #print("Total VA-hours Imported="+str(Translate.uint32))


"""
#####################################################################

        Modbus Error/Exception Functions

#####################################################################
"""

"""
@brief:        Last Error on Inverter Modbus Communication
@created:      15th Feb 2017
@return:       Error Codes see http://www.modbusdriver.com/doc/libmbusmaster/group__buserror.html                  
"""
def inv_lastError():
    return mb_inverter.last_error()

"""
@brief:        Last Except on Inverter Modbus Communication
@created:      15th Feb 2017
@return:       Codes see http://modbus.org/docs/PI_MBUS_300.pdf
"""
def inv_lastExcept():
    return mb_inverter.last_except()

"""
@brief:        Last Error on Smart Meter Modbus Communication
@created:      15th Feb 2017
@return:       Error Codes see http://www.modbusdriver.com/doc/libmbusmaster/group__buserror.html                  
"""
def mtr_lastError():
    return mb_meter.last_error()

"""
@brief:        Last Except on Smart Meter Modbus Communication
@created:      15th Feb 2017
@return:       Codes see http://modbus.org/docs/PI_MBUS_300.pdf
"""
def mtr_lastExcept():
    return mb_meter.last_except()





# Test Prints
"""

"""

