# VirtualBox Networking & Hardware Wi-Fi Passthrough

**Author**: Tadigotla Vasanth Diwakar (USN: `25BTRCL270`)  
**Target Environment**: Oracle VirtualBox on Windows Host

---

## 1. VirtualBox Network Emulation Modes

When running MicroOS inside Oracle VirtualBox, it is critical to understand the distinction between Virtual Ethernet and Physical Wireless Hardware:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        WINDOWS HOST SYSTEM                             │
│   Host Wi-Fi Card (Connected to Home/Campus Wi-Fi AP)                  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
    ┌───────────────────────────────┴───────────────────────────────┐
    ▼                                                               ▼
┌─────────────────────────────────┐   ┌──────────────────────────────────┐
│        1. VIRTUALBOX NAT        │   │       2. VIRTUALBOX BRIDGED      │
│  Host acts as Router/NAT        │   │  VM acts as distinct device on   │
│  Guest receives virtual Ethernet│   │  LAN with independent IP         │
│  (enp0s3 / eth0)                │   │  (enp0s3 / eth0)                 │
└────────────────┬────────────────┘   └─────────────────┬────────────────┘
                 │                                      │
                 ▼                                      ▼
┌────────────────────────────────────────────────────────────────────────┐
│                    MICROOS GUEST OPERATING SYSTEM                      │
│  Internet access works perfectly via Virtual Ethernet!                 │
│  However, MicroOS CANNOT scan physical Wi-Fi channels through NAT.     │
└────────────────────────────────────────────────────────────────────────┘
```

> [!NOTE]
> **Why Wi-Fi Scanning Doesn't Work via NAT**:
> VirtualBox NAT exposes a virtual wired Intel PRO/1000 or VirtIO Ethernet card (`enp0s3`) to the guest. It does NOT pass the 802.11 radio transceiver commands (`nl80211`). Therefore, internet and web browsing work seamlessly, but Micro Wi-Fi Scanner will report that no wireless hardware is present.

---

## 2. Enabling Real Wi-Fi Scanning via USB Passthrough

To discover surrounding Wi-Fi networks from MicroOS inside VirtualBox, pass a compatible USB Wi-Fi adapter directly to the VM:

### Step 1: Install VirtualBox Extension Pack
Ensure the **Oracle VM VirtualBox Extension Pack** is installed on your Windows host. This enables the USB 2.0 (EHCI) and USB 3.0 (xHCI) controllers.

### Step 2: Plug in a Compatible USB Wi-Fi Dongle
Plug a USB Wi-Fi dongle into your Windows PC. Supported chipsets with native Linux drivers include:
- **Atheros** (`ath9k_htc`): TP-Link TL-WN722N v1
- **Ralink / MediaTek** (`rt2800usb` / `mt7601u`): Panda Wireless PAU05 / PAU06, RT5370
- **Realtek** (`rtl8xxxu` / `rtl8192cu`): EDUP, TP-Link TL-WN823N

### Step 3: Attach the USB Device to MicroOS
In the running VirtualBox window:
1. Open the top menu: **Devices** -> **USB**.
2. Select your Wi-Fi Adapter from the list (e.g., `Realtek 802.11n NIC` or `Atheros USB2.0 WLAN`).
3. Windows will detach the adapter, and VirtualBox will hand full hardware control to MicroOS.

### Step 4: Verify Inside MicroOS
In MicroShell, execute:
```bash
micro-wifi
```
The kernel will detect the new `wlan0` interface, trigger `nmcli device wifi rescan`, and populate the Micro Wi-Fi Scanner with real nearby access points!
