# BẢNG THIẾT KẾ GIAO DIỆN (UI/UX DESIGN SPECIFICATION)
## Chức năng: Thống kê & Báo cáo Sử dụng Thực phẩm (Food Analytics & Reports)

Tài liệu thiết kế chi tiết cho module Thống kê gồm 3 tính năng cốt lõi:
1. **Xem lịch sử sử dụng thực phẩm** (Food Usage History)
2. **Thống kê thực phẩm lãng phí** (Food Waste Statistics)
3. **Đánh giá hiệu quả sử dụng** (Usage Efficiency Evaluation)

---

## 1. Kiến trúc Giao diện & Điều hướng (Information Architecture)

```
                            [ Màn hình Thống kê: ReportsScreen ]
                                             |
                  +--------------------------+--------------------------+
                  |                          |                          |
        [Tab 1: Lịch sử sử dụng]   [Tab 2: Thực phẩm lãng phí]  [Tab 3: Đánh giá hiệu quả]
                  |                          |                          |
        - Bộ lọc kỳ (Tuần/Tháng)   - Hero Card: Tổng kg lãng phí- Điểm hiệu quả (Score/Gauge)
        - Thẻ tóm tắt tổng lượng   - Tỷ lệ lãng phí theo nhóm   - Tỷ lệ tận dụng kho (%)
        - Timeline danh sách dùng  - Biểu đồ phân bố lý do      - Xu hướng so sánh kỳ trước
        - Tag trạng thái (Kịp thời)- Danh sách chi tiết lô hỏng  - Đề xuất & Insights thông minh
```

---

## 2. Bảng Đặc tả Chi tiết Thành phần UI (UI Component Specifications)

### 2.1 Tab 1: Lịch sử sử dụng thực phẩm (Food Usage History)

| STT | Thành phần UI | Quy cách thiết kế (Design Tokens / Layout) | Dữ liệu & Trạng thái | Hành vi người dùng |
|:---|:---|:---|:---|:---|
| 1 | **Header Summary Card** | Container `primaryContainer`, border-radius `Radii.brLg` (16dp), padding `Gap.md` | Hiển thị: Tổng số lượt dùng (vd: "38 lượt"), Tổng khối lượng ("14.5 kg"), Kỳ thống kê | Tự động cập nhật khi đổi kỳ `PeriodSelector` |
| 2 | **Usage Timeline Card** | Card `surfaceContainerLowest`, viền `hairline`, padding `Gap.md`, margin dọc `Gap.xs` | - Tên nguyên liệu (`text.titleMedium`, bold)<br>- Số lượng + đơn vị (vd: "300 g", "500 ml")<br>- Món ăn chế biến hoặc "Tiêu thụ trực tiếp"<br>- Badge trạng thái: `Kịp thời` (Xanh lá) hoặc `Quá hạn` (Đỏ gạch)<br>- Thời gian: Ngày giờ định dạng `dd/MM/yyyy · HH:mm` | Chạm để xem chi tiết phiên nấu hoặc chi tiết lô kho tương ứng |
| 3 | **Empty State** | Icon `Icons.history_toggle_off_rounded`, `EmptyState` chuẩn | "Chưa có lịch sử sử dụng" - "Các lượt nấu ăn và tiêu thụ thực phẩm sẽ hiển thị tại đây." | Nút CTA: "Khám phá gợi ý món" dẫn về `/suggestions` |

### 2.2 Tab 2: Thống kê thực phẩm lãng phí (Food Waste Statistics)

