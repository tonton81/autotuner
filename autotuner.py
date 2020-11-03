from os import system
import threading
import signal
import subprocess
from subprocess import Popen, PIPE
import sys, termios, tty, os, time, json, queue, shutil
import cmd, readline
import os.path
from os import path

class getcmd(cmd.Cmd):
    history_file = ""
    result = ""
    prompt = ""
    def default(self, line):
        self.result = line
        readline.write_history_file(self.history_file)
        return True

    def set_history_file(self, filepath):
        self.result = ""
        self.history_file = filepath
        readline.clear_history()
        if not os.path.exists(filepath):
            open(filepath, 'w').close()
        readline.read_history_file(filepath)

class TMGTuner:

    def __init__(self):
        self.user_input = ""
        self.thread_once = 0
        self.menuscreen = "main"
        self.input_queue = queue.Queue()

    def get_input_key(self):
        if not self.thread_once:
            self.thread_once = 1
            self.input_thread = threading.Thread(target=self.key_capturing, args=(), daemon=True).start()

    def key_capturing(self):
        self.input_queue.put(self.getch())
        self.thread_once = 0

    def getch(self):
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

    def get_input_string(self):
        if not self.thread_once:
            self.thread_once = 1
            self.input_thread = threading.Thread(target=self.read_kbd_input, args=(), daemon=True).start()

    def read_kbd_input(self):
        console_input = input()
        self.input_queue.put(console_input)
        self.thread_once = 0

    def input_queued(self):
        return_value = False
        if self.input_queue.qsize() > 0:
            return_value = True
        return return_value

    def input_get(self):
        return_value = ""
        if self.input_queue.qsize() > 0:
            return_value = self.input_queue.get()
        return return_value







#######################################################################################
def main_screen():
    nbi.user_input = nbi.input_get()
    if nbi.user_input == "":
        nbi.get_input_key()

    system('clear')
    print ("\n\n\n\r\t\t\033[1m\033[4mWhat would you like to mod today?\033[0m\n\n\r")
    print ("\t\t\t1) BP, V, Kp, Ki\n\r")
    print ("\t\t\t2) Kf, Steer Ratio, Steer Rate Cost\n\r")
    print ("\t\t\tF) Load AutoECU\n\r")
    print ("\t\t\tx) exit\n\r")
    print ("\n\n\n\n\r")

    if nbi.user_input == "1":
        nbi.menuscreen = "bpvkpki"

    if nbi.user_input == "2":
        nbi.menuscreen = "KfSrSrc"

    if nbi.user_input == "F":
        nbi.menuscreen = "autoecu_menu"

    if nbi.user_input == "x":
        os.system('stty sane')
        sys.exit(0)

    time.sleep(0.2)
#######################################################################################
def autoecu_signal_handler(sig, frame):
    print ("\n\t\tREBOOT COMMA AND RESTART CAR WHEN FLASHING IS 'COMPLETE'!\r")

def autoecu_menu():
    subprocess.call(["pkill", "./manager.py"])
    system('clear')
    signal.signal(signal.SIGINT, autoecu_signal_handler)
    signal.signal(signal.SIGQUIT, autoecu_signal_handler)
    signal.signal(signal.SIGTSTP, autoecu_signal_handler)
    print ("\n\n\n\r\t\t\033[1m\033[4mAutoECU Loading...\033[0m\n\n\r")
    process = subprocess.Popen(["pm", "list", "packages", "chrome"], stdin=PIPE, stdout=PIPE, stderr=PIPE)
    output, err = process.communicate()
    process.terminate()
    if output != b'package:com.android.chrome\n':
        print ("\t\tInstalling Chrome...\n\r")
        subprocess.call(["cp", "-rf", "/data/autotuner/chrome.apk", "/storage/emulated/0/"], stdout=PIPE)
        subprocess.call(["pm", "install", "-r", "-d", "/storage/emulated/0/chrome.apk"], stdout=PIPE)
        print ("\n\t\tChrome Installed! Loading...\n\r")
    subprocess.call(["pkill", "chrome"])
    subprocess.call(["rm", "-rf", "/data/data/com.android.chrome/app_tabs/0"])
    subprocess.call(["am", "start", "-n", "com.android.chrome/com.google.android.apps.chrome.Main", "-d", "autoecu.io"], stdout=PIPE)
    print ("\n\t\tREBOOT COMMA AND RESTART CAR WHEN FLASHING IS 'COMPLETE'!\r")
    while True:
        time.sleep(2) # Don't exit, do nothing
