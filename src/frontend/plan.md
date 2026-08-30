# SweepFood — Kế hoạch Frontend (Flutter mobile + web)

> Tài liệu này phục vụ việc **design từng screen** rồi hiện thực hoá bằng Flutter.
> Nguồn đặc tả gốc: `../../AISC26_Mau_Thuyet_Minh_Du_An.md` (team Phantoms, AISC 2026).
> Phạm vi: **chỉ frontend**. Backend hiện mới có `GET /api/health` → frontend chạy **mock-first**.

---

## 1. Bối cảnh & nguyên tắc thiết kế

**Người dùng:** người trẻ 18–30 tuổi ở đô thị, sống một mình / ở ghép, tự nấu ≥ 3 bữa/tuần, **ngại nhập liệu thủ công**.

**3 giá trị cốt lõi phải thể hiện xuyên suốt UI (mục 10 spec):**
1. Tiết kiệm thực phẩm → hiển thị **số nguyên liệu đã dùng trước hạn** / lượng tránh lãng phí (kg), ưu tiên nguyên liệu cận hạn. *(Không hiển thị giá trị tiền: OCR quét không lấy được giá nguyên liệu — bỏ toàn bộ tính năng "tiền tiết kiệm".)*
2. Giảm thời gian ra quyết định → chỉ 3–5 gợi ý món, không danh sách dài.
3. Hỗ trợ lựa chọn bữa ăn → dinh dưỡng E/P/C/L theo khẩu phần, dễ so sánh.

**Nguyên tắc UX:**
- **Ít thao tác nhất.** Mọi luồng nhập liệu ưu tiên camera/giọng nói; nhập tay là phương án cuối.
- **Preview trước khi lưu.** Kết quả OCR/giọng nói luôn cho user xem & sửa trước khi ghi vào kho.
- **Ưu tiên theo hạn dùng.** Màu sắc + thứ tự sắp xếp phản ánh mức khẩn cấp.
- **Vòng lặp khép kín:** nhập kho → thấy cận hạn → gợi ý món → xác nhận đã nấu → tự trừ kho + ghi nhận chống lãng phí.
- Ngôn ngữ mặc định **tiếng Việt**. Tiền tệ `39.000đ`, ngày `05/09`, hạn dùng dạng tương đối "còn 2 ngày" / "quá hạn 1 ngày".
- Mobile-first. Web/tablet: bố cục căn giữa, `max-width` ~ 520–600px cho MVP (2-pane để sau).

---

## 2. Kiến trúc & stack (tham chiếu nhanh)

| Hạng mục | Lựa chọn |
|---|---|
| State management | Riverpod (+ riverpod_generator) |
| Routing | go_router (hỗ trợ deep link từ FCM) |
| HTTP | dio; lớp `ApiClient` abstract → `DioApiClient` \| `MockApiClient`, chọn qua `--dart-define=BACKEND=mock\|live` |
| Model | freezed + json_serializable |
| Cấu trúc | Clean architecture, feature-first: `features/<x>/{data,domain,presentation}` + `core/` + `shared/domain/` |
| i18n | flutter_localizations + intl (`app_vi.arb` mặc định) |
| Charts | fl_chart (macro dinh dưỡng, báo cáo) |
| Media | image_picker/camera + image_cropper + permission_handler + record (ghi âm) |
| Thông báo | firebase_messaging + flutter_local_notifications |

Cây thư mục `lib/` chi tiết: xem phần 8. Hợp đồng API frontend giả định: xem phần 9.

---

## 3. Design System — làm trước tiên

### 3.1 Tokens
- **Màu thương hiệu:** seed xanh lá (food / eco). Sinh color scheme Material 3 light + dark.
- **Màu ngữ nghĩa theo hạn dùng (dùng cho badge, viền card, chấm tròn):**
  | Trạng thái | Ý nghĩa | Gợi ý màu |
  |---|---|---|
  | `expired` | Quá hạn | đỏ |
  | `critical` | ≤ 2 ngày / tầng "Ăn liền" | cam |
  | `soon` | 3–5 ngày | vàng |
  | `ok` | > 5 ngày | xanh trung tính |
