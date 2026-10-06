# CHNT DDSU666 Single-Phase Power Meter Driver for Sun2000MeterTransposer
import time

class meter:
    
    def __init__(self, client, sun2000):
        self._client = client
        self._sun2000 = sun2000
        self._last_import_kwh = 0.0
        self._last_export_kwh = 0.0
        
    def updateRegisters(self):
        s2k = self._sun2000
        sladdr = 11  # Modbus ID for CHNT DDSU666 (configured to 11)
        
        # 1. Read instantaneous measurements:
        # 0x2000 (8192): Voltage (U) [V]
        # 0x2002 (8194): Current (I) [A]
        # 0x2004 (8196): Active Power (P) [kW]
        # 0x2006 (8198): Reactive Power (Q) [kvar]
        # 0x2008 (8200): Apparent Power (S) [kVA]
        # 0x200A (8202): Power Factor (PF)
        # 0x200C (8204): Phase Angle
        # 0x200E (8206): Frequency (f) [Hz]
        regs = self._client.read_input_registers(slave_addr=sladdr, starting_address=30001+8192, register_quantity=8)
        if len(regs) >= 6:
            voltage = regs[0]
            current = regs[1]
            active_power = regs[2]  # Keep sign: >0 for Import (Grid->House), <0 for Export (Inverter->Grid)
            reactive_power = regs[3]
            apparent_power = regs[4]
            power_factor = regs[5]
            if power_factor < 0.1 and voltage > 100.0 and current > 0.1:
                calc_pf = (abs(active_power) * 1000.0) / (voltage * current)
                power_factor = min(1.0, max(0.0, calc_pf))
            if power_factor < 0.05:
                power_factor = 0.99
                
            freq = 50.0
            if len(regs) >= 8 and regs[7] > 40.0:
                freq = regs[7]
                
            power_w = active_power * 1000.0
            reactive_var = reactive_power * 1000.0
            apparent_va = apparent_power * 1000.0
            
            # Map single phase to Huawei DTSU666-H registers (321xx in Watts)
            s2k.set_register(s2k.PHASE1_VOLTAGE_VOLT, voltage)
            s2k.set_register(s2k.PHASE2_VOLTAGE_VOLT, 0.0)
            s2k.set_register(s2k.PHASE3_VOLTAGE_VOLT, 0.0)
            s2k.set_register(s2k.PHASE1_MIN_PHASE2_VOLTAGE, voltage)
            
            s2k.set_register(s2k.PHASE1_CURRENT_AMP, current)
            s2k.set_register(s2k.PHASE2_CURRENT_AMP, 0.0)
            s2k.set_register(s2k.PHASE3_CURRENT_AMP, 0.0)
            
            s2k.set_register(s2k.PHASE1_POWER_KW, power_w)
            s2k.set_register(s2k.PHASE2_POWER_KW, 0.0)
            s2k.set_register(s2k.PHASE3_POWER_KW, 0.0)
            s2k.set_register(s2k.TOTALSYSTEM_POWER_KW, power_w)
            
            s2k.set_register(s2k.PHASE1_POWER_KVOLTAMPSREACTIVE, reactive_var)
            s2k.set_register(s2k.PHASE2_POWER_KVOLTAMPSREACTIVE, 0.0)
            s2k.set_register(s2k.PHASE3_POWER_KVOLTAMPSREACTIVE, 0.0)
            s2k.set_register(s2k.TOTALSYSTEM_POWER_KVOLTAMPSREACTIVE, reactive_var)
            
            s2k.set_register(s2k.PHASE1_POWER_KVOLTAMPS, apparent_va)
            s2k.set_register(s2k.PHASE2_POWER_KVOLTAMPS, 0.0)
            s2k.set_register(s2k.PHASE3_POWER_KVOLTAMPS, 0.0)
            s2k.set_register(s2k.TOTALSYSTEM_POWER_KVOLTAMPS, apparent_va)
            
            s2k.set_register(s2k.PHASE1_PF, power_factor)
            s2k.set_register(s2k.PHASE2_PF, power_factor)
            s2k.set_register(s2k.PHASE3_PF, power_factor)
            s2k.set_register(s2k.TOTALSYSTEM_PF, power_factor)
            s2k.set_register(s2k.FREQUENCY_HZ, freq)
            
            # Map single phase to Huawei DDSU666-H Native Registers (CHNT 0x2000 series / 38193... in kW)
            s2k.set_register(30001+8192, voltage)          # 0x2000: Voltage (V)
            s2k.set_register(30001+8194, current)          # 0x2002: Current (A)
            s2k.set_register(30001+8196, active_power)     # 0x2004: Active Power (P in kW)
            s2k.set_register(30001+8198, active_power)     # 0x2006: Active Power Real-time query (P in kW)
            s2k.set_register(30001+8200, apparent_power)   # 0x2008: Apparent Power (kVA)
            s2k.set_register(30001+8202, power_factor)     # 0x200A: Power Factor
            s2k.set_register(30001+8204, power_factor)     # 0x200C: Power Factor
            s2k.set_register(30001+8206, freq)             # 0x200E: Frequency (Hz)
            s2k.set_register(30001+8208, power_factor)     # 0x2010: Power Factor
            s2k.set_register(30001+8210, power_factor)     # 0x2012: Power Factor
            s2k.set_register(30001+8212, power_factor)     # 0x2014: Power Factor
            s2k.set_register(30001+8214, power_factor)     # 0x2016: Power Factor
            s2k.set_register(30001+8216, power_factor)     # 0x2018: Power Factor
            s2k.set_register(30001+8218, power_factor)     # 0x201A: Power Factor
            s2k.set_register(30001+8220, power_factor)     # 0x201C: Power Factor
            s2k.set_register(30001+8222, freq)             # 0x201E: Frequency (Hz)
            s2k.set_register(30001+8224, freq)             # 0x2020: Frequency (Hz)

        else:
            raise OSError('Could not read instantaneous measurements from DDSU666')
        
        time.sleep_ms(25)

        # 2. Read Total Active Import Energy (Dien mua luoi / tieu thu): 0x4000 (16384) [kWh]
        try:
            regs_imp = self._client.read_input_registers(slave_addr=sladdr, starting_address=30001+16384, register_quantity=1)
            if len(regs_imp) == 1 and regs_imp[0] > 0:
                self._last_import_kwh = regs_imp[0]
                # DTSU666-H registers
                s2k.set_register(s2k.TOTALIMPORT_KWH, self._last_import_kwh)
                s2k.set_register(s2k.TOTAL_SYSTEM_ENERGY_KWH, self._last_import_kwh)
                s2k.set_register(s2k.TOTAL_PHASE1_ENERGY_KWH, self._last_import_kwh)
                # DDSU666-H native registers (0x4000..0x400E)
                s2k.set_register(30001+16384, self._last_import_kwh) # 0x4000: Total Energy
                s2k.set_register(30001+16386, self._last_import_kwh) # 0x4002
                s2k.set_register(30001+16388, self._last_import_kwh) # 0x4004
                s2k.set_register(30001+16390, self._last_import_kwh) # 0x4006
                s2k.set_register(30001+16392, self._last_import_kwh) # 0x4008
                s2k.set_register(30001+16394, self._last_import_kwh) # 0x400A: Positive Active Energy (Import / Yongdian)
                s2k.set_register(30001+16396, self._last_import_kwh) # 0x400C
                s2k.set_register(30001+16398, self._last_import_kwh) # 0x400E
        except Exception:
            pass

        time.sleep_ms(25)

        # 3. Read Total Active Export Energy (Dien phat len luoi): 0x400A (16394) [kWh]
        try:
            regs_exp = self._client.read_input_registers(slave_addr=sladdr, starting_address=30001+16394, register_quantity=1)
            if len(regs_exp) == 1 and regs_exp[0] > 0:
                self._last_export_kwh = regs_exp[0]
                # DTSU666-H registers
                s2k.set_register(s2k.TOTALEXPORT_KWH, self._last_export_kwh)
                # DDSU666-H native registers (0x4010..0x4014: Reverse Active Energy / Fadian)
                s2k.set_register(30001+16400, self._last_export_kwh) # 0x4010: Reverse Energy
                s2k.set_register(30001+16402, self._last_export_kwh) # 0x4012
                s2k.set_register(30001+16404, self._last_export_kwh) # 0x4014: Reverse Active Energy (Export / Fadian)
        except Exception:
            pass

        # Live monitor print
        print(f"[CHNT DDSU666] U={voltage:.1f}V | I={current:.2f}A | P={power_w:.1f}W ({active_power:.3f}kW) | PF={power_factor:.3f} | f={freq:.1f}Hz | Mua={self._last_import_kwh:.2f}kWh | Phat={self._last_export_kwh:.2f}kWh")


