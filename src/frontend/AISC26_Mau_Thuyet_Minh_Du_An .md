TRƯỜNG ĐẠI HỌC CÔNG NGHỆ THÔNG TIN

KHOA HỆ THỐNG THÔNG TIN

**BAN TỔ CHỨC AISC’26**

**MẪU CHUẨN**

**THUYẾT MINH DỰ ÁN**

**ADVANCED INFORMATION SYSTEMS CONTEST 2026**

**PHẦN I: THÔNG TIN CHUNG**

1.  **Tên đội thi:** Phantoms
2.  **Chủ đề đăng ký:** _Data Driven Business_
**PHẦN II: THÔNG TIN DỰ ÁN**

1.  **Tên dự án (tên đề tài)**

| **Tên Tiếng Việt** | SweepFood - Trợ lý quản lý nguyên liệu và gợi ý bữa ăn thông minh |
| --- | --- |
| **Tên Tiếng Anh** | SweepFood - Smart Pantry and Meal Planning Assistant |
| --- | --- |

**Lĩnh vực:** Công nghệ ẩm thực & sức khỏe (FoodTech & HealthTech)

1.  **Bối cảnh và bài toán**
    1.  **Bối cảnh:**

Lãng phí thực phẩm là một vấn đề có quy mô lớn trên toàn cầu. Theo Chương trình Môi trường Liên Hợp Quốc, khoảng 1,05 tỷ tấn thực phẩm đã bị lãng phí tại hộ gia đình, dịch vụ ăn uống và bán lẻ trong năm 2022; trong đó, hộ gia đình tạo ra khoảng 60% tổng lượng lãng phí được ghi nhận \[1\].

Tại Việt Nam, một khảo sát của CEL Consulting năm 2018 ước tính khoảng 8,8 triệu tấn thực phẩm bị thất thoát trước khi đến khâu chế biến hoặc phân phối, tương đương khoảng 3,9 tỷ USD \[2\]. Số liệu này phản ánh thất thoát trong chuỗi cung ứng, không phải riêng lượng thực phẩm bị bỏ đi tại hộ gia đình. Ở góc độ người tiêu dùng, Food Bank Vietnam dẫn lại kết quả cho thấy 87% người được hỏi thừa nhận đã lãng phí trung bình khoảng hai đĩa thức ăn mỗi tuần \[3\].

Bên cạnh đó, cơ cấu hộ gia đình tại Việt Nam đang thay đổi. Năm 2024, Việt Nam có hơn 28,1 triệu hộ dân cư; trong đó, hộ chỉ có một người chiếm 12,1%. Tỷ lệ hộ một người tại khu vực thành thị đạt 14,7%, cao hơn khu vực nông thôn là 10,3% \[4\]. Sự gia tăng của nhóm sống một mình cho thấy nhu cầu ngày càng lớn đối với các giải pháp hỗ trợ quản lý thực phẩm, khẩu phần và bữa ăn cá nhân.

Đồng thời, tỷ lệ sử dụng điện thoại thông minh tại Việt Nam đã đạt mức cao, tạo điều kiện thuận lợi cho việc triển khai một giải pháp quản lý bữa ăn dưới dạng ứng dụng di động \[5\].

Từ bối cảnh trên, nhóm đề xuất SweepFood nhằm hỗ trợ người trẻ sống một mình hoặc ở ghép ghi nhận nguyên liệu nhanh, theo dõi thời gian bảo quản, ưu tiên sử dụng thực phẩm trước khi bị lãng phí và lựa chọn món ăn phù hợp với nhu cầu dinh dưỡng.

- 1.  **Vấn đề cần giải quyết**
- _Ai đang gặp vấn đề?_

Đối tượng gặp vấn đề chính là người trẻ từ 18–30 tuổi đang sống một mình hoặc ở ghép tại khu vực đô thị, có thói quen tự nấu ăn từ ba bữa mỗi tuần nhưng chưa có phương pháp quản lý nguyên liệu trong bếp.

Nhóm người dùng này thường mua thực phẩm với số lượng nhỏ, có lịch sinh hoạt không ổn định và dễ thay đổi kế hoạch ăn uống. Vì vậy, thực phẩm đã mua có thể bị quên, hết hạn hoặc không được sử dụng hết.

Trong giai đoạn phát triển tiếp theo, sản phẩm có thể mở rộng đến các gia đình trẻ có từ hai đến bốn thành viên.

- _Vấn đề là gì?_

Người dùng đang gặp ba khó khăn chính:

- Không nhớ chính xác trong bếp còn những nguyên liệu nào, số lượng bao nhiêu và khi nào nên sử dụng.
- Không biết nguyên liệu nào cần được ưu tiên sử dụng trước, đặc biệt với thực phẩm tươi không có hạn sử dụng rõ ràng, dẫn đến tình trạng bỏ quên hoặc để thực phẩm hư hỏng.
- Mỗi ngày phải tự quyết định món ăn từ đầu, trong khi các công thức tìm được có thể yêu cầu mua thêm nhiều nguyên liệu.

Các khó khăn trên tạo thành một vòng lặp: mua dư → quên nguyên liệu → không biết nấu món gì → tiếp tục mua thêm → thực phẩm cũ bị bỏ phí.

- _Vì sao cần giải quyết?_

Vấn đề cần được giải quyết vì xảy ra thường xuyên và gây ra ba tác động trực tiếp. Thứ nhất, người dùng mất tiền cho những thực phẩm đã mua nhưng không sử dụng. Thứ hai, họ mất thời gian kiểm tra nguyên liệu và quyết định món ăn mỗi ngày. Thứ ba, thực phẩm bị bỏ đi làm gia tăng lượng rác thải và tác động tiêu cực đến môi trường.

Tuy nhiên, giải pháp chỉ có thể mang lại hiệu quả nếu việc cập nhật nguyên liệu đủ nhanh và đơn giản. Vì vậy, SweepFood tập trung giảm tối đa thao tác nhập liệu thay vì yêu cầu người dùng quản lý tủ bếp như một hệ thống kho phức tạp.

- 1.  **Đối tượng hướng đến**

Khách hàng mục tiêu chính

