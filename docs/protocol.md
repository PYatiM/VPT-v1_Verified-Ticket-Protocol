# VTP/1 — Verified Ticket Protocol v1

## 1. Introduction

VTP/1 is a simple security protocol made to **protect a client-server connection from replay attacks and fake messages**.

It uses:
- Tickets given by the server
- Session keys created using nonces
- Sequence numbers to track order
- HMAC to verify messages

The main goal is to show how real protocols use **state and cryptography together**.

---

## 2. Basic Idea

The protocol works like this:
1. Client says hello
2. Server gives a challenge and a ticket
3. Client proves it owns the session key
4. Server allows secure data messages

Only a client with the correct session key can send valid data.

---

## 3. Terminology

    | Term            | Meaning                         |
    |-----------------|---------------------------------|
    | Ticket          | Server-created ID for a session |
    | Session Key     | Secret key for MAC generation   |
    | Nonce           | Random number for freshness     |
    | Sequence Number | Counter for message order       |
    | MAC             | Proof that message is real      |

---

## 4. Message Flow

    Client → Server: HELLO
    Server → Client: CHALLENGE
    Server → Client: TICKET
    Client → Server: ACTIVATE
    Server → Client: OK
    Client → Server: DATA


---

## 5. Message Types

### HELLO
Starts the connection.

Fields:
- type
- client_nonce

---

### CHALLENGE
Server sends its nonce.

Fields:
- type
- server_nonce

---

### TICKET
Server sends ticket.

Fields:
- type
- ticket
- ttl

---

### ACTIVATE
Client proves it has the session key.

Fields:
- type
- ticket
- proof

---

### OK
Server confirms activation.

Fields:
- type

---

### DATA
Secure message.

Fields:
- type
- ticket
- seq
- payload
- mac

---

## 6. How Keys Are Made

### Ticket

ticket = HMAC(server_secret, client_nonce + server_nonce + ip + time)


### Session Key

session_key = HMAC(server_secret, ticket + client_nonce + server_nonce)


### Message MAC

mac = HMAC(session_key, seq + payload)


---

## 7. Session States

    START → PENDING → ACTIVE → EXPIRED


### Rules
- DATA before ACTIVE → Reject
- ACTIVATE after EXPIRED → Reject
- Old sequence number → Reject

---

## 8. Sequence Rules

- Starts at 0
- Must increase by 1 each time
- Server rejects duplicates or old numbers

---

## 9. Error Handling

    | Problem        | Server Action  |
    |----------------|----------------|
    | Bad MAC        | Ignore message |
    | Expired ticket | Reject         |
    | Wrong proof    | Reject         |
    | Bad format     | Disconnect     |

---

## 10. Security Features

    | Feature             | How It Works     |
    |---------------------|------------------|
    | Replay Protection   | Sequence numbers |
    | Authenticity        | HMAC             |
    | Freshness           | Nonces           |       
    | Session Binding     | Ticket + IP      |
    | Tamper Detection    | MAC              |

---

## 11. Limitations

- No encrypted messages (without TLS)
- No forward secrecy
- One main server secret
- No user login system

---

## 12. Mental Model

> Ticket = Who you are  
> Session key = Proof you are real  
> Sequence = Time order  
> MAC = Message proof