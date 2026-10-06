import os
import subprocess
import sys

mpremote_exe = os.path.join(os.environ.get("LOCALAPPDATA", ""), r"Programs\Thonny\Scripts\mpremote.exe")
port = "COM3"

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

print("=== DANG NAP FILE VAO RP2040 (COM3) ===")

for local, remote in files:
    print(f"Nap file: {local} -> {remote} ...")
    res = subprocess.run([mpremote_exe, "connect", port, "fs", "cp", local, remote], capture_output=True, text=True)
    if res.returncode != 0:
        print(f"  [!] Loi: {res.stderr}")
    else:
        print("  [OK]")

print("\n=== KIEM TRA DANH SACH FILE TREN RP2040 ===")
res = subprocess.run([mpremote_exe, "connect", port, "fs", "ls"], capture_output=True, text=True)
print(res.stdout)
res = subprocess.run([mpremote_exe, "connect", port, "fs", "ls", ":modbus"], capture_output=True, text=True)
print(res.stdout)
print("=== NAP CODE HOAN TAT 100% ===")
