#1.0V PoW miner

import json
import socket
import threading
import hashlib
from datetime import datetime
import sys
import signal
import os
import time
from colorama import Fore, Back, Style, init
init(autoreset=True)

running = True
prev_hash = ""
diff = ""
increment = 0
mining = True
spinning = False

def dummy():
    1+1

def spinning_cursor():
    global spinning
    while spinning:
        for cursor in '|/-\\':
            yield cursor

def spinning_cursor_thread():
    global spinning
    spinning = True
    spinner = spinning_cursor()
    while spinning:
        sys.stdout.write(next(spinner))
        sys.stdout.flush()
        time.sleep(0.1)
        sys.stdout.write('\b')


def restartError():
    pretty_print("Restarting the program in 5 seconds....", "warn", "SYS")
    time.sleep(5)
    os.execl(sys.executable, sys.executable, *sys.argv)

def getNetworkData(type):
    if type == 1:
        return "193.86.97.192"
    elif type == 2:
        return 12345

def enterExit():
    global running, mining, spinning
    running = False
    mining = False
    spinning = False
    pretty_print("Press any key to exit the program...", "warn", "SYS")
    input()
    sys.exit()

def create_thread(function, *args, **kwargs):
    thread = threading.Thread(target=function, args=args, kwargs=kwargs)
    thread.start()
    return thread

def difficulty_to_int(leading_zeros):
    base_difficulty = 1
    integer_difficulty = 2 ** (leading_zeros - base_difficulty)
    return integer_difficulty

def pretty_print(msg: str = None,
                 state: str = "success",
                 sender: str = "sys"):
    
    global spinning
    spinning = False
    if sender.startswith("NET"):
        bg_color = Back.GREEN
    elif sender.startswith("JOB"):
        bg_color = Back.BLUE
    elif sender.startswith("SYS"):
        bg_color = Back.MAGENTA

    if state == "success":
        fg_color = Fore.GREEN
    elif state == "info":
        fg_color = Fore.BLUE
    elif state == "error":
        fg_color = Fore.RED
    else:
        fg_color = Fore.YELLOW

    print("\n" +
        Fore.WHITE + datetime.now().strftime(Style.DIM + "%H:%M:%S.%f")[:-3]
        + Style.RESET_ALL + " " + Style.BRIGHT + bg_color + " " + sender + " "
        + Style.NORMAL + Back.RESET + " " + fg_color + msg.strip())

def fetch_or_create_config():
    config_file = 'config.json'
    
    if os.path.exists(config_file):
        with open(config_file, 'r') as file:
            config = json.load(file)
        
        if 'username' in config:
            return config['username']
        
    pretty_print("Enter your username:", "warn", "SYS")
    username = input()
    config = {'username': username}
    
    with open(config_file, 'w') as file:
        json.dump(config, file, indent=4)
    
    return username

user = fetch_or_create_config()

def fetch(client):
        try:
            client.send(bytes("INFO", encoding="utf8"))
        except Exception as e:
            pretty_print(f"Unknow error while handling sockets! Error: {e}", "error", "NET")
            restartError()
                
def mine(client):
        global mining, running, prev_hash, diff, increment
        mining = True
        increment = 0
        pretty_print(f"Started mining, <--JOB INFO--> PREVIOUS BLOCK> {prev_hash} / DIFFICULTY> {difficulty_to_int(len(diff))}", "info", "JOB")
        create_thread(spinning_cursor_thread)
        while running and mining:
            try:
                while mining:
                    hash = hashlib.sha256(f"{prev_hash}{increment}".encode()).hexdigest()
                    if hash.startswith('0' * len(diff)):
                        pretty_print(f"Block was found! Sending for rewiev..., BLOCK> {hash} / NONCE> {increment}", "warn", "JOB")
                        client.send(bytes(f"SUBMIT,{hash},{increment},{user}", encoding="utf8"))
                        mining = False
                    else:
                        increment = increment + 1
                        break
            except Exception as e:
                pretty_print(f"Unknow error while handling sockets! Error: {e}", "error", "NET")
                restartError()
                break

def send_messages(client):
    try:
        client.send(bytes("MSG", encoding="utf8"))
        time.sleep(1)
        create_thread(fetch,client)
        while running:
            dummy()
    except Exception as e:
        pretty_print(f"Unknow error while handling sockets! Error: {e}", "error", "NET")
        restartError()

    pretty_print(f"Reciving thread stopped", "warn", "SYS")
    client.close()

def receive_messages(client):
    global running, mining, diff, prev_hash
    while running:
        try:
            data = client.recv(1024).decode()
            if not data:
                break
            
            data = data.split(",")
            
            if data[0] == "CHANGE":
                pretty_print("Someone else found the block, fetching new job", "warn", "NET")
                mining = False
                create_thread(fetch,client)
            elif data[0] == "INFO":
                prev_hash = data[1]
                diff = data[2]
                pretty_print(f"New job fetched, PREVIOUS BLOCK> {prev_hash} / DIFFICULTY> {difficulty_to_int(len(diff))}", "info", "NET")
                create_thread(mine,client)
            elif data[0] == "TRUE":
                mining = False
                pretty_print("YOHOO> Block was accepted", "success", "JOB")
                create_thread(fetch,client)
            elif data[0] == "FALSE":
                mining = False
                pretty_print("UHHOUU> Block was found to be invalid", "error", "JOB")
                create_thread(fetch,client)
            elif data[0] == "MSG":
                pretty_print(f"{data[1]}", "success", "NET")
            else:
                #print(data[0])
                dummy()


        except Exception as e:
            pretty_print(f"Unknow error while handling sockets! Error: {e}", "error", "NET")
            restartError()
            break
                
    

    pretty_print(f"Reciving thread stopped", "warn", "SYS")
    client.close()

def signal_handler(sig, frame):
    pretty_print("Interrupt received, stopping client...", "warn", "SYS")
    enterExit()

def start_client():
    try:
        adress = getNetworkData(1)
        port = getNetworkData(2)
        pretty_print(f"Trying to connect to the server... USER> {user} / ADRESS: {adress} / PORT: {port}", "info", "NET")
        create_thread(spinning_cursor_thread)
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((adress, port))
    except:
        pretty_print("Cannot connect to the server!", "error", "NET")
        restartError()
        ##enterExit()
        

    send_thread = threading.Thread(target=send_messages, args=(client,))
    send_thread.start()

    receive_thread = threading.Thread(target=receive_messages, args=(client,))
    receive_thread.start()

    return client, receive_thread, send_thread

pretty_print("Welcome to the Single Thread ELAP Miner 1.0", "warn", "SYS")
try:
    client, receive_thread, send_thread = start_client()
except:
    pretty_print("Something went wrong!", "error", "NET")
    restartError()

signal.signal(signal.SIGINT, signal_handler)
receive_thread.join()
send_thread.join()