- Độ tuổi: 18–30.
- Khu vực: Thành phố Hồ Chí Minh và các đô thị lớn.
- Hoàn cảnh sống: sống một mình hoặc ở ghép.
- Hành vi: tự nấu ít nhất ba bữa mỗi tuần.
- Khó khăn: mua dư, quên thực phẩm, không biết nấu món gì.
- Động lực: tiết kiệm chi phí, giảm thời gian suy nghĩ và ăn uống hợp lý hơn.
- Rào cản: không muốn nhập thủ công quá nhiều thông tin.

1.  **Mục tiêu của đề tài**

**Mục tiêu tổng quát:**

Xây dựng ứng dụng di động giúp người trẻ sống một mình quản lý nguyên liệu và tận dụng thực phẩm sắp hết hạn thông qua cơ chế nhập liệu nhanh và gợi ý bữa ăn phù hợp.

**Mục tiêu cụ thể:**

1.  Cho phép người dùng ghi nhận nguyên liệu từ tem nhãn, hóa đơn, giọng nói hoặc nhập thủ công.
2.  Theo dõi thời hạn sử dụng, hỗ trợ người dùng kiểm tra tình trạng thực phẩm và ước tính thời gian bảo quản đối với những nguyên liệu không có hạn sử dụng cụ thể.
3.  Đề xuất từ 3 đến 5 món ăn dựa trên nguyên liệu hiện có, ưu tiên thực phẩm cần dùng sớm và hạn chế số nguyên liệu cần mua thêm.
4.  Cung cấp thông tin dinh dưỡng ước tính theo món và theo khẩu phần, bao gồm năng lượng, protein, carbohydrate và lipid
5.  Tự động cập nhật số lượng nguyên liệu sau khi người dùng xác nhận đã nấu.
6.  Thử nghiệm với người dùng thật để đánh giá thời gian nhập liệu, mức độ hữu ích và khả năng duy trì sử dụng.
7.  **Tính cấp thiết, tính mới, ý tưởng khoa học của dự án**

**Tính cấp thiết**

Người trẻ sống một mình hoặc ở ghép thường phải tự thực hiện toàn bộ quá trình từ mua nguyên liệu, bảo quản, quyết định món ăn đến theo dõi lượng thực phẩm còn lại. Do quy cách đóng gói chưa phù hợp với khẩu phần một người và lịch sinh hoạt thường xuyên thay đổi, họ dễ mua dư, quên thực phẩm hoặc tiếp tục mua thêm khi trong bếp vẫn còn nguyên liệu.

Những vấn đề này không chỉ gây lãng phí tiền bạc mà còn tạo ra áp lực phải quyết định “hôm nay ăn gì” mỗi ngày. Tuy nhiên, một giải pháp quản lý tủ bếp chỉ có giá trị khi việc nhập và cập nhật dữ liệu đủ nhanh để người dùng duy trì lâu dài.

**Tính khác biệt của giải pháp**

Các chức năng quản lý nguyên liệu, theo dõi hạn sử dụng và gợi ý công thức đã xuất hiện riêng lẻ trên một số ứng dụng quốc tế. Vì vậy, tính khác biệt của SweepFood không nằm ở từng chức năng đơn lẻ, mà ở cách kết hợp chúng thành một quy trình được thiết kế cho hành vi mua sắm và nấu ăn của người Việt.

SweepFood tập trung vào bốn điểm khác biệt: nhận diện hóa đơn và tem cân phù hợp với dữ liệu tiếng Việt; hỗ trợ nguyên liệu tươi mua tại chợ bằng giọng nói hoặc nhập nhanh, đồng thời hướng dẫn người dùng kiểm tra tình trạng thực phẩm để ước tính thời gian bảo quản tham khảo; ưu tiên món Việt và khẩu phần phù hợp với người sống một mình; tự động cập nhật lượng nguyên liệu sau khi người dùng xác nhận đã nấu. Hệ thống đồng thời cung cấp thông tin dinh dưỡng ước tính theo khẩu phần để hỗ trợ người dùng lựa chọn món ăn.

Lợi thế dài hạn của sản phẩm là dữ liệu về tem nhãn, hóa đơn, nguyên liệu, món ăn và hành vi sử dụng thực phẩm tại thị trường Việt Nam. Dữ liệu này giúp hệ thống ngày càng phù hợp hơn với người dùng trong nước.

**Khả năng ứng dụng**

Giải pháp có thể được triển khai dưới dạng ứng dụng di động, sử dụng camera và microphone có sẵn trên điện thoại. Trong giai đoạn đầu, sản phẩm tập trung vào một số loại hóa đơn, tem nhãn và nguyên liệu phổ biến nhằm đảm bảo khả năng hoàn thiện prototype.

**Khả năng thương mại hóa**

Sản phẩm áp dụng mô hình Freemium. Các chức năng quản lý nguyên liệu và cảnh báo cơ bản được cung cấp miễn phí; các tính năng như lập thực đơn tuần, báo cáo chi tiêu, báo cáo thực phẩm đã tiết kiệm và chia sẻ tủ bếp được đưa vào gói Premium. Khả năng trả phí, giới hạn giữa các gói và mức giá sẽ được kiểm chứng thông qua khảo sát, thử nghiệm giá và hành vi sử dụng thực tế.

1.  **Các giải pháp khác hiện nay để xử lý vấn đề tương tự? Ưu điểm và hạn chế**

**Nền tảng đề xuất Công thức dựa trên nguyên liệu. Ví dụ**: **Ứng dụng SuperCook - Zero Waste Recipe Generator \[8\]**

Đây là mô hình công cụ tìm kiếm theo cơ chế “Có gì nấu nấy”. Người dùng sẽ tiến hành nhập các nguyên liệu họ có sẵn, hệ thống sẽ rà soát chéo với cơ sở dữ liệu và trả về danh sách các món ăn có thể nấu. Người dùng không cần mua thêm nguyên liệu.