- **Màu theo tầng bảo quản** (4 tầng — xem 4.x): mỗi tầng 1 icon + 1 accent nhẹ.
- **Spacing:** 4 / 8 / 12 / 16 / 24 / 32. **Radius:** 8 (control), 16 (card), 24 (sheet). **Elevation:** 0/1/3.
- **Typography:** display / headline / title / body / label — scale Material 3, kiểm tra độ dài tiếng Việt (dài hơn tiếng Anh ~ 15–20%).

### 3.2 Component sheet (thiết kế 1 lần, tái dùng)
`PantryItemCard` · `DishCard` (+ biến thể `SuggestionCard` có điểm & badge) · `ExpiryBadge` · `TierChip` · `MacroRing` / `MacroChip` / `MacroBar` · `QuotaBanner` (X/40 nguyên liệu, X/10 lượt quét) · `ConfidenceField` (ô OCR sửa được + mức tin cậy) · `WaveformRecorder` · `QuickActionSheet` (4 nút) · `CategoryPicker` · `QtyStepper` · `UnitPicker` · `DateField` · `PrimaryButton` / `SecondaryButton` / `TextButton` · `PaywallCard` · `EmptyState` · `ErrorView` · `LoadingSkeleton` (list / card / detail) · `SectionHeader` · `WasteSavedPill` (số nguyên liệu dùng trước hạn — không có tiền).

### 3.3 Quy ước trạng thái (mọi screen phải có bản thiết kế cho 4 trạng thái)
`Loading` (skeleton, không spinner toàn màn) · `Empty` (minh hoạ + CTA rõ ràng) · `Error` (thông điệp + nút "Thử lại") · `Loaded`. Bổ sung `Offline` nếu screen phụ thuộc mạng mạnh.

### 3.4 Accessibility & responsive
- Tương phản ≥ WCAG AA; vùng chạm ≥ 48dp; hỗ trợ phóng chữ hệ thống.
- Không dùng **chỉ màu** để truyền tải trạng thái hạn dùng → luôn kèm text/icon.
- Dark mode: **có trong MVP** (cần bạn xác nhận — xem phần 11).

---

## 4. Điều hướng & Sơ đồ thông tin (IA)

**Bottom navigation — 5 tab:**
1. **Trang chủ** (Dashboard)
2. **Kho** (Pantry)
3. **Gợi ý** (Suggestions)
4. **Mua sắm** (Shopping list)
5. **Cá nhân** (Settings)

- **FAB "Thêm nguyên liệu"** xuất hiện ở tab Trang chủ & Kho → mở `AddEntryChooser` (bottom sheet).
- **Icon chuông** góc trên phải tab Trang chủ → Trung tâm thông báo.
- **Luồng modal** (che toàn màn / bottom sheet lớn): Ingest (nhập liệu), Xác nhận sau nấu, Paywall.
- **Deep link từ FCM:** notification cận hạn → mở thẳng `PantryItemDetail` hoặc `SuggestionList` đã lọc theo nguyên liệu đó.

```
Splash
 ├─ (chưa đăng nhập) → Welcome → Login / Register → Onboarding → Shell
 └─ (đã đăng nhập)   → Shell
Shell (bottom nav)
 ├─ Trang chủ ──> Notification Center ──> Near-expiry detail ──> Dish detail
 ├─ Kho ──> Pantry item detail ──> Add/Edit ingredient
 │        └─ FAB ──> AddEntryChooser ──> {Quét tem | Quét hoá đơn | Nói | Nhập tay} ──> Review ──> Kho
 ├─ Gợi ý ──> Score breakdown / Dish detail ──> Cooking ──> Post-cook confirm ──> (Leftover save) ──> Kho
 ├─ Mua sắm ──> (từ Thực đơn tuần) Shopping list
 └─ Cá nhân ──> Subscription / Paywall · Preferences · Notification settings · Pantry sharing · About
Premium (gated): Thực đơn tuần · Báo cáo · Mục tiêu dinh dưỡng · Chia sẻ tủ bếp
```

---

## 5. DANH SÁCH SCREEN (để design)

> Ký hiệu `[P]` = tính năng Premium (thiết kế kèm trạng thái khoá + Paywall). `[S]` = có trạng thái phụ cần vẽ riêng.

