import struct

class sun2000:

    PHASE1_VOLTAGE_VOLT = 32111
    PHASE2_VOLTAGE_VOLT = 32113
    PHASE3_VOLTAGE_VOLT = 32115
    PHASE1_CURRENT_AMP = 32103
    PHASE2_CURRENT_AMP = 32105
    PHASE3_CURRENT_AMP = 32107
    PHASE1_POWER_KW = 32129
    PHASE2_POWER_KW = 32131
    PHASE3_POWER_KW = 32133
    PHASE1_POWER_KVOLTAMPS = 32145
    PHASE2_POWER_KVOLTAMPS = 32147
    PHASE3_POWER_KVOLTAMPS = 32149
    PHASE1_POWER_KVOLTAMPSREACTIVE = 32137
    PHASE2_POWER_KVOLTAMPSREACTIVE = 32139
    PHASE3_POWER_KVOLTAMPSREACTIVE = 32141
    PHASE1_PF = 32153
    PHASE2_PF = 32155
    PHASE3_PF = 32157
    TOTALSYSTEM_POWER_KW = 32127
    TOTALSYSTEM_POWER_KVOLTAMPS = 32143
    TOTALSYSTEM_POWER_KVOLTAMPSREACTIVE = 32135
    TOTALSYSTEM_PF = 32151
    FREQUENCY_HZ = 32125
    TOTALIMPORT_KWH = 32167
    TOTALEXPORT_KWH = 32175
    PHASE1_MIN_PHASE2_VOLTAGE = 32119
    PHASE2_MIN_PHASE3_VOLTAGE = 32121
    PHASE3_MIN_PHASE1_VOLTAGE = 32123
    TOTAL_SYSTEM_ENERGY_KWH = 32159
    TOTAL_PHASE1_ENERGY_KWH = 32161
    TOTAL_PHASE2_ENERGY_KWH = 32163
    TOTAL_PHASE3_ENERGY_KWH = 32165
    # DDSU666-H Native Registers (CHNT DDSU666 format for 1-phase)
    # 0x2000 (8192 + 30001 = 38193): U (V)
    # 0x2002 (8194 + 30001 = 38195): I (A)
    # 0x2004 (8196 + 30001 = 38197): P (kW)
    # 0x2006 (8198 + 30001 = 38199): Q (kvar)
    # 0x2008 (8200 + 30001 = 38201): S (kVA)
    # 0x200A (8202 + 30001 = 38203): PF
    # 0x200E (8206 + 30001 = 38207): Freq (Hz)
    # 0x4000 (16384 + 30001 = 46385): Import Energy (kWh)
    # 0x400A (16394 + 30001 = 46395): Export Energy (kWh)
    DDSU_VOLTAGE_VOLT    = 30001 + 8192   # 38193
    DDSU_CURRENT_AMP     = 30001 + 8194   # 38195
    DDSU_POWER_KW        = 30001 + 8196   # 38197
    DDSU_POWER_KVAR      = 30001 + 8198   # 38199
    DDSU_POWER_KVA       = 30001 + 8200   # 38201
    DDSU_PF              = 30001 + 8202   # 38203
    DDSU_FREQUENCY_HZ    = 30001 + 8206   # 38207
    DDSU_IMPORT_KWH      = 30001 + 16384  # 46385
    DDSU_EXPORT_KWH      = 30001 + 16394  # 46395

    def __init__(self, model='DDSU666-H'):
        self.registers = dict()
        self.set_model(model)
        
        # Pre-initialize all possible register blocks
        for r in range(32000, 32300):
            if r not in self.registers:
                self.registers[r] = 0
                
        for r in range(38190, 38240):
            if r not in self.registers:
                self.registers[r] = 0
                
        for r in range(46380, 46430):
            if r not in self.registers:
                self.registers[r] = 0

    def set_model(self, model):
        self.model = model
        if model == 'DDSU666-H':
            model_id = 0x3B01  # Huawei DDSU666-H 1-Phase Model ID
        elif model == 'DTSU666-H-100A':
            model_id = 0x3B12  # Huawei DTSU666-H 100A Model ID
        else:
            model_id = 0x3B11  # Huawei DTSU666-H 250A Model ID

        for prefix in [0, 10000, 20000, 30000, 40000]:
            for offset in range(2000, 2005):
                self.registers[prefix + offset + 1] = model_id

    def set_register(self, regnum, value):
        value = float(value)
        dualregs = struct.unpack('>HH', struct.pack('>f', value))
        
        # Store in primary address
        self.registers[regnum + 0] = dualregs[0]
        self.registers[regnum + 1] = dualregs[1]
        
        # Also store across all function code prefixes (3xxxx for FC03, 4xxxx for FC04, 0xxxx raw)
        base = (regnum - 1) % 10000
        for prefix in [0, 30000, 40000]:
            self.registers[prefix + base + 1] = dualregs[0]
            self.registers[prefix + base + 2] = dualregs[1]

    def get_register(self, regnum):
        if regnum in self.registers:
            return self.registers[regnum]
        # Fallback to base address
        base = (regnum - 1) % 10000
        for prefix in [30000, 40000, 0]:
            target = prefix + base + 1
            if target in self.registers:
                return self.registers[target]
        return 0



    