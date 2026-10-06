# HƯỚNG DẪN CHI TIẾT & LƯU Ý DEBUG HỆ THỐNG Sun2000MeterTransposer
**(Chuyển đổi Công tơ CHNT DDSU666 1 Pha cho Biến tần Huawei SUN2000L)**

---

## 1. TRẠNG THÁI HIỆN TẠI CỦA HỆ THỐNG

Dựa trên dữ liệu thực tế từ App FusionSolar của bạn:
- **Trạng thái kết nối:** ĐÃ KẾT NỐI THÀNH CÔNG (Biểu tượng đồng hồ chấm xanh lá, trạng thái `正常` - Bình thường).
- **Điện áp pha A (A相电压):** `224.8V` -> **ĐÃ ĐỌC ĐÚNG** từ công tơ CHNT DDSU666.
- **Dòng điện pha A (A相电流):** `7.83A` -> `4.36A` -> **ĐÃ ĐỌC ĐÚNG** theo dòng tiêu thụ thực tế.
- **Hệ số công suất (功率因数 PF):** `0.972` -> `0.324` -> **ĐÃ ĐỌC ĐÚNG**.
- **Tần số lưới (电网频率):** `50.15Hz` -> **ĐÃ ĐỌC ĐÚNG**.

---

## 2. GIẢI THÍCH CHI TIẾT CÁC ĐIỂM CẦN LƯU Ý

### Lưu ý 1: Tại sao Pha B và Pha C hiển thị `0.0V` và `0.00A`?
- Biến tần của bạn là **SUN2000L-5KTL-CN-4G (1 pha)** và công tơ của bạn là **CHNT DDSU666 (1 pha)**.
- Lưới điện nhà bạn là điện 1 pha (chỉ có 1 dây pha Lửa nối vào Pha A và 1 dây Nguội N).
- Khi chọn giao thức đồng hồ 3 pha `DTSU666-H`, App sẽ hiển thị cả 3 pha. Vì không có pha B và pha C nên giá trị `0.0V` và `0.00A` là **HOÀN TOÀN CHÍNH XÁC VÀ BÌNH THƯỜNG**. Biến tần chỉ dùng dữ liệu của **Pha A** và **Tổng công suất (Total Power)** để tính toán bám tải.

### Lưu ý 2: Tại sao trên App FusionSolar phải chọn loại `DTSU666-H` (thay vì `DDSU666-H`)?
- File `sun2000.py` khai báo mã nhận diện thiết bị là `self.registers[32002] = 0x3b11`.
- `0x3b11` là mã định danh của model **DTSU666-H**.
- Khi bạn chọn `DDSU666-H` trên app, biến tần gửi lệnh kiểm tra mã ID, thấy trả về `0x3b11` (DTSU666-H) nên biến tần báo không khớp loại và không đọc thanh ghi.
- **Do đó: Trên App FusionSolar luôn chọn loại công tơ là `DTSU666-H`**.

### Lưu ý 3: Tại sao Công suất (用电功率) từng bị hiển thị `0.001kW`?
- **Nguyên nhân lệch đơn vị:**
  - Công tơ CHNT DDSU666 trả về giá trị công suất theo đơn vị **kW** (ví dụ tải đang dùng là `1.758 kW`).
  - Nhưng thanh ghi công suất của Huawei SUN2000L (thanh ghi `32127` và `32129`) lại mong muốn nhận giá trị theo đơn vị **Watt (W)** (ví dụ `1758.0 W`).
  - Khi truyền số `1.758` sang biến tần, biến tần hiểu là `1.758 Watt` nên chia cho 1000 và hiển thị trên app thành `0.001 kW`.
- **Cách xử lý:** Trong file `ddsu666.py`, công suất đọc từ DDSU666 đã được nhân với **`1000.0`** (`power_w = active_power * 1000.0`) trước khi ghi vào biến tần.

---

## 3. SƠ ĐỒ CHÂN PHẦN CỨNG (RP2040-Zero & 2x Module RS485 XY-017)

Module RS485 của bạn là loại **XY-017 / HW-519 Tự động chuyển chiều (Auto Flow Control)**, chỉ có 4 chân TTL: `VCC, TXD, RXD, GND`.

| Chân trên RP2040-Zero | Chân Module RS485 | Chức năng & Kết nối |
| :--- | :--- | :--- |
| **3V3** (hoặc **5V**) | `VCC` (cả 2 module) | Cấp nguồn cho module RS485 |
| **GND** | `GND` (cả 2 module) | Nối mass chung |
| **GP0** (Pin `0` góc phải trên) | `TXD` Module #1 | Giao tiếp **Biến tần Huawei SUN2000L** (UART0 TX) |
| **GP1** (Pin `1` góc phải trên) | `RXD` Module #1 | Giao tiếp **Biến tần Huawei SUN2000L** (UART0 RX) |
| **GP4** (Pin `4` góc phải) | `TXD` Module #2 | Giao tiếp **Công tơ CHNT DDSU666** (UART1 TX) |
| **GP5** (Pin `5` góc phải) | `RXD` Module #2 | Giao tiếp **Công tơ CHNT DDSU666** (UART1 RX) |

