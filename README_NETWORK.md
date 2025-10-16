# 🎯 Quick Reference: Network Configuration

## ⚡ When You Change Networks (Simple 3 Steps)

### 1️⃣ Find Your New IP
```bash
ip addr show wlp2s0 | grep "inet "
# Example: inet 192.168.23.187/24 ...
```

### 2️⃣ Edit ONE File Only
```bash
nano server/config.py
```
Change **line 9**:
```python
SERVER_IP = os.getenv("SERVER_IP", "192.168.23.187")  # ← Update this
```

### 3️⃣ Push to GitHub
```bash
git add server/config.py
git commit -m "update: IP to 192.168.23.187"
git push origin main
```

**That's it!** Both `client.py` and `client_minimal.py` will automatically use the new IP.

---

## 📱 In Termux (Phone)

```bash
cd ~/CampusConvo
git pull origin main
python client.py "test"
```

---

## �� Super Quick One-Liner

Copy-paste this on your laptop:

```bash
NEW_IP=$(ip addr show wlp2s0 | grep "inet " | awk '{print $2}' | cut -d'/' -f1) && sed -i "s/SERVER_IP = os.getenv(\"SERVER_IP\", \"[0-9.]*\")/SERVER_IP = os.getenv(\"SERVER_IP\", \"$NEW_IP\")/" server/config.py && git add server/config.py && git commit -m "update: IP to $NEW_IP" && git push origin main && echo "✓ Updated to $NEW_IP"
```

---

## 📂 File Structure

```
CampusConvo/
├── server/
│   └── config.py          ← EDIT THIS (line 9: SERVER_IP)
├── client.py              ← Auto-imports from config.py
└── client_minimal.py      ← Auto-imports from config.py
```

---

## �� How It Works

1. `server/config.py` defines `SERVER_IP`
2. Both clients import `WEBSOCKET_URL` from config
3. **You only update ONE place**: `server/config.py`
4. Everything else updates automatically! 🎉

---

See [NETWORK_SETUP.md](NETWORK_SETUP.md) for detailed hotspot instructions.
