# -*- coding: utf-8 -*-
"""
@author:         stoberblog
@detail:         Functions in this file deal with storing and retrieval
                 of data to a database. Generic functions are used for
                 abstraction, allowing ease to change database backend.
                
@created:     Friday 17th Feburary 2017
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

"""
import gc # Garbage collection - Clean close of database
import time 

import configuration
if configuration.DATABASE_TYPE == "mariadb":
    import mysql.connector as mariadb


class interval_struct:
    epoch       = 0
    DC_s1_v     = 0.0
    DC_s2_v     = 0.0
    pf_feed     = 0.0
    pf_inv      = 0.0
    pow_prod    = 0.0
    pow_feed    = 0.0
    eng_tot_prod= 0
    eng_tot_out = 0
    eng_tot_in  = 0
    volt_feed   = 0.0
    cur_inv     = 0.0
    freq_feed = 50.0

class daily_struct:
    epoch               = 0
    thres_rise_epoch    = 0
    thres_fall_epoch    = 0
    thres_perc_exp      = 0.0
    pow_max             = 0.0
    eng_day             = 0
    eng_tot_prod        = 0
    eng_tot_out         = 0
    eng_tot_in          = 0
    error_flag          = 0

class log_struct:
    epoch   = 0
    level   = 0
    message = ''


databaseCursor = None
databaseConnection = None

"""
@brief:         Open connection to database
@created:       18th Feb 2017
@return:        True: Success
                False: Failed
"""
def openConnection():
    if configuration.DATABASE_TYPE == "mariadb":
        return maria_Open()
    else:
        return True

"""
@brief:         Close connection to database
@created:       18th Feb 2017
@return:        True: Success
                False: Failed
"""
def closeConnection():
    if configuration.DATABASE_TYPE == "mariadb":
        return maria_Close()
    else:
        return True

"""
@brief:         Store Interval Data to database
@created:       18th Feb 2017
@return:        True: Success
                False: Failed
"""
def storeInterval(dataStructure):
    if configuration.DATABASE_TYPE == "mariadb":
        return maria_storeInterval(dataStructure)
    else:
        return False
    

"""
@brief:         Store Daily Data to database
@created:       19th Feb 2017
@return:        True: Success
                False: Failed
"""
def storeDaily(dataStructure):
    if configuration.DATABASE_TYPE == "mariadb":
        return maria_storeDaily(dataStructure)
    else:
        return False
    
    
    
"""
@brief:         Get feed in power from interval database, with a specified time
@created:       18th Feb 2017
@return:        None: Failure
                array: retuned data, in rows of [id, epoch, pow_feed]
"""
def getPowEpoch(epochStart, epochEnd):
    if configuration.DATABASE_TYPE == "mariadb":
        return maria_getPowEpoch(epochStart, epochEnd)
    else:
        return None



"""
@brief:         Get the maximum produced energy with a time period
@created:       18th Feb 2017
@return:        None: Failure
                array: retuned maximum
"""
def getMaxProduced(epochStart, epochEnd):
    if configuration.DATABASE_TYPE == "mariadb":
        return maria_getMaxProduced(epochStart, epochEnd)
    else:
        return None

"""
@brief:         Log to database
@created:       25th Feb 2017
@return:        None: Failure
"""
def logMsg(level, message):
    if configuration.DATABASE_TYPE == "mariadb":
        maria_logMsg(level, message)
    else:
        return None




"""
#####################################################################

        Maria DB / MySQL

#####################################################################
"""
"""
@brief:         Open connection to database
@created:       18th Feb 2017
@return:        True: Success
                False: Failed
"""
def maria_Open():
    global databaseConnection
    global databaseCursor
    databaseConnection = mariadb.connect(user=configuration.DATABASE_USER, password=configuration.DATABASE_PASSWD, database=configuration.DATABASE_DB)
    databaseCursor = databaseConnection.cursor(buffered=True)
    # a try and catch are needed here
    return True

"""
@brief:         Close connection to database
@created:       18th Feb 2017
@return:        True: Success
                False: Failed
"""
def maria_Close():
    ret=databaseConnection.close()
    gc.collect() # Garbage collection - https://ianhowson.com/blog/a-quick-guide-to-using-mysql-in-python/
    return ret
    