### Kết nối cổng RS485 (A / B):
- **Module #1 (Biến tần):**
  - Chân `A+` $\rightarrow$ Chân **RS485A** (Pin 7) cổng COM biến tần SUN2000L.
  - Chân `B-` $\rightarrow$ Chân **RS485B** (Pin 9) cổng COM biến tần SUN2000L.
- **Module #2 (Công tơ):**
  - Chân `A+` $\rightarrow$ Chân **24** trên công tơ CHNT DDSU666.
  - Chân `B-` $\rightarrow$ Chân **25** trên công tơ CHNT DDSU666.

---

## 4. CẤU TRÚC CODE & CÁCH CHỈNH SỬA DEBUG

Tất cả code nằm trong thư mục `src/`:

```text
src/
├── ddsu666.py               # Driver đọc chỉ số từ CHNT DDSU666 1 pha
├── main.py                  # File khởi động tự động khi cấp nguồn Pico
├── s2kserver.py             # Server Modbus UART0 (Huawei) và Client UART1 (DDSU666)
├── sun2000.py               # Ánh xạ bảng thanh ghi của Huawei SUN2000
├── test_meter.py            # Script kiểm tra đọc trực tiếp công tơ DDSU666
├── test_loopback.py         # Script kiểm tra nối chéo 2 module RS485
└── modbus/                  # Thư viện xử lý Modbus RTU
    ├── uModBusConst.py
    ├── uModBusFunctions.py
    ├── uModBusSerial.py
    └── uModBusServer.py
```

### Chi tiết các thông số trong file `ddsu666.py`:

```python
class meter:
    def __init__(self, client, sun2000):
        self._client = client
        self._sun2000 = sun2000
        
    def updateRegisters(self):
        s2k = self._sun2000
        sladdr = 11  # Địa chỉ Modbus của công tơ CHNT (bạn đã đổi thành 11)
        
        # 1. Đọc các thông số tức thời (Địa chỉ Hex 0x2000 = Dec 8192, đọc 6 số thực Float)
        # regs[0]: Điện áp (V)
        # regs[1]: Dòng điện (A)
        # regs[2]: Công suất tác dụng (kW)
        # regs[3]: Công suất phản kháng (kvar)
        # regs[4]: Công suất biểu kiến (kVA)
        # regs[5]: Hệ số công suất (PF)
        regs = self._client.read_input_registers(slave_addr=sladdr, starting_address=30001+8192, register_quantity=6)
        if len(regs) == 6:
            voltage = regs[0]
            current = regs[1]
            active_power = regs[2]
            reactive_power = regs[3]
            apparent_power = regs[4]
            power_factor = regs[5]
            
            # Quy đổi kW sang Watt cho Huawei
            power_w = active_power * 1000.0
            reactive_var = reactive_power * 1000.0
            apparent_va = apparent_power * 1000.0
            
            # Ghi vào thanh ghi giả lập Huawei SUN2000
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
```

---

## 5. HƯỚNG DẪN KHI CẮM LAPTOP KHÁC VÀO PICO ĐỂ DEBUG

1. **Cài đặt Thonny IDE trên Laptop mới:**
   - Tải và cài đặt Thonny từ: `https://thonny.org/`
2. **Kết nối Pico:**
   - Cắm cáp Type-C từ Laptop vào RP2040-Zero.
   - Mở Thonny, chọn Interpreter ở góc dưới bên phải là: **`MicroPython (Raspberry Pi Pico)`** với cổng COM tương ứng (ví dụ `COM3`, `COM4`...).
3. **Xem file trong Pico:**
   - Vào menu **View** $\rightarrow$ Tích chọn **Files**.
   - Cửa sổ bên trái phía dưới sẽ hiện mục **Raspberry Pi Pico**.
4. **Cách chạy & theo dõi log:**
   - Mở file `s2kserver.py` trên Pico.
   - Bấm nút **Run (F5)** (hoặc nút Play màu xanh lá).
   - Cửa sổ Shell phía dưới sẽ in ra log quá trình nhận gói tin từ Biến tần và đọc gói tin từ Công tơ.
5. **Thêm lệnh in kiểm tra nhanh nếu cần:**
   - Bạn có thể thêm dòng: `print(f"U={voltage}V, I={current}A, P={power_w}W")` ngay trong hàm `updateRegisters()` của file `ddsu666.py` để theo dõi chỉ số nhảy theo thời gian thực trên màn hình Shell.
