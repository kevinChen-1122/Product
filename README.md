# Product
## Project Structure
```
Product/
├─ deploy/
│  └─ mongo/
│     ├─ init/
│     │  └─ init-mongo.js         # 初始化腳本
│     ├─ data/                    # Mongo 資料卷（會自動生成）
│     └─ log/                     # Mongo 日誌卷（可選）
├─ services/
│  ├─ search_product_service/
│  ├─ auto_bargain_service/
│  └─ notify_service/
├─ .env.sample
├─ .gitignore
├─ docker-compose.yml
├─ Makefile
└─ README.md

```
---
