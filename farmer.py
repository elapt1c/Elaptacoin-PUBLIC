import os
import random
import json
import time
from Crypto.Hash import SHAKE128
from tqdm import tqdm
from colorama import Fore, Back
import socket
import threading
import signal
import struct
import traceback
import ast

def clear_line(n=1):
    LINE_UP = '\033[1A'
    LINE_CLEAR = '\x1b[2K'
    for i in range(n):
        print(LINE_UP, end=LINE_CLEAR)

def clear_screen():
    if os.name == 'nt':  # For Windows
        os.system('cls')
    else:  # For Linux and macOS
        os.system('clear')

def get_first_entry(input_str):
    try:
        # Extract the part of the string that looks like a list
        list_str = input_str.split(']')[0] + ']'
        
        # Safely evaluate the list part of the string
        extracted_list = ast.literal_eval(list_str)
        
        # Get the first entry from the list
        first_entry = extracted_list[0]
        
        return first_entry
    except (SyntaxError, ValueError, IndexError):
        return None

# Function to create default config
def create_default_config():
    default_config = {
        "plot_directories": ["D:\\", os.path.dirname(os.path.realpath(__file__))],
        "username": "jerrbear",
        "server_ip": "147.185.221.21:20234"
    }
    with open('config.json', 'w') as config_file:
        json.dump(default_config, config_file, indent=4)
    return default_config

# Load or create configuration
config_path = 'config.json'
if not os.path.exists(config_path):
    print("Config file not found. Creating default config...")
    config = create_default_config()
else:
    with open(config_path, 'r') as config_file:
        config = json.load(config_file)

# Check if server_ip is in the config, if not, add it
if 'server_ip' not in config:
    config['server_ip'] = "147.185.221.21:20234"
    with open(config_path, 'w') as config_file:
        json.dump(config, config_file, indent=4)

register = False
running = True
submit = False
index = None

address = config['username']
server_ip, server_port = config['server_ip'].split(':')
server_port = int(server_port)
plotting_dir = str(config['plot_directories'])

class Print:
    def success(header, message):
        print(f'[{time.strftime("%H:%M:%S")}] {Fore.GREEN + header + Fore.RESET} {message}')

    def error(header, message):
        print(f'[{time.strftime("%H:%M:%S")}] {Fore.RED + header + Fore.RESET} {message}')
    
    def payout(header, message):
        print(f'[{time.strftime("%H:%M:%S")}] {Fore.BLUE + header + Fore.RESET} {message}')

    def neutral(message):
        print(f'[{time.strftime("%H:%M:%S")}] {message}')

    def skipped(message):
        clear_line(2)
        print(f'[{time.strftime("%H:%M:%S")}] {message}')

    def suspense(message):
        l = len(f"| {message} |")
        print("".join("-" for i in range(0, l)))
        print(f"| {message} |")
        print("".join("-" for i in range(0, l)))

printf = Print

