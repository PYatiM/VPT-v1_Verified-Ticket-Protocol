# VTP/1 — Verified Ticket Protocol
    

VTP/1 is a small security protocol I built to learn how **real client-server systems protect themselves from replay attacks, fake packets, and session abuse**.

It runs on top of TCP and uses:
- Server-issued tickets  
- Random nonces  
- Sequence numbers  
- HMAC-SHA256  

The main idea is simple:  
**If you don’t have the session key, you can’t send valid messages.**

---

## What This Project Is About

Most networking projects just “send data.”  
This one focuses on **how systems decide whether data should be trusted**.

VTP/1 shows:
- How a server remembers past messages
- How a client proves it owns a secret
- How message order is enforced
- How fake or replayed packets get rejected

---

## Folder Layout

    vtp-protocol/
    ├── README.md
    ├── LICENSE
    ├── requirements.txt
    ├── docs/
    │ ├── protocol.md
    │ ├── threat-model.md
    │ ├── architecture.md
    │ └── diagrams/
    │ ├── sequence.png
    │ ├── state-machine.png
    │ └── data-flow.png
    ├── src/
    │ ├── common/
    │ │ ├── crypto.py
    │ │ ├── framing.py
    │ │ └── config.py
    │ ├── server/
    │ │ ├── session_store.py
    │ │ ├── handlers.py
    │ │ └── server.py
    │ ├── client/
    │ │ └── client.py
    │ └── main.py
    ├── tests/
    │ ├── replay_test.py
    │ ├── injection_test.py
    │ └── load_test.py
    └── examples/
    ├── simple_client.py
    └── simple_server.py


---

## How the Protocol Works (Simple View)

1. Client says hello  
2. Server sends a challenge and a ticket  
3. Client proves it owns the session key  
4. Server allows secure messages  
5. Every message must increase a counter  

If a message is:
- Old  
- Changed  
- Or out of order  

The server ignores it.

---

## Message Flow

    Client → Server: HELLO
    Server → Client: CHALLENGE
    Server → Client: TICKET
    Client → Server: ACTIVATE
    Server → Client: OK
    Client → Server: DATA (seq, mac)


---

## Security Ideas Used

- **Tickets**  
  Act like session IDs that are hard to fake

- **Session Keys**  
  Used to prove the client is real

- **Sequence Numbers**  
  Stop replay attacks

- **MAC (HMAC)**  
  Detect message changes

---

## Running the Project

### Requirements
- Python 3.11+

### Install

    pip install -r requirements.txt

### Start the server

    python src/main.py --mode server

### Start the client

    python src/main.py --mode client

You should see the server printing messages sent by the client after the handshake finishes.

## Testing Ideas

### Replay Test
Try sending the same data packet twice.
The server should accept the first and ignore the second.

### Tamper Test
Change the message after the MAC is created.
The server should reject it.

### Load Test
Run multiple clients at once and see if the server stays responsive.

## Why I Designed It This Way
- Tickets Instead of Simple Tokens
- A ticket alone isn’t enough.
- The client must also prove it owns the session key.
  
### Nonces
They make every session unique and hard to predict.

### Sequence Numbers
They give the server “memory” of what it has already seen.

## Limitations

- Messages are not encrypted unless TLS is added
- No forward secrecy
- One main server secret
- No login or user accounts

## What I’d Improve Next

- Add TLS for encrypted traffic
- Use ECDH for forward secrecy
- Store sessions in Redis
- Add logs and basic monitoring
- Add protocol versioning

## License


MIT License
