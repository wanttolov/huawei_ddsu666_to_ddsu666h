# Test 2 module RS485 giao tiep truc tiep voi nhau tren ban lam viec
# Yeu cau dau day giua 2 module:
# - Module 1 A+  noi  Module 2 A+
# - Module 1 B-  noi  Module 2 B-

from machine import UART, Pin
import time

print("=== BAT DAU TEST GIAO TIEP 2 MODULE RS485 (LOOPBACK TEST) ===")
print("Module 1: TX=GP0, RX=GP1 (Gia lap Bien tan)")
print("Module 2: TX=GP4, RX=GP5 (Gia lap Cong to)")
print("Dau day test: Noi A+ cua Module 1 sang A+ cua Module 2; B- cua Module 1 sang B- cua Module 2\n")

uart0 = UART(0, baudrate=9600, bits=8, parity=None, stop=1, tx=Pin(0), rx=Pin(1), timeout=200)
uart1 = UART(1, baudrate=9600, bits=8, parity=None, stop=1, tx=Pin(4), rx=Pin(5), timeout=200)

count = 1
while True:
    print(f"--- Lan truyen {count} ---")
    
    # 1. Module 1 gui du lieu sang Module 2
    msg_gui = f"PING_TU_MODULE_1_#{count}".encode()
    uart0.write(msg_gui)
    print(f"[Module 1] Da gui -> {msg_gui.decode()}")
    
    time.sleep(0.1) # Cho truyen qua duong day RS485
    
    if uart1.any():
        msg_nhan = uart1.read()
        print(f"[Module 2] DA NHAN THANH CONG <- {msg_nhan.decode()}")
    else:
        print("[Module 2] Chua nhan duoc! (Kiem tra da noi A+ voi A+, B- voi B- chua)")
    
    # 2. Module 2 gui phan hoi lai cho Module 1
    resp_gui = f"PONG_TU_MODULE_2_#{count}".encode()
    uart1.write(resp_gui)
    print(f"[Module 2] Da gui phan hoi -> {resp_gui.decode()}")
    
    time.sleep(0.1)
    
    if uart0.any():
        resp_nhan = uart0.read()
        print(f"[Module 1] DA NHAN PHAN HOI THANH CONG <- {resp_nhan.decode()}")
    else:
        print("[Module 1] Chua nhan duoc phan hoi!")
        
    print("--------------------------------------------------\n")
    count += 1
    time.sleep(1.5)
