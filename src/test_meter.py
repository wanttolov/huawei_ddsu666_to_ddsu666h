# Tool test ket noi truc tiep cong to CHNT DDSU666 tren GP4 / GP5
from machine import UART, Pin
import time
import struct

print("=== BAT DAU SCAN / TEST CONG TO CHNT DDSU666 ===")
print("Chan: TX=GP4, RX=GP5\n")

def calc_crc(data):
    crc = 0xFFFF
    for pos in data:
        crc ^= pos
        for _ in range(8):
            if (crc & 1) != 0:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return struct.pack('<H', crc)

# Danh sach cac cau hinh de test
baudrates = [9600, 2400, 4800]
slave_ids = [11, 1]
func_codes = [0x04, 0x03]  # 0x04 = Read Input Registers, 0x03 = Read Holding Registers

found = False

for baud in baudrates:
    print(f"--- Thu Baudrate: {baud} 8N1 ---")
    uart = UART(1, baudrate=baud, bits=8, parity=None, stop=1, tx=Pin(4), rx=Pin(5), timeout=500)
    
    for slave_id in slave_ids:
        for func in func_codes:
            # Tao goi tin doc Dien ap o dia chi 0x2000 (2 thanh ghi = 1 float)
            pdu = bytearray([slave_id, func, 0x20, 0x00, 0x00, 0x02])
            crc = calc_crc(pdu)
            packet = pdu + crc
            
            # Xoa buffer cu
            while uart.any():
                uart.read()
            
            # Gui goi tin
            uart.write(packet)
            func_name = "0x04 (Input)" if func == 0x04 else "0x03 (Holding)"
            print(f"Gui [ID={slave_id}, Func={func_name}]: {[hex(x) for x in packet]}")
            
            # Doi phan hoi
            time.sleep(0.15)
            
            if uart.any():
                resp = uart.read()
                print(f"--> NHAN DUOC ({len(resp)} bytes): {[hex(x) for x in resp]}")
                if len(resp) >= 7:
                    try:
                        val = struct.unpack('>f', resp[3:7])[0]
                        print(f"===> GIA TRI DIEN AP DOC DUOC: {val:.2f} V\n")
                        found = True
                        
                        # Test doc them Dien nang Mua luoi 0x4000 va Phat luoi 0x400A
                        print("--- Kiem tra doc Thanh ghi Dien nang (Energy) ---")
                        # 1. 0x4000 Import
                        pdu_imp = bytearray([slave_id, 0x04, 0x40, 0x00, 0x00, 0x02])
                        uart.write(pdu_imp + calc_crc(pdu_imp))
                        time.sleep(0.15)
                        if uart.any():
                            r_imp = uart.read()
                            if len(r_imp) >= 7:
                                v_imp = struct.unpack('>f', r_imp[3:7])[0]
                                print(f"===> DIEN MUA LUOI / TIEU THU (0x4000): {v_imp:.2f} kWh")
                                
                        # 2. 0x400A Export
                        pdu_exp = bytearray([slave_id, 0x04, 0x40, 0x0A, 0x00, 0x02])
                        uart.write(pdu_exp + calc_crc(pdu_exp))
                        time.sleep(0.15)
                        if uart.any():
                            r_exp = uart.read()
                            if len(r_exp) >= 7:
                                v_exp = struct.unpack('>f', r_exp[3:7])[0]
                                print(f"===> DIEN PHAT NGUOC LEN LUOI (0x400A): {v_exp:.2f} kWh")
                                
                    except Exception as e:
                        print(f"Loi giai ma float: {e}")
            else:
                print("--> Khong co phan hoi (Timeout)\n")
                
    uart.deinit()
    if found:
        break

if not found:
    print("===================================================================")
    print("KET QUA: Khong nhan duoc phan hoi nao tu cong to!")
    print("Kiem tra cac nguyen nhan:")
    print("1. Dao nguoc 2 day A+ va B- noi giua Module RS485 va cong to.")
    print("2. Kiem tra xem cong to da duoc cap dien AC 220V va bat sang man hinh chua.")
    print("3. Kiem tra nguon cap cho module RS485 (thu noi VCC sang 5V).")
    print("4. Kiem tra chan A+ noi vao chan 24, B- noi vao chan 25 tren DDSU666.")
    print("===================================================================")
else:
    print("=== THANH CONG! DA KET NOI DUOC VOI CONG TO ===")