#######################################################################################
def KfSrSrc_screen():
    exit_condition = False
    selection = 0
    srpercent = 15
    srval = 0.5
    srcpercent = 15
    srcval = 0.05
    kfpercent = 15
    kfval = 0.00001
    while exit_condition == False:
        system('clear')
        print ("\n\n\n\r\t\t\t\t\033[1m\033[4mSteer Ratio, Steer Rate Cost, Kf\033[0m\n\r")
        with open('/data/autotuner.json', 'r') as file: #read our configuration
            config_data = json.loads(file.read())
        kf = float(config_data['kf'])
        sr = float(config_data['steer_ratio'])
        src = float(config_data['steer_rate_cost'])
        print ("    Steer Ratio: ", sr, "\r")
        print ("    Steer Rate Cost: ", src, "\r")
        print ("    Kf: ", format(kf , ".8f"), "\n\n\r")
        nbi.user_input = nbi.input_get()
        if nbi.user_input == "":
            nbi.get_input_key()
        print ("\t\t  *** Pick your inc/dec value ***\n\n\t\t\r")
        print ("\t\t\t1) Enter a new steering ratio\n\r")
        print ("\t\t\t2) Tune steering ratio by percentage (Default: 15%, Currently: " + str(srpercent) + ("% \033[92m<-------- selected\033[0m" if selection == 0 else " ") + ")\n\r")
        print ("\t\t\t3) Tune steering ratio by value. Currently:" + str(srval) + (" \033[92m<-------- selected\033[0m" if selection == 1 else " ") + ")\n\r")
        print ("\t\t\t4) Enter a new steering rate cost\n\r")
        print ("\t\t\t5) Tune steering rate cost by percentage (Default: 15%, Currently: " + str(srcpercent) + ("% \033[92m<-------- selected\033[0m" if selection == 2 else " ") + ")\n\r")
        print ("\t\t\t6) Tune steering rate cost by value. Currently: " + str(srcval) + (" \033[92m<-------- selected\033[0m" if selection == 3 else " ") + ")\n\r")
        print ("\t\t\t7) Enter a new kf value\n\r")
        print ("\t\t\t8) Tune kf by percentage (Default: 15%, Currently: " + str(kfpercent) + ("% \033[92m<-------- selected\033[0m" if selection == 4 else " ") + ")\n\r")
        print ("\t\t\t9) Tune kf by value. Currently: " + str(format(kfval, ".8f")) + (" \033[92m<-------- selected\033[0m" if selection == 5 else " ") + ")\n\r")
        print ("\t\t\td) decrease\n\r")
        print ("\t\t\ti) increase\n\r")
        print ("\t\t\tx) exit\n\r")
        if nbi.user_input != "":
            if nbi.user_input == '\x1b': #special keycode escape (possible arrow key)
                arrow_key = check_for_arrows() # here but not used, saved for future reference
            with open('/data/autotuner.json', 'r') as file: #read our configuration
                config_data = json.loads(file.read())
            if nbi.user_input == "1":
                selection = 0
                print ("  * Input your desired steering ratio *")
                input_history = getcmd()
                input_history.set_history_file("/data/autotuner/floats_history")
                input_history.cmdloop()
                if input_history.result != "":
                    try:
                        config_data['steer_ratio'] = format(eval(input_history.result), ".8f")
                    except:
                        pass
            if nbi.user_input == "2":
                selection = 0
                print ("  * Input your desired percentage without the symbol *")
                input_history = getcmd()
                input_history.set_history_file("/data/autotuner/random_history")
                input_history.cmdloop()
                if input_history.result != "":
                    try:
                        srpercent = int(eval(input_history.result))
                    except:
                        pass
            if nbi.user_input == "3":
                selection = 1
                print ("  * Input your desired value rate *")
                input_history = getcmd()
                input_history.set_history_file("/data/autotuner/floats_history")
                input_history.cmdloop()
                if input_history.result != "":
                    try:
                        srval = format(eval(input_history.result), ".8f")
                    except:
                        pass
            if nbi.user_input == "4":
                selection = 2
                print ("  * Input your desired steering rate cost *")
                input_history = getcmd()
                input_history.set_history_file("/data/autotuner/floats_history")
                input_history.cmdloop()
                if input_history.result != "":
                    try:
                        config_data['steer_rate_cost'] = format(eval(input_history.result), ".8f")
                    except:
                        pass
            if nbi.user_input == "5":
                selection = 2
                print ("  * Input your desired percentage without the symbol *")
                input_history = getcmd()
                input_history.set_history_file("/data/autotuner/random_history")
                input_history.cmdloop()
                if input_history.result != "":
                    try:
                        srcpercent = int(eval(input_history.result))
                    except:
                        pass
            if nbi.user_input == "6":
                selection = 3
                print ("  * Input your desired value rate *")
                input_history = getcmd()
                input_history.set_history_file("/data/autotuner/floats_history")
                input_history.cmdloop()
                if input_history.result != "":
                    try:
                        srcval = format(eval(input_history.result), ".8f")
                    except:
                        pass
            if nbi.user_input == "7":
                selection = 4
                print ("  * Input your desired kf value *")
                input_history = getcmd()
                input_history.set_history_file("/data/autotuner/floats_history")
                input_history.cmdloop()
                if input_history.result != "":
                    try:
                        config_data['kf'] = format(eval(input_history.result), ".8f")
                    except:
                        pass
            if nbi.user_input == "8":
                selection = 4
                print ("  * Input your desired percentage without the symbol *")
                input_history = getcmd()
                input_history.set_history_file("/data/autotuner/random_history")
                input_history.cmdloop()
                if input_history.result != "":
                    try:
                        kfpercent = int(eval(input_history.result))
                    except:
                        pass
            if nbi.user_input == "9":
                selection = 5
                print ("  * Input your desired value rate *")
                input_history = getcmd()
                input_history.set_history_file("/data/autotuner/floats_history")
                input_history.cmdloop()
                if input_history.result != "":
                    try:
                        kfval = format(eval(input_history.result), ".8f")
                    except:
                        pass
            if nbi.user_input == "d":
                if selection == 0:
                    sr = abs(( float(sr) * (srpercent/100) ) - float(sr))
                    config_data['steer_ratio'] = str(sr)
                if selection == 1:
                    config_data['steer_ratio'] = str(float(sr) - float(srval))
                if selection == 2:
                    src = abs(( float(src) * (srcpercent/100) ) - float(src))
                    config_data['steer_rate_cost'] = str(src)
                if selection == 3:
                    config_data['steer_rate_cost'] = str(float(src) - float(srcval))
                if selection == 4:
                    kf = abs(( float(kf) * (kfpercent/100) ) - float(kf))
                    config_data['kf'] = str(kf)
                if selection == 5:
                    config_data['kf'] = str(float(kf) - float(kfval))
            if nbi.user_input == "i":
                if selection == 0:
                    sr = abs(( float(sr) * (srpercent/100) ) + float(sr))
                    config_data['steer_ratio'] = str(sr)
                if selection == 1:
                    config_data['steer_ratio'] = str(float(sr) + float(srval))
                if selection == 2:
                    src = abs(( float(src) * (srcpercent/100) ) + float(src))
                    config_data['steer_rate_cost'] = str(src)
                if selection == 3:
                    config_data['steer_rate_cost'] = str(float(src) + float(srcval))
                if selection == 4:
                    kf = abs(( float(kf) * (kfpercent/100) ) + float(kf))
                    config_data['kf'] = str(kf)
                if selection == 5:
                    config_data['kf'] = str(float(kf) + float(kfval))
            if nbi.user_input == "x":
                nbi.menuscreen = "main"
                return
            with open('/data/autotuner.tmp', 'w', encoding='utf8') as file:
                json.dump(config_data, file, indent=2, sort_keys=True, separators=(',', ': '), ensure_ascii=False)
                file.flush()
            shutil.move("/data/autotuner.tmp", "/data/autotuner.json") #change it as main config file
        time.sleep(0.4)
