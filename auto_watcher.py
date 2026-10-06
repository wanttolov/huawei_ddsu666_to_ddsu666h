import sys
import time
import os
import subprocess

def get_serial_ports():
    try:
        import serial.tools.list_ports
        return list(serial.tools.list_ports.comports())
    except Exception:
        return []

def main():
    mpremote_exe = os.path.join(os.environ.get("LOCALAPPDATA", ""), r"Programs\Thonny\Scripts\mpremote.exe")
    if not os.path.exists(mpremote_exe):
        mpremote_exe = "mpremote"
        
    print("====================================================================")
    print(" [AUTO-WATCHER] DANG CHAY NGAM VA CHO MACH RP2040 CAM VAO MAY TINH")
    print("====================================================================")
    print("[*] Chi can cam cap USB vao may, script se TU DONG nap code va debug ngay lap tuc!")

    already_flashed = None
    
    while True:
        ports = get_serial_ports()
        detected_port = None
        
        for p in ports:
            desc = (p.description or "").lower()
            hwid = (p.hwid or "").lower()
            if "pico" in desc or "rp2040" in desc or "micropython" in desc or "2e8a" in hwid or "serial" in desc or "ch340" in desc or "cp210" in desc or "ftdi" in desc:
                detected_port = p.device
                break
        
        if not detected_port and len(ports) >= 1:
            detected_port = ports[0].device

        if detected_port and detected_port != already_flashed:
            print(f"\n[!] PHAT HIEN THIET BI TAI CONG: {detected_port}")
            print(f"[*] Dang kiem tra ket noi toi {detected_port}...")
            time.sleep(1) # wait for USB enumeration
            
            try:
                # Ping device
                test = subprocess.run([mpremote_exe, "connect", detected_port, "eval", "1+1"], capture_output=True, text=True, timeout=5)
                if "2" not in test.stdout:
                    print(f"[*] Dang thu ket noi lai voi REPL tren {detected_port}...")
                
                print("[*] Dang nap toan bo source code vao RP2040...")
                subprocess.run([mpremote_exe, "connect", detected_port, "fs", "mkdir", ":modbus"], capture_output=True)
                
                files = [
                    ("src/main.py", ":main.py"),
                    ("src/s2kserver.py", ":s2kserver.py"),
                    ("src/ddsu666.py", ":ddsu666.py"),
                    ("src/sun2000.py", ":sun2000.py"),
                    ("src/test_meter.py", ":test_meter.py"),
                    ("src/test_loopback.py", ":test_loopback.py"),
                    ("src/modbus/uModBusConst.py", ":modbus/uModBusConst.py"),
                    ("src/modbus/uModBusFunctions.py", ":modbus/uModBusFunctions.py"),
                    ("src/modbus/uModBusSerial.py", ":modbus/uModBusSerial.py"),
                    ("src/modbus/uModBusServer.py", ":modbus/uModBusServer.py"),
                ]
                
                for local, remote in files:
                    if os.path.exists(local):
                        print(f"    -> Nạp file {local}...")
                        subprocess.run([mpremote_exe, "connect", detected_port, "fs", "cp", local, remote], capture_output=True)

                print(f"[+] NAP CODE THANH CONG VAO RP2040 TREN {detected_port}!")
                print("====================================================================")
                print("   [LIVE DEBUG] DANG CHAY VA THEO DOI LOG HE THONG...")
                print("====================================================================")
                
                already_flashed = detected_port
                
                # Run the server and follow output
                proc = subprocess.Popen([mpremote_exe, "connect", detected_port, "run", "src/s2kserver.py"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
                for line in iter(proc.stdout.readline, ''):
                    print(line, end='', flush=True)
                    
            except Exception as e:
                print(f"[-] Loi trong qua trinh nap/debug: {e}")
                time.sleep(2)
                
        elif not detected_port:
            already_flashed = None
            
        time.sleep(1)

if __name__ == "__main__":
    main()
