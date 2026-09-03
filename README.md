# Superstore Sales Performance Dashboard

โปรเจกต์ที่ 1 ในซีรีส์พอร์ต Data Analytics (Beginner → Advanced) — วิเคราะห์ revenue, profit, และ regional trend ของร้านค้าปลีก (Superstore) ด้วย Excel และ Power BI

## Dataset

- ที่มา: [Superstore Dataset Final (Kaggle)](https://www.kaggle.com/datasets/vivek468/superstore-dataset-final)
- ไฟล์ที่ใช้: `data/superstore.csv` (ยังไม่ได้ดาวน์โหลด — ดูขั้นตอนด้านล่าง)

Kaggle บล็อกการดาวน์โหลดแบบไม่ล็อกอิน ต้องโหลดผ่านเบราว์เซอร์เอง:

1. เข้าลิงก์ dataset ด้านบน กด Download
2. แตกไฟล์ วางไฟล์ `.csv` ไว้ที่ `data/superstore.csv`

## เป้าหมายการวิเคราะห์

- Revenue & Profit ตามช่วงเวลา (trend)
- Revenue & Profit แยกตาม Region / Category / Sub-Category
- Top/Bottom performing products
- Profit margin ต่ำผิดปกติ (ขาดทุนทั้งที่ยอดขายสูง) — จุดที่ dashboard ต้อง flag ให้เห็นทันที

## Tools

- Python/pandas — ทำความสะอาดและสำรวจข้อมูลเบื้องต้น
- Power BI — dashboard หลัก

## สถานะ

- [x] สร้าง repo
- [ ] โหลด dataset
- [ ] EDA เบื้องต้น
- [ ] สร้าง dashboard ใน Power BI
