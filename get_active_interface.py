import subprocess

def get_active_interface():
    try:
        cmd = ["nmcli", "-t", "-f", "DEVICE,TYPE,STATE", "device"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        for line in result.stdout.strip().split('\n'):
            if "wifi" in line and "connected" in line:
                parts = line.split(':')
                return parts[0]
    except Exception:
        pass
    return None