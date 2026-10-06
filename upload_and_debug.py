import sys
import time
import os
import subprocess
import serial.tools.list_ports

def get_pico_port():
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        desc = (p.description or "").lower()
        hwid = (p.hwid or "").lower()
        if "pico" in desc or "rp2040" in desc or "micropython" in desc or "2e8a" in hwid or "serial" in desc:
            return p.device
    if len(ports) >= 1:
        return ports[0].device
    return None

def main():
    print("=" * 60)
    print("    RP2040 AUTO-SYNC & LIVE DEBUG TOOL")
    print("=" * 60)
    
    mpremote_exe = os.path.join(os.environ.get("LOCALAPPDATA", ""), r"Programs\Thonny\Scripts\mpremote.exe")
    if not os.path.exists(mpremote_exe):
        mpremote_exe = "mpremote"

    print("Dang tim kiem mach RP2040 / Raspberry Pi Pico...")
    port = None
    for attempt in range(10):
        port = get_pico_port()
        if port:
            print(f"[+] Da phat hien mach tai cong: {port}")
            break
        print(".", end="", flush=True)
        time.sleep(1)
    print()

    if not port:
        print("[-] Khong tim thay cong COM cua RP2040!")
        print("    -> Vui long kiem tra:")
        print("       1. Da cam cap USB Type-C tu RP2040 vao may tinh chua?")
        print("       2. Cap USB co truyen duoc du lieu (Data cable) khong?")
        print("       3. RP2040 da duoc nap firmware MicroPython chua?")
        sys.exit(1)

    print(f"\n[1/3] Ket noi toi {port} va kiem tra thu muc tren Pico...")
    try:
        res = subprocess.run([mpremote_exe, "connect", port, "fs", "ls"], capture_output=True, text=True, timeout=10)
        print(res.stdout)
    except Exception as e:
        print(f"Loi ket noi: {e}")

    print("\n[2/3] Dang nap toan bo source code da fix vao RP2040...")
    
    files_to_copy = [
        ("src/main.py", ":main.py"),
        ("src/s2kserver.py", ":s2kserver.py"),
        ("src/ddsu666.py", ":ddsu666.py"),
        ("src/sun2000.py", ":sun2000.py"),
        ("src/test_meter.py", ":test_meter.py"),
        ("src/test_loopback.py", ":test_loopback.py"),
    ]
    
    # Create modbus dir if not exists
    subprocess.run([mpremote_exe, "connect", port, "fs", "mkdir", ":modbus"], capture_output=True)
    
    modbus_files = [
        ("src/modbus/uModBusConst.py", ":modbus/uModBusConst.py"),
        ("src/modbus/uModBusFunctions.py", ":modbus/uModBusFunctions.py"),
        ("src/modbus/uModBusSerial.py", ":modbus/uModBusSerial.py"),
        ("src/modbus/uModBusServer.py", ":modbus/uModBusServer.py"),
    ]
    
    for local, remote in files_to_copy + modbus_files:
        if os.path.exists(local):
            print(f"  -> Dang copy {local} -> Pico{remote}")
            res = subprocess.run([mpremote_exe, "connect", port, "fs", "cp", local, remote], capture_output=True, text=True)
            if res.returncode != 0:
                print(f"     [!] Warning: {res.stderr}")

    print("\n[+] Nap code thanh cong!")
    print("\n[3/3] Khoi chay va theo doi log truc tiep (Live Debug)...")
    print("      (Nhan Ctrl+C de dung theo doi)\n")
    print("-" * 60)
    
    try:
        subprocess.run([mpremote_exe, "connect", port, "run", "src/s2kserver.py"])
    except KeyboardInterrupt:
        print("\nDa dung theo doi log.")

if __name__ == "__main__":
    main()
