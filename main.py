import time
from get_active_interface import get_active_interface
from get_active_wifi_info import get_active_wifi_info
import db_manager
from parse_nethogs_output import NethogsMonitor

def main():
    db_manager.init_db()

    interface = get_active_interface()
    if not interface:
        return

    monitor = NethogsMonitor(interface=interface)
    monitor.start()

    try:
        while True:
            time.sleep(60)
            
            wifi_info = get_active_wifi_info()
            bssid = wifi_info.get("bssid")
            ssid = wifi_info.get("name")
            
            if not bssid or not ssid:
                continue
                
            db_manager.register_network(bssid, ssid)
            
            deltas = monitor.get_traffic_deltas()
            
            if deltas:
                for prog, stats in deltas.items():
                    db_manager.update_traffic(
                        bssid=bssid,
                        program_name=prog,
                        download_delta=stats['download'],
                        upload_delta=stats['upload']
                    )
    except KeyboardInterrupt:
        pass
    finally:
        monitor.stop()

if __name__ == "__main__":
    main()