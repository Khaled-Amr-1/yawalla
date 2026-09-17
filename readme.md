# YaWalla 🌐

This is a demo for an alternative to available data usage tracking apps. There was no solution for my needs in linux.

All I needed was a Linux tool that tracks Wi-Fi usage by **Network name (SSID)** and shows **which apps consumed this usage**.

**For example:**
* **Home Wifi:** 5 GB (Brave: 3.5 GB, Code: 1.5 GB)
* **Office Wifi:** 7 GB (Discord: 3 GB, Chrome: 4 GB)

---

## How It Works

I used Python for faster development to finish it in a couple of hours. 
* I wrapped `nmcli` to get info about the Wi-Fi network name (SSID) and the MAC of the router I'm directly connected to (BSSID).
* I used `nethogs` to track data usage. It did well until I realized I couldn't track packets using the UDP/QUIC protocol (like YouTube streams in modern browsers). As of Sep 17, 2026, `nethogs` is primarily used to track only TCP connections.

### The Database Architecture
I used SQLite to save the data usage with a simple schema of two tables:

**1. `networks` Table:**
* `bssid` (Primary Key): The MAC address of the router (assuming a single broadband signal).
* `ssid`: The network name to display it conveniently.
* `alias`: A custom name in case I connect to two networks with the same SSID and need to differentiate them.

**2. `traffic_logs` Table:**
* `log_date`: I wanted to accumulate traffic per day instead of adding a new row every couple of seconds.
* `bssid`: Linked to the router MAC.
* `program_name`: The app name extracted from the PID (though it came with some challenges, AI handled it for the demo XD).
* `download_bytes` / `upload_bytes`.

I made a Composite Primary Key of (`log_date`, `bssid`, `program_name`). This prevents the database from growing massively Instead of inserting millions of rows, it performs an **UPSERT** (updating the existing row for that app on that day), keeping the DB size tiny.

---

## Naming 

Now for the most important part: Naming the tool XD.

I was trying to come up with a name while listening to an Egyptian artist named Abdelbaset Hamouda. In his popular song *"Kolak Agebny"* ([Watch on YouTube](https://youtu.be/NoQnWLgTDSE)), he repeatedly sings: 

> *"I like everything about you, boy, I really do."*

In Arabic songs, it's very common to address female lovers using masculine pronouns or terms. He kept repeating the phrase "You boy", which is pronounced **"Ya Walla"**. So, I just decided to name it **YaWalla**.

---

## Run it

If you want to run this Python version, follow these steps:

### Prerequisites:
You need to have `nethogs` and `NetworkManager` installed on your Linux machine.
For Fedora:
```bash
sudo dnf install nethogs NetworkManager

```

For Ubuntu/Debian:

```bash
sudo apt install nethogs network-manager

```

### Running the App:

1. Clone the repository and navigate to the project folder.
2. Start the network monitor daemon (requires `sudo` for `nethogs`):
```bash
sudo python3 main.py

```


3. In a new terminal window, start the web interface:
```bash
python3 app.py

```


4. Open your browser and go to `http://127.0.0.1:5000` to see your traffic visualized!

---

## 🔮 What's Next? 

From today onwards, I'll be working on a much better version of this app. It will be a Native Desktop Application instead of opening a web browser on localhost.

* **The Stack:** I chose **Wails** for the frontend desktop wrap.
* **The Core:** I'll use **Go** for the backend, leveraging `cilium/ebpf` to write the core traffic sniffing by injecting into the kernel directly. This will bypass the `nethogs` UDP limitation and capture 100% of the traffic accurately.
* **The Goal:** I'll try to start and finish it today.

I would be proud if I made this app that I really need in my day-to-day life, and I would be even more proud if it helped anyone searching for the same solution. This means a lot to me to officially be a part of the open-source community that I relied on for years and that made my life easier!