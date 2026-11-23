# MicroOS Web Browser Configuration

**Browser**: Mozilla Firefox (Quantum / Gecko)  
**Configuration Path**: `/etc/firefox/policies/policies.json`  
**Default Homepage**: `file:///usr/share/microos/startpage.html`

---

## 1. Browser Architecture & Integration

Mozilla Firefox is installed as the primary web browser in MicroOS. It provides:
- Complete web standards support (HTML5, CSS3, JavaScript ES2024, WebAssembly, WebGL).
- Hardware-accelerated rendering when running with VirtualBox guest additions or native GPU.
- Sandboxed process model isolating web tabs from OS privileges.

---

## 2. Enterprise Policy Configuration (`policies.json`)

To tailor Firefox to the MicroOS engineering environment and prevent intrusive default popups or tracking, MicroOS deploys enterprise policies:

```json
{
  "policies": {
    "DisableAppUpdate": true,
    "DisableTelemetry": true,
    "DisableFirefoxStudies": true,
    "DontCheckDefaultBrowser": true,
    "Homepage": {
      "URL": "file:///usr/share/microos/startpage.html",
      "Locked": false,
      "StartPage": "homepage"
    },
    "NewTabPage": false,
    "SearchBar": "unified"
  }
}
```

---

## 3. MicroOS Engineering Start Page

The default start page (`microos/desktop/browser/startpage.html`) provides a minimalist, dark-themed engineering dashboard:
- Web search query box defaulting to DuckDuckGo without tracking cookies.
- Quick technical documentation cards:
  - *The Linux Kernel* (kernel.org)
  - *Ubuntu 24.04 Packages Search*
  - *IEEE Xplore Digital Library*
  - *ACM Digital Library*
- Direct links to local MicroOS documentation.

---

## 4. Connectivity Verification

Inside MicroOS, verify that Firefox is correctly passing traffic through VirtualBox NAT or the physical Wi-Fi interface:
```bash
curl -I https://example.com
```
Then launch Firefox from Micro Hub or terminal:
```bash
firefox https://example.com
```
