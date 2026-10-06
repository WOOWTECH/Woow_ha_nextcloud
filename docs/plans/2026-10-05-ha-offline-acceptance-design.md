# HA candidate inventory gate — bounded offline design

## Scope and decision

Continuation `STATE.next_action=HA_PHP84_ARTIFACT_AND_RUNTIME_GATES` authorizes
an independent local fail-closed harness and stub tests while signed APT/build
is blocked. This unit implements the **offline evidence evaluator only**.
It never collects observations, launches commands, reads PGDATA, connects to a
service, starts Docker/Kubernetes/SSH, or authorizes runtime work.

Alternatives: a live in-container probe needs an approved build/runtime slot
that is not available; a shell wrapper around commands risks host/service access.
A standard-library Python JSON evaluator is chosen to separate collection from
validation. No dependencies or cloud/model spend are added.

## Contract

A caller explicitly supplies a JSON observation bundle for an isolated synthetic
candidate. The evaluator checks both CLI and FPM PHP8.4 modules/ini, FPM binary,
socket/PID/master identity, nginx config-to-socket consistency, CODE discovery,
websocket and save observations, and source/candidate PG16 locale inventories.
The two inventories include libc/ICU, OS locales, all database locale/provider
versions and per-database collation versions. Missing, malformed, duplicate,
failed or inconsistent observations block the gate. Even an explicit empty
collation inventory is insufficient evidence for this gate.

Any libc/ICU/locale/provider/collation version drift blocks this first gate:
there is intentionally no auto-refresh/reindex or waiver flag. A later approved
synthetic migration must establish index rebuild and full rollback evidence
before designing a reviewed drift-disposition contract. This conservative gate
is expected to reject bookworm→trixie inventories, not silently bless them.

## Trust and result boundary

Input is an assertion from a future collector, **not authenticated evidence**.
The report always sets `runtime_verified=false`, `haos_verified=false` and
`production_authorized=false`. Exit 0 means only `inventory_checks_passed`;
exit 1 means blocked observations, exit 2 invalid input/usage. Stub bundles
cannot become runtime acceptance. No manifest/image build, upgrade/restore,
ARM, HAOS, or production gate is satisfied by this tool.

Tests generate synthetic bundles, perturb each required gate, exercise CLI
failure handling, and verify no process/network/file-writing collector APIs
exist in the evaluator. Existing packaging/control-flow tests remain required.
The future collector and immutable artifact lock are separate bounded units;
APT permission repair and runtime operations still need operator approval.
