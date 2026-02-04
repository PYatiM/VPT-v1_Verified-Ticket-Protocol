# VTP/1 — System Architecture

## 1. Overview

VTP/1 is a small client-server system that focuses on **secure communication and replay protection**. The main idea is to separate different responsibilities into layers so the system is easier to understand, test, and improve later.

Instead of putting everything in one file, the project is divided into parts for:
- Network communication
- Message formatting
- Security (crypto)
- Session memory
- Protocol rules

This helps keep the code clean and avoids mixing logic that should stay separate.

---

## 2. Layered Design

The system follows a simple flow from bottom to top:

    Application Logic
          ↓
    Protocol Rules
          ↓
    Message Framing
          ↓
    TCP Network


### What This Means

- **TCP Network**  
  Sends and receives raw data.
- **Message Framing**  
  Makes sure full messages are read properly.
- **Protocol Rules**  
  Decides what messages are allowed and in what order.
- **Application Logic**  
  Handles the actual data sent by the client.

---

## 3. System Components

### Client Side

**VTP Client**
- **Crypto Module**
  - Creates HMAC values
  - Helps generate session keys
- **Framing Module**
  - Adds and removes length headers for messages
- **Protocol Logic**
  - Runs the handshake
  - Tracks sequence numbers
  - Sends secure data messages

---

### Server Side

**VTP Server**
- **Network Listener**
  - Accepts client connections
  - Reads and sends messages
- **Protocol Handlers**
  - Checks if messages follow the rules
  - Verifies MACs
  - Controls session state
- **Session Store**
  - Saves active and pending sessions
  - Tracks last sequence number
  - Handles timeouts and expiration

---

### External Parts

- **Session Backend**
  - Can be memory or Redis
- **Time Source**
  - Used for ticket expiration
- **TLS (Optional)**
  - Can be added for encrypted communication

---

## 4. Trust Boundaries

The system is divided into different trust zones.

### Zones

- Client Machine
- Server Machine
- Session Store
- Network (Untrusted)

### Why This Matters

Anything coming from the **network cannot be trusted**.  
Only after checking:
- Ticket
- Sequence number
- MAC

The server accepts a message as valid.

---

## 5. File Responsibilities

### `main.py`
This is the entry point.
It decides:
- Run as server
- Or run as client

---

### `common/config.py`
This file stores:
- Server secret
- Protocol version
- Timeouts and TTL values

It makes it easy to change security settings without changing the protocol code.

---

### `common/crypto.py`
This file handles:
- Random number generation
- HMAC creation

The rest of the system just asks this file to “make a MAC” instead of doing crypto itself.

---

### `common/framing.py`
This file fixes a TCP problem:
TCP sends streams, not messages.

So this file:
- Adds message length headers
- Makes sure full messages are read properly

---

### `server/session_store.py`
This is the memory of the server.
It stores:
- Pending tickets
- Active sessions
- Sequence numbers
- IP addresses
- Expiration times

---

### `server/handlers.py`
This file is the “brain” of the system.
It:
- Enforces message order
- Verifies MACs
- Controls session state

---

### `server/server.py`
This file only handles networking.
It:
- Accepts connections
- Sends and receives messages
- Passes messages to handlers

It does NOT do crypto or protocol checks.

---

### `client/client.py`
This file acts like a real protocol user.
It:
- Runs the handshake
- Generates proofs
- Sends secure messages

---

## 6. Scaling Model

### Single Node
- Sessions stored in memory
- Good for testing and learning

### Redis-Based
- Sessions stored in Redis
- Allows multiple servers to share session state

### Load Balanced
- Multiple servers
- One shared session store
- Clients can connect to any server

---

## 7. Deployment Model

### Development
- No TLS
- In-memory session store
- Debug logs

### Production
- TLS enabled
- Redis session store
- Logging and monitoring

---

## 8. How a Packet Moves

Client:
1. Creates payload
2. Adds MAC
3. Frames message
4. Sends over TCP

Server:
1. Reads framed message
2. Checks session
3. Verifies sequence
4. Verifies MAC
5. Accepts or rejects

---

## 9. Why This Design Is Useful

This design helps:
- Keep security logic separate
- Make testing easier
- Add new features without breaking old ones
- Understand where errors happen

---

## 10. Simple Mental Model

> Framing sends messages  
> Crypto proves identity  
> Session store remembers state  
> Handlers enforce rules  
> Server connects clients  
> Client follows the protocol