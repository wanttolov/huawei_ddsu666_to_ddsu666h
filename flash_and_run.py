import sys
import time
import os
import subprocess
import serial.tools.list_ports

mpremote_exe = os.path.join(os.environ.get("LOCALAPPDATA", ""), r"Programs\Thonny\Scripts\mpremote.exe")
port = "COM3"

print("Dang ket noi toi RP2040...")
for attempt in range(10):
    try:
        import serial
        s = serial.Serial(port)
        s.close()
        break
    except Exception:
        print(".", end="", flush=True)
        time.sleep(0.5)
print()

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

print(f"=== DANG NAP CODE VAO RP2040 ({port}) ===")
subprocess.run([mpremote_exe, "connect", port, "soft-reset"], capture_output=True, timeout=5)
subprocess.run([mpremote_exe, "connect", port, "fs", "mkdir", ":modbus"], capture_output=True, timeout=5)

for local, remote in files:
    print(f"Nap file: {local} -> {remote} ...")
    res = subprocess.run([mpremote_exe, "connect", port, "fs", "cp", local, remote], capture_output=True, text=True)
    if res.returncode == 0:
        print("  [OK]")
    else:
        print(f"  [!] Loi: {res.stderr}")

print("\n=== NAP CODE HOAN TAT 100%! DANG CHAY LIVE DEBUG ===")
try:
    subprocess.run([mpremote_exe, "connect", port, "run", "src/s2kserver.py"])
except KeyboardInterrupt:
    pass
