from machine import UART, Pin
import sys
sys.path.append('modbus')
from uModBusServer import *
from uModBusSerial import *
import _thread
from sun2000 import *


# ##########################################################################################
# Start of user configurable settings
# ##########################################################################################

# Adjust below settings to be the same as for your electricity meter Modbus RS485 settings 
METER_UART_BAUDRATE = 9600
METER_UART_BITS     = 8
METER_UART_PARITY   = None
METER_UART_STOPBITS = 1

# Hardware Flow Control Pins (DE/RE)
# Your XY-017 / HW-519 RS485 modules have AUTOMATIC flow control (4 pins: VCC, TXD, RXD, GND),
# so NO DE/RE direction pins are needed (set to None).
SERVER_CTRL_PIN = None
CLIENT_CTRL_PIN = None

# Select Huawei meter profile emulation:
# 'DDSU666-H' -> 1-phase meter model (ID 0x3B01) - Matches CHNT DDSU666 & SUN2000L perfectly!
# 'DTSU666-H' -> 3-phase meter model (ID 0x3B11)
HUAWEI_METER_MODEL = 'DDSU666-H'

# Select meter driver module:
from ddsu666 import *
#from dtsu666 import *
#from sdm630 import *

# ##########################################################################################
# End of user configurable settings
# ##########################################################################################



# This callback function gets called by the modbus server for every register which has to be read.
def readRegister(server, starting_addr, quantity):
    # print(f"[HUAWEI SUN2000] Inverter dang doc {quantity} thanh ghi tu dia chi {starting_addr}")
    while quantity > 0:
        value = s2k.get_register(starting_addr)
        server.sendreg(value)
        starting_addr = starting_addr + 1
        quantity = quantity - 1


import time

# The server thread is run in background and handles queries from an external Sun2000 modbus client
def serverthread():
    while True:
        try:
            server.receive()
        except Exception as e:
            print('serverthread exception occured: ' + str(e))
        time.sleep_ms(2)

# Below 2 lines instantiate a modbus server and client.
# UART0 on RP2040-Zero: GP0 (TX), GP1 (RX) -> connects to Huawei SUN2000L RS485 module
# UART1 on RP2040-Zero: GP4 (TX), GP5 (RX) -> connects to CHNT DDSU666 RS485 module
server = uModBusServer(slave_id=11, uart_id=0, baudrate=9600, data_bits=8, stop_bits=1, parity=None, pins=(Pin(0), Pin(1)), ctrl_pin=SERVER_CTRL_PIN, loopbacked=False, callbackfunction=readRegister)
client = uModBusSerial(uart_id=1, baudrate=METER_UART_BAUDRATE, data_bits=METER_UART_BITS, stop_bits=METER_UART_STOPBITS, parity=METER_UART_PARITY, pins=(Pin(4), Pin(5)), ctrl_pin=CLIENT_CTRL_PIN, loopbacked=False)
s2k = sun2000(model=HUAWEI_METER_MODEL)
mtr = meter(client, s2k)

print("=== Sun2000MeterTransposer Started ===")
print(f"Huawei Emulation: {HUAWEI_METER_MODEL} (Model ID: 0x{s2k.registers[32002]:04X})")
print("Inverter Server: UART0 (GP0 TX, GP1 RX) | Slave ID: 11 | 9600 8N1")
print("Meter Client:    UART1 (GP4 TX, GP5 RX) | Slave ID: 11 | 9600 8N1")

_thread.start_new_thread(serverthread, ())

# Below thread does continously read your electricity meter data and push them to sun2000 module registers
while True:
    try:
        mtr.updateRegisters()
    except Exception as e:
        print('clientthread exception occured: ' + str(e))
    time.sleep_ms(150)
    