class Farmer:

    def __init__(self, paths):
        self.paths = paths

    def plot(self, data_dict, out, chunk=1024 * 1024):
        data = json.dumps(data_dict, sort_keys=True).encode('utf-8')
        
        shake = SHAKE128.new()
        shake.update(data)
        
        size = int(3.5 * 1024 * 1024 * 1024)  # 3.5 GB

        with open(out, 'wb') as f:
            for _ in tqdm(range(0, size, chunk), unit=" MB"):
                chunk_data = shake.read(chunk)
                if chunk_data is None:
                    raise ValueError("Failed to read from SHAKE128 object.")
                if len(chunk_data) == 0:
                    raise ValueError("Read an empty chunk from SHAKE128 object.")
                f.write(chunk_data)

        print(f"{size / (1024 * 1024 * 1024):.2f} GB plot generated to {out}")

    def extract(self, file, index, n_bits=256):
        n_bytes = n_bits // 8
        size = os.path.getsize(file)
        if size < n_bytes:
            return False

        with open(file, 'rb') as f:
            f.seek(index)
            extracted_bytes = f.read(n_bytes)

        return extracted_bytes.hex(), index

    def proof(self, file, n_bits=256):
        size = os.path.getsize(file)
        index = random.randint(0, size - n_bits // 8)

        data, index = self.extract(file, index)
        return data, index

farmer = Farmer([])

def receive_messages(client):
    global running, submit, index, plots
    while running:
        try:
            raw_msglen = client.recv(4)
            if not raw_msglen:
                break
            msglen = struct.unpack('>I', raw_msglen)[0]
            data = client.recv(msglen)
            if not data:
                break
            try:
                r = json.loads(data.decode())
                if r["type"] == "proof":
                    if r["address"] == address:
                        printf.success("YOU ARE UP!", r["message"])
                        index = {"seed": r["seed"], "index": r["index"]}
                        submit = True
                        #print(f"Received proof request: seed={r['seed']}, index={r['index']}")
                    else:
                        clear_line(1)
                        printf.neutral(r["message"])
                        
                elif r["type"] == "error":
                    printf.error("Uh Oh!", r["message"])
                elif r["type"] == "suspense":
                    printf.suspense(r["message"])
                elif r["type"] == "winner":
                    printf.success("WOOHOO!", r["message"])
                elif r["type"] == "payout":
                    printf.success("PAYOUT!", r["message"])
                elif r["type"] == "skipped":
                    printf.neutral(r["message"])
                    clear_line(1)
                else:
                    printf.neutral(r["message"])
            except json.JSONDecodeError:
                print("Received invalid JSON from server.")
        except Exception as e:
            print(f"Error receiving data: {e}")
            traceback.print_exc()
            break
    print("Receiving thread stopped.")
    client.close()

def prepare(data):
    json_bytes = json.dumps(data).encode()
    msglen = struct.pack('>I', len(json_bytes))
    return msglen + json_bytes

def send_messages(client):
    global running, index, submit, plots
    client.sendall(prepare({"type": "register", "address": address}))
    while running:
        try:
            time.sleep(0.1)
            if submit:
                #print(f"Preparing to submit for seed {index['seed']}, index {index['index']}")
                submit = False
                valid_plot = False
                for plot in plots.list_plots():
                    if plot["seed"] == str(index["seed"]):
                        data, _ = farmer.extract(plot["path"], index["index"])
                        print(f"Submitting data: {data}")
                        client.sendall(prepare({"type": "submit", "address": address, "data": [data, index["index"]]}))
                        valid_plot = True
                        break
                if not valid_plot:
                    clear_line(1)
                    client.sendall(prepare({"type": "reject", "address": address}))
        except Exception as e:
            print(f"Error in send_messages: {e}")
            traceback.print_exc()
            break
    print("Sending thread stopped.")
    client.close()

def signal_handler(sig, frame):
    global running
    print("\nInterrupt received, stopping client...")
    running = False

def start_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((server_ip, server_port))

    receive_thread = threading.Thread(target=receive_messages, args=(client,))
    receive_thread.start()
    
    send_thread = threading.Thread(target=send_messages, args=(client,))
    send_thread.start()

    return client, receive_thread, send_thread

class Plots:
    def __init__(self, paths):
        self.plots = []
        for path in paths:
            if os.path.exists(path):
                files = os.listdir(path)
                for file in files:
                    if file.endswith('.tiny'):
                        self.plots.append({"name": file, "path": os.path.join(path, file), "seed": file.replace(".tiny", "").replace("plot_", "")})
            else:
                print(f"Warning: Directory {path} does not exist.")

    def list_plots(self):
        return self.plots

print("Retrieving plots...")
plots = Plots(config['plot_directories'])
print(f"Found plots: {plots.list_plots()}")

if __name__ == "__main__":
    print(Fore.CYAN + """
 _____ _            ______      _           
|_   _(_)           |  _  \    (_)          
  | |  _ _ __  _   _| | | |_ __ ___   _____ 
  | | | | '_ \| | | | | | | '__| \ \ / / _ \\
  | | | | | | | |_| | |/ /| |  | |\ V /  __/
  \_/ |_|_| |_|\__, |___/ |_|  |_| \_/ \___|
                __/ |                       
               |___/                        
""" + Fore.RESET)
    while True:
        print(f"Welcome {Fore.CYAN}{address}{Fore.RESET}! Enter {Fore.GREEN}'plot'{Fore.RESET} to start / edit plots, {Fore.GREEN}'farm'{Fore.RESET} to start earning, or {Fore.GREEN}'config'{Fore.RESET} to edit configuration!" + Fore.RESET)
        command = input()
        print()
        if command == "farm":
            signal.signal(signal.SIGINT, signal_handler)
            client, receive_thread, send_thread = start_client()
            print(f"You have started farming... Connected to server at {server_ip}:{server_port}")
            receive_thread.join()
            send_thread.join()
            break
        elif command == "plot":
            dir = get_first_entry(plotting_dir)
            while True:
                seed = int(input("Enter a seed (should be unique from your other plots) (0 - 32):\n"))
                if seed >= 0 and seed <= 32:
                    break
                else:
                    print(printf.error("Seed must be between or equal to 0 - 24", ""))
            farmer.plot({"address": address, "seed": seed}, os.path.join(dir, f"{seed}.tiny"))
            
            # Update config with new plot directory if it's not already there
            if dir not in config['plot_directories']:
                config['plot_directories'].append(dir)
                with open('config.json', 'w') as config_file:
                    json.dump(config, config_file, indent=4)
            
            plots = Plots(config['plot_directories'])  # Refresh the plots after creating a new one
            print(f"Updated plots: {plots.list_plots()}")
        elif command == "config":
            print("Current configuration:")
            print(json.dumps(config, indent=4))
            print("\nEnter the setting you want to change (e.g., 'username', 'server_ip'), or 'done' to finish:")
            while True:
                setting = input().strip().lower()
                if setting == 'done':
                    break
                elif setting in config:
                    new_value = input(f"Enter new value for {setting}: ")
                    config[setting] = new_value
                    print(f"{setting} updated to: {new_value}")
                else:
                    print(f"Invalid setting: {setting}")
            
            with open('config.json', 'w') as config_file:
                json.dump(config, config_file, indent=4)
            print("Configuration updated and saved.")

            # If server_ip was changed, update the global variables
            if 'server_ip' in config:
                server_ip, server_port = config['server_ip'].split(':')
                server_port = int(server_port)
            
            # If username was changed, update the global variable
            if 'username' in config:
                address = config['username']

        else:
            print("Invalid command. Please enter 'plot', 'farm', or 'config'.")
