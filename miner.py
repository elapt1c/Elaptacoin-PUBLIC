#2.0V PoW miner

import pip
import sys
import os
import threading
from pathlib import Path
import time
import json
from platform import python_version, machine as cputype
import signal
import subprocess
from datetime import datetime
import stat
from urllib.request import urlretrieve
import socket

running = True
prev_hash = ""
diff = ""
spinning = False
closeage = True
lock = False
key_pressed = False
globalFind = False
hasherName = "EXAvatorNT"
hasherSub = None

def is_venv():
    return (hasattr(sys, 'real_prefix') or
            (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix))

def check_python_ver():
    ver = python_version()
    if ver.startswith("3.9"):
        return
    
    if ver.startswith("3.8"):
        return
    
    print(f"Please use python 3.9.x or 3.8.x! Your version: {ver}, Follow the github guide. Exiting miner...")
    os._exit(1)

def check_inside_venv():
    if not is_venv():
      print("Please run miner in virtual environment! Follow the github guide. Exiting miner...")  
      os._exit(1)


def check_for_sudo():
    try:
        osName = os.name
        if osName == 'posix':
            if not os.getuid() == 0:
                print("Please run miner as root! Follow the github guide. Exiting miner...")
                os._exit(1)

    except Exception as e:
        print(f"Expection occurred! Exiting miner. Error: {e}")
        os._exit(1)

check_for_sudo()
check_python_ver()
#check_inside_venv()

def install(package):
    try:
        pip.main(["install",  package])
    except AttributeError:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
    except Exception or ImportError as e:
        print(f"Expection occurred! Exiting miner. Error: {e}")
        os._exit(1)

    subprocess.call([sys.executable] + sys.argv)
    os._exit(1)

try:
    from colorama import Back, Fore, Style, init
except ModuleNotFoundError:
    print("Colorama is not installed. "
          + "Miner will try to automatically install it "
          + "If it fails, please manually execute "
          + "python3 -m pip install colorama")
    install("colorama")

try:
    import keyboard
except ModuleNotFoundError:
    print("Keyboard is not installed. "
          + "Miner will try to automatically install it "
          + "If it fails, please manually execute "
          + "python3 -m pip install keyboard")
    install("keyboard")


init(autoreset=True)

class thread_with_trace(threading.Thread):
  def __init__(self, *args, **kwargs):
    threading.Thread.__init__(self, *args, **kwargs)
    self.killed = False

  def start(self):
    self.__run_backup = self.run
    self.run = self.__run      
    threading.Thread.start(self)

  def __run(self):
    sys.settrace(self.globaltrace)
    self.__run_backup()
    self.run = self.__run_backup

  def globaltrace(self, frame, event, arg):
    if event == 'call':
      return self.localtrace
    else:
      return None

  def localtrace(self, frame, event, arg):
    if self.killed:
      if event == 'line':
        raise SystemExit()
    return self.localtrace

  def kill(self):
    self.killed = True

mineThread = thread_with_trace()

def terminateMining():
    global mineThread, hasherSub
    mineThread.kill()
    try:     
        hasherSub.terminate()
    except:
        pass

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


def stopAll():
    global running, spinning, closeage
    closeage = True
    terminateMining()
    running = False
    spinning = False

def interrupt_restart():
    global key_pressed
    input()
    key_pressed = True
    pretty_print("Key pressed! Interrupting the restart process. Goodbye!", "info", "SYS")
    os._exit(1)

def restartError():
    global running, spinning, closeage, lock, key_pressed

    if lock:
        return

    lock = True
    closeage = False
    terminateMining()
    running = False
    spinning = False
    pretty_print(">>> Restarting the program in 5 seconds.... Press any key to shutdown the miner <<<", "warn", "SYS")

    interrupt_thread = thread_with_trace(target=interrupt_restart)
    interrupt_thread.start()

    for _ in range(5):
        time.sleep(1)
        if key_pressed:
            return

    #interrupt_thread.join()

    subprocess.call([sys.executable] + sys.argv)
    os._exit(1)

def fetch_or_create_config():
    if lock == True:
        return
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

