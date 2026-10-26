# SQLPhantom Security Policy

The SQLPhantom project takes software security, responsible disclosure, and defensive engineering seriously. This document outlines our vulnerability disclosure process, supported software versions, and internal security guardrails.

---

## 1. Reporting a Vulnerability

If you discover a security vulnerability in SQLPhantom (such as a command injection vector, unauthorized file access, privilege escalation, or scope guardrail bypass), please report it responsibly.

### Disclosure Channels
- **GitHub Security Advisory**: Submit a private advisory via [GitHub Security Advisories](https://github.com/sqlphantom/sqlphantom/security/advisories/new).
- **Security Email**: If you cannot use GitHub Advisories, email the maintainers directly at:
  ```
  security@sqlphantom.org
  ```

### What to Include
To help us triage and resolve the issue quickly, please provide:
1. **Description**: A clear summary of the vulnerability and its potential impact.
2. **Steps to Reproduce**: A minimal, reproducible proof-of-concept (PoC), script, or configuration.
3. **Affected Versions**: SQLPhantom version, operating system, and Python environment.
4. **Suggested Fix**: Any recommended code or configuration remediation (if known).

### Response SLA & Coordination
- **Initial Acknowledgement**: Within **48 hours** of report receipt.
- **Triage & Assessment**: Within **5 business days**, detailing validity and severity score (CVSS v3.1).
- **Fix & Advisory Release**: Coordinated patch and advisory release within **14–30 days**, or sooner for critical vulnerabilities.

We ask that you refrain from public disclosure until an official fix is published.

---

## 2. Supported Versions

Security updates and patches are provided for the following versions:

| Version | Supported | Release Type | Notes |
| :--- | :--- | :--- | :--- |
| **0.1.x** | **Yes** | Active Development | Current development baseline (Phase 1 Foundation). |
| `< 0.1.0` | No | Pre-Alpha | Deprecated internal prototypes. |

When version `1.0.0` is released, security patches will follow Semantic Versioning with dedicated patch releases (`1.0.x`).

---

## 3. Security Engineering & Architecture Guardrails

SQLPhantom is designed with defensive programming principles to ensure that operator security and target safety are protected:

### 3.1. Strict Target Scope Guardrails
- **Pre-Flight Host Validation**: Before any HTTP scan task is submitted to the engine, target URLs are parsed and evaluated against the user-defined scope whitelist.
- **CIDR Network Range Validation**: Resolves target hostnames to IP addresses and verifies that the resolved address falls within authorized network blocks, preventing DNS rebinding or accidental multi-tenant scanning.
- **Redirect Interception**: Disallows uncontrolled following of redirects that lead out-of-scope.

### 3.2. Automatic Credential & Data Redaction
- **Header & Token Masking**: Sensitive HTTP headers (including `Authorization`, `Cookie`, `X-Api-Key`, `Token`) are automatically masked with `***REDACTED***` in console displays, SQLite log records, and generated report artifacts.
- **Database Dump Privacy**: Extracted column data can be automatically scrubbed for common sensitive patterns (passwords, credit card numbers, social security identifiers) prior to report generation.

### 3.3. Safe Subprocess Execution
- **Zero Shell Interpolation**: Subprocess execution (including spawning `sqlmapapi.py`) strictly uses sanitized parameter lists rather than shell strings (`shell=False` everywhere).
- **Executable Validation**: Subprocesses are spawned using absolute, validated paths to the active Python interpreter.

### 3.4. Local File & SQLite Permission Isolation
- **Restricted Access Modes**: SQLite session databases (`sqlphantom.db`) and exported reports are created with restrictive permissions (`0600` on POSIX systems; restricted owner DACLs on Windows) to prevent local privilege leakage.

---

## 4. Anti-Evasion & Non-Stealth Policy

> [!IMPORTANT]
> **Strict Non-Stealth / Compliance Design**
> SQLPhantom is engineered exclusively for authorized security assessment, compliance verification, and penetration testing.
> 
> In accordance with this principle:
> - SQLPhantom does **not** provide anti-virus (AV) evasion, Endpoint Detection and Response (EDR) bypassing, process hollowing, or rootkit capabilities.
> - SQLPhantom does **not** provide autonomous weaponized exploitation modules.
> - While SQLPhantom exposes upstream sqlmap tamper scripts for WAF encoding compliance testing, it does not package weaponized payloads or illegal exploitation utilities.

---

## 5. Authorized Testing & Legal Mandate

> [!CAUTION]
> **Mandatory Authorization Notice**
> SQLPhantom is a dual-use security utility. You must **only** use SQLPhantom against systems, networks, and applications that you own or for which you have received **explicit, written authorization** from the lawful asset owner.
> 
> Executing security tests against unauthorized targets is a criminal offense under the United States Computer Fraud and Abuse Act (18 U.S.C. § 1030), the United Kingdom Computer Misuse Act 1990, the European Union Cybercrime Directive (2013/40/EU), and equivalent legislation globally.
> 
> The developers and contributors of SQLPhantom accept **no responsibility or liability** for misuse, damage, or legal consequences arising from the use of this software.