### Nhóm 0 — Toàn cục / dùng chung
| ID | Screen | Mục đích | Ghi chú design |
|---|---|---|---|
| G-01 | Splash | Kiểm tra phiên đăng nhập, điều hướng | Logo + tối giản; không progress bar |
| G-02 | App Shell + Bottom Nav | Khung 5 tab + FAB | Trạng thái active/inactive, badge số thông báo |
| G-03 | AddEntryChooser (sheet) | Chọn phương thức nhập | 4 mục lớn: Quét tem · Quét hoá đơn · Nói · Nhập tay + icon |
| G-04 | Permission priming (sheet) ×3 | Xin quyền camera / mic / thông báo | Giải thích lợi ích trước khi gọi quyền hệ thống; trạng thái "đã từ chối" → mở Cài đặt |
| G-05 | Paywall | So sánh Free / Premium tháng / Premium năm | Bảng tính năng theo mục 12.1 spec; giá 0đ / 39.000đ / 299.000đ; gói Gia đình = "Sắp có" |
| G-06 | Global states kit | Empty / Error / Offline / Loading | Bộ minh hoạ + copy mẫu, tái dùng |
| G-07 | Snackbar / Toast | Thành công / lỗi / hoàn tác | Ví dụ: "Đã thêm 3 nguyên liệu · Hoàn tác" |

### Nhóm 1 — Auth & Onboarding
| ID | Screen | Nội dung chính | Trạng thái |
|---|---|---|---|
| A-01 | Welcome / Value prop | 3 slide theo 3 giá trị cốt lõi | — |
| A-02 | Đăng nhập | email + mật khẩu, "quên mật khẩu", link đăng ký | loading, lỗi sai thông tin |
| A-03 | Đăng ký | tên, email, mật khẩu, điều khoản | lỗi validation từng trường (422) |
| A-04 | Quên mật khẩu `[S]` | nhập email → màn "đã gửi" | — |
| A-05 | Onboarding · Ưu tiên dinh dưỡng | chọn: cân bằng / nhiều protein / ít năng lượng / nhiều rau | có thể bỏ qua |
| A-06 | Onboarding · Hướng dẫn nhập kho lần đầu | 2–3 bước minh hoạ multi-modal, CTA "Thêm nguyên liệu đầu tiên" | — |

### Nhóm 2 — Trang chủ
| ID | Screen | Thành phần | Trạng thái |
|---|---|---|---|
| H-01 | Dashboard | Header lời chào + `WasteSavedPill`; section **"Cần dùng sớm"** (card ngang, ưu tiên cận hạn); **Gợi ý nhanh** (3–5 `SuggestionCard` thu gọn); **Tổng quan kho** 4 tầng (đếm + mini bar); FAB thêm nguyên liệu | Loaded / **Empty (kho trống → CTA nhập kho)** / Loading skeleton / Error |

### Nhóm 3 — Kho thực phẩm
| ID | Screen | Thành phần | Trạng thái |
|---|---|---|---|
| K-01 | Danh sách kho | Segmented theo **4 tầng**: *Ăn liền/Nấu trong ngày* · *Ngăn mát* · *Ngăn đông* · *Kệ đồ khô*. Sắp xếp: ưu tiên cận hạn (mặc định) / tên / mới thêm. Tìm kiếm + lọc theo danh mục. `QuotaBanner` X/40 (free). Mỗi dòng: `PantryItemCard` (tên, số lượng+đơn vị, `ExpiryBadge`, `TierChip`, icon nguồn nhập) | Loaded / Empty theo từng tầng / Loading / Error / **Đạt giới hạn 40 (free) → nhắc nâng cấp** |
| K-02 | Chi tiết nguyên liệu | Tên, danh mục, số lượng+đơn vị, tầng bảo quản, ngày thêm / đóng gói / HSD, "thời gian bảo quản tham khảo" (khi không có HSD nhà SX), giá, nguồn nhập. Hành động: Sửa · **Đã dùng** (mở K-04) · Xoá · **Tìm món dùng nguyên liệu này** | Loaded / Loading / Error |
| K-03 | Thêm / Sửa nguyên liệu (thủ công) | `CategoryPicker` + gợi ý theo lịch sử; `QtyStepper`; `UnitPicker`; chọn tầng; `DateField` (đóng gói / HSD); giá (tuỳ chọn). Nếu chọn tầng "Ngăn mát/Đông" mà thiếu HSD → hiện chip "bảo quản tham khảo: 3–5 ngày…" | validation từng trường; chế độ Thêm vs Sửa |
| K-04 | Điều chỉnh số lượng (sheet) | Dùng một phần (slider/nhập) · Dùng hết · Nhập số mới | — |