def format_hashrate(rate):
    units = ["H/s", "kH/s", "MH/s", "GH/s", "TH/s", "PH/s", "EH/s", "ZH/s", "YH/s"]
    power = 0
    
    while rate >= 1000 and power < len(units) - 1:
        rate /= 1000
        power += 1

    return f"{rate:.2f} {units[power]}"

def getNetworkData(type):
    if type == 1:
        return "193.86.97.192"
    elif type == 2:
        return 12345
    elif type == 3:
        return "10.10.0.60"

def enterExit():
    global running, spinning, closeage, lock
    if lock == True:
        return
    lock = True
    closeage = False
    running = False
    terminateMining()
    spinning = False
    pretty_print(">>> Press any key to exit the program... <<<", "warn", "SYS")
    input()
    pretty_print("Exiting.... Goodbye!", "info", "SYS")
    os._exit(1)

def create_thread(function, *args, **kwargs):
    global mineThread
    thread = thread_with_trace(target=function, args=args, kwargs=kwargs)
    if function == mine:
        mineThread = thread
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
def checkHasher():
    global lock
    if lock == True:
        return
    global hasherName, if_linux
    if_linux = False
    try:
        osName = os.name
        if osName == 'nt':
            pretty_print(f"Architecture NT (Windows) detected. Running checks...", "info", "SYS")
            hasherName = "./EXAvatorNT.exe"
            if Path(hasherName).is_file():
                pretty_print(f"Hasher exists. Continuing....", "success", "SYS")
                return
        
        elif osName == "posix":
            if_linux = True
            if cputype() == "aarch64":
                pretty_print(f"Architecture aarch64 (64x ARM) detected. Running checks...", "info", "SYS")
                hasherName = "./EXAvatorArm64"
                if Path(hasherName).is_file():
                    pretty_print(f"Hasher exists. Continuing....", "success", "SYS")
                    return
                
            elif cputype() == "x86_64":
                pretty_print(f"Architecture x86_64 (Linux) detected. Running checks...", "info", "SYS")
                hasherName = "./EXAvatorLinux"
                if Path(hasherName).is_file():
                    pretty_print(f"Hasher {hasherName} exists. Continuing....", "success", "SYS")
                    return
                
            else:
                pretty_print(f"Unsupported system architecture detected. Contact support at Elaptacoin discord server. Your architecture: {cputype()}", "error", "SYS")
                enterExit()
                return

        pretty_print(f"Installing {hasherName} hasher....", "info", "SYS")
        urlretrieve(f"https://github.com/tommarekCZE/PoW-ElaptaCoin/raw/main/{hasherName}", hasherName)
        if if_linux == True:
            os.chmod(hasherName, os.stat(hasherName).st_mode | stat.S_IEXEC)

        pretty_print(f"Hasher installed. Continuing....", "success", "SYS")

    except Exception or KeyboardInterrupt as e:
        pretty_print(f"Exception occurred while checking hasher... Error: {e}", "error", "SYS")
        stopAll()
        restartError()

def fetch(client):
        global lock
        if lock == True:
            return
        try:
            client.send(bytes("INFO", encoding="utf8"))
        except Exception or KeyboardInterrupt as e:
            pretty_print(f"Exception occurred while handling sockets! Error: {e}", "error", "NET")
            create_thread(stopAll)
                
