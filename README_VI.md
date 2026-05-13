
## Cấu trúc thư mục chi tiết
```
fastapi-project
├── alembic/            # Thư mục quản lý migrations
├── src/
│   ├── auth/           # Domain Authentication
│   │   ├── router.py, schemas.py, models.py, dependencies.py, config.py, 
│   │   ├── constants.py, exceptions.py, service.py, utils.py
│   ├── gcp/            # là phân tương tác với các dịch vụ như cloudstorage của google cloud
│   ├── posts/          # Domain Posts
│   │   ├── router.py, schemas.py, models.py, dependencies.py, constants.py,
│   │   ├── exceptions.py, service.py, utils.py
│   ├── main.py         # Khởi tạo ứng dụng
│   ├── config.py       # Cấu hình global
│   ├── database.py     # Kết nối DB
│   ├── models.py       # Global models
│   ├── exceptions.py   # Global exceptions
│   └── pagination.py   # Global pagination module
├── tests/              # Thư mục kiểm thử (đã chia theo domain)
│   ├── auth/
│   ├── aws/
│   └── posts/
├── templates/          # Thư mục chứa giao diện (HTML)
│   └── index.html
├── requirements/       # Quản lý thư viện
│   ├── base.txt, dev.txt, prod.txt
├── .env
├── .gitignore
├── logging.ini
└── alembic.ini
```

## Cách chạy dự án

1. **Cài đặt thư viện:**
   ```bash
   pip install -r requirements/dev.txt
   ```

2. **Chạy ứng dụng:**
   ```bash
   uvicorn src.main:app --reload
   ```

3. **Tài liệu API:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
