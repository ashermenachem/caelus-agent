# Changelog

All notable changes to Caelus Terminal are documented here.

## 0.1.0 — 2026-07-14

### Added
- Isolated local Hermes runtime launcher with loopback API configuration and health/status controls.
- Persistent Hermes sessions, structured run-event streaming, tool activity display, and run cancellation.
- Safe allowlisted agent-template export/import with checksum validation and extraction protections.
- A disclosed, three-attempt local access gate that stores only a salted verifier.
- MIT licensing, Hermes runtime attribution, a wheel build, isolated installer validation, and GitHub Actions release verification.

### Security and privacy
- Caelus runtime setup, templates, release artifacts, and installer tests exclude personal Hermes profiles, credentials, sessions, memory, logs, and browser state by construction.
- The local access gate is documented as a deterrent, not server-side authentication.