#######################################################################################
def BP_V_Ki_Kp_screen():
    system('clear')
    refresh_BPVKPKI_list()
    nbi.user_input = nbi.input_get()
    if nbi.user_input == "":
        nbi.get_input_key()
    print ("\t\t\t1) Change / Edit current BP and V lists\n\r")
    print ("\t\t\t2) Change / Edit current Kp and Ki lists\n\r")
    print ("\t\t\t3) Tune Kp and Ki\n\r")
    print ("\t\t\t4) Tune Midpoint of BP\n\r")
    print ("\t\t\t5) Tune Kf\n\r")
    print ("\t\t\t6) Toggle an estimated KP\n\r")
    print ("\t\t\tx) exit\n\r")
    if nbi.user_input == "1":
        change_BPV_list_entry()
    if nbi.user_input == "2":
        change_KpKi_list_entry()
    if nbi.user_input == "3":
        change_KpKi_tuning_entry()
    if nbi.user_input == "4":
        change_Midpoint_BP_tuning_entry()
    if nbi.user_input == "5":
        change_Kf_tuning_entry()
    if nbi.user_input == "6":
        with open('/data/autotuner.json', 'r') as file: #read our configuration
            config_data = json.loads(file.read())
        BPV_list = eval(config_data['torqueBPV'])
        KpKi_list = eval(config_data['pidKpKi'])
        global estimated_kp_select
        estimated_kp_select = not estimated_kp_select
        if estimated_kp_select:
            KpKi_list[0][0] = round((3840/BPV_list[0][-1]/1.04166669270833), 5)
            KpKi_list[1][0] = round((3840/BPV_list[0][-1]/1.04166669270833)/3, 5)
        else:
            KpKi_list[0][0] = round((3840/BPV_list[0][-1]/2.69416964849505), 5)
            KpKi_list[1][0] = round((3840/BPV_list[0][-1]/2.69416964849505)/3, 5)
        config_data['pidKpKi'] = str(KpKi_list)
        with open('/data/autotuner.tmp', 'w', encoding='utf8') as file:
            json.dump(config_data, file, indent=2, sort_keys=True, separators=(',', ': '), ensure_ascii=False)
            file.flush()
        shutil.move("/data/autotuner.tmp", "/data/autotuner.json") #change it as main config file
    if nbi.user_input == "x":
        nbi.menuscreen = "main"
    time.sleep(0.2)
