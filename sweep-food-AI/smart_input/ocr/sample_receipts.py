"""Sample Vietnamese Supermarket Receipts for Smart Input Testing & 1-Click Demo."""

SAMPLE_RECEIPTS = [
    {
        "id": "winmart_family",
        "store_name": "WinMart+ - Cửa Hàng 124 Nguyễn Thị Thập",
        "title": "Hóa đơn WinMart: Thịt Bò, Cá Điêu Hồng & Rau",
        "date": "2026-09-05 17:30",
        "raw_text": """WINMART+ 124 NGUYEN THI THAP
HOA DON BAN LE: #WM-20260905-882
NGAY: 05/09/2026 17:30:15
----------------------------------------
TEN HANG             SL    D.GIA   T.TIEN
----------------------------------------
1. THIT BO UC NHAP   0.45 kg 280,000 126,000
2. CA DIEU HONG LAM SACH 0.70 kg 85,000 59,500
3. RAU MUONG NUOC 500G 1.00 go 15,000  15,000
4. CA CHUA DA LAT    0.35 kg  32,000  11,200
5. TOI CO DON VIET   0.15 kg  90,000  13,500
6. NUOC RUA CHEN SUNLIGHT 1.00 chai 35,000 35,000
7. TUI TIEU CHUAN WINMART 1.00 cai    1,000   1,000
----------------------------------------
TONG CONG:                      261,200 VND
TIEN MAT:                       300,000 VND
TIEN THOI:                       38,800 VND
CAM ON QUY KHACH VA HEN GAP LAI!"""
    },
    {
        "id": "bachhoaxanh_student",
        "store_name": "BÁCH HÓA XANH - 45 Lê Văn Lương",
        "title": "Hóa đơn Bách Hóa Xanh: Trứng, Đậu Hũ & Rau Củ",
        "date": "2026-09-06 09:15",
        "raw_text": """BACH HOA XANH - LE VAN LUONG
PHIEU THANH TOAN: #BHX-9941
THOI GIAN: 06/09/2026 09:15
----------------------------------------
TRUNG GA BA HUAN (HOP 10 QUẢ)
 1.00 HOP x 32,000               32,000
DAU HU NON ICHIBAN 250G
 2.00 MIENG x 12,000             24,000
THIT HEO XAY CP 300G
 1.00 KHAY x 45,000              45,000
BAP CAI TRANG DA LAT
 0.65 KG x 20,000                13,000
HANH LA 100G
 1.00 BO x 5,000                  5,000
KHAN GIAY UOT BOBBY 100 TO
 1.00 GOI x 38,000               38,000
----------------------------------------
TONG TIEN:                      157,000
THANH TOAN MOMO:                157,000"""
    },
    {
        "id": "coopmart_seafood",
        "store_name": "Co.opmart Cống Quỳnh",
        "title": "Hóa đơn Co.opmart: Hải Sản Tươi & Nấm Canh",
        "date": "2026-09-05 11:45",
        "raw_text": """CO.OPMART CONG QUYNH
HOA DON GTGT: 0049281
NGAY 05/09/2026
----------------------------------------
1. TOM THE CHAN TRANG TUOI
   0.40 KG x 195,000/KG          78,000
2. MUC ONG TUOI SONG
   0.50 KG x 260,000/KG         130,000
3. NAM KIM CHAM HAN QUOC 150G
   2.00 GOI x 14,000/GOI         28,000
4. CAI THIA SACH CO.OP 300G
   1.00 GOI x 18,000/GOI         18,000
5. GUNG TUOI VIET NAM
   0.10 KG x 40,000/KG            4,000
6. XA PHONG LIFEBUOY 90G
   1.00 CUC x 16,000/CUC         16,000
----------------------------------------
TONG CONG:                      274,000 VND"""
    },
    {
        "id": "bhx_label_caithia",
        "store_name": "BÁCH HÓA XANH - Tem Nhãn Bao Bì",
        "title": "Nhãn Mác Bách Hóa Xanh: Cải Thìa Sạch VietGAP",
        "date": "2026-09-06",
        "type": "label",
        "raw_text": """SIEU THI BACH HOA XANH
CAI THIA SACH DA LAT VIETGAP
KLT: 500g
NSX: 05/09/2026
HSD: 09/09/2026
XUAT XU: LAM DONG
BAO QUAN: NGAN MAT TU LANH (4-8 DO C)
DON GIA: 26,000 D/KG
THANH TIEN: 13,000 D"""
    },
    {
        "id": "bhx_label_thitheo",
        "store_name": "BÁCH HÓA XANH - Tem Thịt Tươi CP",
        "title": "Nhãn Mác Bách Hóa Xanh: Thịt Ba Rọi Heo CP Chilled",
        "date": "2026-09-06",
        "type": "label",
        "raw_text": """BACH HOA XANH - THIT TUOI MOI NGAY
THIT BA ROI HEO CP CHILLED
TRONG LUONG: 0.420 kg
DONG GOI: 06/09/2026 06:30
HAN SU DUNG: 08/09/2026
XUAT XU: DONG NAI - VIET NAM
DON GIA: 165,000 D/KG
THANH TIEN: 69,300 D"""
    }
]