<div class="joplin-table-wrapper"><table><thead><tr><th><p><strong>Ưu điểm</strong></p></th><th><p><strong>Nhược điểm</strong></p></th></tr><tr><th><ul><li>Giảm thiểu lãng phí nguyên liệu: Có thể phản hồi nhanh chóng và xử lý lượng nguyên liệu lẻ tẻ</li><li>Cơ sở dữ liệu lớn: Sở hữu hàng triệu công thức nấu ăn khác nhau, từ đó có thể đề xuất ra rất nhiều món ăn, tạo ra sự lựa chọn đa dạng cho người dùng</li><li>Thao tác đơn giản: Người dùng chỉ cần thao tác nhập liệu bằng tay, hoặc lựa chọn nguyên liệu bằng cách chạm tay, hoặc có thể sử dụng giọng nói.</li></ul></th><th><ul><li>SuperCook tập trung vào tìm kiếm công thức từ danh sách nguyên liệu, trong khi quản lý số lượng, thời hạn và vòng đời của nguyên liệu không phải chức năng trọng tâm.</li></ul></th></tr></thead></table></div>

**Ứng dụng quản lý tồn kho bếp & quét mã vạch món ăn. Ví dụ: KitchenPal \[9\], Pantry Check \[10\]**

Mô hình hoạt động như một hệ thống quản trị kho hàng thu nhỏ. Người dùng dùng camera điện thoại để quét mã vạch (barcode) của sản phẩm sau khi mua về. Ứng dụng sẽ số hóa danh sách thực phẩm, tự động đếm ngược hạn sử dụng để người dùng dễ theo dõi, cũng như mua thêm khi sắp hết nguyên liệu đó.

<div class="joplin-table-wrapper"><table><thead><tr><th><p><strong>Ưu điểm</strong></p></th><th><p><strong>Nhược điểm</strong></p></th></tr><tr><th><ul><li>Quản trị chi tiết: Theo dõi chính xác ngày hết hạn, chống lãng phí cực kỳ hiệu quả với các thực phẩm đồ hộp, đóng gói.</li><li>Kiểm soát dinh dưỡng tốt: Đọc được thông tin macro/calories trực tiếp từ mã vạch của nhà sản xuất.</li><li>Đồng bộ gia đình: Cho phép các thành viên trong nhà cùng theo dõi tủ lạnh và chia sẻ danh sách mua sắm.</li></ul></th><th><ul><li>Việc duy trì dữ liệu kho vẫn yêu cầu người dùng cập nhật thường xuyên. Thông tin công khai của các sản phẩm chưa cho thấy sự tập trung vào hóa đơn tiếng Việt, tem cân, tên nguyên liệu mua tại chợ, đơn vị đo địa phương và món ăn dành cho khẩu phần một người tại Việt Nam.</li></ul></th></tr></thead></table></div>

Tóm lại, SuperCook cho phép người dùng xây dựng danh sách nguyên liệu và tìm công thức từ những gì đang có, đồng thời hỗ trợ nhập nguyên liệu bằng giọng nói \[8\]. KitchenPal cung cấp nhiều chức năng như quản lý pantry, barcode, cảnh báo thời hạn, gợi ý món, dinh dưỡng, danh sách mua sắm và đồng bộ gia đình \[9\]. Pantry Check tập trung vào quét barcode, theo dõi số lượng, giá và thời hạn sử dụng \[10\].

Các sản phẩm trên chứng minh nhu cầu quản lý thực phẩm và tìm món ăn đã tồn tại. Tuy nhiên, thông tin công khai của các sản phẩm này chưa cho thấy sự tập trung vào hóa đơn, tem cân, tên nguyên liệu, đơn vị đo và món ăn đặc trưng của thị trường Việt Nam.

| Tiêu chí | SuperCook | KitchenPal | PantryCheck | SweepFood |
| --- | --- | --- | --- | --- |
| Tìm món từ nguyên liệu có sẵn | Có  | Có  | Không phải trọng tâm | Có  |
| --- | --- | --- | --- | --- |
| Theo dõi số lượng và thời hạn | Không phải trọng tâm | Có  | Có  | Có  |
| --- | --- | --- | --- | --- |
| Nhập barcode | Không phải trọng tâm | Có  | Có  | Có thể hỗ trợ |
| --- | --- | --- | --- | --- |
| Nhập bằng giọng nói | Có  | Có  | Hạn chế | Có  |
| --- | --- | --- | --- | --- |
| Dinh dưỡng món ăn | Không phải trọng tâm | Có  | Không phải trọng tâm | Có, theo khẩu phần |
| --- | --- | --- | --- | --- |
| Quét hóa đơn/ tem cân Việt Nam | Chưa thấy công bố hỗ trợ | Chưa thấy công bố hỗ trợ | Chưa thấy công bố hỗ trợ | Chức năng trọng tâm |
| --- | --- | --- | --- | --- |
| Món Việt và khẩu phần một người | Chưa phải trọng tâm | Chưa phải trọng tâm | Chưa phải trọng tâm | Phân khúc trọng tâm |
| --- | --- | --- | --- | --- |
| Ưu tiên thực phẩm cần dùng sớm | Hạn chế | Có  | Có cảnh báo | Có, gắn với gợi ý món |
| --- | --- | --- | --- | --- |
| Cập nhật kho theo luồng nấu | Chưa phải trọng tâm | Có quản lý tồn kho | Người dùng đánh dấu đã dùng | Tự trừ sau khi xác nhận nấu |
| --- | --- | --- | --- | --- |

Qua phân tích, SweepFood không cạnh tranh bằng số lượng công thức hoặc số lượng tính năng. Sản phẩm tập trung vào trải nghiệm bản địa hóa cho người Việt và duy trì dữ liệu kho thực phẩm với ít thao tác nhất.

_Nguồn: Tổng hợp của nhóm từ thông tin công khai của SuperCook, KitchenPal và Pantry Check \[8\], \[9\], \[10\]. Các tính năng có thể thay đổi theo phiên bản._

1.  **Giải pháp đề xuất của nhóm**

**6.1. Tổng quan giải pháp SweepFood**

SweepFood là ứng dụng di động hỗ trợ người trẻ sống một mình quản lý nguyên liệu và quyết định bữa ăn hằng ngày. Người dùng có thể nhập thực phẩm bằng cách chụp hóa đơn, quét tem nhãn hoặc sử dụng giọng nói. Hệ thống theo dõi thời hạn sử dụng, ưu tiên nguyên liệu cần dùng sớm và đề xuất khoảng 5-7 món ăn phù hợp. Đối với thực phẩm không có hạn sử dụng cụ thể, ứng dụng hỗ trợ người dùng kiểm tra một số thông tin liên quan đến tình trạng và điều kiện bảo quản để đưa ra thời gian bảo quản tham khảo.

