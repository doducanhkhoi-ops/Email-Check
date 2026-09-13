# AI Mail Dashboard

Một bảng điều khiển gọn nhẹ giúp đọc, phân loại và tóm tắt email tự động bằng AI (Google Gemini 3.5 Flash Lite) ngay trên máy cá nhân. Không cần đồng bộ qua các app bên thứ 3 phức tạp.

## Tính năng nổi bật

- **Đa tài khoản**: Hỗ trợ thêm nhiều tài khoản Gmail/Google Workspace cùng lúc, chuyển đổi mượt mà qua dropdown.
- **Phân loại thông minh**: Tự động chia email thành các nhóm logic (Công việc, Mạng xã hội, Học tập, Quảng cáo...) thay vì đổ dồn vào một đống.
- **Tóm tắt siêu tốc**: Giao diện đọc mail 2 cột trực quan. Một bên hiển thị nguyên bản HTML của email (link click được), một bên hiển thị các gạch đầu dòng tóm tắt từ AI.
- **Chạy ngầm (Silent mode)**: Tích hợp sẵn script khởi động ngầm trên Windows, không bị vướng cửa sổ dòng lệnh. Tự động dọn dẹp port thừa.

## Yêu cầu hệ thống

- Python 3.10 trở lên
- Tài khoản Google có API Key của Gemini.

## Cài đặt

1. Clone thư mục này về máy:
   ```bash
   git clone <link-repo-cua-ban>
   cd MailDashboard
   ```

2. Cài đặt các thư viện cần thiết:
   ```bash
   pip install flask google-genai
   ```

## Cấu hình

Dự án cần 2 file cấu hình để hoạt động. Đã có sẵn 2 file mẫu (`.example`) đi kèm.

**1. Cấu hình chạy ngầm & API Key**
- Copy file `run.example.bat` và đổi tên thành `run.bat`.
- Mở `run.bat` bằng Notepad, điền `GEMINI_API_KEY` của bạn vào.

**2. Cấu hình tài khoản Email**
- Copy file `accounts.example.json` và đổi tên thành `accounts.json`.
- Thêm danh sách các tài khoản email bạn muốn dùng.
- **Lưu ý quan trọng**: Ở phần `app_password`, bạn PHẢI dùng **Mật khẩu ứng dụng (App Passwords)** gồm 16 chữ cái của Google, không dùng mật khẩu đăng nhập thông thường. (Vào *Tài khoản Google > Bảo mật > Xác minh 2 bước > Mật khẩu ứng dụng* để tạo).

Mẫu `accounts.json`:
```json
[
    {
        "email": "congviec@gmail.com",
        "app_password": "xxxx xxxx xxxx xxxx"
    },
    {
        "email": "canhan@gmail.com",
        "app_password": "yyyy yyyy yyyy yyyy"
    }
]
```

## Sử dụng

- Click đúp vào file `run.bat` (Bạn có thể Send to > Desktop để tạo shortcut cho tiện).
- Hệ thống sẽ tự động quét port 5000, ngắt các phiên cũ, chạy ngầm server mới và mở trình duyệt web.
- Giao diện có sẵn bộ lọc thời gian (Hôm nay, Hôm qua, 7 ngày qua, hoặc chọn ngày cụ thể).

## Kiến trúc

- **Backend**: Python (Flask) + `imaplib` (kết nối trực tiếp tới server IMAP của Google thay vì dùng Outlook COM, giúp bypass các hạn chế của New Outlook).
- **Frontend**: HTML/JS thuần + Tailwind CSS (via CDN). Không cần build step, dễ dàng chỉnh sửa.
- **AI**: Tích hợp SDK `google-genai` phiên bản mới nhất, sử dụng model `gemini-3.5-flash-lite` cho tốc độ xử lý nhanh nhất với JSON Schema.
