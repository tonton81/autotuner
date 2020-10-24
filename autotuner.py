from os import system
import threading
import subprocess
import sys, termios, tty, os, time, json, queue, shutil
import cmd, readline

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
#        self.string_input = ""
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
    print ("\t\t\tx) exit\n\r")
    print ("\n\n\n\n\r")

    if nbi.user_input == "1":
        nbi.menuscreen = "bpvkpki"

    if nbi.user_input == "x":
        os.system('stty sane')
        sys.exit(0)

    time.sleep(0.2)
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
    print ("    pid.ki: ", KpKi_list[1], "\n\n\r")
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
def change_KpKi_tuning_entry():
    with open('/data/autotuner.json', 'r') as file: #read our configuration
        config_data = json.loads(file.read())
    BPV_list = eval(config_data['torqueBPV'])
    exit_condition = False
    selection_cases = [0.1, 0.01, 0.001, 0.0001]
    selection = 0
    divider = 3.3333
    if ( len(BPV_list[0]) > 3 ):
        bp_included = "Disabled due to larger list"
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
        print ("\t\t\t1) 0.1" + (" <-------- selected" if selection == 0 else " ") + "\n\r")
        print ("\t\t\t2) 0.01" + (" <-------- selected" if selection == 1 else " ") + "\n\r")
        print ("\t\t\t3) 0.001" + (" <-------- selected" if selection == 2 else " ") + "\n\r")
        print ("\t\t\t4) 0.0001" + (" <-------- selected" if selection == 3 else " ") + "\n\r")
        print ("\t\t\t5) Change Ki divider? (Default: 3.3333, Currently:" + str(divider) + ")\n\r")
        print ("\t\t\t6) Include breakpoint in calculation? (Currently: " + bp_included + ")\n\r")
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
            if nbi.user_input == "6":
                if ( len(BPV_list[0]) > 3 ):
                    bp_included = "Disabled due to larger list"
                else:
                    if bp_included == "no":
                        bp_included = "yes"
                    else:
                        bp_included = "no"
            if nbi.user_input == "d":
                KpKi_list[0][0] = round(float(KpKi_list[0][0]) - selection_cases[selection], 5)
            if nbi.user_input == "i":
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
if __name__ == '__main__':
    nbi = TMGTuner()
    finished_processing = False
    while not finished_processing:
        while nbi.menuscreen == "main":
            nbi.user_input = ""
            main_screen()

        while nbi.menuscreen == "bpvkpki":
            nbi.user_input = ""
            BP_V_Ki_Kp_screen()

