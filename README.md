# Terminal Chat

A terminal-based chat application with end-to-end encryption.

## Features

- RAM only, no disk usage
- No http, no websocket, just raw tcp
- E2E encryption: Fernet (AES-128-CBC + HMAC-SHA256)
- Zero dependencies on web frameworks, only asyncio and cryptography
- Password-protected rooms
- Colored usernames (8 unique colors)
- Simple JSON-based protocol

## Usage

### Start Server

```bash
tc serve <host> <port> --password <password>
```

Example:
```bash
tc serve 0.0.0.0 5000 --password mypassword
```

### Connect Client

```bash
tc connect <host> <port> <username> <password>
```

Example:
```bash
tc connect localhost 5000 Alice mypassword
```

### Commands

- `/quit` - Leave the chat room
- `/help` - Show available commands

![terminal_chat_01](https://github.com/user-attachments/assets/e6caf86b-c9fa-4b70-9f0e-76dd57aa2070)

## How It Works

```text
┌───────────────────────────────────────────────────────────────────┐
│                      PASSWORD AUTHENTICATION                      │
├───────────────────────────────────────────────────────────────────┤
│                                                                   │
│  CLIENT                                                   SERVER  │
│    │                                                         │    │
│    │══════════ TCP CONNECT (plaintext) ═════════════════════►│    │
│    │                                                         │    │
│    │────────── {"type":"auth","password":"secret"} ─────────►│    │
│    │           (password sent in plaintext)                  │    │
│    │                                                         │    │
│    │◄───────── {"type":"init","room_salt":"hex"} ────────────│    │
│    │           (room_salt = 16 bytes)                        │    │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

```text
┌──────────────────────────────────────────────────────────────────┐
│                 E2E ENCRYPTED CHAT (same socket)                 │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  CLIENT                                                  SERVER  │
│    │                                                        │    │
│    │──── {"type":"msg","user":"Alice","text":encrypted} ───►│    │
│    │     (Fernet-encrypted payload)                         │    │
│    │                                                        │    │
│    │◄─── {"type":"msg","user":"Bob","text":encrypted} ──────│    │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

```text
┌──────────────────────────────────────────────────────────────────┐
│                          KEY HIERARCHY                           │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
|  password                                                        |
|     │                                                            |
|     └── HKDF(password, room_salt)                                |
|          │                                                       |
|          └── room_key (shared)                                   |
│                                                                  │
│  room_salt : generated once at server start (16 bytes)           │
│  room_key  : same for all clients with same password             │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

## Encryption Details

- **Algorithm**: Fernet (AES-128-CBC + HMAC-SHA256)
- **Key Derivation**: HKDF-SHA256 with 16-byte salt
- **Key Length**: 256 bits (32 bytes)
- **Context String**: `b"cmd-chat-room-key"`

## License

MIT License.