Sau khi người dùng chọn và hoàn thành một món, ứng dụng tự động trừ lượng nguyên liệu dự kiến, đồng thời cho phép điều chỉnh nhanh lượng thực tế đã sử dụng. Nhờ đó, kho thực phẩm được duy trì chính xác mà không yêu cầu người dùng nhập lại quá nhiều thông tin.

**6.2. Kiến trúc hệ thống và Tech Stack**

SweepFood được xây dựng dưới dạng ứng dụng di động theo mô hình Client–Server. Ứng dụng phía người dùng hỗ trợ camera, microphone và các thao tác quản lý nguyên liệu; phía máy chủ xử lý dữ liệu, quản lý tài khoản, lưu trữ kho thực phẩm và thực hiện đề xuất món ăn.

Hệ thống dự kiến sử dụng Flutter để phát triển ứng dụng di động, FastAPI cho backend và PostgreSQL làm cơ sở dữ liệu chính. Các công nghệ OCR, nhận diện giọng nói và xử lý hình ảnh được sử dụng để hỗ trợ nhập nguyên liệu từ hóa đơn, tem nhãn hoặc lời nói. Công nghệ cụ thể có thể được điều chỉnh trong quá trình thử nghiệm nhằm cân bằng giữa độ chính xác, tốc độ và chi phí vận hành.

Trong giai đoạn MVP, nhóm ưu tiên hoàn thiện nhập liệu từ hóa đơn hoặc tem nhãn, nhập bằng giọng nói, quản lý thời hạn, gợi ý món ăn và cập nhật kho sau khi nấu. Các chức năng nhận diện hình ảnh nâng cao sẽ được phát triển sau khi vòng lặp cốt lõi được kiểm chứng.

**6.3. Chi tiết các phân hệ chức năng chính**

**6.3.1. Phân hệ nhập liệu đa phương thức thông minh**

SweepFood được định hướng để hỗ trợ năm phương thức nhập liệu. Trong phạm vi MVP, nhóm ưu tiên quét tem nhãn, quét hóa đơn, nhập bằng giọng nói và nhập thủ công. Nhận diện thực phẩm tươi sống từ hình ảnh là hướng phát triển sau khi các phương thức nhập liệu cốt lõi được kiểm chứng.

- Thứ nhất, quét tem nhãn sản phẩm tận dụng nhãn cân có sẵn trên thực phẩm đóng gói tại các chuỗi bán lẻ như Bách Hóa Xanh, WinMart... Hệ thống sử dụng OCR kết hợp với phân tích mẫu ký tự để trích xuất các trường thông tin như tên nguyên liệu, khối lượng tịnh, ngày đóng gói, hạn sử dụng và giá tiền.
- Thứ hai, quét hóa đơn thanh toán cho phép người dùng chụp hóa đơn sau khi mua sắm. Hệ thống nhận diện các mặt hàng thực phẩm và gợi ý thông tin ban đầu để người dùng xác nhận. Đối với thực phẩm không có hạn sử dụng cụ thể, hệ thống tiếp tục hướng dẫn người dùng bổ sung các thông tin cần thiết trước khi đưa ra thời gian bảo quản tham khảo.
- Thứ ba, trong giai đoạn mở rộng, hệ thống có thể ứng dụng thị giác máy tính để hỗ trợ nhận diện một số loại rau, củ, quả, thịt và cá không có bao bì. Do hình ảnh không thể xác định chính xác khối lượng, người dùng vẫn cần xác nhận hoặc bổ sung định lượng.
- Thứ tư, nhập liệu bằng giọng nói cho phép người dùng nhập thông tin khi đang bận tay làm bếp hoặc mang đồ từ bên ngoài về. Công nghệ Speech-to-Text chuyển đổi giọng nói thành văn bản, sau đó hệ thống bóc tách các thông tin như số lượng, đơn vị và tên nguyên liệu.
- Thứ năm, nhập thủ công cung cấp giao diện đơn giản với danh mục các nguyên liệu phổ biến và gợi ý dựa trên lịch sử sử dụng của người dùng.

**6.3.2. Phân hệ quản lý kho thực phẩm và hỗ trợ ước tính thời gian bảo quản**

Kho thực phẩm được tổ chức theo trạng thái và điều kiện bảo quản nhằm hỗ trợ người dùng theo dõi và xác định nguyên liệu cần ưu tiên sử dụng. Hệ thống phân biệt các nhóm như thực phẩm cần dùng trong ngày, bảo quản ngăn mát, ngăn đông và thực phẩm khô.

Đối với sản phẩm có hạn sử dụng do nhà sản xuất cung cấp, SweepFood ưu tiên sử dụng thông tin trên bao bì. Đối với thực phẩm tươi hoặc thực phẩm không có hạn sử dụng cụ thể, hệ thống hỗ trợ người dùng thông qua một quy trình kiểm tra có hướng dẫn.

Sau khi nguyên liệu được ghi nhận, ứng dụng hiển thị các thông tin cần người dùng xác nhận phù hợp với từng nhóm thực phẩm, chẳng hạn thời điểm mua hoặc mở bao bì, điều kiện bảo quản và một số dấu hiệu có thể quan sát được. Các thông tin này được kết hợp với dữ liệu bảo quản tham khảo để đưa ra thời gian bảo quản tham khảo và mức độ ưu tiên sử dụng.

Hệ thống định kỳ theo dõi trạng thái kho và gửi nhắc nhở khi nguyên liệu cần được ưu tiên sử dụng, đồng thời có thể kết hợp với chức năng gợi ý món ăn để hỗ trợ tận dụng thực phẩm kịp thời.

Thời gian bảo quản do hệ thống đưa ra chỉ mang tính tham khảo, không thay thế hạn sử dụng của nhà sản xuất hoặc việc người dùng tự đánh giá tình trạng thực tế của thực phẩm. Khi thông tin không đầy đủ hoặc có dấu hiệu bất thường, ứng dụng không đưa ra kết luận về mức độ an toàn của thực phẩm.

**6.3.3. Phân hệ đề xuất món ăn thông minh**