#######################################################################################
def refresh_BPVKPKI_list():
    print ("\n\n\n\r\t\t\t\t\033[1m\033[4mBP, V, Kp, Ki\033[0m\n\r")
    with open('/data/autotuner.json', 'r') as file: #read our configuration
        config_data = json.loads(file.read())
    BPV_list = eval(config_data['torqueBPV'])
    KpKi_list = eval(config_data['pidKpKi'])
    print ("  torqueBP: ", BPV_list[0], "\r")
    print ("   torqueV: ", BPV_list[1], "\r")
    print ("    pid.kp: ", KpKi_list[0], "\r")
    print ("    pid.ki: ", KpKi_list[1], "\r")
    print ("    Estimated KP values: " + str(round(3840/BPV_list[0][-1]/1.04166669270833, 5)) + ", " + str(round(3840/BPV_list[0][-1]/2.69416964849505, 5)) + "\n\n\r")
#######################################################################################
def check_for_arrows(): # '\x1b'
    nbi.user_input = nbi.input_get()
    if nbi.user_input == "": #try to get 2nd byte
        nbi.get_input_key()
    while nbi.user_input == "":
        nbi.user_input = nbi.input_get()
        if nbi.user_input != "":
            nbi.user_input = nbi.input_get()
        if nbi.user_input == "": #try to get 3rd byte
            nbi.get_input_key()
        while nbi.user_input == "":
            nbi.user_input = nbi.input_get()
            if nbi.user_input != "":
                if nbi.user_input == "A":
                    return "UP"
                if nbi.user_input == "B":
                    return "DOWN"
                if nbi.user_input == "D":
                    return "LEFT"
                if nbi.user_input == "C":
                    return "RIGHT"
#######################################################################################
def change_Kf_tuning_entry():
    with open('/data/autotuner.json', 'r') as file: #read our configuration
        config_data = json.loads(file.read())
    exit_condition = False
    selection_cases = [0.0001, 0.00001, 0.000001]
    selection = 1
    while exit_condition == False:
        system('clear')
        print ("\n\n\n\r\t\t\t\t *** \033[1m\033[4mKF TUNER\033[0m ***\r")
        refresh_BPVKPKI_list()
        print ("  Kf: ", format(eval(config_data['kf']), ".8f"), "\n\n\r")

        nbi.user_input = nbi.input_get()
        if nbi.user_input == "":
            nbi.get_input_key()
        print ("\t\t  *** Pick your inc/dec value ***\n\n\t\t\r")
        print ("\t\t\t1) 0.0001" + (" <-------- selected" if selection == 0 else " ") + "\n\r")
        print ("\t\t\t2) 0.00001" + (" <-------- selected" if selection == 1 else " ") + "\n\r")
        print ("\t\t\t3) 0.000001" + (" <-------- selected" if selection == 2 else " ") + "\n\r")
        print ("\t\t\t4) Change value of Kf\n\r")
        print ("\t\t\td) decrease\n\r")
        print ("\t\t\ti) increase\n\r")
        print ("\t\t\tx) exit\n\r")
        if nbi.user_input != "":
            if nbi.user_input == '\x1b': #special keycode escape (possible arrow key)
                arrow_key = check_for_arrows() # here but not used, saved for future reference
            with open('/data/autotuner.json', 'r') as file: #read our configuration
                config_data = json.loads(file.read())
            if nbi.user_input == "1":
                selection = 0
            if nbi.user_input == "2":
                selection = 1
            if nbi.user_input == "3":
                selection = 2
            if nbi.user_input == "4":
                print ("  * Input your desired Kp *")
                input_history = getcmd()
                input_history.set_history_file("/data/autotuner/floats_history")
                input_history.cmdloop()
                if input_history.result != "":
                    try:
                        config_data['kf'] = str(float(input_history.result))
                    except:
                        pass
            if nbi.user_input == "d":
                config_data['kf'] = format(eval(config_data['kf']) - selection_cases[selection], ".8f")
            if nbi.user_input == "i":
                config_data['kf'] = format(eval(config_data['kf']) + selection_cases[selection], ".8f")
            if nbi.user_input == "x":
                return
            with open('/data/autotuner.tmp', 'w', encoding='utf8') as file:
                json.dump(config_data, file, indent=2, sort_keys=True, separators=(',', ': '), ensure_ascii=False)
                file.flush()
            shutil.move("/data/autotuner.tmp", "/data/autotuner.json") #change it as main config file
        time.sleep(0.2)
