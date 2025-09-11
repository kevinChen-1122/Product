// 可重複執行、與官方 entrypoint 相容
(function () {
  const env = (typeof process !== 'undefined' && process.env) ? process.env : {};

  // 入口提供的 root（由 Docker 官方 entrypoint 建立，不在這裡重建）
  const ROOT_USER = env.MONGO_INITDB_ROOT_USERNAME || 'admin';
  const ROOT_PASS = env.MONGO_INITDB_ROOT_PASSWORD || 'admin';

  // 業務資料庫與應用使用者（請在 .env 填好）
  const APP_DB   = env.MONGO_INITDB_DATABASE || 'product';
  const APP_USER = env.MONGO_APP_USERNAME || 'app_user';
  const APP_PASS = env.MONGO_APP_PASSWORD || 'app_pass';

  // 切到 admin，以 root 權限操作（此檔在「第一次初始化」階段執行，無需手動 auth）
  db = db.getSiblingDB('admin');

  // 確認 root 是否存在（避免你另一個環境沒用 entrypoint 的 root 建立）
  if (!db.getUser(ROOT_USER)) {
    print(`[init] root user not found in admin, creating: ${ROOT_USER}`);
    db.createUser({
      user: ROOT_USER,
      pwd:  ROOT_PASS,
      roles: [{ role: 'root', db: 'admin' }]
    });
  } else {
    print(`[init] root user already exists: ${ROOT_USER}`);
  }

  // 切到業務 DB，建立/確保應用使用者
  db = db.getSiblingDB(APP_DB);
  if (!db.getUser(APP_USER)) {
    print(`[init] creating app user ${APP_USER} on db ${APP_DB}`);
    db.createUser({
      user: APP_USER,
      pwd:  APP_PASS,
      roles: [{ role: 'readWrite', db: APP_DB }]
    });
  } else {
    print(`[init] app user already exists: ${APP_USER} on ${APP_DB}`);
  }

  print('[init] done');
})();