Phân hệ đề xuất món ăn sử dụng trạng thái kho hiện tại để xếp hạng và lựa chọn từ 3 đến 5 món có khả năng tận dụng nguyên liệu tốt. Mỗi ứng viên được xem xét theo mức độ cận hạn của nguyên liệu, tỷ lệ đáp ứng khối lượng, mức cân bằng dinh dưỡng, khẩu phần, thời gian, sở thích và lượng nguyên liệu cần mua thêm. Chi tiết quy trình lọc ứng viên, điều chỉnh khẩu phần và mô hình xếp hạng được trình bày tại Mục 11.

**6.3.4. Phân hệ phân tích dinh dưỡng và ước tính theo khẩu phần**

Phân hệ sử dụng loại nguyên liệu và khối lượng do người dùng xác nhận để ước tính tổng năng lượng, protein, carbohydrate và lipid của món ăn. Kết quả được hiển thị cho toàn bộ món và cho từng khẩu phần.

Công thức tổng quát:

Nguồn dữ liệu chính dự kiến là công cụ tra cứu thành phần thực phẩm và món ăn của Viện Dinh dưỡng Quốc gia \[6\]. Với nguyên liệu chưa có dữ liệu phù hợp, nhóm có thể sử dụng nguồn bổ sung nhưng phải ghi rõ xuất xứ.

Người dùng có thể lựa chọn một số ưu tiên cơ bản như bữa ăn cân bằng, nhiều protein, ít năng lượng hoặc nhiều rau. Các lựa chọn này được dùng như tiêu chí hỗ trợ xếp hạng món ăn.

Kết quả dinh dưỡng phụ thuộc vào loại nguyên liệu, định lượng và cách chế biến nên chỉ mang tính ước tính, không thay thế tư vấn của chuyên gia dinh dưỡng hoặc y tế.

**6.3.5. Phân hệ cập nhật nguyên liệu sau khi nấu**

Khi người dùng chọn một món ăn, hệ thống dự kiến số lượng nguyên liệu sẽ được sử dụng. Sau khi hoàn thành, người dùng có thể xác nhận “đã nấu” và lựa chọn một trong các thao tác nhanh: dùng đúng định lượng, dùng một nửa, dùng hết hoặc tự điều chỉnh.

Hệ thống sau đó tự động cập nhật số lượng nguyên liệu còn lại. Nếu món ăn chưa được sử dụng hết, người dùng có thể lưu phần còn lại dưới dạng thức ăn đã nấu và đặt thời gian nhắc sử dụng.

Cơ chế này giúp tủ bếp duy trì độ chính xác mà không yêu cầu người dùng nhập lại từng nguyên liệu sau mỗi bữa.

**6.3.6. Phân hệ danh sách mua sắm tối ưu**

Phân hệ này phân tích thực đơn đã lựa chọn trong tuần để tự động tạo danh sách các gia vị và nguyên liệu phụ cần mua thêm. Danh sách được đối chiếu với trạng thái của kho thực phẩm nhằm hạn chế việc mua trùng các nguyên liệu đã có sẵn trong bếp.

**6.4. Phân tích ưu điểm và hạn chế của giải pháp**

**6.4.1. Ưu điểm**

Giảm số lượng thao tác nhập liệu. Nhờ cơ chế đa phương thức, người dùng có thể số hóa kho thực phẩm thông qua nhiều hình thức như quét tem nhãn, quét hóa đơn, nhận diện thực phẩm tươi sống hoặc nhập liệu bằng giọng nói, từ đó giảm đáng kể sự phụ thuộc vào thao tác nhập thủ công.

Hỗ trợ quản lý thời gian bảo quản linh hoạt. Với thực phẩm có thông tin từ nhà sản xuất, hệ thống ưu tiên dữ liệu trên bao bì. Đối với thực phẩm tươi không có hạn sử dụng rõ ràng, SweepFood hướng dẫn người dùng bổ sung thông tin về điều kiện và tình trạng bảo quản để đưa ra mốc sử dụng tham khảo, giúp việc theo dõi thực phẩm phù hợp hơn với từng trường hợp.

Gợi ý món ăn theo ngữ cảnh thay vì liệt kê công thức đơn thuần. Thuật toán đề xuất xem xét đồng thời trạng thái kho, mức độ cận hạn và nhu cầu bổ sung nguyên liệu để lựa chọn một số món ăn phù hợp, qua đó giảm tình trạng quá tải thông tin.

Thông tin dinh dưỡng dễ tiếp cận. Mỗi món ăn được hiển thị năng lượng, protein, carbohydrate và lipid ước tính trên từng khẩu phần, giúp người dùng so sánh và lựa chọn món phù hợp hơn mà không phải sử dụng thêm một ứng dụng khác.

Tiềm năng thương mại hóa. Trong tương lai, hệ thống có thể mở rộng chức năng liên kết các nguyên liệu còn thiếu với nền tảng đi chợ hộ và dịch vụ giao hàng trực tuyến, tạo thành một quy trình khép kín từ quản lý kho, lập thực đơn đến mua sắm.

**6.4.2. Hạn chế và hướng khắc phục**

Chất lượng OCR có thể suy giảm khi tem nhãn bị rách, nhăn, mờ hoặc hóa đơn giấy nhiệt bị phai mực. Để giảm ảnh hưởng của các trường hợp này, hệ thống có thể áp dụng các bước tiền xử lý ảnh như khử nghiêng, cân bằng tương phản và phân đoạn nhị phân, đồng thời cung cấp giao diện xem trước để người dùng kiểm tra và chỉnh sửa thông tin trước khi lưu.

Ước tính thời gian bảo quản có độ bất định. Tình trạng thực phẩm chịu ảnh hưởng bởi nhiệt độ, quá trình vận chuyển, cách bảo quản và nhiều yếu tố mà ứng dụng không thể quan sát đầy đủ. Vì vậy, SweepFood chỉ cung cấp thông tin tham khảo dựa trên dữ liệu và thông tin người dùng xác nhận, ưu tiên hạn sử dụng của nhà sản xuất khi có và không thay thế việc kiểm tra thực phẩm thực tế.

Khó xác định khối lượng tuyệt đối đối với thực phẩm tươi sống không có bao bì. Khi sử dụng thị giác máy tính để nhận diện thực phẩm từ ảnh, hệ thống khó có thể suy ra chính xác khối lượng nếu không có thêm thông tin về kích thước hoặc thiết bị đo. Hướng khắc phục là sử dụng định lượng khẩu phần tham khảo cho từng nhóm thực phẩm và cho phép người dùng bổ sung khối lượng bằng giọng nói hoặc nhập thủ công.

