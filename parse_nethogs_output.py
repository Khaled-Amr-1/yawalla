import subprocess
import threading
import os

class NethogsMonitor:
    def __init__(self, interface):
        self.interface = interface
        self.running = False
        self.lock = threading.Lock()
        
        self.pid_trackers = {}
        self.pending_traffic = {}

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._worker, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False

    def _get_clean_name(self, raw_program):
        """دالة مساعدة لاستخراج اسم البرنامج النظيف بدون تشوهات"""
        executable_path = raw_program.split()[0]
        
        if ":" in executable_path and "-" in executable_path:
            return "Unidentified"
            
        parts_slash = executable_path.split('/')
        if len(parts_slash) >= 3 and parts_slash[-1].isdigit() and parts_slash[-2].isdigit():
            actual_path = "/".join(parts_slash[:-2])
            program_name = os.path.basename(actual_path)
        else:
            program_name = os.path.basename(executable_path)
            
        if not program_name or "unknown" in program_name.lower():
            return "Unidentified"
            
        return program_name

    def _worker(self):
        cmd = ["sudo", "nethogs", "-t", "-v", "2", self.interface]
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True, stderr=subprocess.PIPE)
        try:
            while self.running:
                line = process.stdout.readline()
                if not line:
                    break
                    
                line = line.strip()
                if not line or "Refreshing:" in line or "Adding local address" in line or "Ethernet link" in line:
                    continue
                    
                parts = line.split()
                if len(parts) >= 3:
                    raw_program = " ".join(parts[:-2])
                    
                    try:
                        upload_bytes = int(float(parts[-2]))
                        download_bytes = int(float(parts[-1]))
                    except ValueError:
                        continue
                        
                    clean_name = self._get_clean_name(raw_program)

                    with self.lock:
                        prev_up, prev_down = self.pid_trackers.get(raw_program, (0, 0))
                        
                        delta_up = upload_bytes - prev_up
                        delta_down = download_bytes - prev_down
                        
                        if delta_up < 0: delta_up = upload_bytes
                        if delta_down < 0: delta_down = download_bytes
                        
                        self.pid_trackers[raw_program] = (upload_bytes, download_bytes)
                        
                        if clean_name not in self.pending_traffic:
                            self.pending_traffic[clean_name] = {"download": 0, "upload": 0}
                            
                        self.pending_traffic[clean_name]["upload"] += delta_up
                        self.pending_traffic[clean_name]["download"] += delta_down
                        
        finally:
            process.terminate()

    def get_traffic_deltas(self):
        with self.lock:
            data_to_save = self.pending_traffic.copy()
            self.pending_traffic = {}
            return data_to_save