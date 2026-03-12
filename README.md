# Angel Cloud Auth Bridge

> The unified Single Sign-On and security bridge for the entire Angel Cloud AI ecosystem.

This project operates under the [ShaneTheBrain Constitution](https://github.com/thebardchat/constitution/blob/main/CONSTITUTION.md).

---

## What This Is

A Node.js + Express authentication bridge that proxies auth requests to Angel Cloud, handling JWT tokens, blockchain wallet integration, TOTP 2FA, and rate-limited API security on behalf of clients.

---

## Infrastructure

All `thebardchat` repositories run on local-first hardware:

| Component | Detail |
|-----------|--------|
| **Compute** | Raspberry Pi 5 (16 GB RAM) |
| **Chassis** | Pironman 5-MAX by Sunfounder (NVMe RAID) |
| **Storage** | 2x WD Blue SN5000 2 TB NVMe — RAID 1 via mdadm |
| **Core path** | `/mnt/shanebrain-raid/shanebrain-core/` |
| **Networking** | Tailscale VPN across all nodes |

> Pi before cloud. Privacy before convenience. — Pillar 4

---

## Installation

```bash
npm install
```

## Usage

Create a `.env` file in the project root (see `.env.example`):

```
ANGEL_CLOUD_API_KEY=your_api_key
ANGEL_CLOUD_BASE_URL=https://api.angel-cloud.dev
```

Then start the server:

```bash
# Production
npm start

# Development (auto-reload)
npm run dev
```

The API will be available at `http://127.0.0.1:3005`.

---

## Endpoints

### POST /auth/token

Proxies the request to the Angel Cloud `/auth/token` endpoint.

**Request Body:**

```json
{
    "username": "your_username",
    "password": "your_password"
}
```

### POST /auth/validate

Proxies the request to the Angel Cloud `/auth/validate` endpoint.

**Request Body:**

```json
{
    "token": "your_token"
}
```

---

## Built With

| Partner | Role |
|---------|------|
| **Claude by Anthropic** · [claude.ai](https://claude.ai) | Co-built this entire ecosystem |
| **Raspberry Pi 5** · [raspberrypi.com](https://www.raspberrypi.com) | Local compute backbone |
| **Pironman 5-MAX** · [pironman.com](https://www.pironman.com) | NVMe RAID 1 chassis that made it real |

---

*[@thebardchat](https://github.com/thebardchat) · Hazel Green, Alabama*