Chi phí xử lý AI có thể tăng khi quy mô người dùng mở rộng. Nhóm dự kiến tối ưu bằng cách tái sử dụng kết quả đối với các tác vụ phù hợp, ưu tiên xử lý cục bộ khi khả thi và lựa chọn công nghệ theo sự cân bằng giữa độ chính xác, tốc độ và chi phí vận hành.

Dữ liệu tồn kho có thể bị sai theo thời gian. Nếu người dùng quên xác nhận sau khi sử dụng nguyên liệu, dữ liệu trong tủ bếp có thể không còn chính xác. Hệ thống khắc phục bằng thao tác cập nhật nhanh, lời nhắc sau khi nấu và cơ chế xác nhận định kỳ.

Khó hình thành thói quen sử dụng. Quản lý tủ bếp là hành vi cần được duy trì thường xuyên. Nhóm sẽ giảm rào cản bằng cách tự động hóa nhập liệu, hiển thị giá trị tiết kiệm và chỉ gửi các thông báo có khả năng tạo hành động.

1.  **Kết quả dự kiến**

_Sau cuộc thi, nhóm dự kiến hoàn thành:_

☒ _Prototype_

☒ _Mobile App_

☒ _AI Model_

☐ _Hệ thống quản trị_

☐ _Khác_

Sau cuộc thi, nhóm dự kiến hoàn thiện prototype ứng dụng di động SweepFood với các chức năng chính gồm nhập và quản lý nguyên liệu, theo dõi thời gian bảo quản, gợi ý món ăn và cung cấp thông tin dinh dưỡng theo khẩu phần.

Bên cạnh các chức năng ứng dụng, nhóm xây dựng quy trình thu thập và khai thác dữ liệu từ trạng thái kho thực phẩm, lịch sử sử dụng và tương tác của người dùng để hỗ trợ hệ thống đưa ra các gợi ý phù hợp hơn.

Sản phẩm sẽ được thử nghiệm với nhóm người dùng thuộc phân khúc mục tiêu nhằm đánh giá chất lượng nhập liệu, mức độ hữu ích của đề xuất món ăn, khả năng tận dụng thực phẩm trước hạn và mức độ duy trì sử dụng ứng dụng.

1.  **Định hướng phát triển**

Ở các giai đoạn tiếp theo, SweepFood ưu tiên hoàn thiện khả năng nhập liệu, mở rộng dữ liệu món ăn và thử nghiệm với người dùng thực tế. Trọng tâm là hoàn thiện vòng lặp cốt lõi gồm quản lý nguyên liệu, gợi ý bữa ăn, ghi nhận hành vi sử dụng và cải thiện đề xuất dựa trên dữ liệu.

**8.1. Cá nhân hóa dựa trên dữ liệu**

Khi có đủ dữ liệu về lịch sử mua sắm, trạng thái kho, món ăn đã lựa chọn và phản hồi của người dùng, SweepFood có thể từng bước xây dựng hồ sơ sở thích nhằm cải thiện chất lượng gợi ý.

Hệ thống có thể nhận biết các nguyên liệu thường được sử dụng, món ăn được ưu tiên, thói quen về khẩu phần, thời gian nấu và một số nhu cầu dinh dưỡng cơ bản. Từ đó, các đề xuất bữa ăn có thể được điều chỉnh phù hợp hơn với từng người dùng thay vì chỉ dựa trên trạng thái kho tại một thời điểm.

Người dùng vẫn có quyền kiểm soát, chỉnh sửa hoặc xóa các thông tin cá nhân hóa đã được ghi nhận.

**8.2. Mở rộng khả năng nhập liệu và tương tác**

Trong các giai đoạn tiếp theo, SweepFood có thể mở rộng khả năng tiếp nhận dữ liệu thông qua hình ảnh, giọng nói và các công nghệ AI đa phương thức nhằm giảm thao tác nhập thủ công.

Ngoài hóa đơn và tem nhãn, hệ thống có thể nghiên cứu hỗ trợ nhận diện một số loại thực phẩm tươi sống, cải thiện khả năng xử lý cách gọi nguyên liệu và đơn vị đo trong tiếng Việt, đồng thời phát triển tương tác bằng giọng nói trong quá trình nấu ăn.

Các tính năng này chỉ được triển khai khi bảo đảm độ chính xác, tốc độ xử lý và chi phí vận hành phù hợp với sản phẩm.

**8.3. Mở rộng hệ sinh thái SweepFood**

Sau khi các chức năng cốt lõi được kiểm chứng, SweepFood có thể nghiên cứu kết nối với các nền tảng mua sắm hoặc dịch vụ giao hàng để hỗ trợ người dùng bổ sung những nguyên liệu còn thiếu trong thực đơn.

Trong dài hạn, hệ thống cũng có thể mở rộng khả năng kết nối với các thiết bị nhà bếp thông minh nhằm hỗ trợ cập nhật trạng thái nguyên liệu tự động. Các hướng phát triển này phụ thuộc vào khả năng kỹ thuật, đối tác triển khai và nhu cầu thực tế của người dùng, không thuộc phạm vi MVP của cuộc thi.

1.  **Nguồn dữ liệu dự kiến sử dụng**

SweepFood khai thác nhiều nhóm dữ liệu nhằm phục vụ quản lý nguyên liệu, tính toán dinh dưỡng và đề xuất bữa ăn. Các nguồn dữ liệu chính gồm:

