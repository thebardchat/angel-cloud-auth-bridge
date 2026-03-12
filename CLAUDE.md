# CLAUDE.md — angel-cloud-auth-bridge

> Claude Code configuration for the `thebardchat/angel-cloud-auth-bridge` repository.

---

## Project Overview

This repository holds the **Angel Cloud Auth Bridge** — the unified Single Sign-On and security bridge for the entire Angel Cloud AI ecosystem. It handles authentication proxying, JWT token management, blockchain wallet integration, TOTP 2FA, and rate-limited API security.

This project operates under the [ShaneTheBrain Constitution](https://github.com/thebardchat/constitution/blob/main/CONSTITUTION.md).

---

## Infrastructure

All `thebardchat` repositories run on the following local-first infrastructure:

| Component | Detail |
|-----------|--------|
| **Compute** | Raspberry Pi 5 (16 GB RAM) |
| **Chassis** | Pironman 5-MAX by Sunfounder (NVMe RAID) |
| **Storage** | 2x WD Blue SN5000 2 TB NVMe — RAID 1 via mdadm |
| **Core path** | `/mnt/shanebrain-raid/shanebrain-core/` |
| **Networking** | Tailscale VPN across all nodes |
| **Dev environment** | Claude Code on Pi 5 |

> Pi before cloud. Privacy before convenience. — Pillar 4

---

## Repository Structure

```
angel-cloud-auth-bridge/
  angel-auth-bridge.js            # Main auth bridge server (Express)
  angel_chat_v2.js                # Angel chat integration
  dispatch_calculator_service.js  # Dispatch calculator service
  launch_angel_cloud.js           # Cloud launcher
  legacy_ai_integration_client.js # Legacy AI integration client
  pulsar_security_core.js         # Pulsar post-quantum security core
  voice_mode_final.js             # Voice mode handler
  mega-dashboard.html             # Unified dashboard UI
  package.json                    # Node.js dependencies
  .env.example                    # Environment variable template
  CLAUDE.md                       # This file — Claude Code project context
  README.md                       # Public-facing summary
```

---

## Tech Stack

- **Runtime:** Node.js + Express
- **Auth:** JWT (jsonwebtoken), bcrypt, TOTP via speakeasy
- **Blockchain:** ethers.js (wallet integration)
- **AI:** Google GenAI SDK
- **Security:** express-rate-limit, QR code generation
- **Tests:** Jest

---

## Working With This Repo

```bash
# Install dependencies
npm install

# Run the auth bridge
npm start

# Development mode (auto-reload)
npm run dev

# Run tests
npm test
```

Environment variables are configured via `.env` — see `.env.example` for required keys.

---

## Credits

Built with Claude (Anthropic) · Runs on Raspberry Pi 5 + Pironman 5-MAX

| Partner | Role |
|---------|------|
| **Claude by Anthropic** · [claude.ai](https://claude.ai) | Co-built this entire ecosystem |
| **Raspberry Pi 5** · [raspberrypi.com](https://www.raspberrypi.com) | Local compute backbone |
| **Pironman 5-MAX** · [pironman.com](https://www.pironman.com) | NVMe RAID 1 chassis that made it real |

---

*[@thebardchat](https://github.com/thebardchat) · Hazel Green, Alabama*
