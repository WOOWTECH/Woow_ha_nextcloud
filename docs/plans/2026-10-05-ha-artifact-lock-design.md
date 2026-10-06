# Offline artifact lock — approved bounded continuation

`STATE.next_action=HA_PHP84_OFFLINE_ARTIFACT_LOCK` authorizes this independent
local unit, not resumption of blocked APT or a build/runtime collector.

## Decision

Use a standard-library Python verifier with an explicit public-artifact root,
manifest and observation-bundle hash. Compared with a checksum-only inventory,
this binds source/candidate image-manifest digests, full source commits,
architecture, versioned package/archive hashes and verification receipts to the
same observation bundle. Compared with an OCI/build/signature validator, it
requires no daemon, network, credentials, installation or approved runtime slot.
The latter remains a separate gate, never implemented through a workaround.

## Contract

Strict schema rejects unknown/missing fields, duplicate JSON keys/IDs, unresolved
pins/statuses, synthetic/stub labels, known repeated-character digest placeholders,
missing/changed files, unreferenced inputs and source/candidate architecture or
digest mismatches. Every image references an image-manifest artifact and a
nonempty package/archive input list; all supplied artifacts must be bound.
Relative regular files only: no absolute paths, traversal, symlink components,
devices, FIFOs or commands. Size and total-read limits bound offline work.

The raw image-manifest bytes are hashed, **not** a Docker-save tarball mislabeled
as a registry manifest digest. This is not OCI graph completeness verification.
Build/provenance receipt hashes bind caller-supplied assertions, not authenticated
signatures or complete dependency/source resolution. `verified` is a caller
claim; the verifier never promotes it to verified trust.

Exit 0 is only `offline_lock_consistent`. All reports keep signed-source,
image-build, runtime, HAOS and production authorization flags false. Synthetic
positive tests craft consistent declarations solely to test this contract; the
checked-in unresolved template and actual public-artifact inventory must remain
blocked. Existing observation evaluator is composed, not changed or bypassed.

## Verification

Temporary synthetic files exercise success, mutation, missing data, schema,
binding, status, path and CLI failures. Hash the already-downloaded public PHP
FPM deb and indexes without executing or installing them; record hashes apart
from signed-source/build trust. Re-run inventory, PHP, upgrade-guard, static,
shell-syntax and diff checks. Keep APT permission, real image/collector,
collation/reindex, NC33→34→35/full rollback, ARM, HAOS and MCP gates pending.