- Dữ liệu dinh dưỡng: sử dụng dữ liệu thành phần thực phẩm từ các nguồn có độ tin cậy như Viện Dinh dưỡng Quốc gia để ước tính năng lượng, protein, lipid và carbohydrate theo khẩu phần.
- Dữ liệu công thức món ăn: tập hợp các công thức món ăn, đặc biệt ưu tiên món Việt Nam, bao gồm danh sách nguyên liệu, định lượng, khẩu phần và hướng dẫn chế biến. Dữ liệu được làm sạch và chuẩn hóa để liên kết với danh mục nguyên liệu của hệ thống.
- Dữ liệu hướng dẫn bảo quản thực phẩm: bao gồm thông tin tham khảo về điều kiện và thời gian bảo quản của từng nhóm thực phẩm từ các nguồn đáng tin cậy, như FoodKeeper \[7\]. Dữ liệu này được sử dụng để xây dựng hướng dẫn kiểm tra và hỗ trợ ước tính thời gian bảo quản đối với thực phẩm không có hạn sử dụng cụ thể.
- Dữ liệu hóa đơn, tem nhãn và giọng nói: được sử dụng để hỗ trợ các phương thức nhập nguyên liệu nhanh. Hệ thống dự kiến khai thác các thông tin như tên thực phẩm, số lượng, khối lượng, ngày mua hoặc thời hạn sử dụng.
- Dữ liệu trạng thái kho và tương tác người dùng: bao gồm nguyên liệu hiện có, vị trí và thời gian bảo quản, các thông tin về tình trạng thực phẩm do người dùng xác nhận, món được đề xuất, món được lựa chọn và các lần xác nhận đã nấu. Dữ liệu này phục vụ theo dõi thực phẩm, đánh giá hiệu quả gợi ý và từng bước cá nhân hóa hệ thống.

Trong giai đoạn chưa có đủ dữ liệu người dùng thực tế, nhóm có thể sử dụng dữ liệu mô phỏng theo các kịch bản tiêu dùng điển hình để kiểm thử hệ thống. Dữ liệu mô phỏng được tách biệt với dữ liệu thu thập từ người dùng thật.

1.  **Phương pháp thu thập và xử lý dữ liệu**

#### 10.1. Thu thập dữ liệu

Dữ liệu đầu vào của SweepFood được thu thập từ các phương thức như chụp hóa đơn hoặc tem nhãn, nhập bằng giọng nói, nhập thủ công, các trường thông tin được người dùng xác nhận trong quá trình kiểm tra tình trạng thực phẩm và các tương tác phát sinh trong quá trình sử dụng ứng dụng.

Đối với dữ liệu từ người dùng thử nghiệm, nhóm chỉ thu thập những thông tin cần thiết cho chức năng của hệ thống và sử dụng dữ liệu khi có sự đồng ý của người tham gia.

#### 10.2. Xử lý và chuẩn hóa

Dữ liệu sau khi tiếp nhận được tiền xử lý và chuẩn hóa trước khi lưu vào hệ thống. Hình ảnh hóa đơn và tem nhãn được xử lý để hỗ trợ OCR; dữ liệu giọng nói được chuyển thành văn bản; tên nguyên liệu và đơn vị đo được ánh xạ về danh mục chung của SweepFood.

Các thông tin như tên nguyên liệu, khối lượng, thời hạn sử dụng và giá trị dinh dưỡng được kiểm tra trước khi lưu. Trong những trường hợp hệ thống không đủ độ tin cậy, người dùng được yêu cầu xác nhận hoặc chỉnh sửa. Đối với thực phẩm không có hạn sử dụng cụ thể, các thông tin về loại thực phẩm, điều kiện bảo quản và tình trạng do người dùng xác nhận được kết hợp với dữ liệu tham khảo để ước tính thời gian bảo quản phù hợp.

#### 10.3. Vòng lặp cải thiện dữ liệu

Các chỉnh sửa của người dùng đối với kết quả nhận diện, thông tin bảo quản được gợi ý và các tương tác như lựa chọn món, xác nhận đã nấu hoặc bỏ qua đề xuất được ghi nhận dưới dạng tín hiệu phản hồi. Các tín hiệu này giúp nhóm nhận diện những trường hợp hệ thống còn xử lý chưa tốt, cập nhật quy tắc chuẩn hóa và từng bước cải thiện mô hình đề xuất trong quá trình thử nghiệm.

**10.4. Bảo mật, quyền riêng tư và quản trị dữ liệu**

SweepFood áp dụng nguyên tắc thu thập tối thiểu, chỉ lưu các dữ liệu cần thiết cho chức năng quản lý nguyên liệu và phân tích hành vi sử dụng. Đối với hóa đơn, hệ thống ưu tiên loại bỏ hoặc che các thông tin không cần thiết như mã giao dịch, số điện thoại hoặc thông tin nhận dạng cá nhân trước khi sử dụng cho mục đích phân tích. Dữ liệu ảnh, âm thanh và lịch sử sử dụng chỉ được sử dụng cho huấn luyện hoặc cải thiện mô hình khi người dùng đồng ý.

Dữ liệu phục vụ phân tích được tách khỏi thông tin định danh trực tiếp và gắn với mã người dùng nội bộ. Người dùng có quyền chỉnh sửa hoặc yêu cầu xóa dữ liệu đã cung cấp. Trong giai đoạn nghiên cứu, dữ liệu thử nghiệm được giới hạn quyền truy cập trong nhóm phát triển và không chia sẻ cho bên thứ ba nếu chưa có sự đồng ý.

1.  **Thuật toán và mô hình phân tích**

Đối với thời gian bảo quản, SweepFood dự kiến sử dụng cơ chế phân tích dựa trên dữ liệu tham khảo kết hợp với loại thực phẩm, điều kiện bảo quản và các thông tin do người dùng xác nhận. Kết quả được sử dụng để đưa ra mốc bảo quản tham khảo và mức độ ưu tiên sử dụng, không nhằm thay thế hạn sử dụng của nhà sản xuất hoặc kết luận về an toàn thực phẩm.

Hệ thống đề xuất món ăn của SweepFood được xây dựng theo hướng khai thác đồng thời dữ liệu trạng thái kho và dữ liệu công thức thay vì chỉ tìm kiếm món dựa trên tên nguyên liệu.

Quy trình đề xuất gồm hai bước chính. Trước hết, hệ thống lọc ra nhóm công thức có khả năng phù hợp dựa trên các nguyên liệu hiện có và khả năng sử dụng thực phẩm cần được ưu tiên. Sau đó, các món ăn được xếp hạng dựa trên nhiều yếu tố như lượng nguyên liệu đang có, thời hạn bảo quản, số nguyên liệu cần mua thêm, khẩu phần, thời gian nấu và thông tin dinh dưỡng.