def mine(client):
        global prev_hash, diff, user, spinning, hasherName, lock, hasherSub
        if lock == True:
            return
        pretty_print(f"Started mining, <--JOB INFO--> PREVIOUS BLOCK> {prev_hash} / DIFFICULTY> {difficulty_to_int(len(diff))}", "info", "JOB")
        create_thread(spinning_cursor_thread)
        try:
            args = [prev_hash, diff]
            hasherSub = subprocess.Popen([hasherName] + args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            stdout, stderr = hasherSub.communicate()
            out = stdout.strip().split(",")
            spinning = False
            if out[0] == "error":
                raise Exception(out[1])
            elif out[0] == "result":
                hash = out[1]
                increment = out[2]
                took = out[3]
                hashrate = out[4]
                pretty_print(f"Block was found in {took} with hashrate of {format_hashrate(int(float(hashrate)))}! Sending for review..., BLOCK> {hash} / NONCE> {increment}", "warn", "JOB".replace('\n', ' '))
                client.send(bytes(f"SUBMIT,{hash},{increment},{user}", encoding="utf8"))
                terminateMining()
            else:
                raise Exception(f"Unexpected result from hasher while mining! Result: {out[0]}")
        except Exception or KeyboardInterrupt as e:
            pretty_print(f"Exception occurred while handling mining thread or while handling socket! Error: {e}", "error", "SYS")
            create_thread(stopAll)

def send_messages(client):
    global lock
    if lock == True:
        return
    try:
        if not running:
            return
        client.send(bytes("MSG", encoding="utf8"))
        time.sleep(1)
        create_thread(fetch,client)
        while running:
            dummy()
    except Exception or KeyboardInterrupt as e:
        pretty_print(f"Exception occurred while handling sockets! Error: {e}", "error", "NET")
        stopAll()

    pretty_print(f"Sending thread stopped", "warn", "SYS")
    client.close()
    if closeage:
        create_thread(restartError)

def receive_messages(client):
    global lock
    if lock == True:
        return
    time.sleep(0.1)
    global running, diff, prev_hash, globalFind
    while running or lock:
        try:
            data = client.recv(4096).decode()
            if not data:
                break
            
            data = data.split(",")
            
            if data[0] == "CHANGE":
                globalFind = True
                pretty_print("Someone else found the block, fetching new job", "warn", "NET")
                terminateMining()
                create_thread(fetch,client)
            elif data[0] == "INFO":
                prev_hash = data[1]
                diff = data[2]
                pretty_print(f"New job fetched, PREVIOUS BLOCK> {prev_hash} / DIFFICULTY> {difficulty_to_int(len(diff))}", "info", "NET")
                create_thread(mine,client)
            elif data[0] == "TRUE":
                globalFind = False
                terminateMining()
                pretty_print("WOOHOO> Block was accepted", "success", "JOB")
                create_thread(fetch,client)
            elif data[0] == "FALSE":
                if globalFind == True:
                    globalFind = False
                else:  
                    terminateMining()
                    pretty_print("Uh Oh!> Block was found to be invalid", "error", "JOB")
                    create_thread(fetch,client)
            elif data[0] == "MSG":
                pretty_print(f"{data[1]}", f"{data[2]}", "NET")
            else:
                #print(data[0])
                dummy()


        except Exception or KeyboardInterrupt as e:
            pretty_print(f"Exception occurred while handling sockets! Error: {e}", "error", "NET")
            stopAll()
            break
                
    

    pretty_print(f"Reciving thread stopped", "warn", "SYS")
    client.close()
    if closeage:
        create_thread(restartError)

def signal_handler(sig, frame):
    create_thread(enterExit)

def start_client():
    global lock
    if lock == True:
        return
    try:
        adress = getNetworkData(1)
        port = getNetworkData(2)
        pretty_print(f"Trying to connect to the server... USER> {user} / ADRESS: {adress} / PORT: {port}", "info", "NET")
        create_thread(spinning_cursor_thread)
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((adress, port))
    except Exception or KeyboardInterrupt as e:
        pretty_print(f"Cannot connect to the server! Error: {e}", "error", "NET")
        create_thread(restartError)
        

    send_thread = threading.Thread(target=send_messages, args=(client,))
    send_thread.start()

    receive_thread = threading.Thread(target=receive_messages, args=(client,))
    receive_thread.start()

    return client, receive_thread, send_thread

print(Fore.LIGHTYELLOW_EX + "Welcome to the Single Thread CPU ELAP Miner 2.0 builded on EXAvator Hasher")

signal.signal(signal.SIGINT, signal_handler)

try:
    user = fetch_or_create_config()
    checkHasher()
    client, receive_thread, send_thread = start_client()
except Exception or KeyboardInterrupt as e:
    pretty_print(f"Something went wrong! Error: {e}", "error", "NET")
    create_thread(restartError)

receive_thread.join()
send_thread.join()