### Nhóm 4 — Nhập liệu đa phương thức
| ID | Screen | Nội dung | Trạng thái cần vẽ |
|---|---|---|---|
| I-01 | Camera — Quét tem | Khung ngắm, đèn flash, nút chụp, gợi ý căn nhãn | quyền bị từ chối; đèn yếu |
| I-02 | Cắt/chỉnh ảnh | Crop, xoay, tăng tương phản | — |
| I-03 | **Review kết quả quét tem** | Các `ConfidenceField`: tên nguyên liệu · khối lượng tịnh · ngày đóng gói · HSD · giá. Trường tin cậy thấp được tô nổi. Hệ thống **gợi ý tầng bảo quản + danh mục** (sửa được). CTA "Thêm vào kho" | đang xử lý OCR; OCR thất bại → I-09; tin cậy thấp toàn phần → nhắc kiểm tra kỹ |
| I-04 | Camera — Quét hoá đơn | Tương tự I-01, khung dài | — |
| I-05 | **Review hoá đơn (nhiều mặt hàng)** | Danh sách dòng hàng; mỗi dòng sửa được (tên, số lượng, đơn vị); gán **nhóm thực phẩm → chu kỳ bảo quản tham khảo**; checkbox chọn/bỏ dòng; nút "Thêm N mục" | đang xử lý; 0 dòng nhận được; một số dòng lỗi |
| I-06 | Ghi âm giọng nói | `WaveformRecorder` + timer + nút dừng; hint "VD: 2 lạng thịt bò, 1 bó cải, 3 quả trứng" | đang ghi; đang chuyển văn bản (Whisper) |
| I-07 | **Review kết quả giọng nói** | Transcript + danh sách item bóc tách (số lượng / đơn vị / tên) sửa được; thêm/xoá dòng | không nghe rõ → gợi ý ghi lại |
| I-08 | Quota đạt giới hạn `[S]` | "Bạn đã dùng 10/10 lượt quét tháng này" → CTA Paywall / nhập tay | — |
| I-09 | Quét thất bại `[S]` | Lý do (mờ, rách, phai mực) + "Chụp lại" / "Nhập tay" | — |

### Nhóm 5 — Gợi ý món
| ID | Screen | Thành phần | Trạng thái |
|---|---|---|---|
| S-01 | Danh sách gợi ý | Tối đa **3–5** `SuggestionCard`: ảnh, tên, thời gian nấu, **điểm tổng**, badge "Dùng X nguyên liệu cận hạn", "Có sẵn 80%", "Cần mua 2". Bộ lọc: bữa (sáng/trưa/tối), thời gian nấu tối đa, ưu tiên dinh dưỡng | Loaded / **Empty (kho quá ít → CTA thêm nguyên liệu)** / Loading / Error |
| S-02 | Giải thích điểm (sheet) | 4 thành phần `0.4E + 0.3A + 0.2P + 0.1U` kèm mô tả ngắn: E = dùng đồ cận hạn · A = tỉ lệ có sẵn · P = hợp khẩu phần/dinh dưỡng/sở thích · U = ít phải mua thêm | — |

