import subprocess

def get_active_wifi_info():
    wifi_info = {
        "name": None,
        "uuid": None,
        "bssid": None
    }
    try:
        cmd_connection = ["nmcli", "-t", "-f", "NAME,TYPE,UUID", "connection", "show", "--active"]
        result_conn = subprocess.run(cmd_connection, capture_output=True, text=True, check=True)
        for line in result_conn.stdout.strip().split('\n'):
            if "802-11-wireless" in line:
                parts = line.split(':')
                wifi_info["name"] = parts[0]
                wifi_info["uuid"] = parts[2]
                break
                
        cmd_device = ["nmcli", "-t", "-f", "ACTIVE,BSSID", "device", "wifi"]
        result_dev = subprocess.run(cmd_device, capture_output=True, text=True, check=True)
        for line in result_dev.stdout.strip().split('\n'):
            if line.startswith("yes:"):
                raw_bssid = line[4:]
                clean_bssid = raw_bssid.replace('\\:', ':')
                wifi_info["bssid"] = clean_bssid
                break
    except Exception:
        pass
        
    return wifi_info