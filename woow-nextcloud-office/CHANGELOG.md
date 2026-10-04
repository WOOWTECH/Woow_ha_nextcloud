# Changelog

## 未發布：升級保護

- Nextcloud 升級失敗時保留非零狀態並停止初始化，不再繼續改設定。
- 既有安裝重啟／升級時不再自動重設管理員密碼；`ADMIN_PASS` 僅用於首次安裝。
- 新增隔離臨時檔案系統的 shell 流程測試；尚未建置新映像或完成 HAOS 升級驗收。

## 0.1.0

- Initial experimental Debian-based all-in-one Nextcloud Office add-on skeleton.
