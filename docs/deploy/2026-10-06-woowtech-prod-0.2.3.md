# woowtech 正式 HA：Nextcloud Office 0.1.6 → 0.2.3 部署紀錄（2026-10-06）

使用者授權：「隨時可以去部署」，並選擇 GHCR 預建映像（HA 只下載不在裝置上建置）。

## 結果

| 步驟 | Release／映像 digest | 停機 | Nextcloud |
|---|---|---|---|
| 0.1.6 → 0.2.1 | v0.2.1 `sha256:4b5194d4…` | 06:45:08–06:47:58Z（另見事故 2） | 33.0.0 → 33.0.9，PHP 8.2 → 8.4，Debian bookworm → trixie |
| 0.2.1 → 0.2.2 | v0.2.2 `sha256:3ae92faf…` | 07:57:04–07:57:20Z | 33.0.9 → 34.0.4 |
| 0.2.2 → 0.2.3 | v0.2.3 `sha256:fe7d0092…` | 08:48:44–08:49:48Z | 34.0.4 → 35.0.1 |

每一步：預先 `docker pull`（服務不中斷）並核對 digest 與 CI 推送一致 → 停止 add-on → `/share/nextcloud` 打包（檔案數與磁碟一致）→ HA 冷備份 → 更新 → 啟動 → 驗證。

## 驗證（每一步前後）

- `occ status` 與公開 `status.php` 版本正確、非維護模式。
- 帳號 2、分享 1、行事曆物件 15、聯絡人 4、使用者檔案數不變；資料目錄、config.php、PGDATA 權限不變（770／640／700）。
- CODE discovery 200、實際 `convert-to/pdf` 成功；HA ingress `/healthz` 200；公開登入頁 200。
- 其他 add-on 狀態與部署前相同；無新的 OOM。
- app：原本啟用的全部保留。NC 34 新增內建 appstore、files_lock、office；NC 35 新增 sharing。richdocuments 10.3.2 → 11.1.2 → 12.0.1，並從非持久 `apps/` 遷移到持久 `custom_apps`。

## 部署帶出的變化（需知悉）

- **notes 6.1.0、tasks 0.18.1 重新可用**：資料庫一直標記為啟用，但程式碼自 2026-09-22 容器重建後遺失（舊版把 app store app 裝在非持久位置）；升級時重新安裝到持久 `custom_apps`。
- **assistant** 被設為停用（不相容；其程式碼同樣早已遺失，原本就無法使用）。
- 升級時清除了 3 個自動產生的 JS 快取檔（`appdata_*/js/core/merged-template-prepend.js*`），會自動重建。

## 備份

- 機上：`/share/woow-nextcloud-backup/pre-0.2.1.tar`、`pre-0.2.2.tar`、`pre-0.2.3.tar`（含 `.sha256`）；HA 備份 `prod-nc-pre-0.2.1`、`prod-nc-pre-0.2.2`、`prod-nc-pre-0.2.3`。
- 機外：pi-agent 私密目錄各一份 `/share` 打包，分段傳輸、雙端 SHA256 相符。
- 回退：用對應版本的 HA 備份還原 add-on（含 PG 與 config）＋還原對應 `/share` 打包；新版開機會自動修正 HA 還原造成的權限變化。

## 事故

1. **（部署前測試）OOM**：在正式機用 Supervisor 本機建置測試版時，apt-get 用掉約 11 GB 觸發 OOM，短暫砍到 Matter Server、Frigate、n8n、Immich、Hermes（均已恢復，Frigate 需手動啟動）。因此改為 GHCR 預建映像。
2. **0.2.1 第一次嘗試**：SSH add-on 的 BusyBox `tar` 不支援 `--xattrs`，腳本在停機後失敗；06:42:08 停止、06:42:34 立即啟動回原版。修正腳本後重新部署。
3. **0.2.3**：`ha store reload` 回應逾時導致腳本中止（備份已完成）；確認商店已讀到 0.2.3 後直接更新，停機約 1 分鐘。

## 其他訂閱同一商店的實例

商店目前提供 0.2.3（NC 35）。仍在 0.1.x／0.2.1（NC 33）的實例若直接更新，Nextcloud 會拒絕跨大版本（開機停止、資料不改）；需先經過 0.2.2（可用 Release v0.2.2 的映像手動處理）。
