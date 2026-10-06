# HA PHP8.4 prototype — approved bounded design

## Decision and limits

User-approved isolated branch `feat/nextcloud-ha-php84`, based on `abc0da3`:
use Debian trixie official PHP8.4 packages, retain PG16 and Nextcloud default
33.0.0. No new third-party PHP repository. This is an **unreleased prototype**,
not an installable-image, migration, or HAOS acceptance claim.

Alternatives considered in the preceding runtime plan: bookworm plus a new PHP
vendor increases trust sources; an official PHP base requires a larger packaging
rewrite. Neither is silently substituted if the trixie candidate fails its gates.

## Bounded implementation

- Change base and PGDG suite together; PG server/client major stays 16.
- Switch all 16 PHP packages and both CLI/FPM ini destinations to 8.4.
- Align s6 FPM binary, generated nginx socket and Office cache-restart PID with
  the official php8.4-fpm package defaults.
- Use trixie's concrete `libsmbclient0` package (which provides `libsmbclient`).
- Retain CODE keyring checksum and `signed-by`; no `trusted=yes` fallback.
- Keep existing upgrade-failure propagation and initial-password-only behavior.
  Do not alter PGDATA, locale initialization, config.yaml version or architectures.

## Verification boundary

Seven offline tests cover the package/ini/path contract and real shell control
flow with temporary paths and stub executables/signals. They must fail against
the old PHP8.2 paths, then pass together with the four existing upgrade guards,
static config test, shell syntax and diff checks. No daemon is started by tests.

Public package declarations and artifact HEAD checks support proceeding locally;
they cannot establish transitive dependency solvability or runtime compatibility.
This worker's isolated APT update was blocked by `/dev/null` permissions in
apt-key (exit 100). That operation was stopped, without permission, sandbox or
trust changes. See `woow-nextcloud-office/RUNTIME-PLAN.md` for exact evidence,
remaining build gates, glibc/collation precautions and the required 33→34→35
synthetic upgrade plus complete rollback rehearsal.
