# NC35封裝相容性盤點（未發布）

## 本輪查證

- Nextcloud v35.0.1官方composer宣告PHP `^8.3`；目前HA封裝仍PHP8.2，不能只改Nextcloud版本號就升35。
- PHP版本相關位置包括Docker apt套件與ini路徑、svc-php-fpm執行檔、nginx socket及richdocuments重啟pid路徑，必須一起修改與測試。
- Debian trixie及PGDG trixie-pgdg Release可取得。實際Debian amd64 Packages index有php8.4-cli／php8.4-fpm `8.4.24-1~deb13u1`，作為「官方PHP8.4套件＋保留PG16」候選；尚未完成套件組合／image build／DB collation相容性驗證。
- CODE官方InRelease已用官方release keyring實際驗證簽章成功。簽署fingerprint：`7EB1530818B7683284483B7BD8915E456E7C440E`。
- Keyring SHA256：`b77f959916c0ec2072b72860d80f9c066910d9bddd2f69534b488f4b4d5ca4dd`。

## 已實作的有界變更

Dockerfile移除CODE來源的`trusted=yes`，改用官方keyring、固定keyring checksum及` signed-by `。keyring變更時build會停下，而不是默認相信新來源。這不等於整個供應鏈或image build已驗收。

## 下輪決策與實作

1. 比較路線：維持bookworm加新PHP來源／改trixie官方PHP8.4／基於官方PHP映像重做封裝。優先減少新增信任來源，但必須驗证PG16既有資料與CODE依賴。
2. 查明PG16在候選base的locale/collation影響，採合成資料演練；不掛載原HA的PGDATA。
3. 核對CODE的架構套件與依賴；不要因config列有aarch64就宣稱已驗證ARM。
4. 選定後一次更新PHP套件、FPM/socket/pid/ini，補靜態與真runtime檢查；建不可變測試映像。
5. NC33→34→35及完整還原在獨立環境逐版跑。普通容器成功不等於HAOS/Supervisor完成。

來源：
- https://raw.githubusercontent.com/nextcloud/server/v35.0.1/composer.json
- https://deb.debian.org/debian/dists/trixie/Release
- https://apt.postgresql.org/pub/repos/apt/dists/trixie-pgdg/Release
- https://www.collaboraoffice.com/repos/CollaboraOnline/CODE-deb/InRelease
- https://collaboraoffice.com/downloads/gpg/collaboraonline-release-keyring.gpg

本輪未改base、PHP或NC預設版本，未發布映像、未更動現有HA/PaaS。GitHub推送仍需可用授權；可先持續本地實作與隔離驗證。
