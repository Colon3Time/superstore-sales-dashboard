# Progress Log

## 2026-09-03

### Setup
- สร้าง repo, push ขึ้น GitHub: https://github.com/Colon3Time/superstore-sales-dashboard
- โหลด dataset จาก Google Drive → `data/superstore.csv` (9,994 rows, ช่วงวันที่ 2014-01-03 ถึง 2017-12-30)
- ลงปลั๊กอิน `csvview.nvim` ให้ nvim เปิด csv เป็นตารางได้ (`:CsvViewEnable` / `:CsvViewToggle`)

### `Clean_EDA_Data.py` — สิ่งที่ทำไปแล้ว
- อ่านไฟล์ + `df.info()` / `df.describe()`
- แปลง `Order Date` เป็น datetime
- นับจำนวนลูกค้าไม่ซ้ำ (`Customer ID`) → 793 คน
- หาวันแรก/วันสุดท้าย + จำนวนวันทั้งหมดของช่วงข้อมูล (1,457 วัน)
- รวมยอดขายทั้งหมด (`Sales.sum()`) → 2,297,200.86
- Group ยอดขายรายเดือน (`groupby(dt.to_period("M"))["Sales"].sum()`) — เห็น พ.ย./ธ.ค. ยอดสูงกว่าเดือนอื่นชัดเจนทุกปี (seasonality)

### TODO ที่ยังค้างอยู่ในโค้ด (ยังไม่ได้ทำ)
- `sales` max=22638 min=0.44 — ต้องเช็ค outlier แบบแยกตาม Category (**ห้ามใช้ IQR รวมทั้งไฟล์** เพราะแต่ละ category ราคาคนละ scale — คุยกันไว้แล้วว่าจะดู boxplot แยกตาม Category แทน)
- `quantity` max=14 min=1 — ยังไม่ได้เช็คอะไรต่อ
- `discount` — เข้าใจว่าเป็น percentage (max=80%) แต่ยังไม่ยืนยัน/เช็คว่าทำไมมีถึง 80%
- `profit` min=-6599 — ยังไม่ได้สืบว่าออเดอร์ไหนขาดทุน เพราะอะไร

### Error ที่เจอวันนี้ + วิธีแก้
| Error | สาเหตุ | วิธีแก้ |
|---|---|---|
| `UnicodeDecodeError` ตอน `read_csv` | ไฟล์ไม่ใช่ UTF-8 ล้วน มี byte `0xa0` | เพิ่ม `encoding="latin1"` |
| `KeyError: 'Customer ID'` (บรรทัดหลังๆ) | `df = pd.to_datetime(df["Order Date"])` เขียนทับตัวแปร `df` ทั้งก้อนกลายเป็น Series | ต้องเป็น `df["Order Date"] = pd.to_datetime(...)` (assign กลับเข้า column ไม่ใช่ทับตัวแปร) |
| `KeyError: 'Order'` | พิมพ์ `df["Order"]` ขาดคำว่า Date | แก้เป็น `df["Order Date"]` |
| `KeyError: 'Order Date'` (จาก Series ไม่ใช่ DataFrame) | รันซ้ำใน kernel เดิมที่ `df` ยังเป็น Series ค้างจากบั๊กก่อนหน้า (kernel state ไม่ได้ล้าง) | `:MoltenRestart!` หรือปิด-เปิด nvim ใหม่ทั้งหมด |
| groupby syntax ผิดหลายรอบ (`.groupby(...["Sales"].sum())`) | ใส่ `["Sales"].sum()` ไว้ *ข้างใน* วงเล็บของ `.groupby()` ทั้งที่ต้องอยู่ข้างนอก | `df.groupby(df["Order Date"].dt.to_period("M"))["Sales"].sum()` — groupby รับแค่ตัวจัดกลุ่ม ส่วน `["Sales"].sum()` ทำงานกับผลลัพธ์ที่ groupby คืนมา |
| kernel ค้าง ไม่ยอมอัปเดต แม้ restart nvim แล้ว | มี `ipykernel` process orphan ค้างในเครื่องจริง (PID เดิมตั้งแต่ 2 ก.ย. ไม่ตาย) | kill process ทิ้งด้วยมือ (`kill -9 <PID>`) แล้ว `:MoltenInit` ใหม่ |

### แนวคิดที่คุยกันไว้ (ยังไม่ได้ลงมือ)
- Outlier ต้องดูแยกตาม Category (boxplot) ไม่ใช่ IQR รวมทั้งไฟล์ เพราะ scale ราคาต่างกันคนละโลก (Furniture vs Office Supplies)
- ใช้ `.dt.to_period("M")` ไม่ใช่ `.dt.month` เวลา group ตามเดือน (ไม่งั้นปีจะถูกรวมกัน)

### ขั้นต่อไป (ยังไม่เริ่ม)
- วิเคราะห์ Profit (margin, ออเดอร์ขาดทุน)
- แยกตาม Region / Category / Sub-Category
- Top/Bottom products
- สร้าง dashboard ด้วย Streamlit (ตัดสินใจไว้แล้วว่าจะใช้ Streamlit ไม่ใช้ Power BI)
