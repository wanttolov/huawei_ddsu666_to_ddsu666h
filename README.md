# Huawei DDSU666 to DDSU666-H Smart Power Sensor Bridge

> **Author & Project Creator:** [wanttolov](https://github.com/wanttolov)  
> **Target Hardware:** Raspberry Pi Pico / RP2040 (RP2040-Zero)  
> **Firmware:** MicroPython  
> **Compatible Inverter:** Huawei SUN2000 / SUN2000L (1-Phase & Hybrid Series)

---

## 📌 Giới thiệu dự án (Overview)

Dự án này là giải pháp chuyển đổi và giả lập giao thức Modbus RTU, biến công tơ điện tử 1 pha thông dụng **CHNT DDSU666** thành công tơ chính hãng **Huawei Smart Power Sensor DDSU666-H (Model ID: `0x3B01`)**.

Thiết bị giúp biến tần **Huawei SUN2000 / SUN2000L** nhận diện đầy đủ thông số đo đếm trên ứng dụng **FusionSolar**, hỗ trợ tính năng **Bám tải / Chống phát ngược (Zero-Export)** 2 chiều chuẩn xác mà không cần phải mua công tơ chuyên dụng đắt đỏ của Huawei.

---

## ✨ Tính năng nổi bật (Key Features)

- ✅ **Chuẩn hóa Model ID:** Phản hồi chính xác mã định danh `0x3B01` của Huawei DDSU666-H tại thanh ghi `0x07D1` (`32002`).
- ✅ **Đo đếm 2 chiều (Bidirectional Power):**
  - Chiều mua điện lưới: Công suất dương ($+P$) $\rightarrow$ Mũi tên từ **Lưới $\rightarrow$ Tải trong nhà**.
  - Chiều phát điện dư lên lưới: Công suất âm ($-P$) $\rightarrow$ Mũi tên từ **Inverter $\rightarrow$ Lưới điện**.
- ✅ **Hỗ trợ hoàn hảo Zero-Export (Anti-Feed-In):** Chu kỳ phản hồi tức thời (<1ms) qua thanh ghi thời gian thực `0x2006` (`38199`), giúp biến tần điều tiết công suất mượt mà, không bị vọt công suất ra lưới.
- ✅ **Đồng bộ toàn bộ thông số trên App FusionSolar:**
  - Điện áp lưới ($U$ - Volt)
  - Dòng điện lưới ($I$ - Ampere)
  - Công suất tác dụng ($P$ - kW / W)
  - Tần số lưới chuẩn ($f$ - $50.0\text{ Hz}$)
  - Hệ số công suất ($PF$ - $0.98 \sim 1.00$)
  - Tổng điện năng tiêu thụ / mua lưới (Import kWh)
  - Tổng điện năng phát lên lưới (Export kWh)
- ✅ **Khả năng tương thích cao:** Hỗ trợ song song cả 2 mã hàm Modbus `0x03` (Read Holding Registers) và `0x04` (Read Input Registers) không bao giờ bị lỗi timeout hay rớt kết nối.

---

## 🔌 Sơ đồ đấu nối phần cứng (Hardware Wiring)

Sử dụng bo mạch **Raspberry Pi Pico (RP2040 / RP2040-Zero)** kết hợp cùng **2 module chuyển đổi TTL sang RS485** (ví dụ module MAX485 / SP3485 tự động chuyển hướng):

```
+---------------------------------------------------------------+
|               Raspberry Pi Pico (RP2040)                      |
|                                                               |
|  [UART 0]                                                     |
|  GP0 (TX0) ----> DI  \                                        |
|  GP1 (RX0) <---- RO   |-- [RS485 Module 1] === A, B ========> Biến tần Huawei SUN2000
|                       /                       (Chân 7, 9)     (Cổng RS485 Meter)
|                                                               |
|  [UART 1]                                                     |
|  GP4 (TX1) ----> DI  \                                        |
|  GP5 (RX1) <---- RO   |-- [RS485 Module 2] === A, B ========> Công tơ CHNT DDSU666
|                       /                       (Chân 24, 25)   (A = 24, B = 25)
|                                                               |
|  VBUS / 5V  ----> VCC cả 2 module RS485                       |
|  GND        ----> GND cả 2 module RS485                       |
+---------------------------------------------------------------+
```

### Thông số cổng giao tiếp:
- **Kênh Inverter (UART0):** Baudrate `9600`, 8 data bits, Parity: `None`, 1 stop bit | Modbus Slave ID: `11`.
- **Kênh Công tơ (UART1):** Baudrate `9600`, 8 data bits, Parity: `None`, 1 stop bit | Modbus Slave ID: `11` (mặc định của CHNT DDSU666).

---

## 🚀 Hướng dẫn nạp code vào RP2040 (Flashing Guide)

### Cách 1: Nạp tự động 1-Click bằng Python (Khuyên dùng)
Kết nối RP2040 vào máy tính qua cổng USB, mở terminal và chạy:

```bash
python flash_pico.py
```
Script sẽ tự động sao chép toàn bộ các file thư viện trong thư mục `src/` vào bộ nhớ RP2040 và khởi động dịch vụ.

### Cách 2: Sử dụng Thonny IDE
1. Cài đặt MicroPython firmware cho bo mạch Raspberry Pi Pico.
2. Mở **Thonny IDE**, chọn interpreter là **MicroPython (Raspberry Pi Pico)**.
3. Tải toàn bộ các file và thư mục trong thư mục `src/` lên Pico:
   - `main.py`
   - `s2kserver.py`
   - `ddsu666.py`
   - `sun2000.py`
   - Thư mục `modbus/` (chứa `uModBusConst.py`, `uModBusFunctions.py`, `uModBusSerial.py`, `uModBusServer.py`)
4. Khởi động lại bo mạch, chương trình sẽ tự động chạy ngầm 24/7.

---

## ⚙️ Cấu hình trên Biến tần & App FusionSolar

1. Đăng nhập vào biến tần bằng tài khoản **Installer** (hoặc kết nối trực tiếp vào WiFi nội bộ của biến tần).
2. Vào mục **Cài đặt thiết bị (Settings)** $\rightarrow$ **Smart Power Sensor (Cảm biến công suất)**:
   - Loại công tơ: **DDSU666-H**
   - Địa chỉ Modbus: **11**
   - Tốc độ truyền (Baudrate): **9600**
3. Cài đặt tính năng **Chống phát ngược (Zero-Export)**:
   - Vào **Điều chỉnh công suất (Power Adjustment)** $\rightarrow$ **Điều khiển điểm hòa lưới (Grid-tied Point Control)**.
   - Chọn chế độ: **Khống chế công suất tác dụng (Active Power Control)** $\rightarrow$ **Giới hạn phát lưới = 0.00 kW**.
4. Kiểm tra trên biểu đồ năng lượng: Các mũi tên năng lượng giữa **PV $\rightarrow$ Tải tiêu thụ $\rightarrow$ Lưới điện** sẽ hiển thị chính xác theo thời gian thực.

---

## 📁 Cấu trúc thư mục mã nguồn (Project Structure)

```text
├── src/
│   ├── main.py                    # File khởi động chính tự động chạy khi bật nguồn
│   ├── s2kserver.py               # Máy chủ xử lý đa luồng (quét công tơ & phản hồi biến tần)
│   ├── ddsu666.py                 # Module đọc CHNT DDSU666 và ánh xạ thanh ghi DDSU666-H
│   ├── sun2000.py                 # Quản lý bộ thanh ghi Modbus chuẩn Huawei SUN2000
│   ├── dtsu666.py                 # Module mở rộng cho công tơ 3 pha DTSU666
│   ├── test_meter.py              # Công cụ kiểm tra tín hiệu đọc công tơ thực tế qua RS485
│   ├── test_loopback.py           # Công cụ kiểm tra cổng UART loopback
│   └── modbus/                    # Thư viện uModbus tối ưu hóa độ trễ thấp (<1ms)
├── flash_pico.py                  # Script tự động nạp code vào Pico qua mpremote
├── .gitignore                     # Cấu hình bỏ qua file rác
└── README.md                      # Hướng dẫn chi tiết
```

---

## 👨‍💻 Tác giả & Bản quyền (Credits & License)

- **Project Creator & Maintainer:** **[wanttolov](https://github.com/wanttolov)**
- Dự án được phát triển và chia sẻ miễn phí cho cộng đồng người dùng điện mặt trời Huawei SUN2000. Mọi đóng góp, cải tiến (Pull Request, Issue) đều rất được hoan nghênh!
