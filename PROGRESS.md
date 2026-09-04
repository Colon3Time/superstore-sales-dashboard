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
- ดึงรายชื่อ Product Name ที่ไม่ซ้ำ (`.unique()`)
- สรุปยอดขายรายปี (`.dt.to_period("Y")`) พิมพ์แยก 2014-2017
- Group Quantity/Profit/Discount รวม แยกตาม Category (`quantity_category`)
- หา Top 10 และ Bottom 10 (`top_sale` / `bottle_sale`) ตาม Profit แยกตาม Product Name + Sub-Category
- หา correlation (`Sales`/`Quantity`/`Discount`/`Profit`) ด้วย `.corr()` (Pearson) — ผลออกมาอ่อน (Discount-Profit = -0.22) ไม่ได้แรงอย่างที่คาด เลยเปลี่ยนไปทำ clustering แทน
- **KMeans clustering สินค้าแยกตาม Sub-Category** (`groupby1` groupby "Sub-Category" รวม Sales/Quantity/Discount/Profit → scale ด้วย `StandardScaler` → หา `best_k` ด้วย Silhouette Score แทนการมองกราฟ elbow ด้วยตา → ได้ `best_k=3` ตรงกับที่เดาไว้)
  - ผลลัพธ์: Cluster 0 = กลุ่มกำไรดี (Accessories/Chairs/Copiers/Phones/Storage/Paper), Cluster 1 = กลุ่มกำไรต่ำ/ขาดทุน (Bookcases/Appliances/Machines/Envelopes/Art/Fasteners/Furnishings/Labels/Supplies/**Tables ขาดทุนหนักสุด -17,725**), Cluster 2 = Binders แยกกลุ่มเดี่ยวเพราะ Discount รวมสูงผิดปกติ (567 vs อันดับ 2 แค่ 137)

### TODO ที่ยังค้างอยู่ในโค้ด (ยังไม่ได้ทำ)
- `sales` max=22638 min=0.44 — ต้องเช็ค outlier แบบแยกตาม Category (**ห้ามใช้ IQR รวมทั้งไฟล์** เพราะแต่ละ category ราคาคนละ scale — คุยกันไว้แล้วว่าจะดู boxplot แยกตาม Category แทน) (เช็คไฟล์โจทย์ต้นฉบับบน Google Drive แล้ว — ไฟล์นั้นเป็นสกรีนช็อต .png ของลิสต์โปรเจกต์พอร์ตทั้ง 6 ตัว ไม่ได้เป็นข้อกำหนดว่าต้องส่งผลงานเป็นไฟล์ .png แต่อย่างใด)
- `quantity` max=14 min=1 — ยังไม่ได้เช็คอะไรต่อ
- `discount` — เข้าใจว่าเป็น percentage (max=80%) แต่ยังไม่ยืนยัน/เช็คว่าทำไมมีถึง 80% — สังเกตเพิ่มวันนี้: มี discount เกิน 1.00 (>100%) จนกว่า profit จะติดลบ (โน้ตไว้ในโค้ดแล้ว ยังไม่ได้สืบต่อ) — คลัสเตอร์ชี้ตรงมาที่ **Binders** ว่าเป็นตัวที่ discount สูงผิดปกติ ควรเจาะที่นี่ก่อน
- `profit` min=-6599 — ยังไม่ได้สืบว่าออเดอร์ไหนขาดทุน เพราะอะไร — คลัสเตอร์ชี้ตรงมาที่ **Tables** ว่าขาดทุนหนักสุดในภาพรวม ควรเจาะที่นี่ก่อนเช่นกัน

### Error ที่เจอวันนี้ + วิธีแก้
| Error | สาเหตุ | วิธีแก้ |
|---|---|---|
| `UnicodeDecodeError` ตอน `read_csv` | ไฟล์ไม่ใช่ UTF-8 ล้วน มี byte `0xa0` | เพิ่ม `encoding="latin1"` |
| `KeyError: 'Customer ID'` (บรรทัดหลังๆ) | `df = pd.to_datetime(df["Order Date"])` เขียนทับตัวแปร `df` ทั้งก้อนกลายเป็น Series | ต้องเป็น `df["Order Date"] = pd.to_datetime(...)` (assign กลับเข้า column ไม่ใช่ทับตัวแปร) |
| `KeyError: 'Order'` | พิมพ์ `df["Order"]` ขาดคำว่า Date | แก้เป็น `df["Order Date"]` |
| `KeyError: 'Order Date'` (จาก Series ไม่ใช่ DataFrame) | รันซ้ำใน kernel เดิมที่ `df` ยังเป็น Series ค้างจากบั๊กก่อนหน้า (kernel state ไม่ได้ล้าง) | `:MoltenRestart!` หรือปิด-เปิด nvim ใหม่ทั้งหมด |
| groupby syntax ผิดหลายรอบ (`.groupby(...["Sales"].sum())`) | ใส่ `["Sales"].sum()` ไว้ *ข้างใน* วงเล็บของ `.groupby()` ทั้งที่ต้องอยู่ข้างนอก | `df.groupby(df["Order Date"].dt.to_period("M"))["Sales"].sum()` — groupby รับแค่ตัวจัดกลุ่ม ส่วน `["Sales"].sum()` ทำงานกับผลลัพธ์ที่ groupby คืนมา |
| kernel ค้าง ไม่ยอมอัปเดต แม้ restart nvim แล้ว | มี `ipykernel` process orphan ค้างในเครื่องจริง (PID เดิมตั้งแต่ 2 ก.ย. ไม่ตาย) | kill process ทิ้งด้วยมือ (`kill -9 <PID>`) แล้ว `:MoltenInit` ใหม่ |
| `SyntaxError: unmatched ')'` ตอนรันผ่าน molten | เลือก visual selection ไม่ครบ statement (ส่ง `)` ลอยๆ เข้า kernel โดยไม่มีวงเล็บเปิดคู่กัน) | เลือกทั้งก้อนตั้งแต่บรรทัดที่มี `= (` ถึงบรรทัดปิด `)` ให้ครบก่อน `<space>mv` |
| `SyntaxError: incomplete input` ตอนรันผ่าน molten | เลือก visual selection สั้นไป 1 บรรทัด (ขาดบรรทัดปิดวงเล็บ) | นับจำนวนบรรทัดให้ครบ หรือใช้ `V` + เลขบรรทัดปลายทาง (`NG`) แทนการนับ `j` เอง |
| `ModuleNotFoundError: No module named 'pandas'` ตอนรัน `python3 file.py` ตรงๆ ในเทอร์มินัล | `python3` ที่เรียกตรงๆ คือ system Python (`/usr/bin/python3`) ไม่มี pandas ติดตั้ง — pandas อยู่ใน venv แยก (`~/venvs/ds`, `~/.venvs/analytics`) | `source ~/venvs/ds/bin/activate` ก่อนรัน หรือรันผ่าน molten kernel ที่ผูก venv นี้ไว้อยู่แล้ว |
| วงเล็บเหลี่ยมเกิน/ผิดรูปตอนเขียน `df.groupby(...)["col1","col2"]]` | เขียน `]` ปิดเกินมาโดยไม่มี `[` เปิดคู่ + ใช้ `[...]` ชั้นเดียวแทน `[[...]]` ตอนเลือกหลายคอลัมน์ | ต้องเป็น `df.groupby("Sub-Category")[["Sales","Quantity","Discount","Profit"]]` (list ซ้อน list) |
| `NameError: name 'grouped' is not defined` | ตั้งตัวแปรไว้ชื่อ `groupby1` แต่บรรทัดหลังกลับไปเรียกชื่อ `grouped` (คนละชื่อ) | เรียกชื่อตัวแปรให้ตรงกับที่ตั้งไว้ตั้งแต่ต้น |
| paste โค้ดยาวๆ เข้า nvim แล้วคำ/นิพจน์ถูกตัดครึ่งขึ้นบรรทัดใหม่ (เช่น `silhouet` / `te_score` แยกกันคนละบรรทัด) พร้อม indent เพี้ยน | auto-indent ของ nvim ทำงานระหว่าง paste แบบปกติ (ไม่ได้เปิด paste mode ก่อน) | เปิด `:set paste` ก่อนวางโค้ดจากที่อื่น แล้ว `:set nopaste` หลังวางเสร็จ — หรือพิมพ์เองทีละบรรทัดแทน |
| `IndentationError: unindent does not match any outer indentation level` | หลังรวมบรรทัดที่ตัดคำกลับเป็นบรรทัดเดียวแล้ว ยังเหลือช่องว่างนำหน้า (indent) ที่ไม่ตรงกับ level ไหนเลยของ for-loop | ไล่เช็ค indent ทีละบรรทัดให้ตรงกับ level ที่ควรอยู่ (0 ช่องถ้าอยู่นอกลูป, 4 ช่องถ้าอยู่ในลูป) |

### ปัญหาเครื่องมือ (Neovim/vim mechanics — ไม่เกี่ยวกับ pandas แต่กินเวลาไปเยอะวันนี้)
- เผลอกด `q` ตามด้วยตัวอักษร (เช่น `qi`) เข้า **macro recording mode** (โชว์ `recording @i`) โดยไม่ตั้งใจ → กด `q` เฉยๆ อีกครั้งเพื่อหยุด
- สับสน `v` (visual **character** mode) กับ `V` (visual **line** mode) ตอนก็อปโค้ดหลายบรรทัด → ต้องใช้ `V` เวลาจะก็อป/รันทั้งบรรทัดเสมอ ไม่ใช่ `v`
- เผลอกด `*`/`#` ตอนเคอร์เซอร์อยู่บนคำ ทำให้ nvim ค้นหา+ไฮไลต์คำนั้นทั่วไฟล์ค้างไว้ → `:noh` เคลียร์ไฮไลต์
- **ใช้คีย์ลัด Molten ผิดตัว** — กด `<space>mr` (`MoltenReevaluateCell`, รันซ้ำ cell เดิม) ทั้งที่ต้องการ `<space>mv` (`MoltenEvaluateVisual`, รันตาม selection ใหม่) ทำให้ผลลัพธ์ไม่อัปเดตตามโค้ดที่เพิ่งแก้
- **paste โค้ดยาวเข้า nvim โดยไม่เปิด paste mode** → auto-indent ตัดคำ/บรรทัดกลางคันเสียหาย (ปัญหาใหม่วันนี้ คนละแบบกับปัญหา visual-selection ของรอบก่อน)
- **พบ gap สำคัญ: Molten kernel รันทีละ cell แยกกัน ไม่บังคับ indent ให้ตรงกับบริบทเหมือนรันทั้งไฟล์แบบ script** — ทำให้บางครั้งเห็นผลลัพธ์ถูกต้องใน kernel ทั้งที่ไฟล์ .py จริงมี IndentationError ซ่อนอยู่ (รันทั้งไฟล์ตรงๆ ถึงจะเจอ) — ต้องรัน `python3 file.py` ทวนทุกครั้งก่อนถือว่าไฟล์เสร็จจริง ไม่ใช่เชื่อแค่ผลใน kernel
- **สรุป root cause ของความช้าวันนี้:** ต้นทุนหลักไม่ใช่ pandas/sklearn logic (เข้าใจแนวคิด clustering/silhouette ได้เร็ว) แต่เป็นปัญหาเครื่องมือ nvim+Molten ต่อเนื่อง (macro/visual mode ช่วงแรก, paste+indent ช่วงหลัง) รวมวันนี้เจอปัญหาจากจุดนี้เกิน 6 รอบ

### เวลาที่ใช้วันนี้ (2026-09-03)
- Git repo สร้าง 13:08:16 น. (เวลาไทย)
- ช่วงจับเวลาที่ 1-2 (ก่อนหน้า): รวม 1 ชม. 13 นาที 28 วินาที (มีพักทำธุระคั่นกลาง ~52 นาที ไม่นับรวม)
- ช่วงจับเวลาที่ 3: 21:46:46–22:10:08 (23 นาที 22 วินาที)
- ช่วงจับเวลาที่ 4: 01:03:39–01:07:34 น. ข้ามเที่ยงคืนเข้า 2026-09-04 (3 นาที 55 วินาที)
- ช่วงจับเวลาที่ 5: 01:09:33–02:09:36 น. (1 ชม. 3 วินาที)
- รวมช่วง 3-5 วันนี้: 1 ชม. 27 นาที 20 วินาที (พักคั่นกลางช่วง 2-3 กับ 3-4 ไม่นับรวม)
- **รวมเวลาทำงานทั้งวัน (ช่วง 1-5): ประมาณ 2 ชม. 40 นาที 48 วินาที**

### แนวคิดที่คุยกันไว้ (ยังไม่ได้ลงมือ)
- Outlier ต้องดูแยกตาม Category (boxplot) ไม่ใช่ IQR รวมทั้งไฟล์ เพราะ scale ราคาต่างกันคนละโลก (Furniture vs Office Supplies)
- ใช้ `.dt.to_period("M")` ไม่ใช่ `.dt.month` เวลา group ตามเดือน (ไม่งั้นปีจะถูกรวมกัน)
- Power BI ใช้ Row-Level Security (RLS) สร้าง dashboard เดียวแล้วตั้งกฎ filter ตาม user login แทนการสร้างหลาย dashboard แยกแผนก — เกี่ยวข้องกับ [[project_da_skill_gap]] เรื่องช่องว่าง Power BI ที่ยังไม่ปิด เพราะเลือกทำ Streamlit เป็นหลัก

## 2026-09-04

### `Clean_EDA_Data.py` — สิ่งที่ทำเพิ่มวันนี้
- **KMeans clustering แยกตาม Region** (`groupby2` groupby "Region" รวม Sales/Quantity/Discount/Profit → scale → silhouette score หา `best_k2`) — Region มีแค่ 4 ค่า (Central/East/South/West) เท่านั้น
  - ผลลัพธ์ (k=3): Cluster 0 = **East, West** (Sales/Profit สูงสุดทั้งคู่ ~91k-108k กำไร), Cluster 1 = **South** (กำไรกลางๆ 46.7k), Cluster 2 = **Central** (กำไรต่ำสุด 39.7k **ทั้งที่ Discount รวมสูงสุด 558.34** เกินทุกภาคอื่น) — แพทเทิร์น discount สูง/กำไรต่ำ ตรงกับที่เจอใน Binders ก่อนหน้า

### Error ที่เจอวันนี้ + วิธีแก้
| Error | สาเหตุ | วิธีแก้ |
|---|---|---|
| `ValueError: Number of labels is 4. Valid values are 2 to n_samples - 1` | copy `k_range = range(2, 11)` มาจากโค้ด Sub-Category (17 แถว) ทั้งที่ `groupby2` (Region) มีแค่ 4 แถว — แบ่งคลัสเตอร์เกินจำนวนตัวอย่างที่มีไม่ได้ | ปรับ `k_range = range(2, 4)` ให้เข้ากับจำนวนแถวจริง |
| `NameError: name 'x1_scaled' is not defined` (ซ่อนอยู่หลัง error แรก) | ตัวแปรที่ scale ไว้จริงชื่อ `x2_scaled` แต่บรรทัด `kmeans.fit_predict(...)` เรียกผิดเป็น `x1_scaled` | แก้เป็น `x2_scaled` ให้ตรงกับที่ประกาศไว้ |

- ยืนยันไฟล์รันจบสมบูรณ์ด้วย `python3 Clean_EDA_Data.py` ตรงๆ ไม่มี error เหลือ

### เวลาที่ใช้วันนี้ (2026-09-04)
- ช่วงจับเวลาที่ 1: เริ่ม 12:30 น. (แจ้งย้อนหลัง)

### ขั้นต่อไป (ยังไม่เริ่ม)
- เจาะ **Tables** (ขาดทุนหนักสุดจาก clustering), **Binders** (discount สูงผิดปกติ), และ **Central** (discount สูงสุด/กำไรต่ำสุดในบรรดา Region) ที่ระดับ order แต่ละแถว หา row ที่ discount >100% / profit ติดลบจริงๆ
- Boxplot ของ `Sales` แยกตาม Category (matplotlib/seaborn) เพื่อดู outlier — ยังไม่เริ่ม
- **เปลี่ยนแผน (2026-09-04): ทำ dashboard ทั้ง 2 ตัว ไม่ใช่เลือกอย่างใดอย่างหนึ่งแล้ว** — Power BI (ตามที่ตกลงไว้เดิมกับ README) **+** Streamlit (ทางที่อยากได้เพิ่ม) — **ให้ความสำคัญกับ Power BI ก่อน** เหตุผล: ตลาดงานไทยใช้ Power BI เยอะกว่า Streamlit ชัดเจน ทำ Power BI ให้เสร็จก่อนแล้วค่อยไป Streamlit ทีหลัง — EDA ระดับภาพรวมตามเป้าหมายใน README (time trend / region / category / top-bottom products) ครบแล้ว พร้อมเริ่ม Power BI ได้เลย