#######################################################################################
def change_Midpoint_BP_tuning_entry():
    with open('/data/autotuner.json', 'r') as file: #read our configuration
        config_data = json.loads(file.read())
    BPV_list = eval(config_data['torqueBPV'])
    exit_condition = False
    selection_cases = [50, 100, 500, 1000]
    selection = 0
    whichBP = "BOTH"
    while exit_condition == False:
        system('clear')
        print ("\n\n\n\r\t\t\t     *** \033[1m\033[4mMIDPOINT BP TUNER\033[0m ***\r")
        refresh_BPVKPKI_list()
        if ( len(BPV_list[0]) > 3 ):
             print ("  * Disabled due to larger list, only 3 value lists allowed *")
             time.sleep(2)
             return
        nbi.user_input = nbi.input_get()
        if nbi.user_input == "":
            nbi.get_input_key()
        print ("\t\t  *** Pick your inc/dec value ***\n\n\t\t\r")
        print ("\t\t\t1) 50" + (" <-------- selected" if selection == 0 else " ") + "\n\r")
        print ("\t\t\t2) 100" + (" <-------- selected" if selection == 1 else " ") + "\n\r")
        print ("\t\t\t3) 500" + (" <-------- selected" if selection == 2 else " ") + "\n\r")
        print ("\t\t\t4) 1000" + (" <-------- selected" if selection == 3 else " ") + "\n\r")
        print ("\t\t\t5) Change value of MP(BP)\n\r")
        print ("\t\t\t6) Change value of MP(V)\n\r")
        print ("\t\t\t7) Change value of BP max\n\r")
        print ("\t\t\t8) Change value of V max\n\r")
        print ("\t\t\t9) Change both MPs / single MP(BP)?  Currently: " + whichBP  + "\n\r")
        print ("\t\t\td) decrease\n\r")
        print ("\t\t\ti) increase\n\r")
        print ("\t\t\tx) exit\n\r")
        if nbi.user_input != "":
            if nbi.user_input == '\x1b': #special keycode escape (possible arrow key)
                arrow_key = check_for_arrows() # here but not used, saved for future reference
            with open('/data/autotuner.json', 'r') as file: #read our configuration
                config_data = json.loads(file.read())
            KpKi_list = eval(config_data['pidKpKi'])
            BPV_list = eval(config_data['torqueBPV'])
            if nbi.user_input == "1":
                selection = 0
            if nbi.user_input == "2":
                selection = 1
            if nbi.user_input == "3":
                selection = 2
            if nbi.user_input == "4":
                selection = 3
            if nbi.user_input == "5":
                print ("  * Input your desired MP(BP) *")
                input_history = getcmd()
                input_history.set_history_file("/data/autotuner/random_history")
                input_history.cmdloop()
                if input_history.result != "":
                    try:
                        BPV_list[0][1] = int(input_history.result)
                    except:
                      pass
            if nbi.user_input == "6":
                print ("  * Input your desired MP(V) *")
                input_history = getcmd()
                input_history.set_history_file("/data/autotuner/random_history")
                input_history.cmdloop()
                if input_history.result != "":
                    try:
                        BPV_list[1][1] = int(input_history.result)
                    except:
                      pass
            if nbi.user_input == "7":
                print ("  * Input your desired BP max *")
                input_history = getcmd()
                input_history.set_history_file("/data/autotuner/random_history")
                input_history.cmdloop()
                if input_history.result != "":
                    try:
                        BPV_list[0][2] = int(input_history.result)
                    except:
                      pass
            if nbi.user_input == "8":
                print ("  * Input your desired V max *")
                input_history = getcmd()
                input_history.set_history_file("/data/autotuner/random_history")
                input_history.cmdloop()
                if input_history.result != "":
                    try:
                        BPV_list[1][2] = int(input_history.result)
                    except:
                      pass
            if nbi.user_input == "9":
                if whichBP == "BOTH":
                    whichBP = "SINGLE (BP)"
                else:
                    whichBP = "BOTH"
            if nbi.user_input == "d":
                BPV_list[0][1] = BPV_list[0][1] - selection_cases[selection]
                if whichBP == "BOTH":
                    BPV_list[1][1] = BPV_list[0][1]
            if nbi.user_input == "i":
                BPV_list[0][1] = BPV_list[0][1] + selection_cases[selection]
                if whichBP == "BOTH":
                    BPV_list[1][1] = BPV_list[0][1]
            if nbi.user_input == "x":
                return
            config_data['torqueBPV'] = str(BPV_list)
            with open('/data/autotuner.tmp', 'w', encoding='utf8') as file:
                json.dump(config_data, file, indent=2, sort_keys=True, separators=(',', ': '), ensure_ascii=False)
                file.flush()
            shutil.move("/data/autotuner.tmp", "/data/autotuner.json") #change it as main config file
        time.sleep(0.2)