### Nhóm 6 — Chi tiết món & Nấu ăn
| ID | Screen | Thành phần | Trạng thái |
|---|---|---|---|
| D-01 | Chi tiết món | Ảnh; `QtyStepper` khẩu phần (đổi khẩu phần → cập nhật định lượng & dinh dưỡng); thời gian chuẩn bị/nấu; **nguyên liệu** (✓ có sẵn / ⚠ thiếu + số cần mua); **gia vị**; **dinh dưỡng** theo món & **theo khẩu phần** (`MacroRing` E/P/C/L); nút "Thêm phần thiếu vào danh sách mua"; CTA **"Đã nấu món này"** | Loaded / Loading / Error |
| D-02 | Các bước nấu `[S]` (tuỳ MVP) | Từng bước, chế độ toàn màn hình, giữ màn sáng, điều hướng bước | — |
| D-03 | Xác nhận sau nấu | `QuickActionSheet`: **Đúng định lượng · Một nửa · Dùng hết · Tự điều chỉnh** | — |
| D-04 | Tự điều chỉnh lượng dùng `[S]` | Danh sách nguyên liệu + slider/nhập lượng thực dùng | — |
| D-05 | Xem trước trừ kho | Bảng "trước → sau" cho từng nguyên liệu; xác nhận | có nguyên liệu về 0 → gợi ý thêm vào danh sách mua |
| D-06 | Lưu phần ăn thừa `[S]` | Số khẩu phần còn lại + đặt **thời gian nhắc dùng** → tạo "thức ăn đã nấu" ở tầng *Ăn liền* | bỏ qua |
| D-07 | Hoàn tất + phản hồi tiết kiệm `[S]` | "Đã cập nhật kho · Bạn vừa tận dụng 2 nguyên liệu cận hạn" | — |

### Nhóm 7 — Dinh dưỡng
| ID | Screen | Thành phần | Ghi chú |
|---|---|---|---|
| N-01 | Ưu tiên khẩu phần | 4 lựa chọn (cân bằng / nhiều protein / ít năng lượng / nhiều rau) | Dùng ở onboarding & Cài đặt; đưa vào xếp hạng gợi ý |
| N-02 | Mục tiêu dinh dưỡng `[P]` | Đặt kcal / macro mục tiêu theo ngày; trạng thái khoá cho Free | — |

### Nhóm 8 — Thực đơn tuần `[P]`
| ID | Screen | Thành phần | Trạng thái |
|---|---|---|---|
| M-01 | Lưới thực đơn tuần | 7 ngày × (sáng/trưa/tối); ô trống "+" và ô đã gán món (ảnh nhỏ + tên) | Loaded / Empty / **Locked (Free) → preview mờ + Paywall** |
| M-02 | Gán món vào ô `[S]` | Chọn từ Gợi ý / Tìm kiếm / Lịch sử món | — |

### Nhóm 9 — Danh sách mua sắm
| ID | Screen | Thành phần | Trạng thái |
|---|---|---|---|
| B-01 | Danh sách mua sắm | Sinh từ thực đơn tuần; **nhóm theo danh mục**; mỗi item: tên, số lượng cần, nhãn "đã có trong kho" (mặc định ẩn khỏi danh sách cần mua), checkbox "đã mua"; tổng chi phí ước tính (tuỳ chọn) | Loaded / **Empty (chưa có thực đơn → CTA lập thực đơn)** / Loading |
| B-02 | Thêm món thủ công `[S]` | tên, số lượng, đơn vị, danh mục | — |
| B-03 | "Mua ở đối tác" `[S]` | Vùng disabled + badge "Sắp có" (định hướng affiliate mục 8.5) | — |

### Nhóm 10 — Thông báo
| ID | Screen | Thành phần | Trạng thái |
|---|---|---|---|
| T-01 | Trung tâm thông báo | Danh sách cảnh báo cận hạn + hệ thống, nhóm theo ngày, chấm "chưa đọc", tap → deep link | Loaded / Empty / Loading |
| T-02 | Chi tiết cảnh báo cận hạn (sheet) `[S]` | Nguyên liệu, "còn X ngày", nút "Xem món gợi ý" · "Đánh dấu đã dùng" | — |

### Nhóm 11 — Báo cáo `[P]`
| ID | Screen | Thành phần | Trạng thái |
|---|---|---|---|
| R-01 | Báo cáo chống lãng phí | Số nguyên liệu dùng trước hạn, lượng rác tránh được (kg), số món đã nấu; theo tuần/tháng; biểu đồ. **Không có số tiền** (thiếu dữ liệu giá) | Loaded / Empty |
| ~~R-02 Báo cáo chi tiêu~~ | Hoãn — cần dữ liệu giá nguyên liệu (OCR chưa lấy được) | — |

