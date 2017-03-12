# -*- coding: utf-8 -*-
"""
@author:         stoberblog
@detail:         This is a configuration file for the Solar Modbus project.
"""

# MODBUS DETAILS
INVERTER_IP = "192.168.1.1"
MODBUS_PORT = 502
METER_ADDR = 240
MODBUS_TIMEOUT = 30 #seconds to wait before failure

# METER INSTALLED
METER_INSTALLED = True

# DATABASE
DATABASE_TYPE = "mariadb"   # Current options: mariadb
DATABASE_ADDR = "127.0.0.1"
DATABASE_USER = "solarUser"
DATABASE_PASSWD = "solarPassed"
DATABASE_DB = "solarDB"

#SCHEDULER
SCHED_INTERVAL = 1          # Minutes between recollecting new data

# DATA
EPOCH_INVERTER = False      # False = Use compueter time, True = get time off inverter (scheduler will still use compurter time)
POW_THERESHOLD = 10         # Watt threshold
LOG_LEVEL = "ERROR"         # Levels: NONE, FATAL, ERROR, NOTICE, DEBUG