#######################################################################################
def change_Ki_tuning_entry():
    with open('/data/autotuner.json', 'r') as file: #read our configuration
        config_data = json.loads(file.read())
    BPV_list = eval(config_data['torqueBPV'])
    exit_condition = False
    percentage = 15
    selection_cases = [0.1, 0.01, 0.001, 0.0001]
    selection = 0
    while exit_condition == False:
        system('clear')
        print ("\n\n\n\r\t\t\t     *** \033[1m\033[4mKI TUNER\033[0m ***\r")
        refresh_BPVKPKI_list()
        nbi.user_input = nbi.input_get()
        if nbi.user_input == "":
            nbi.get_input_key()
        print ("\t\t  *** Pick your inc/dec value ***\n\n\t\t\r")
        print ("\t\t0) Set Ki initial value\r")
        print ("\t\t1) 0.1" + (" <-------- selected" if selection == 0 else " ") + "\r")
        print ("\t\t2) 0.01" + (" <-------- selected" if selection == 1 else " ") + "\r")
        print ("\t\t3) 0.001" + (" <-------- selected" if selection == 2 else " ") + "\r")
        print ("\t\t4) 0.0001" + (" <-------- selected" if selection == 3 else " ") + "\r")
        print ("\t\t5) Change by percentage? (Def: 15%, Cur: " + str(percentage) + "%)" + (" <-------- selected" if selection == 4 else " ") + "\r")
        print ("\t\td) decrease\r")
        print ("\t\ti) increase\r")
        print ("\t\tx) exit\r")
        if nbi.user_input != "":
            if nbi.user_input == '\x1b': #special keycode escape (possible arrow key)
                arrow_key = check_for_arrows() # here but not used, saved for future reference
            KpKi_list = eval(config_data['pidKpKi'])
            if nbi.user_input == "0":
                print ("  * Input your desired float *")
                input_history = getcmd()
                input_history.set_history_file("/data/autotuner/floats_history")
                input_history.cmdloop()
                if input_history.result != "":
                    try:
                        KpKi_list[1][0] = abs(round(float(input_history.result), 5))
                        config_data['pidKpKi'] = str(KpKi_list)
                    except:
                      pass
            if nbi.user_input == "1":
                selection = 0
            if nbi.user_input == "2":
                selection = 1
            if nbi.user_input == "3":
                selection = 2
            if nbi.user_input == "4":
                selection = 3
            if nbi.user_input == "5":
                selection = 4
                print ("  * Enter percentage, without the symbol *")
                input_history = getcmd()
                input_history.set_history_file("/data/autotuner/floats_history")
                input_history.cmdloop()
                if input_history.result != "":
                    try:
                        percentage = int(input_history.result)
                        continue
                    except:
                      pass
            if nbi.user_input == "d":
                if selection == 4:
                    old_ki = KpKi_list[1][0]
                    new_ki = abs(( float(old_ki) * (percentage/100) ) - float(old_ki))
                    KpKi_list[1][0] = round(new_ki ,5)
                else:
                    KpKi_list[1][0] = round(float(KpKi_list[1][0]) - selection_cases[selection], 5)
            if nbi.user_input == "i":
                if selection == 4:
                    old_ki = KpKi_list[1][0]
                    new_ki = abs(( float(old_ki) * (percentage/100) ) + float(old_ki))
                    KpKi_list[1][0] = round(new_ki ,5)
                else:
                    KpKi_list[1][0] = round(float(KpKi_list[1][0]) + selection_cases[selection], 5)
            if nbi.user_input == "x":
                return
            config_data['pidKpKi'] = str(KpKi_list)
            with open('/data/autotuner.tmp', 'w', encoding='utf8') as file:
                json.dump(config_data, file, indent=2, sort_keys=True, separators=(',', ': '), ensure_ascii=False)
                file.flush()
            shutil.move("/data/autotuner.tmp", "/data/autotuner.json") #change it as main config file
        time.sleep(0.2)