### Nhóm 12 — Cá nhân / Cài đặt
| ID | Screen | Thành phần |
|---|---|---|
| P-01 | Hồ sơ / tài khoản | tên, email, avatar; đổi mật khẩu; đăng xuất; xoá tài khoản |
| P-02 | Gói dịch vụ | gói hiện tại + quyền lợi; CTA nâng cấp → G-05 |
| P-03 | Tuỳ chọn | ưu tiên dinh dưỡng (N-01), đơn vị đo mặc định, ngôn ngữ |
| P-04 | Cài đặt thông báo | bật/tắt loại thông báo, thời điểm nhắc cận hạn |
| P-05 | Chia sẻ tủ bếp `[P]` | mời thành viên (tối đa 4), danh sách thành viên; **MVP: chỉ trạng thái khoá + Paywall** |
| P-06 | Giới thiệu & dữ liệu | nguồn dinh dưỡng (Viện Dinh dưỡng Quốc gia [6], FoodKeeper [7]); **disclaimer**: thông tin dinh dưỡng chỉ mang tính ước tính, không thay thế tư vấn y tế; nhắc kiểm tra màu/mùi thực phẩm thực tế |

**Tổng: ~55 screen/biến thể.** Ưu tiên MVP: Nhóm 0–7 + 9 (một phần) + 10 + 12. Nhóm 8, 11 và P-05 chỉ cần bản thiết kế + trạng thái khoá.

---

## 6. Checklist thiết kế cho mỗi screen (copy vào từng file design)

- [ ] **Mục đích** (1 câu)
- [ ] **Vào từ đâu / đi tới đâu** (điểm vào & ra)
- [ ] **Dữ liệu hiển thị** — map tới entity/field ở phần 8/9
- [ ] **Component tái dùng** đã dùng (phần 3.2)
- [ ] **4 trạng thái**: Loading / Empty / Error / Loaded (+ Offline nếu cần)
- [ ] **Hành động** & kết quả (bao gồm undo/confirm)
- [ ] **Freemium**: có bị gate không? thiết kế trạng thái khoá + điểm chạm Paywall
- [ ] **Edge case**: text tiếng Việt dài, số lượng/đơn vị lạ, danh sách rất dài, quyền bị từ chối, không có mạng
- [ ] **Dark mode**
- [ ] **Liên kết mục spec** (VD: 6.3.3)

---

## 7. Thứ tự thực hiện (design → code)

| Giai đoạn | Design | Code (sau khi design duyệt) |
|---|---|---|
| **0. Nền tảng** | Tokens + Component sheet (3.2) + G-01..G-07 + IA | fix `.gitignore` (`lib/`), `flutter create` android/ios/web, deps, theme, l10n vi, router shell, `AppConfig`, Dio + interceptors, `Failure`, `MockApiClient` + `assets/mock/*.json`, CI |
| **1. Auth + Onboarding** | A-01..A-06 | auth flow, lưu token, guard, onboarding |
| **2. Home + Kho (lõi)** | H-01, K-01..K-04 | pantry list 4 tầng, detail, thêm/sửa/consume thủ công, dashboard |
| **3. Nhập đa phương thức** | I-01..I-09 | camera + crop, 3 luồng review, quota + xử lý 402 |
| **4. Gợi ý + Món + Nấu** | S-01..S-02, D-01..D-07 | suggestion list, dish detail, post-cook confirm → trừ kho, leftover |
| **5. Dinh dưỡng + Thông báo** | N-01, T-01..T-02 | dietary preference vào gợi ý; FCM + đăng ký device + deep link + notification center |
| **6. Premium** | G-05, M-01..M-02, B-01..B-03, R-01..R-02, N-02, P-05 | meal plan, shopping list (dedup vs kho), reports, paywall + gating toàn app |
| **7. Hoàn thiện** | minh hoạ empty/error, motion, rà dark mode | golden test, integration test vòng lặp cốt lõi (thêm→gợi ý→nấu→trừ kho), a11y, build flavors, APK/TestFlight beta |

---

## 8. Cây thư mục `lib/` (khi bắt đầu code)

