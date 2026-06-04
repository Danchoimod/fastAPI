Edited NOTE.md
Viewed utils.py:1-17

Về cơ bản là **ĐÚNG**, tư duy đó sẽ giúp bạn làm việc với FastAPI rất nhanh. 

Trong một dự án FastAPI chuẩn, chiến thuật "thường dùng" sẽ là:

1.  **Dùng `async def` cho:**
    *   **Router**: Tất cả các hàm xử lý API.
    *   **Service**: Tất cả các hàm nghiệp vụ có đụng đến Database.
    *   **Dependencies**: Các hàm bổ trợ (như kiểm tra Token, lấy DB session).
    *   *Lý do*: Vì những chỗ này chắc chắn sẽ phải đợi (I/O) từ Database hoặc Request.

2.  **Dùng `def` cho:**
    *   **Utils**: Như mã hóa mật khẩu, định dạng ngày tháng, tính toán toán học.
    *   **Schemas / Models**: Các phương thức logic bên trong class.
    *   **Mappers**: Chuyển đổi dữ liệu từ Object này sang Object khác.
    *   *Lý do*: Vì chúng chạy cực nhanh trong CPU, không cần phải đợi chờ gì cả.

### Một lưu ý cực kỳ quan trọng (Expert Tip):
Có một trường hợp ngoại lệ: Nếu bạn dùng một thư viện **không hỗ trợ async** (ví dụ thư viện `requests` cũ của Python thay vì `httpx`), bạn **KHÔNG ĐƯỢC** dùng `async def`. 

*   Nếu bạn dùng `async def` + `requests.get()` -> Cả website của bạn sẽ bị "đứng hình" khi có người đang tải dữ liệu.
*   Lúc đó, hãy dùng `def` thông thường. FastAPI sẽ tự động chạy nó trên một "đường cao tốc riêng" (Thread pool) để không làm ảnh hưởng đến luồng chính.

**Tóm lại chiến thuật của bạn:** 
> "Cứ `async def` cho Router và Service. Còn lại mấy hàm bổ trợ tính toán thì dùng `def`." 

=> Đây là một chiến thuật rất chuẩn cho người mới bắt đầu với FastAPI! Bạn cứ tự tin áp dụng nhé.