#######################################################################################
def change_KpKi_tuning_entry():
    with open('/data/autotuner.json', 'r') as file: #read our configuration
        config_data = json.loads(file.read())
    BPV_list = eval(config_data['torqueBPV'])
    exit_condition = False
    percentage = 15
    selection_cases = [0.1, 0.01, 0.001, 0.0001]
    selection = 0
    divider = 3.3333
    if ( len(BPV_list[0]) > 3 ):
        bp_included = "Disabled, requires 3 BP max"
    else:
        bp_included = "no"
    while exit_condition == False:
        system('clear')
        print ("\n\n\n\r\t\t\t     *** \033[1m\033[4mKP TUNER\033[0m ***\r")
        refresh_BPVKPKI_list()
        nbi.user_input = nbi.input_get()
        if nbi.user_input == "":
            nbi.get_input_key()
        print ("\t\t  *** Pick your inc/dec value ***\n\n\t\t\r")
        print ("\t\t0) Set Kp initial value\r")
        print ("\t\t1) 0.1" + (" <-------- selected" if selection == 0 else " ") + "\r")
        print ("\t\t2) 0.01" + (" <-------- selected" if selection == 1 else " ") + "\r")
        print ("\t\t3) 0.001" + (" <-------- selected" if selection == 2 else " ") + "\r")
        print ("\t\t4) 0.0001" + (" <-------- selected" if selection == 3 else " ") + "\r")
        print ("\t\t5) Change by percentage? (Def: 15%, Cur: " + str(percentage) + "%)" + (" <-------- selected" if selection == 4 else " ") + "\r")
        print ("\t\t6) Change Ki divider? (Def: 3.3333, Cur: " + str(divider) + ")\r")
        print ("\t\t7) Include BP in calculation? (Cur: " + bp_included + ")\r")
        print ("\t\t8) Manually adjust Ki\r")
        print ("\t\td) decrease\r")
        print ("\t\ti) increase\r")
        print ("\t\tx) exit\r")
        if nbi.user_input != "":
            if nbi.user_input == '\x1b': #special keycode escape (possible arrow key)
                arrow_key = check_for_arrows() # here but not used, saved for future reference
            KpKi_list = eval(config_data['pidKpKi'])
            if nbi.user_input == "0":
                print ("  * Input your desired float *")
                input_history = getcmd()
                input_history.set_history_file("/data/autotuner/floats_history")
                input_history.cmdloop()
                if input_history.result != "":
                    try:
                        KpKi_list[0][0] = abs(round(float(input_history.result), 5))
                        config_data['pidKpKi'] = str(KpKi_list)
                    except:
                      pass
            if nbi.user_input == "1":
                selection = 0
            if nbi.user_input == "2":
                selection = 1
            if nbi.user_input == "3":
                selection = 2
            if nbi.user_input == "4":
                selection = 3
            if nbi.user_input == "5":
                selection = 4
                print ("  * Enter percentage, without the symbol *")
                input_history = getcmd()
                input_history.set_history_file("/data/autotuner/floats_history")
                input_history.cmdloop()
                if input_history.result != "":
                    try:
                        percentage = int(input_history.result)
                        continue
                    except:
                      pass
            if nbi.user_input == "6":
                print ("  * Input your desired float *")
                input_history = getcmd()
                input_history.set_history_file("/data/autotuner/floats_history")
                input_history.cmdloop()
                if input_history.result != "":
                    try:
                        divider = float(input_history.result)
                        continue
                    except:
                      pass
            if nbi.user_input == "7":
                if ( len(BPV_list[0]) > 3 ):
                    bp_included = "Disabled due to larger list"
                else:
                    if bp_included == "no":
                        bp_included = "yes"
                    else:
                        bp_included = "no"
            if nbi.user_input == "8":
                change_Ki_tuning_entry()
            if nbi.user_input == "d":
                if selection == 4:
                    old_kp = KpKi_list[0][0]
                    new_kp = abs(( float(old_kp) * (percentage/100) ) - float(old_kp))
                    KpKi_list[0][0] = round(new_kp ,5)
                else:
                    KpKi_list[0][0] = round(float(KpKi_list[0][0]) - selection_cases[selection], 5)
            if nbi.user_input == "i":
                if selection == 4:
                    old_kp = KpKi_list[0][0]
                    new_kp = abs(( float(old_kp) * (percentage/100) ) + float(old_kp))
                    KpKi_list[0][0] = round(new_kp ,5)
                else:
                    KpKi_list[0][0] = round(float(KpKi_list[0][0]) + selection_cases[selection], 5)
            if nbi.user_input == "x":
                return
            if bp_included == "yes":
                BPV_list[0][-1] = round(float(BPV_list[1][-1]) * 0.8 / float(KpKi_list[0][0]))
                config_data['torqueBPV'] = str(BPV_list)
            KpKi_list[1][0] = round(float(KpKi_list[0][0]) / 3, 5)
            config_data['pidKpKi'] = str(KpKi_list)
            with open('/data/autotuner.tmp', 'w', encoding='utf8') as file:
                json.dump(config_data, file, indent=2, sort_keys=True, separators=(',', ': '), ensure_ascii=False)
                file.flush()
            shutil.move("/data/autotuner.tmp", "/data/autotuner.json") #change it as main config file
        time.sleep(0.2)
