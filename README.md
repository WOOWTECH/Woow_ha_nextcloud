# Woow_ha_nextcloud — WoowTech Nextcloud Home Assistant Add-on Repository

[![Add repository to Home Assistant](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2FWOOWTECH%2FWoow_ha_nextcloud)

Home Assistant add-on repository for [Nextcloud](https://nextcloud.com) with a
bundled PostgreSQL 16 (pgvector) and Redis (HTTP/LAN variant — use a Cloudflare
Tunnel for HTTPS).

Nextcloud 一體式 Home Assistant add-on 倉庫,內建 PostgreSQL 16(pgvector)
與 Redis(HTTP 區網版本,對外請以 Cloudflare Tunnel 建立 HTTPS)。

## Add-ons in this repository | 本倉庫的 add-on

| Add-on | Description |
|---|---|
| [Woow Nextcloud](nextcloud/) | Nextcloud + PostgreSQL 16 (pgvector) + Redis, all-in-one (amd64/aarch64) |

## Installation | 安裝

1. Click the badge above (or **Settings → Add-ons → Add-on Store → ⋮ →
   Repositories**) and add:
   `https://github.com/WOOWTECH/Woow_ha_nextcloud`
2. Find **Woow Nextcloud** in the store and click **INSTALL**.
3. Details, options and troubleshooting: [nextcloud/README.md](nextcloud/README.md)

> **Migrated from `Woow_nextcloud_docker_compose_all` (branch `ha`)** — if you
> added the old repository URL, remove it and add this one to keep receiving
> updates.
> 若你先前加入的是舊倉庫網址,請移除並改加本倉庫,才能繼續收到更新。

## Other deployment platforms | 其他部署平台

- Docker/Podman Compose → [Woow_podman_nextcloud](https://github.com/WOOWTECH/Woow_podman_nextcloud)
- K3s/Kubernetes Helm chart → [Woow_k3s_nextcloud](https://github.com/WOOWTECH/Woow_k3s_nextcloud)