| STT | Thành phần UI | Quy cách thiết kế (Design Tokens / Layout) | Dữ liệu & Trạng thái | Hành vi người dùng |
|:---|:---|:---|:---|:---|
| 1 | **Hero Waste Card** | Container màu cảnh báo nhẹ `BrandPalette.brick100`, viền cam gạch, padding `Gap.lg` | - Khối lượng lãng phí: "1.25 kg" (`headlineMedium`, `brick500`)<br>- Số món bị bỏ: "3 món/lô"<br>- Tỷ lệ lãng phí trên tổng kho | Trực quan hóa mức độ cần chú ý để giảm thiểu |
| 2 | **Category Breakdown Card** | Card `surfaceContainerLowest`, chứa danh sách thanh tiến trình (Linear Progress Bars) | Phân bố lãng phí theo nhóm thực phẩm:<br>- Rau củ quả: 60% (màu xanh lá úa)<br>- Sữa & Chế phẩm: 24% (màu vàng cam)<br>- Thịt cá tươi sống: 16% (màu đỏ gạch) | Hiển thị tỷ lệ % và số kg tương ứng |
| 3 | **Waste Reasons Card** | Card dạng pills / chips với số lượng | - Hết hạn sử dụng: 66.7%<br>- Hư hỏng do bảo quản: 33.3% | Giúp người dùng nhận diện thói quen gây lãng phí |
| 4 | **Wasted Items List** | Danh sách các `ListTile` gọn gàng | Tên nguyên liệu, số lượng bỏ phí, ngày hết hạn/loại bỏ, lý do bỏ | Xem lại các thực phẩm đã bỏ để rút kinh nghiệm mua sắm |

### 2.3 Tab 3: Đánh giá hiệu quả sử dụng (Usage Efficiency Evaluation)

| STT | Thành phần UI | Quy cách thiết kế (Design Tokens / Layout) | Dữ liệu & Trạng thái | Hành vi người dùng |
|:---|:---|:---|:---|:---|
| 1 | **Efficiency Score Gauge** | Circular/Arc Progress Indicator trung tâm hoặc Hero Score Card, màu động theo điểm: >=85 (Xanh lá `green600`), 70-84 (Vàng chanh), <70 (Cam/Đỏ) | Điểm số lớn: **88 / 100**<br>Huy hiệu: "Quản lý Bếp Xuất sắc" (Badge với icon `workspace_premium`) | Nhấn vào để xem cách tính điểm |
| 2 | **KPI Comparison Row** | 2 thẻ con đối xứng `Row` chia đều: | - **Tận dụng kho:** 92.1% (icon `trending_up`, xanh)<br>- **Tỷ lệ lãng phí:** 7.9% (icon `trending_down`, cam) | So sánh xu hướng (+3.2% so với kỳ trước) |
| 3 | **Smart Insights & Tips** | Danh sách các Card bo góc, icon bóng đèn `lightbulb_rounded` hoặc `eco_rounded` | Gợi ý hành động thông minh dựa trên dữ liệu thực tế:<br>1. *Ưu điểm:* Bạn sử dụng 92% thực phẩm cận hạn kịp thời.<br>2. *Lời khuyên:* Nhóm rau lá dễ hỏng sau 3 ngày, hãy ưu tiên nấu trong 48h đầu sau khi mua. | Cung cấp giá trị thiết thực giúp tiết kiệm chi phí |

---

## 3. Bảng Màu & Typography (Design System Tokens)

```scss
// Colors
Primary Green:       BrandPalette.green600 (#2E7D32)
Primary Light:       BrandPalette.green100 (#E8F5E9)
Waste Accent:        BrandPalette.brick500 (#C62828)
Waste Light:         BrandPalette.brick100 (#FFEBEE)
Warning Amber:       BrandPalette.warnPrimary (#F57C00)
Surface Lowest:      theme.colorScheme.surfaceContainerLowest (#FFFFFF)
Hairline Border:     context.sweep.hairline (#E0E0E0 / #333333)

// Typography
Score Display:       TextTheme.displaySmall / headlineLarge (Weight 800)
Section Title:       TextTheme.titleMedium (Weight 700)
Subhead / Metric:    TextTheme.bodyMedium (Weight 500)
Caption / Timestamps:TextTheme.bodySmall (Weight 400, onSurfaceVariant)
```

---

## 4. Xử lý Trạng thái Màn hình (States Handling)

| Trạng thái | Giao diện hiển thị |
|:---|:---|
| **Loading** | Shimmer Skeleton hoặc `CircularProgressIndicator` đồng bộ ở trung tâm tab |
| **Empty** | `EmptyState` widget với hình minh họa, thông điệp rõ ràng theo ngữ cảnh từng tab |
| **Error / Offline** | Thẻ cảnh báo lỗi kèm nút "Thử lại" (`onRetry`), tự động fallback sang offline cache hoặc mock data chuẩn |
| **Success** | Nội dung render mượt mà với hoạt ảnh chuyển động nhẹ (fade/slide transition) |
