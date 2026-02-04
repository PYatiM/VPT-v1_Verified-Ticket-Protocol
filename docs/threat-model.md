# VTP/1 — Threat Model

## 1. Goal

This document explains:
- What needs protection
- What attackers can do
- How the protocol defends itself
- What risks still exist

---

## 2. Assets

    | Asset         | Why It Matters            |
    |---------------|---------------------------|
    | Session State | Keeps protocol correct    |
    | Session Keys  | Allows sending valid data |
    | Server Secret | Root of all security      |
    | Tickets       | Identify sessions         |
    | User Messages | Should not be changed     |
    
---

## 3. Attacker Model

An attacker can:
- Listen to network traffic
- Replay old messages
- Send fake packets
- Modify messages
- Try to reuse tickets

An attacker cannot:
- Access the server directly
- Steal the server secret
- Break HMAC

---

## 4. Trust Zones

Zones:
- Attacker
- Network
- Client
- Server
- Session Store

The network is always untrusted.

---

## 5. Main Threats

### Spoofing
Trying to act like a real client.  
Defense: Session key proof.

---

### Tampering
Changing messages in transit.  
Defense: MAC check.

---

### Replay
Sending old messages again.  
Defense: Sequence numbers and TTL.

---

### Denial of Service
Sending too many or large messages.  
Defense:
- Size limits
- Timeouts
- Early rejection

---

### Privilege Abuse
Using a ticket without a session key.  
Defense: Proof validation.

---

## 6. Threat Mapping

    | Threat        | Defense             |
    |---------------|---------------------|
    | Fake Client   | Proof-of-possession |
    | Modified Data | HMAC                |
    | Replay        | Sequence            |
    | Ticket Theft  | IP binding          |
    | Flooding      | Limits and timeouts |
   
---

## 7. Attack Points

- Network entry
- Protocol state checks
- Session lookup
- MAC verification

---

## 8. Remaining Risks

    | Risk          | Impact          |
    |---------------|-----------------|
    | No TLS        | MITM possible   |
    | Server hacked | Full compromise |
    | Clock issues  | TTL problems    |
    | Redis exposed | Session leak    |

---

## 9. Defense Layers

    Network
        ↓
    Frame Check
        ↓
    State Check
        ↓
    Session Check
        ↓
    Sequence Check
        ↓
    MAC Check
        ↓
    Application


---

## 10. Summary

Security in this project comes from:
- Remembering past actions
- Checking message order
- Proving ownership of keys
- Rejecting invalid input early

This shows that **security is not just encryption, but system design.**