```
lib/
├── main.dart
├── bootstrap.dart
├── app/
│   ├── app.dart                  # MaterialApp.router
│   ├── router/                   # go_router: routes, auth guard, deep links
│   └── theme/                    # tokens, color scheme, typography
├── l10n/                         # app_vi.arb (mặc định), app_en.arb
├── core/
│   ├── config/                   # AppConfig (--dart-define), flavor, ApiPaths
│   ├── network/                  # ApiClient (abstract) | DioApiClient | MockApiClient
│   │   ├── interceptors/         # auth, refresh, logging, retry
│   │   └── api_result.dart
│   ├── error/                    # Failure (sealed) + mapper
│   ├── storage/                  # SecureStorage (token), Prefs
│   ├── notifications/            # FcmService + local notifications
│   ├── permissions/              # camera / mic / notification
│   ├── entitlements/             # Entitlements, provider, <Gated>, PaywallSheet
│   ├── analytics/                # AnalyticsService + events
│   ├── media/                    # ImageCaptureService, AudioRecorderService
│   ├── utils/                    # formatters: currency_vnd, expiry_text
│   └── widgets/                  # component sheet ở 3.2
├── features/
│   ├── auth/        onboarding/   pantry/        ingest/
│   ├── suggestions/ dishes/       cooking/       nutrition/
│   ├── meal_plan/   shopping_list/ notifications/ reports/   settings/
└── shared/domain/                # nutrition_info, storage_tier, unit
```
Mỗi feature: `data/{datasources,models,repositories}` · `domain/{entities,repositories}` · `presentation/{controllers,screens,widgets}`. Lớp `usecases/` tuỳ chọn — CRUD đơn giản gọi thẳng repository.

---

## 9. Hợp đồng API frontend giả định (mock-first)

Base `/api/v1`, Bearer JWT. Dùng làm `../../docs/api-contract.md` chung với backend; trong lúc chờ, `MockApiClient` trả JSON từ `assets/mock/`.

- **Auth:** `POST /auth/register` · `/auth/login` · `/auth/refresh` · `/auth/logout` · `GET /auth/me`
- **Catalog:** `GET /ingredients?query=` (autocomplete + dinh dưỡng/100g) · `GET /ingredients/{id}`
- **Pantry:** `GET /pantry/items?tier=&status=&sort=priority` · `POST /pantry/items` · `POST /pantry/items:batch` · `PATCH /pantry/items/{id}` · `DELETE` · `POST /pantry/items/{id}/consume` · `GET /pantry/summary`
- **Scan:** `POST /scan/label` · `/scan/receipt` · `/scan/voice` (multipart) → `ScanJob` · `GET /scan/jobs/{id}` · `POST /scan/jobs/{id}/confirm` · trả `402` khi vượt quota
- **Suggestions:** `POST /suggestions/dishes {dietaryPreference,maxCookTime,mealType,limit=5}` → `List<DishSuggestion>` (server chấm `0.4E+0.3A+0.2P+0.1U`) · `GET /dishes/{id}`
- **Cooking:** `POST /dishes/{id}/cook {mode,customUsage,servingsCooked}` → `{updatedPantryItems, leftover?}` · `POST /pantry/cooked-food`
- **Meal plan `[P]`:** `GET /meal-plans?weekStart=` · `PUT /meal-plans/{weekStart}` · entry CRUD
- **Shopping list:** `POST /shopping-lists/generate {weekStart|mealPlanId}` (dedup vs pantry) · `GET /shopping-lists/{id}` · `PATCH …/items/{itemId} {checked}`
- **Devices/Notifications:** `POST /devices {fcmToken,platform}` · `DELETE /devices/{token}` · `GET /notifications` · `POST /notifications/{id}/read`
- **Subscription:** `GET /subscription` (tier + entitlements) · `POST /subscription/checkout` (MVP: mock)
- **Reports:** `GET /reports/waste-reduction?period=` (đếm nguyên liệu dùng trước hạn + kg tránh lãng phí)

