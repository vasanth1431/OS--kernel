# MicroOS Network Implementation Guide

**Author**: Tadigotla Vasanth Diwakar (USN: `25BTRCL270`)  
**Components**: `microos/network-center/network_center.py`, `micro-network`, `micro-ip`, `micro-internet`

---

## 1. Real-Time Bandwidth Measurement Implementation

MicroOS does not use synthetic estimates to calculate download (RX) and upload (TX) speeds. It polls the Linux virtual kernel file `/proc/net/dev`:

```python
def _get_bytes_transferred(iface):
    with open("/proc/net/dev", "r") as f:
        for line in f:
            if iface in line:
                parts = line.split(":")[1].split()
                rx_bytes = int(parts[0])  # Received bytes counter
                tx_bytes = int(parts[8])  # Transmitted bytes counter
                return rx_bytes, tx_bytes
```

The difference between successive reads over an interval `dt` gives instantaneous bandwidth:
$$\text{Speed}_{\text{RX}} = \frac{\Delta \text{Bytes}_{\text{RX}}}{\Delta t \times 1024} \quad (\text{KB/s})$$

---

## 2. 3-Tier Connectivity Verification Algorithm

To avoid reporting false "Connected" status when only an internal IP is assigned, MicroOS implements a 3-tier verification sequence in `network_center.py` and `micro-internet`:

```text
                  ┌──────────────────────────────┐
                  │   Query Local Network State  │
                  └──────────────┬───────────────┘
                                 │
                                 ▼
                  ┌──────────────────────────────┐
                  │ Tier 1: Ping Default Gateway │
                  └──────────────┬───────────────┘
                        FAIL     │ PASS
         ┌───────────────────────┴───────────────────────┐
         ▼                                               ▼
┌─────────────────┐                       ┌──────────────────────────────┐
│  DISCONNECTED   │                       │ Tier 2: Ping External 1.1.1.1│
│ (No Link/Cable) │                       └──────────────┬───────────────┘
└─────────────────┘                             FAIL     │ PASS
                                  ┌──────────────────────┴───────────────┐
                                  ▼                                      ▼
                       ┌──────────────────────┐        ┌──────────────────────────────┐
                       │ LIMITED CONNECTIVITY │        │ Tier 3: Resolve example.com  │
                       │ (No External Route)  │        └──────────────┬───────────────┘
                       └──────────────────────┘              FAIL     │ PASS
                                                       ┌──────────────┴───────────────┐
                                                       ▼                              ▼
                                            ┌──────────────────────┐       ┌──────────────────────┐
                                            │ LIMITED CONNECTIVITY │       │      CONNECTED       │
                                            │     (DNS Failure)    │       │ (Full Internet Acc.) │
                                            └──────────────────────┘       └──────────────────────┘
```

### Implementation Details:
1. **Tier 1 (Gateway)**: Identifies the active default gateway using `ip route show default` and sends an ICMP echo request with a 1-second timeout.
2. **Tier 2 (Public IP)**: Pings `1.1.1.1` directly to test raw layer-3 IP forwarding bypassing DNS.
3. **Tier 3 (DNS & HTTPS)**: Executes a socket address resolution (`getent hosts example.com`) and an HTTP HEAD request (`curl -I https://example.com`) to verify that port 53 and port 443 are passing traffic.
