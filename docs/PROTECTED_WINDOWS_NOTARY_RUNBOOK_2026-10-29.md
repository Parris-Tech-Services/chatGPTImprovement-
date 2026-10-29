# Protected Windows Notary — Safe Activation and Verification Checklist (not executed)

**Why this exists:** The GitHub-hosted CI proof establishes that AgentWitness and LLMAccountability's V2 policy/CLI run, but does **not** prove the privileged Windows SYSTEM notary/worker/runner. That trust boundary cannot be emulated by a Linux test or a non-privileged fake local API.

**Current state:** NO access from this ChatGPT environment to a Windows workstation, its localhost port 8123, or its signing key. **No installation or service action was performed.** The actions below require the authorised Windows machine owner / administrator. Do not expose the notary over the public internet or paste secrets into chat.

## 1. Read existing implementation before changing the machine

On an approved Windows machine with the real [LLMAccountability](https://github.com/Parris-Tech-Services/LLMAccountability) checkout, read:

- `README.md`, `docs/ARCHITECTURE.md` and `docs/THREAT_MODEL.md`;
- `install_service.ps1` *before any elevated execution*;
- `agy_service.py`, `agy_worker.py`, `agy.py`;
- [AgentWitness hardened backend implementation](https://github.com/Parris-Tech-Services/AgentCheck/blob/main/src/agentwitness/backends.py).

The installer creates/changing Windows identities, ACLs, scheduled tasks and logon rights: **do not run automatically** as part of a general ChatGPT task, hosted PR, or public CI.

## 2. Read-only preflight checks

These do not install or change machine configuration:

```powershell
Get-NetTCPConnection -LocalAddress 127.0.0.1 -LocalPort 8123 -State Listen -ErrorAction SilentlyContinue
Get-NetTCPConnection -LocalAddress 127.0.0.1 -LocalPort 8124 -State Listen -ErrorAction SilentlyContinue
Test-NetConnection -ComputerName 127.0.0.1 -Port 8123
Test-NetConnection -ComputerName 127.0.0.1 -Port 8124
```

Check locally that the expected process identity and protected key ACLs are consistent with the documented architecture, **without printing private key contents, credentials or HMAC values**. Reachable ports alone are insufficient to verify trust.

## 3. Controlled test job (after confirming existing service)

Run from a clean, non-sensitive test repository only:

```powershell
python -m pytest -q
python agy.py audit-report .\test-report.md --repo-path C:\SafeTestRepo --test-profile python-full --enforce
```

`test-report.md` must exist and contain only checkable claims matching actual performed work. A pre-existing fixture should cover supported `tests-pass` and `pushed` claims with real local/remote SHA. Unsupported `no-secrets`, `security-reviewed` or `fully-complete` wording must remain INCONCLUSIVE/FAIL unless independently supported.

Then, in the same safe authorised repository, run the real AgentWitness anchored contract and `aw task verify --hardened` / `aw final --hardened`. Independently check signing key trust, the returned signature, exact report/subject binding and user-visible task outcome.

**Important current gap:** LLMAccountability's existing V2 CLI sends `sha256:dummy` as the report subject digest; this is an outstanding L02 issue and prevents relying on that field as a trustworthy report-content binding. Do not certify full cryptographic report integrity until this is fixed and re-tested.

## 4. Future hosted-to-local bridge — design boundary

A safe optional bridge should:
- take only **explicitly authorised**, narrowly scoped jobs from a private queue or trusted runner;
- restrict actor credentials/permissions and source checkout to exact trusted SHAs;
- isolate untrusted PR code and tools from the SYSTEM notary host;
- support nonce/replay protection, strict timeouts, output redaction and expiring signed results;
- verify resulting attestations and original external evidence on the consumer side;
- never use a fake localhost server, copied private key, unsigned transcript import or unverified result as a substitute for the actual protected service;
- require a separately authorised machine/security review before enabling anything remotely.

An unattended or privileged agent must not start these services simply to make a completion metric green. When not configured, the right state is **BLOCKED — protected service unavailable**, not PASS.

## Remaining ownership

- **L01/L02:** Windows notary current-state proof and real report hash binding (LLMAccountability).
- **I01:** actual user-facing app acceptance and evidence from a substantive engineering task.
- **A02/I04:** safe structured broker/final-hook integration for reachable hosted clients.
- **S01/S02:** least privilege, consent, signing key protection and independent audit.

This checklist is a deploy/verification **runbook**, not a claim of completed Windows installation, service access, hardening, or protected attestation.
