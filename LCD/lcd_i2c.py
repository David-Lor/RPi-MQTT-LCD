#!/usr/bin/python
#--------------------------------------
#        ___    ___    _ ____
#     / _ \/ _ \(_) __/__    __ __
#    / , _/ ___/ /\ \/ _ \/ // /
# /_/|_/_/    /_/___/ .__/\_, /
#                                /_/     /___/
#
#    lcd_i2c.py
#    LCD test script using I2C backpack.
#    Supports 16x2 and 20x4 screens.
#
# Author : Matt Hawkins
# Date     : 20/09/2015
#
# Edited by EnforcerZhukov (https://www.github.com/enforcerzhukov)
#
# http://www.raspberrypi-spy.co.uk/
#
# Copyright 2015 Matt Hawkins
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.    If not, see <http://www.gnu.org/licenses/>.
#
#--------------------------------------

#Native libraries
import time
import atexit
import threading
#Installed libraries
#import smbus
import smbus2
#Own files
#from Settings import *

# Define some device parameters
LCD_I2C_ADDRESS    = 0x3F # I2C device address

LCD_WIDTH = 16     # Maximum characters per line

# Define some device constants
LCD_CHR = 1 # Mode - Sending data
LCD_CMD = 0 # Mode - Sending command

LINES = (
    0x80, # LCD RAM address for the 1st line
    0xC0, # LCD RAM address for the 2nd line
    0x94, # LCD RAM address for the 3rd line
    0xD4, # LCD RAM address for the 4th line
)

LCD_BACKLIGHT    = 0x08    # On
#LCD_BACKLIGHT = 0x00    # Off

ENABLE = 0b00000100 # Enable bit

# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005

#Open I2C interface
#bus = smbus.SMBus(0)    # Rev 1 Pi uses 0
#bus = smbus.SMBus(1) # Rev 2 Pi uses 1
bus = smbus2.SMBus(1) # Rev 2 Pi uses 1 - SMBUS2


@atexit.register
def atexit_f():
    #Clear LCD when program ends
    lcd_clear()
    bus.close()

def lcd_init():
    # Initialise display
    lcd_byte(0x33,LCD_CMD) # 110011 Initialise
    lcd_byte(0x32,LCD_CMD) # 110010 Initialise
    lcd_byte(0x06,LCD_CMD) # 000110 Cursor move direction
    lcd_byte(0x0C,LCD_CMD) # 001100 Display On,Cursor Off, Blink Off 
    lcd_byte(0x28,LCD_CMD) # 101000 Data length, number of lines, font size
    lcd_byte(0x01,LCD_CMD) # 000001 Clear display
    time.sleep(E_DELAY)

def lcd_byte(bits, mode):
    # Send byte to data pins
    # bits = the data
    # mode = 1 for data
    #                0 for command

    bits_high = mode | (bits & 0xF0) | LCD_BACKLIGHT
    bits_low = mode | ((bits<<4) & 0xF0) | LCD_BACKLIGHT

    # High bits
    bus.write_byte(LCD_I2C_ADDRESS, bits_high)
    lcd_toggle_enable(bits_high)

    # Low bits
    bus.write_byte(LCD_I2C_ADDRESS, bits_low)
    lcd_toggle_enable(bits_low)

def lcd_toggle_enable(bits):
    # Toggle enable
    time.sleep(E_DELAY)
    bus.write_byte(LCD_I2C_ADDRESS, (bits | ENABLE))
    time.sleep(E_PULSE)
    bus.write_byte(LCD_I2C_ADDRESS,(bits & ~ENABLE))
    time.sleep(E_DELAY)

lock = threading.Lock()

def lcd_print(message,line):
    # Send string to display
    # message=string, line=LCD line to print (0,1,2,3)
    if "**ignore**" in message:
        return
    if not lock.acquire(timeout=0.1):
    #if not lock.acquire(blocking=False):
        return
    try:
        message = message.ljust(LCD_WIDTH," ")
        lcd_byte(LINES[line], LCD_CMD)
        for i in range(LCD_WIDTH):
            lcd_byte(ord(message[i]),LCD_CHR)
    
    except Exception as ex: #Avoid main pinging program to stop because the LCD isn't working properly
        print("Error printing LCD string:\n{}".format(ex))
    
    finally:
        if lock.locked():
            lock.release()

def lcd_clear():
    # Clear LCD screen
    lcd_byte(0x01, LCD_CMD)

## END: init LCD

lcd_init()