Trong giai đoạn đầu, nhóm dự kiến thử nghiệm mô hình Learning-to-Rank, với XGBoost/LambdaMART là một phương án phù hợp để học mối quan hệ giữa các đặc trưng của kho thực phẩm và mức độ phù hợp của món ăn. Mục tiêu của mô hình là đưa ra một số lượng nhỏ các lựa chọn có khả năng thực hiện cao thay vì trả về danh sách công thức quá dài.

Khi có thêm dữ liệu người dùng thực tế, các tín hiệu như món được lựa chọn, xác nhận đã nấu và phản hồi sau sử dụng có thể được sử dụng để điều chỉnh mô hình, giúp hệ thống ngày càng phù hợp với thói quen của từng người dùng.

Trong phạm vi prototype, nhóm ưu tiên kiểm chứng tính khả thi của quy trình đề xuất và khả năng tận dụng nguyên liệu cận hạn. Các thông số kỹ thuật và cấu hình mô hình có thể được điều chỉnh sau quá trình thử nghiệm.

Trong giai đoạn phát triển prototype, nhóm sử dụng dữ liệu mô phỏng để kiểm tra tính đúng đắn của quy trình đề xuất trước khi thử nghiệm với người dùng thực tế. Kết quả đánh giá chính thức sẽ ưu tiên các chỉ số phản ánh mức độ phù hợp của món ăn và khả năng hỗ trợ người dùng tận dụng thực phẩm.

1.  **Chỉ số đánh giá hiệu quả**

Nhóm sử dụng một số chỉ số đại diện cho các giai đoạn chính của vòng lặp dữ liệu, từ chất lượng nhập liệu, trải nghiệm sử dụng, hiệu quả đề xuất đến khả năng hỗ trợ giảm lãng phí. Các ngưỡng đánh giá cụ thể sẽ được xác định và điều chỉnh sau quá trình thử nghiệm prototype với người dùng thuộc phân khúc mục tiêu.

| Nhóm đánh giá | Chỉ số | Ý nghĩa |
| --- | --- | --- |
| Chất lượng nhập liệu | Độ chính xác trích xuất thông tin | Đánh giá khả năng nhận diện tên, số lượng, khối lượng và thời hạn sử dụng |
| --- | --- | --- |
| Trải nghiệm nhập liệu | Thời gian hoàn thành nhập nguyên liệu | Đánh giá mức độ thuận tiện so với nhập thủ công |
| --- | --- | --- |
| Chất lượng đề xuất | Tỷ lệ người dùng lựa chọn món được gợi ý | Đánh giá mức phù hợp của đề xuất |
| --- | --- | --- |
| Hiệu quả sử dụng thực phẩm | Tỷ lệ nguyên liệu cận hạn được sử dụng | Đánh giá khả năng hỗ trợ giảm lãng phí |
| --- | --- | --- |
| Duy trì sử dụng | Tỷ lệ người dùng quay lại | Đánh giá khả năng hình thành thói quen sử dụng |
| --- | --- | --- |
| Hỗ trợ bảo quản | Điểm đánh giá mức độ hữu ích của hướng dẫn kiểm tra và thời gian bảo quản tham khảo | Đánh giá mức độ dễ hiểu và hữu ích thông qua khảo sát sau trải nghiệm |
| --- | --- | --- |

1.  **Kết quả phân tích hoặc dashboard dự kiến**

Dashboard dự kiến phục vụ hai mục tiêu: giúp người dùng thấy giá trị nhận được và giúp nhóm phát triển theo dõi chất lượng vòng lặp dữ liệu. Phần người dùng tập trung vào tỷ lệ dùng thực phẩm trước hạn, lượng nguyên liệu cận hạn được tận dụng, xu hướng lãng phí và nhóm thực phẩm có nguy cơ cao. Phần sản phẩm tập trung vào chất lượng nhập liệu và funnel từ yêu cầu gợi ý → xem công thức → chọn món → xác nhận đã nấu.

Trong giai đoạn chưa có đủ dữ liệu người dùng thật, hình dưới sử dụng dữ liệu mô phỏng để minh họa cấu trúc dashboard. Sau khi triển khai thử nghiệm MVP, các số liệu mô phỏng sẽ được thay thế bằng dữ liệu thực và được gắn nhãn thời gian thử nghiệm rõ ràng.

**DASHBOARD PHÂN TÍCH DỰ KIẾN**

Lưu ý: toàn bộ số liệu trên chỉ là mô phỏng để minh họa cấu trúc dashboard, không phải là kết quả thử nghiệm người dùng thực tế.

1.  **Tài liệu tham khảo**

\[1\] [United Nations Environment Programme, Food Waste Index Report 2024, 2024.](https://www.unep.org/resources/publication/food-waste-index-report-2024)

\[2\] [CEL Consulting, Food Losses in Vietnam: The Shocking Reality, 2018.](https://www.cel-consulting.com/post/2018/08/10/food-losses-in-vietnam-the-shocking-reality)

\[3\] [Food Bank Vietnam, Lãng phí thực phẩm – Nguyên nhân từ đâu?](https://foodbankvietnam.com/lang-phi-thuc-pham-nguyen-nhan-tu-dau/)

\[4\] [Báo Nhân Dân, “Làn sóng độc thân trong xã hội,” ngày 07/07/2026.](https://nhandan.vn/lan-song-doc-than-trong-xa-hoi-post973907.html)

\[5\] [Bộ Thông tin và Truyền thông, MIC plans to boost digital infrastructure, digital applications in 2024, 2024.](https://english.mic.gov.vn/mic-plans-to-boost-digital-infrastructure-digital-applications-in-2024-197240105081122147.htm)

\[6\] [Viện Dinh dưỡng Quốc gia, Tra cứu giá trị dinh dưỡng thực phẩm.](https://viendinhduong.vn/vi/cong-cu-va-tien-ich/gia-tri-dinh-duong-thuc-pham)

\[7\] [FoodSafety.gov, FoodKeeper App.](https://www.foodsafety.gov/keep-food-safe/foodkeeper-app)

\[8\] [SuperCook, SuperCook Recipe By Ingredient – App Store.](https://apps.apple.com/us/app/supercook-recipe-by-ingredient/id1477747816)

\[9\] [KitchenPal, Pantry Tracker, Meal Planner & Shopping List App.](https://kitchenpalapp.com/en/)

\[10\] [Pantry Check, Grocery and Food Planning.](https://pantrycheck.com/)