# Sun2000MeterTransposer

-> Enable other Smartmeters like SDM630 to connect to Huawei Sun2000 and look like DTSU-666.

This was my solution to address the fact, that DTSU-666 and its variants availability was "null".

<img src="https://github.com/xyphro/Sun2000MeterTransposer/raw/main/photos/Installed%20in%20meter%20cabinet.jpg" width="50%"/>

It works rock solid since several months without a single interruption.

The project is based on RP2040 Raspberry pi Zero module. It will work on the Wifi variant too, but there is no network access enabled.

Note: I did not document the HW very well (yet), but want to share it still with the community. Build it at your own risk. The pinning of the 2 UART channels can be seen in s2kserver.py module (or schematic).

Warning: This project works with high voltage AC supply. You risk killing yourself, your family and friends, your pets. Take care and only work with line voltages when you are experienced in how much pain it causes to touch 230V :-)

# Folder structure

- hw: contains schematic / PCB in Eagle format.
- src: Micropython sourcecode - can be directly uploaded to RP2040 module using e.g. Thony IDE
- DinRainHousing: STL files for the 3D printed Dinrail housing
- photos: Some pictures of the actual build as inspiration

# Adjustments to other meters

Copy file sdm630.py and rename it to your meter name. Adjust it, such that the equivalent registers of your meter are read out and written to s2k module registers.
Within file s2kserver.py:
- You might need to change the UART settings like baudrate, parity in s2kserver during instatiation of uModBusSerial module.
- change ```from sdm630 import *``` to your module name

# Sourcecode orientation

main.py purpose is only to start s2kserver.py.
s2kserver instantiates 2 threads to server requests from Sun2000 inverter and poll SDM630 meter continously.

# Credits

Credits go to:
- uModbus [1] project. I changed the file slightly and included all dependencies within the src folder. Main modifications were done for speed/latency purposes
- DTSU666-Modbus [2] project: This project was of major support for the idea and to get register details. 
- GitHub user salakrzy
- Kai for testing it in endless debug sessions remotely whilr I was still busy ibstalling my solar installation and could not test myself
- Radek for making and providing his Chint DTSU666 module

# Compatibility

Tested with sun2000 3 phase 10kW inverters and proven working with spc147 and 148 firmware versions. As of now there is no newer one available.

# Updates

## CHNT DDSU666 1-Phase Support (Huawei DDSU666-H Emulation)

Added full emulation support for **CHNT DDSU666 1-phase** smart meter to emulate **Huawei DDSU666-H** (Model ID: `0x3B01`):
- Accurate 2-way energy & power measurement (Grid Import $\leftarrow$ / Grid Export $\rightarrow$).
- Full zero-export / anti-feed-in compatibility with Huawei SUN2000 / SUN2000L inverters.
- Synchronized all real-time registers (Voltage, Current, Active Power, Power Factor, Frequency 50Hz, Import/Export Total kWh) matching FusionSolar expectations.
- Universal register resolution for both Modbus Function Code `0x03` (Holding) and `0x04` (Input).
- Helper tools included:
  - `flash_pico.py`: Automated flashing tool to upload MicroPython scripts to Raspberry Pi Pico (RP2040).
  - `src/test_meter.py`: RS485 communication diagnostic script for CHNT DDSU666.
  - `src/test_loopback.py`: UART loopback verification.

[1] https://github.com/pycom/pycom-modbus/tree/master/uModbus

[2] https://github.com/elfabriceu/DTSU666-Modbus