#######################################################################################
def change_BPV_list_entry():
    exit_condition = False
    while exit_condition == False:
        system('clear')
        refresh_BPVKPKI_list()
        print ("  *** Enter new list for BP and V, or 'x' to cancel ***", "\n\n\t\t\r")
        input_history = getcmd()
        input_history.set_history_file("/data/autotuner/bpvkpki_history")
        input_history.cmdloop()
        if input_history.result == "x":
            return
        try:
            evaluate_string = eval(input_history.result)
            if type(evaluate_string) is list and len(evaluate_string) == 2:
                with open('/data/autotuner.json', 'r') as file: #read our configuration
                    config_data = json.loads(file.read())
                BPV_list = input_history.result
                config_data['torqueBPV'] = str(BPV_list)
                with open('/data/autotuner.tmp', 'w', encoding='utf8') as file:
                    json.dump(config_data, file, indent=2, sort_keys=True, separators=(',', ': '), ensure_ascii=False)
                    file.flush()
                shutil.move("/data/autotuner.tmp", "/data/autotuner.json") #change it as main config file
                return
        except:
            print ("\t\t\tInvalid entry, try again...")
            time.sleep(1.0)
#######################################################################################
def change_KpKi_list_entry():
    exit_condition = False
    while exit_condition == False:
        system('clear')
        refresh_BPVKPKI_list()
        print ("  *** Enter new list for Kp and Ki, or 'x' to cancel ***", "\n\n\t\t\r")
        input_history = getcmd()
        input_history.set_history_file("/data/autotuner/bpvkpki_history")
        input_history.cmdloop()
        if input_history.result == "x":
            return
        try:
            evaluate_string = eval(input_history.result)
            if type(evaluate_string) is list and len(evaluate_string) == 2:
                with open('/data/autotuner.json', 'r') as file: #read our configuration
                    config_data = json.loads(file.read())
                KpKi_list = input_history.result
                config_data['pidKpKi'] = str(KpKi_list)
                with open('/data/autotuner.tmp', 'w', encoding='utf8') as file:
                    json.dump(config_data, file, indent=2, sort_keys=True, separators=(',', ': '), ensure_ascii=False)
                    file.flush()
                shutil.move("/data/autotuner.tmp", "/data/autotuner.json") #change it as main config file
                return
        except:
            print ("\t\t\tInvalid entry, try again...")
            time.sleep(1.0)
#######################################################################################
def do_nothing_on_signal(sig, frame):
    print ("") #Do nothing
if __name__ == '__main__':
    subprocess.call(["bash", "autotuner.sh"], cwd="/data")
    subprocess.call(["bash", "autotuner.sh"], cwd="/data")
    subprocess.call(["bash", "autotuner.sh"], cwd="/data")

    signal.signal(signal.SIGINT, do_nothing_on_signal)
    signal.signal(signal.SIGQUIT, do_nothing_on_signal)
    signal.signal(signal.SIGTSTP, do_nothing_on_signal)

    if not path.exists("/system/comma/home/autotuner.py"):
        subprocess.call(["su", "root", "mount", "-o", "rw,remount,rw", "/system"])
        subprocess.call(["su", "root", "rm", "/system/comma/home/autotuner.py"], stdout=PIPE)
        with open('/system/comma/home/autotuner.py', 'w') as f:
            f.write("import subprocess\nimport signal\ndef signal_handler(sig, frame):\n    print ("")\nsignal.signal(signal.SIGINT, signal_handler)\nsignal.signal(signal.SIGQUIT, signal_handler)\nsignal.signal(signal.SIGTSTP, signal_handler)\nsubprocess.call([\"python\", \"autotuner.py\"], cwd=\"/data\")")
        subprocess.call(["mount", "-o", "ro,remount,ro", "/system"])
        subprocess.call(["sync"], stdout=PIPE)
        os.system('stty sane')
        sys.exit(0)

    if not path.exists("/data/openpilot/autotuner.py"):
        subprocess.call(["su", "root", "rm", "/system/comma/home/autotuner.py"], stdout=PIPE)
        with open('/data/openpilot/autotuner.py', 'w') as f:
            f.write("import subprocess\nimport signal\ndef signal_handler(sig, frame):\n    print ("")\nsignal.signal(signal.SIGINT, signal_handler)\nsignal.signal(signal.SIGQUIT, signal_handler)\nsignal.signal(signal.SIGTSTP, signal_handler)\nsubprocess.call([\"python\", \"autotuner.py\"], cwd=\"/data\")")
        subprocess.call(["sync"], stdout=PIPE)
        os.system('stty sane')
        sys.exit(0)

    nbi = TMGTuner()
    estimated_kp_select = 0
    finished_processing = False
    while not finished_processing:
        while nbi.menuscreen == "main":
            nbi.user_input = ""
            main_screen()

        while nbi.menuscreen == "bpvkpki":
            nbi.user_input = ""
            BP_V_Ki_Kp_screen()

        while nbi.menuscreen == "KfSrSrc":
            nbi.user_input = ""
            KfSrSrc_screen()

        while nbi.menuscreen == "autoecu_menu":
            nbi.user_input = ""
            autoecu_menu()

