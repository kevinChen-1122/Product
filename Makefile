# =========
# Makefile
# =========

# 依需要修改
PROJECT_NAME ?= product
COMPOSE_FILE ?= docker-compose.yml
ENV_FILE     ?= .env

# 服務名稱（對應 docker-compose.yml）
MONGO_SVC         ?= mongo
KEYWORD_CONFIG_SVC ?= keyword-config-service

# 預設指令
.DEFAULT_GOAL := help

# --- 工具變數 ---
DC = docker compose --project-name $(PROJECT_NAME) --env-file $(ENV_FILE) -f $(COMPOSE_FILE)

# --- 幫助 ---
.PHONY: help
help: ## 顯示可用指令
	@echo ""
	@echo "Usage: make <target>"
	@echo ""
	@echo "Common:"
	@grep -E '^[a-zA-Z0-9\-_]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-22s\033[0m %s\n", $$1, $$2}'
	@echo ""

.PHONY: env
env: ## 檢查 .env 是否存在
	@test -f $(ENV_FILE) || (echo "ERROR: $(ENV_FILE) 不存在"; exit 1)

.PHONY: build
build: env ## build 所有服務
	$(DC) build --pull

.PHONY: rebuild
rebuild: env ## 重新建置（不使用快取）
	$(DC) build --no-cache

.PHONY: up
up: env ## 啟動所有服務（背景）
	$(DC) up -d

.PHONY: stop
stop: env ## 停止所有容器
	$(DC) stop

.PHONY: down
down: env ## 停止並移除所有容器（保留 volumes）
	$(DC) down

.PHONY: down-v
down-v: env ## 停止並移除所有容器與 volumes（會清空資料！）
	$(DC) down -v

.PHONY: ps
ps: env ## 查看服務狀態
	$(DC) ps

.PHONY: logs
logs: env ## 追蹤全部服務日誌
	$(DC) logs -f --tail=200

# --- Mongo 常用 ---
.PHONY: up-mongo
up-mongo: env ## 只啟動 Mongo
	$(DC) up -d $(MONGO_SVC)

# 看 logs
.PHONY: logs-mongo
logs-mongo: env ## 只看 Mongo 日誌
	$(DC) logs -f $(MONGO_SVC)

.PHONY: bash-mongo
bash-mongo: env ## 進入 mongosh（用 .env 的 root 帳密）
	@echo "使用 $(MONGO_ROOT_USER) / **** 連線到 admin 資料庫"
	@docker exec -it $$($(DC) ps -q $(MONGO_SVC)) mongosh "mongodb://$${MONGO_ROOT_USER}:$${MONGO_ROOT_PASS}@localhost:$${MONGO_PORT:-27017}/admin?authSource=admin"

.PHONY: mongo-reseed
mongo-reseed: env ## 重跑 init 腳本（會清空資料卷！）
	@read -p "這會刪除 Mongo 資料卷並重跑 init，確定嗎? [y/N] " ans; \
	if [ "$$ans" = "y" ] || [ "$$ans" = "Y" ]; then \
		$(DC) down -v; \
		$(DC) up -d $(MONGO_SVC); \
		$(DC) logs -f $(MONGO_SVC); \
	else \
		echo "已取消"; \
	fi

.PHONY: mongo-dump
mongo-dump: env ## 匯出全部資料庫到 ./backup/mongo
	@mkdir -p backup/mongo
	@docker exec $$($(DC) ps -q $(MONGO_SVC)) sh -c 'mongodump --archive' > backup/mongo/backup.$(shell date +%Y%m%d-%H%M%S).archive
	@echo "已輸出到 backup/mongo/*.archive"

.PHONY: mongo-restore
mongo-restore: env ## 從檔案還原：make mongo-restore FILE=backup/mongo/backup.x.archive
	@if [ -z "$(FILE)" ]; then echo "請指定 FILE=..."; exit 1; fi
	@cat "$(FILE)" | docker exec -i $$($(DC) ps -q $(MONGO_SVC)) mongorestore --archive
	@echo "還原完成"

# --- keyword-config-service 常用 ---
# 啟動
.PHONY: up-keyword-config
up-keyword-config: env ## 只啟動 keyword-config
	$(DC) up -d $(KEYWORD_CONFIG_SVC)

# 看 logs
.PHONY: logs-keyword-config
logs-keyword-config: env
	$(DC) logs -f $(KEYWORD_CONFIG_SVC)

# 進容器
.PHONY: bash-keyword-config
bash-keyword-config: env
	$(DC) exec $(KEYWORD_CONFIG_SVC) bash

# --- 開發便利 ---
.PHONY: restart
restart: env ## 重新啟動（不中斷 volumes）
	$(DC) down
	$(DC) up -d

.PHONY: refresh
refresh: env ## 重新建置並啟動
	$(DC) build --pull
	$(DC) up -d
	$(DC) ps