### Domain model rút gọn
`User` · `SubscriptionTier{free,premiumMonthly,premiumYearly,premiumFamily}` · `Entitlements{maxActiveIngredients(40/∞), scansPerMonth(10/∞), weeklyPlanner, nutritionGoals, reports, pantrySharing, dishHistory, customReminders}`
`StorageTier{eatSoon,fridge,freezer,pantryShelf}` · `Unit{g,kg,ml,l,cai,bo,hop,goi,…}`
`Ingredient{id,name,category,defaultUnit,nutritionPer100g?}`
`PantryItem{id,ingredientId,name,category,quantity,unit,storageTier,addedAt,packedDate?,expiryDate?,referenceShelfLifeDays?,source,priceVnd?,status}` + computed `daysUntilExpiry`,`priorityScore`,`isNearExpiry`
`NutritionInfo{energyKcal,proteinG,carbG,lipidG}`
`Dish{id,name,imageUrl?,servings,prepTimeMin,cookTimeMin,cuisine,ingredients:[DishIngredient{qty,unit,isSeasoning,availableInPantry,missingQty}],steps:[CookingStep{order,text,durationMin?}],nutritionTotal,nutritionPerServing}`
`DishSuggestion{dish,score,breakdown{e,a,p,u},nearExpiryIngredients,availabilityRatio,toBuyCount}`
`CookConfirmation{dishId,mode{exact,half,all,custom},customUsage:Map,leftoverServings?,leftoverReminderAt?}`
`CookedFood` · `MealPlan/MealPlanEntry{date,mealType,dishId}`
`ShoppingList/ShoppingListItem{name,qty,unit,category,checked,fromDishIds,estPriceVnd?}`
`ScanJob{type,status,rawText?,parsedItems:[ParsedItemDraft{name,qty?,unit?,packedDate?,expiryDate?,priceVnd?,confidence,suggestedStorageTier,suggestedCategory}]}`
`ExpiryAlert` · `WasteReductionSummary`

---

## 10. Analytics (phục vụ đo lường thử nghiệm — mục 7 & 13 spec)

Phát event cho: hoàn tất setup kho lần đầu · thời gian nhập 1 nguyên liệu (theo phương thức) · **tỉ lệ user sửa field OCR** (proxy độ chính xác) · quét thất bại · retention (D1/D7) · số món được mở / được chọn nấu · **tỉ lệ dùng nguyên liệu trước hạn** · mở Paywall / chọn gói · bật thông báo.

---

## 11. Cần chốt trước khi design sâu

1. **Bottom nav 5 tab** như phần 4 ổn chứ? (thay thế: gộp "Mua sắm" vào "Kho", thêm "Thực đơn").
2. **Dark mode** có nằm trong MVP không? (ảnh hưởng khối lượng design ~1.6×)
3. **Nguồn design**: bắt đầu từ Material 3 mặc định + seed tự chọn, hay có Figma/brand kit sẵn (Khánh Vi – HTTT)?
4. **Auth**: chỉ email/mật khẩu, hay thêm Google / OTP SĐT? (ảnh hưởng A-02..A-04)
5. **Bước nấu (D-02)**: có làm chế độ nấu từng bước toàn màn hình trong MVP không, hay chỉ liệt kê trong D-01?
6. **Ảnh món ăn**: có nguồn ảnh thật hay dùng placeholder cho MVP?
7. **Web**: là target demo thật hay chỉ tiện dev? (ảnh hưởng việc vẽ layout ≥ 600px)
8. **Package id / tên app**: đề xuất `com.cloudian.sweepfood` / `sweep_food` / hiển thị "SweepFood".
9. **Deadline cuộc thi / ngày demo** để chốt độ dài từng giai đoạn ở phần 7.

---

## 12. Việc backend đang chặn (gửi cho người phụ trách backend)

1. Thêm **CORS middleware** (cho `localhost:*` khi dev) — bắt buộc cho Flutter web.
2. Đổi prefix router `/api` → **`/api/v1`** (`src/backend/src/app.py` đặt tên `v1_router` nhưng prefix chỉ `/api`).
3. Auth + JWT (register/login/refresh/me).
4. Chốt `docs/api-contract.md` (hoặc OpenAPI) làm nguồn chung FE⇄BE.
5. Endpoint multipart cho scan (tem/hoá đơn/giọng nói); quyết định sync vs async + job polling.
6. Envelope lỗi thống nhất `{error:{code,message,fields?}}`; dùng `402` cho quota; quy ước pagination.
7. Hosting ảnh món (trả URL) hoặc placeholder.
8. FCM sender + endpoint đăng ký device token.
