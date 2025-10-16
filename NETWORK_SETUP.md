# �� Network Setup Guide

## Quick IP Update (When Changing Networks)

### Step 1: Find Your New IP
```bash
# On your laptop (server)
ip addr show wlp2s0 | grep "inet "

# Example output:
# inet 192.168.23.187/24 ...
# Your IP is: 192.168.23.187
```

### Step 2: Update Config (ONE PLACE ONLY!)
```bash
# Edit server/config.py
nano server/config.py

# Change line 9:
SERVER_IP = os.getenv("SERVER_IP", "192.168.23.187")  # <- Update this IP
```

### Step 3: Commit and Push
```bash
git add server/config.py
git commit -m "update: change IP to 192.168.23.187"
git push origin main
```

### Step 4: Update Termux
```bash
# In Termux
cd ~/CampusConvo
git pull origin main

# Test
python client.py "test"
```

---

## 🚀 Quick One-Liner

```bash
# On laptop - Get IP, update config, and push
NEW_IP=$(ip addr show wlp2s0 | grep "inet " | awk '{print $2}' | cut -d'/' -f1) && \
sed -i "s/SERVER_IP = os.getenv(\"SERVER_IP\", \"[0-9.]*\")/SERVER_IP = os.getenv(\"SERVER_IP\", \"$NEW_IP\")/" server/config.py && \
echo "Updated to: $NEW_IP" && \
git add server/config.py && \
git commit -m "update: IP to $NEW_IP" && \
git push origin main
```

---

## 📱 Hotspot Setup

### Phone Hotspot → Laptop Server
1. Enable hotspot on phone
2. Connect laptop to phone's hotspot
3. Find laptop's IP: `ip addr show wlp2s0 | grep "inet "`
4. Update `server/config.py` with new IP
5. Push to GitHub

### Laptop Hotspot → Phone Client
1. Enable hotspot on laptop:
   ```bash
   nmcli device wifi hotspot ssid "CampusConvo" password "campusconvo123"
   ```
2. Laptop IP is usually: `10.42.0.1` or `192.168.173.1`
3. Update `server/config.py` with `10.42.0.1`
4. Push to GitHub

---

## 📊 Common IP Ranges

| Network Type | Typical IP Range | Example |
|--------------|------------------|---------|
| Home WiFi | 192.168.0.x - 192.168.255.x | 192.168.1.100 |
| Office/College | 10.0.0.x - 10.255.255.x | 10.0.1.50 |
| Phone Hotspot (Android) | 192.168.43.x | 192.168.43.1 |
| Phone Hotspot (iPhone) | 172.20.10.x | 172.20.10.1 |
| Laptop Hotspot (Linux) | 10.42.0.x | 10.42.0.1 |
| Laptop Hotspot (Windows) | 192.168.137.x | 192.168.137.1 |

---

## ✅ Verification

Test connection:
```bash
# In Termux
ping 192.168.23.187  # Your server IP

# If ping works, test client
python client.py "hello"
```