"""
@brief:         Store Interval Data to database
@created:       18th Feb 2017
@return:        True: Success
                False: Failed
"""
def maria_storeInterval(dataStructure):
    if not hasattr(dataStructure, 'epoch'):
        return False
    try:        
        databaseCursor.execute("INSERT INTO `interval` (epoch,DC_s1_v,DC_s2_v,pf_feed,pf_inv,pow_prod,pow_feed,eng_tot_prod,eng_tot_out,eng_tot_in,volt_feed,cur_inv,freq_feed) VALUES ("+
                           str(dataStructure.epoch)+","+str(dataStructure.DC_s1_v)+","+str(dataStructure.DC_s2_v)+","+str(dataStructure.pf_feed)+","+str(dataStructure.pf_inv)+","+str(dataStructure.pow_prod)+","+
                            str(dataStructure.pow_feed)+","+str(dataStructure.eng_tot_prod)+","+str(dataStructure.eng_tot_out)+","+str(dataStructure.eng_tot_in)+","+
                            str(dataStructure.volt_feed)+","+str(dataStructure.cur_inv)+","+str(dataStructure.freq_feed)+")")
            
    except mariadb.Error as error:
        print("Error: {}".format(error))
        return False
    databaseConnection.commit()
    return True
    
    
"""
@brief:         Store Daily Data to database
@created:       18th Feb 2017
@return:        True: Success
                False: Failed
"""
def maria_storeDaily(dataStructure):
    if not hasattr(dataStructure, 'epoch'):
        return False
    try:        
        databaseCursor.execute("INSERT INTO `daily` (epoch,thres_rise_epoch,thres_fall_epoch,thres_perc_exp,pow_max,eng_day,eng_tot_prod,eng_tot_out,eng_tot_in,error_flag) VALUES ("+
                           str(dataStructure.epoch)+","+str(dataStructure.thres_rise_epoch)+","+str(dataStructure.thres_fall_epoch)+","+str(dataStructure.thres_perc_exp)+","+str(dataStructure.pow_max)+","+str(dataStructure.eng_day)+","+
                            str(dataStructure.eng_tot_prod)+","+str(dataStructure.eng_tot_out)+","+str(dataStructure.eng_tot_in)+","+str(dataStructure.error_flag)+")")
    except mariadb.Error as error:
        print("Error: {}".format(error))
        return False
    databaseConnection.commit()
    return True


"""
@brief:         Log Message to database
@created:       18th Feb 2017
@return:        True: Success
                False: Failed
"""
def maria_logMsg(level, message):
    try:
        databaseCursor.execute( "INSERT INTO `log` (`epoch`,`level`,`message`) VALUES ("+str(time.time())+","+str(level)+",\""+str(message)+"\")" )
    except mariadb.Error as error:
        print("Error: {}".format(error))
        return False
    databaseConnection.commit()
    return True


"""
@brief:         Get feed in power from interval database, with a specified time
@created:       18th Feb 2017
@return:        None: Failure
                array: retuned data, in rows of [id, epoch, pow_feed]
"""
def maria_getPowEpoch(epochStart, epochEnd):
    try:        
        databaseCursor.execute("SELECT `id`, `epoch`, `pow_feed`, `pow_prod` FROM `interval` WHERE `epoch` BETWEEN "+str(epochStart)+" AND "+str(epochEnd))
    except mariadb.Error as error:
        print("Error: {}".format(error))
        return None
    databaseConnection.commit()
    return databaseCursor.fetchall()


"""
@brief:         Get the maximum produced energy with a time period
@created:       18th Feb 2017
@return:        None: Failure
                array: retuned maximum
"""
def maria_getMaxProduced(epochStart, epochEnd):
    try:        
        databaseCursor.execute("SELECT MAX(`pow_prod`) AS `pow_prod` FROM `interval` WHERE `epoch` BETWEEN "+str(epochStart)+" AND "+str(epochEnd))
    except mariadb.Error as error:
        print("Error: {}".format(error))
        return None
    databaseConnection.commit()
    return databaseCursor.fetchall()















