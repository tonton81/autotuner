import re
import struct
import hashlib
import binascii
import argparse
import time
import math
from copy import deepcopy
from os import system
import threading
import signal
import subprocess
from subprocess import Popen, PIPE
import sys, termios, tty, os, time, json, queue, shutil
import cmd, readline
import os.path
from os import path

stock_speed_clamp = []
stock_table_rows = []
stock_filter_rows = []
mod_speed_clamp = []
mod_table_rows = []
mod_filter_rows = []
userbin_hash = 0
debug_eps_tool = 0
detected_model = 0
forced_model = 0

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


class TMGTuner_autoecu:

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


system('clear')
if not path.exists("/data/autotuner/user.bin"):
    print ("\n\n\t\t ***WARNING ***\n\n\r")
    print ("\tuser.bin NOT FOUND.\n\tPut it in the /data/autotuner/ directory.")
    input("\tPress Enter to exit...")
    sys.exit(0)

with open("/data/autotuner/user.bin",'rb+') as u:
    userbin = u.read()
    userbin_hash = hashlib.md5(userbin).hexdigest()
    if debug_eps_tool:
        print ("\nFirmware Hash: " + str(userbin_hash) + "\n")


def forced_table(input_model):
    global forced_model
    global mod_table_rows
    global mod_filter_rows
    global mod_speed_clamp
    forced_model = 0
    with open("/data/autotuner/eps_tool.py",'r') as f:
        section_found = 0
        table_row_check = 0
        table_rows_found = 0
        forced_table_rows = []
        eps_tool = f.readlines()
        for line in eps_tool:
            if "Detected bin:" in line:
                if input_model in line:
                    forced_model = list(re.findall('\'([^\']*)\'', line))
                    print (str(forced_model[0]))
                    section_found = 1
                continue
            if section_found == 1:
                if "elif input_bin_hash ==" in line:
                    section_found = 0
                    mod_table_rows = deepcopy(forced_table_rows)
                    return 1
                    break
                else:
                    if "data_old = [" in line:
                        table_row_check = 1
                        continue
                    if table_row_check == 1:
                        table_row = list(re.findall(r'0x[0-9a-fA-F]+',line))
                        if len(table_row) == 9:
                            table_rows_found = 1
                            print (table_row)
                            forced_table_rows.append(table_row)
                            continue
                        if table_rows_found == 1:
                            if debug_eps_tool:
                                print ("'" + str(forced_table_rows[0]).replace("'","").replace("[","").replace("]","") + "'")
                                print ("'" + str(forced_table_rows[1]).replace("'","").replace("[","").replace("]","") + "'")
                                print ("'" + str(forced_table_rows[2]).replace("'","").replace("[","").replace("]","") + "'")
                                print ("'" + str(forced_table_rows[3]).replace("'","").replace("[","").replace("]","") + "'")
                                print ("'" + str(forced_table_rows[4]).replace("'","").replace("[","").replace("]","") + "'")
                                print ("'" + str(forced_table_rows[5]).replace("'","").replace("[","").replace("]","") + "'")
                                print ("'" + str(forced_table_rows[6]).replace("'","").replace("[","").replace("]","") + "'")
                                print ("")
                                print (str(len(forced_table_rows)) + " rows.\n")
                            table_row_check = 0
        return 0 






with open("/data/autotuner/eps_tool.py",'r') as f:
    section_found = 0
    speed_clamp_check = 0
    table_row_check = 0
    table_rows_found = 0
    filter_row_check = 0
    filter_rows_found = 0
    eps_tool = f.readlines()
    for line in eps_tool:
        if str(userbin_hash) in line:
            section_found = 1
            continue
        if section_found == 1:
            if "elif input_bin_hash ==" in line:
                section_found = 0
            else:
                if "car_model" in line:
                    detected_model = list(re.findall('\'([^\']*)\'', line))
                    if debug_eps_tool:
                        print ("Firmware ID: " + str(detected_model[0]) + "\n")
                    continue

                if "data_old = [" in line:
                    speed_clamp_check = 1
                    continue

                if speed_clamp_check == 1:
                    speed_clamp = list(re.findall(r'0x[0-9a-fA-F]+',line))
                    if len(speed_clamp) == 1:
                        stock_speed_clamp.append(speed_clamp)
                        mod_speed_clamp.append(speed_clamp)
                        speed_clamp_check = 0
                        if debug_eps_tool:
                            print ("'" + str(stock_speed_clamp[0]).replace("'","").replace("[","").replace("]","") + "'" + "\n")
                        table_row_check = 1
                        continue

                if table_row_check == 1:
                    table_row = list(re.findall(r'0x[0-9a-fA-F]+',line))
                    if len(table_row) == 9:
                        table_rows_found = 1
                        stock_table_rows.append(table_row)
                        continue
                    if table_rows_found == 1:
                        if debug_eps_tool:
                            print ("'" + str(stock_table_rows[0]).replace("'","").replace("[","").replace("]","") + "'")
                            print ("'" + str(stock_table_rows[1]).replace("'","").replace("[","").replace("]","") + "'")
                            print ("'" + str(stock_table_rows[2]).replace("'","").replace("[","").replace("]","") + "'")
                            print ("'" + str(stock_table_rows[3]).replace("'","").replace("[","").replace("]","") + "'")
                            print ("'" + str(stock_table_rows[4]).replace("'","").replace("[","").replace("]","") + "'")
                            print ("'" + str(stock_table_rows[5]).replace("'","").replace("[","").replace("]","") + "'")
                            print ("'" + str(stock_table_rows[6]).replace("'","").replace("[","").replace("]","") + "'")
                            print ("")
                            print (str(len(stock_table_rows)) + " rows.\n")
                        filter_row_check = 1
                        table_row_check = 0

                if filter_row_check == 1:
                    filter_row = list(re.findall(r'0x[0-9a-fA-F]+',line))
                    if len(filter_row) == 9:
                        filter_rows_found = 1
                        stock_filter_rows.append(filter_row)
                        continue
                    if filter_rows_found == 1:
                        if debug_eps_tool:
                            print ("'" + str(stock_filter_rows[0]).replace("'","").replace("[","").replace("]","") + "'")
                            print ("'" + str(stock_filter_rows[1]).replace("'","").replace("[","").replace("]","") + "'")
                            print ("'" + str(stock_filter_rows[2]).replace("'","").replace("[","").replace("]","") + "'")
                            print ("'" + str(stock_filter_rows[3]).replace("'","").replace("[","").replace("]","") + "'")
                            print ("'" + str(stock_filter_rows[4]).replace("'","").replace("[","").replace("]","") + "'")
                            print ("'" + str(stock_filter_rows[5]).replace("'","").replace("[","").replace("]","") + "'")
                            print ("'" + str(stock_filter_rows[6]).replace("'","").replace("[","").replace("]","") + "'")
                            print ("")
                            print (str(len(stock_filter_rows)) + " rows.\n")
                        filter_row_check = 0
    if debug_eps_tool:
        print ("CAPTURED STOCK DATA!")

mod_table_rows = deepcopy(stock_table_rows)
mod_filter_rows = deepcopy(stock_filter_rows)
mod_speed_clamp[0] = "{0:#0{1}x}".format(int(stock_speed_clamp[0][0],16),6)


idx_row_sedan = []
idx_row_sedan.append([0x0, 0xDE, 0x14D, 0x1EF, 0x290, 0x377, 0x454, 0x610, 0x6EE])
idx_row_sedan.append([0x0, 0xDE, 0x14D, 0x1EF, 0x290, 0x377, 0x454, 0x610, 0x6EE])
idx_row_sedan.append([0x0, 0xDE, 0x14D, 0x1EF, 0x290, 0x377, 0x454, 0x610, 0x6EE])
idx_row_sedan.append([0x0, 0xDE, 0x14D, 0x1EF, 0x290, 0x377, 0x454, 0x610, 0x6EE])
idx_row_sedan.append([0x0, 0xDE, 0x14D, 0x1EF, 0x290, 0x377, 0x454, 0x610, 0x6EE])
idx_row_sedan.append([0x0, 0xDE, 0x14D, 0x1EF, 0x290, 0x377, 0x454, 0x610, 0x6EE])
idx_row_sedan.append([0x0, 0xDE, 0x1BB, 0x299, 0x377, 0x455, 0x532, 0x610, 0x6EE])

idx_row_hatch = []
idx_row_hatch.append([0x0, 0x67, 0x107, 0x1CB, 0x294, 0x35E, 0x457, 0x60D, 0x6EE])
idx_row_hatch.append([0x0, 0xDE, 0x14D, 0x1EF, 0x290, 0x377, 0x454, 0x610, 0x6EE])
idx_row_hatch.append([0x0, 0xDE, 0x14D, 0x1EF, 0x290, 0x377, 0x454, 0x610, 0x6EE])
idx_row_hatch.append([0x0, 0xDE, 0x14D, 0x1EF, 0x290, 0x377, 0x454, 0x610, 0x6EE])
idx_row_hatch.append([0x0, 0xDE, 0x14D, 0x1EF, 0x290, 0x377, 0x454, 0x610, 0x6EE])
idx_row_hatch.append([0x0, 0xDE, 0x14D, 0x1EF, 0x290, 0x377, 0x454, 0x610, 0x6EE])
idx_row_hatch.append([0x0, 0xDE, 0x1BB, 0x299, 0x377, 0x455, 0x532, 0x610, 0x6EE])

idx_row_hatch2 = []
idx_row_hatch2.append([0x0, 0x6B, 0xF7, 0x1BE, 0x295, 0x35E, 0x457, 0x60D, 0x6EE])
idx_row_hatch2.append([0x0, 0x67, 0x107, 0x1CB, 0x294, 0x35D, 0x457, 0x60D, 0x6EE])
idx_row_hatch2.append([0x0, 0x67, 0x107, 0x1CB, 0x294, 0x35D, 0x457, 0x60D, 0x6EE])
idx_row_hatch2.append([0x0, 0x6C, 0xFE, 0x1BD, 0x295, 0x385, 0x457, 0x60D, 0x6EE])
idx_row_hatch2.append([0x0, 0x6C, 0xFE, 0x1BD, 0x295, 0x385, 0x457, 0x60D, 0x6EE])
idx_row_hatch2.append([0x0, 0xDE, 0x14D, 0x1EF, 0x290, 0x377, 0x454, 0x610, 0x6EE])
idx_row_hatch2.append([0x0, 0xDE, 0x1BB, 0x299, 0x377, 0x455, 0x532, 0x610, 0x6EE])

idx_row_crv = []
idx_row_crv.append([0x0, 0x98, 0xD6, 0x13E, 0x180, 0x201, 0x293, 0x378, 0x67F])
idx_row_crv.append([0x0, 0x9A, 0xDE, 0x13B, 0x180, 0x203, 0x291, 0x378, 0x67F])
idx_row_crv.append([0x0, 0xDE, 0x1B5, 0x275, 0x356, 0x454, 0x51C, 0x610, 0x6EE])
idx_row_crv.append([0x0, 0xDE, 0x1B5, 0x275, 0x356, 0x454, 0x51C, 0x610, 0x6EE])
idx_row_crv.append([0x0, 0xDE, 0x1B5, 0x275, 0x356, 0x454, 0x51C, 0x610, 0x6EE])
idx_row_crv.append([0x0, 0xDE, 0x1B5, 0x275, 0x356, 0x454, 0x51C, 0x610, 0x6EE])
idx_row_crv.append([0x0, 0xDE, 0x1BB, 0x299, 0x377, 0x454, 0x532, 0x610, 0x67F])

idx_row_hatch_eu = []
idx_row_hatch_eu.append([0x0, 0x67, 0x107, 0x1CB, 0x294, 0x35E, 0x457, 0x60D, 0x6EE])
idx_row_hatch_eu.append([0x0, 0x67, 0x107, 0x1CB, 0x294, 0x35E, 0x457, 0x60D, 0x6EE])
idx_row_hatch_eu.append([0x0, 0x67, 0x107, 0x1CB, 0x294, 0x35E, 0x457, 0x60D, 0x6EE])
idx_row_hatch_eu.append([0x0, 0xDE, 0x14D, 0x1EF, 0x290, 0x377, 0x454, 0x610, 0x6EE])
idx_row_hatch_eu.append([0x0, 0xDE, 0x14D, 0x1EF, 0x290, 0x377, 0x454, 0x610, 0x6EE])
idx_row_hatch_eu.append([0x0, 0xDE, 0x14D, 0x1EF, 0x290, 0x377, 0x454, 0x610, 0x6EE])
idx_row_hatch_eu.append([0x0, 0xDE, 0x1BB, 0x299, 0x377, 0x455, 0x532, 0x610, 0x6EE])


# assign index tables for lookups
if userbin_hash == '9ccedbdd7d4d8d0eb356fadcc763353d': # 39990-TBA-A030
    idx_row_chosen = idx_row_sedan
if userbin_hash == '39710b41653f6b73b3b8c678d82790c0': # 39990-TGG-A020
    idx_row_chosen = idx_row_hatch
    idx_row_chosen[0][7] = 0x60C
if userbin_hash == '11ba08b27a643c3e3b23bbd08463a40e': # 39990-TGG-A120
    idx_row_chosen = idx_row_hatch
if userbin_hash == 'a062d1b894ef57efc2f54c392f47d9f0': # 39990-TBA-C120
    idx_row_chosen = idx_row_hatch2
if userbin_hash == '0c21cdf567d6a5a5faaf4512af1029f0': # 39990-TPA-G030
    idx_row_chosen = idx_row_crv
if userbin_hash == '98f133c5e3b72653e71fee5ea3ef52e8': # 39990-TGN-E120
    idx_row_chosen = idx_row_hatch_eu



use_idx_row = 0
max_stepping_combined = 0
max_step1 = 15
max_step2 = 15
max_step3 = 15
max_step = 37.927
point_1_torque_multiplier = 0
point_2_torque_multiplier = 0
point_3_torque_multiplier = 0
mod_type = ""
breakpoints_size = 9




def kiril_mod(): # 3 point kiril mod
    global mod_type
    global max_step1
    global max_step2
    global max_step3
    global point_1_torque_multiplier
    global point_2_torque_multiplier
    global point_3_torque_multiplier
    for i in range(len(mod_table_rows)):
        mod_table_rows[i][6] = hex(round(int(mod_table_rows[i][6-1],16) + max_step1 * (idx_row_chosen[i][6] - idx_row_chosen[i][6-1])))
        mod_table_rows[i][7] = hex(round(int(mod_table_rows[i][7-1],16) + max_step2 * (idx_row_chosen[i][7] - idx_row_chosen[i][7-1])))
        mod_table_rows[i][8] = hex(round(int(mod_table_rows[i][8-1],16) + max_step3 * (idx_row_chosen[i][8] - idx_row_chosen[i][8-1])))

    point_1_torque_multiplier = int(mod_table_rows[0][6],16) / int(stock_table_rows[0][5],16)
    point_2_torque_multiplier = int(mod_table_rows[0][7],16) / int(stock_table_rows[0][6],16)
    point_3_torque_multiplier = int(mod_table_rows[0][8],16) / int(stock_table_rows[0][7],16)

    for i in range(len(mod_filter_rows)): # update filters
        mod_filter_rows[i][7] = "{0:#0{1}x}".format(0x400,6)
        mod_filter_rows[i][8] = "{0:#0{1}x}".format(0x480,6)

    if debug_eps_tool:
        print ("\nMultiplier steps: " + str(round(point_1_torque_multiplier,7)) + "x, " + str(round(point_2_torque_multiplier,7)) + "x, " + str(round(point_3_torque_multiplier,7)) + "x")
        print ("Actual multiplier: " + str(round(int(mod_table_rows[0][8],16) / int(stock_table_rows[0][8],16),7)) + "x\n")

        for i in range(len(idx_row_chosen)):
            for j in range(0, len(idx_row_chosen[0])):
                print (" " + str(hex(int(round(idx_row_chosen[i][j] / math.sqrt(3), 0)) << 2)) + " ", end='')
            print ("")
        # 9 point BPV
        print ("\n[[", end='')
        for j in range(0, len(mod_table_rows[0])):
            print (str((mod_table_rows[use_idx_row][j])), end='')
            if j < 8:
                print(",", end='')
        print ("],[", end='')
        for j in range(0, len(idx_row_chosen[0])):
            print (str(hex(int(round(idx_row_chosen[use_idx_row][j] / math.sqrt(3), 0)) << 2)), end='')
            if j < 8:
                print(",", end='')
        print ("]]")
        # 3 point BPV
        print ("\n[[0, ", end='')
        print (str((int(round(idx_row_chosen[use_idx_row][5] / math.sqrt(3), 0)) << 2)), end='')
        print (", 12000],[0, ", end='')
        print (str((int(round(idx_row_chosen[use_idx_row][5] / math.sqrt(3), 0)) << 2)) + ", ", end='')
        print (str((int(round(idx_row_chosen[use_idx_row][8] / math.sqrt(3), 0)) << 2)), end='')
        print ("]]\n")

    subprocess.call(["pkill", "chrome"])
    subprocess.call(["rm", "-rf", "/data/data/com.android.chrome/app_tabs/0"])
    show_chart = "http://www.plotvar.com/line.php?title=&yaxis=&xvalues=&serie1=Stock&values_serie1=" + stock_table_rows[use_idx_row][0] + "%2C" + stock_table_rows[use_idx_row][1] + "%2C" + stock_table_rows[use_idx_row][2] + "%2C" + stock_table_rows[use_idx_row][3] + "%2C" + stock_table_rows[use_idx_row][4] + "%2C" + stock_table_rows[use_idx_row][5] + "%2C" + stock_table_rows[use_idx_row][6] + "%2C" + stock_table_rows[use_idx_row][7] + "%2C" + stock_table_rows[use_idx_row][8] + "&serie3=Modded&values_serie3=" + mod_table_rows[use_idx_row][0] + "%2C" + mod_table_rows[use_idx_row][1] + "%2C" + mod_table_rows[use_idx_row][2] + "%2C" + mod_table_rows[use_idx_row][3] + "%2C" + mod_table_rows[use_idx_row][4] + "%2C" + mod_table_rows[use_idx_row][5] + "%2C" + mod_table_rows[use_idx_row][6] + "%2C" + mod_table_rows[use_idx_row][7] + "%2C" + mod_table_rows[use_idx_row][8]
    subprocess.call(["am", "start", "-n", "com.android.chrome/com.google.android.apps.chrome.Main", "-d", show_chart], stdout=PIPE)

def generate_eps_tool():
    with open("/data/autotuner/eps_tool_new.py",'w') as n:
        with open("/data/autotuner/eps_tool.py",'r') as f:
            section_found = 0
            speed_clamp_check = 0
            table_row_check = 0
            table_rows_found = 0
            filter_row_check = 0
            filter_rows_found = 0
            process_row = 0
            eps_tool = f.readlines()
            for line in eps_tool:
                if str(userbin_hash) in line:
                    section_found = 1
                    n.writelines(line)
                    continue
                if section_found == 1:
                    if "elif input_bin_hash ==" in line:
                        section_found = 0
                    else:
                        if "car_model" in line:
                            firmware_id = list(re.findall('\'([^\']*)\'', line))
                            if debug_eps_tool:
                                print ("Firmware ID: " + str(firmware_id[0]) + "\n")
                            n.writelines(line)
                            continue

                        if "data_new = [" in line:
                            speed_clamp_check = 1
                            n.writelines(line)
                            continue

                        if speed_clamp_check == 1:
                            speed_clamp = list(re.findall(r'0x[0-9a-fA-F]+',line))
                            if len(speed_clamp) == 1:
                                speed_clamp_check = 0
                                line = line.replace(str(speed_clamp[0]), str(mod_speed_clamp[0]).replace("'","").replace("[","").replace("]",""))
                                n.writelines(line)
                                if debug_eps_tool:
                                    print ("Stock: '" + str(stock_speed_clamp[0]).replace("'","").replace("[","").replace("]","") + "'")
                                    print (line)
                                table_row_check = 1
                                continue

                        if table_row_check == 1:
                            table_row = re.findall(r'0x[0-9a-fA-F]+',line)
                            if len(table_row) == 9:
                                line = line.replace(str(re.findall(r'0x[0-9a-fA-F]+',line)).replace("'","").replace("[","").replace("]","") + "'", str(str(mod_table_rows[process_row]).replace("'","").replace("[","").replace("]","") + "'"))
                                n.writelines(line)
                                if debug_eps_tool:
                                    print (line, end='')
                                table_rows_found = 1
                                process_row += 1
                                continue
                            if table_rows_found == 1:
                                if debug_eps_tool:
                                    print ("\n")
                                filter_row_check = 1
                                process_row = 0
                                table_row_check = 0

                        if filter_row_check == 1:
                            filter_row = list(re.findall(r'0x[0-9a-fA-F]+',line))
                            if len(filter_row) == 9:
                                line = line.replace(str(re.findall(r'0x[0-9a-fA-F]+',line)).replace("'","").replace("[","").replace("]","") + "'", str(str(mod_filter_rows[process_row]).replace("'","").replace("[","").replace("]","") + "'"))
                                n.writelines(line)
                                if debug_eps_tool:
                                    print (line, end='')
                                filter_rows_found = 1
                                process_row += 1
                                continue
                            if filter_rows_found == 1:
                                 if debug_eps_tool:
                                    print ("\n")
                                 process_row = 0
                                 filter_row_check = 0
                n.writelines(line)
            if debug_eps_tool:
                print ("FINALIZED MOD!")



def main_screen():
    global breakpoints_size
    global mod_type
    global max_step1
    global max_step2
    global max_step3
    global point_1_torque_multiplier
    global point_2_torque_multiplier
    global point_3_torque_multiplier
    global mod_table_rows
    global mod_filter_rows
    global mod_speed_clamp
    if autoecu.user_input == "":
        autoecu.get_input_key()

    system('clear')
    print ("\n\r\t\t\033[32m\033[4mWelcome to the TMG Firmware tuner!\n\033[0m\033[32m\r")
    print ("\t\tDetected Firmware: " + detected_model[0] + "\n\r")

    print ("\t\033[32m\033[4mStock torqueBP:\033[0m\033[32m\n\r")
    for i in range(len(stock_table_rows)):
        print ("\t[", end='')
        for j in range(0, len(stock_table_rows[0])):
            print (str(stock_table_rows[i][j]), end='')
            if j < len(stock_table_rows[0]) - 1:
                print (", ", end='')
        print ("]\r")

    if forced_model == 0:
        modified_table = ""
    else:
        modified_table = " (Table from " + str(forced_model[0]).replace("Detected bin: ","") + ")"

    print ("\n\t\033[32m\033[4mModded torqueBP:\033[0m\033[32m" + modified_table + "\n\r")
    for i in range(len(mod_table_rows)):
        print ("\t[", end='')
        for j in range(0, len(mod_table_rows[0])):
            print (str(mod_table_rows[i][j]), end='')
            if j < len(mod_table_rows[0]) - 1:
                print (", ", end='')
        print ("]\r")

    print ("\n\t\t\t1) View index and torqueV tables\r")
    print ("\t\t\t2) Steer to " + str(int(mod_speed_clamp[0],16)) + "km/h, (" + str(int(int(mod_speed_clamp[0],16) * 0.621371)) + "mph)\r")
    print ("\t\t\t3) 3 or 9 breakpoints? (Currently: " + str(breakpoints_size) + ")\r")
    print ("\t\t\t4) Force torque table from another model\r")


    if breakpoints_size == 3:
        print ("\n[[0, ", end='')
        print (str((int(round(idx_row_chosen[use_idx_row][5] / math.sqrt(3), 0)) << 2)), end='')
        print (", 12000],[0, ", end='')
        print (str((int(round(idx_row_chosen[use_idx_row][5] / math.sqrt(3), 0)) << 2)) + ", ", end='')
        print (str((int(round(idx_row_chosen[use_idx_row][8] / math.sqrt(3), 0)) << 2)), end='')
        print ("]]\r")
    else:
        print ("\n[[", end='')
        for j in range(0, len(mod_table_rows[0])):
            print (str((mod_table_rows[use_idx_row][j])), end='')
            if j < 8:
                print(",", end='')
        print ("],[", end='')
        for j in range(0, len(idx_row_chosen[0])):
            print (str(hex(int(round(idx_row_chosen[use_idx_row][j] / math.sqrt(3), 0)) << 2)), end='')
            if j < 8:
                print(",", end='')
        print ("]]\r")


    print ("\t\t\t\033[32m\033[4mMod types:\033[0m\033[32m\r")
    print ("\t\t          k) kiril (3 point curve)\r")
    if mod_type == "kiril":
        print ("\t\t           ^-- step1: " + str(max_step1) + " step2: " + str(max_step2) + " step3: " + str(max_step3) + "\r")
        print ("\t\t           ^-- " + str(round(point_1_torque_multiplier,5)) + "x, " + str(round(point_2_torque_multiplier,5)) + "x, " + str(round(point_3_torque_multiplier,5)) + "x\r")
        print ("\t\t           ^-- Actual: " + str(round(int(mod_table_rows[0][8],16) / int(stock_table_rows[0][8],16),7)) + "x\r")

    print ("\n\t\t\tS) Generate Stock RWD\r")
    if mod_type != "":
        print ("\t\t\tG) Generate Modded RWD\r")
    if path.exists("/data/autotuner/last_rwd.txt"):
        print ("\t\t\tV) View last RWD details\r")
    print ("\t\t\tx) exit\n\r")
    print ("\n\n\n\n\r")

    while autoecu.user_input == "":
        autoecu.user_input = autoecu.input_get()

    if autoecu.user_input == "1":
        autoecu.menuscreen = "torquevindextables"

    if autoecu.user_input == "2":
        print ("Enter a new speed:\r")
        input_history = getcmd()
        input_history.set_history_file("/data/autotuner/random_history")
        input_history.cmdloop()
        if input_history.result != "":
            try:
                mod_speed_clamp[0] = "{0:#0{1}x}".format(eval(input_history.result),6)
            except:
                pass

    if autoecu.user_input == "3":
        if breakpoints_size != 3:
            breakpoints_size = 3
        else:
            breakpoints_size = 9


    if autoecu.user_input == "4":
        mod_type = ""
        print ("Enter a firmware model:\r")
        input_history = getcmd()
        input_history.set_history_file("/data/autotuner/random_history")
        input_history.cmdloop()
        if input_history.result != "":
            try:
                forced_table(input_history.result)
            except:
                pass




    if autoecu.user_input == "k":
        mod_type = "kiril"
        print ("Enter your 3 values separated with a comma, or one value for all 3:\r")
        input_history = getcmd()
        input_history.set_history_file("/data/autotuner/random_history")
        input_history.cmdloop()
        if input_history.result != "":
            try:
                if isinstance(eval(input_history.result), (tuple)):
                    if len(list(eval(input_history.result))) == 3:
                        max_step1 = list(eval(input_history.result))[0]
                        max_step2 = list(eval(input_history.result))[1]
                        max_step3 = list(eval(input_history.result))[2]
                if isinstance(eval(input_history.result), (int, float)):
                    max_step1 = eval(input_history.result)
                    max_step2 = eval(input_history.result)
                    max_step3 = eval(input_history.result)
                kiril_mod()
            except:
                pass


    if autoecu.user_input == "G":
        system('clear')
        subprocess.call(["python", "/data/autotuner/eps_tool_new.py"])
        print ("Press any key to return to menu...")
        with open('/data/autotuner/last_rwd.txt', 'w') as f:

            f.write("Index table:\n")
            for i in range(len(idx_row_chosen)):
                f.write("\t[")
                for j in range(0, len(idx_row_chosen[0])):
                    f.write(str(hex(int(round(idx_row_chosen[i][j], 0)))))
                    if j < len(idx_row_chosen[0]) - 1:
                        f.write(", ")
                f.write("]\n")

            f.write("\nStock torqueBP:\n")
            for i in range(len(stock_table_rows)):
                f.write("\t[")
                for j in range(0, len(stock_table_rows[0])):
                    f.write(str(stock_table_rows[i][j]))
                    if j < len(stock_table_rows[0]) - 1:
                        f.write(", ")
                f.write("]\n")

            f.write("\nModded torqueBP:\n")
            for i in range(len(mod_table_rows)):
                f.write("\t[")
                for j in range(0, len(mod_table_rows[0])):
                    f.write(str(mod_table_rows[i][j]))
                    if j < len(mod_table_rows[0]) - 1:
                        f.write(", ")
                f.write("]\n")

            f.write("\n3 point breakpoints")
            f.write("\n\t[[0, ")
            f.write(str((int(round(idx_row_chosen[use_idx_row][5] / math.sqrt(3), 0)) << 2)))
            f.write(", 12000],[0, ")
            f.write(str((int(round(idx_row_chosen[use_idx_row][5] / math.sqrt(3), 0)) << 2)) + ", ")
            f.write(str((int(round(idx_row_chosen[use_idx_row][8] / math.sqrt(3), 0)) << 2)))
            f.write("]]\n")
            f.write("\n9 point breakpoints")
            f.write("\n\t[[")
            for j in range(0, len(mod_table_rows[0])):
                f.write(str((mod_table_rows[use_idx_row][j])))
                if j < 8:
                    f.write(",")
            f.write("],[")
            for j in range(0, len(idx_row_chosen[0])):
                f.write(str(hex(int(round(idx_row_chosen[use_idx_row][j] / math.sqrt(3), 0)) << 2)))
                if j < 8:
                    f.write(",")
            f.write("]]\n")

            f.write("\nSteer to " + str(int(mod_speed_clamp[0],16)) + "km/h, (" + str(int(int(mod_speed_clamp[0],16) * 0.621371)) + "mph)\n")

            show_chart = "http://www.plotvar.com/line.php?title=&yaxis=&xvalues=&serie1=Stock&values_serie1=" + stock_table_rows[use_idx_row][0] + "%2C" + stock_table_rows[use_idx_row][1] + "%2C" + stock_table_rows[use_idx_row][2] + "%2C" + stock_table_rows[use_idx_row][3] + "%2C" + stock_table_rows[use_idx_row][4] + "%2C" + stock_table_rows[use_idx_row][5] + "%2C" + stock_table_rows[use_idx_row][6] + "%2C" + stock_table_rows[use_idx_row][7] + "%2C" + stock_table_rows[use_idx_row][8] + "&serie3=Modded&values_serie3=" + mod_table_rows[use_idx_row][0] + "%2C" + mod_table_rows[use_idx_row][1] + "%2C" + mod_table_rows[use_idx_row][2] + "%2C" + mod_table_rows[use_idx_row][3] + "%2C" + mod_table_rows[use_idx_row][4] + "%2C" + mod_table_rows[use_idx_row][5] + "%2C" + mod_table_rows[use_idx_row][6] + "%2C" + mod_table_rows[use_idx_row][7] + "%2C" + mod_table_rows[use_idx_row][8]
            f.write("\nLine plot:\n" + show_chart + "\n")

            if mod_type == "kiril":
                f.write("\n kiril mod 3 point <-- step1: " + str(max_step1) + " step2: " + str(max_step2) + " step3: " + str(max_step3) + "\n")
                f.write("\n kiril mod 3 point <-- " + str(round(point_1_torque_multiplier,5)) + "x, " + str(round(point_2_torque_multiplier,5)) + "x, " + str(round(point_3_torque_multiplier,5)) + "x\n")
                f.write("\n kiril mod 3 point <-- Actual: " + str(round(int(mod_table_rows[0][8],16) / int(stock_table_rows[0][8],16),7)) + "x\n")

        autoecu.user_input = ""
        autoecu.get_input_key()
        while autoecu.user_input == "":
            autoecu.user_input = autoecu.input_get()
        autoecu.user_input = ""
        shutil.copy("/data/autotuner/user_patched.rwd", "/sdcard/autotuner.rwd")

    if autoecu.user_input == "S":
        mod_type = ""
        system('clear')
        mod_table_rows = deepcopy(stock_table_rows)
        mod_filter_rows = deepcopy(stock_filter_rows)
        mod_speed_clamp[0] = "{0:#0{1}x}".format(int(stock_speed_clamp[0][0],16),6)
        generate_eps_tool()
        subprocess.call(["python", "/data/autotuner/eps_tool_new.py"])
        print ("Press any key to return to menu...")
        with open('/data/autotuner/last_rwd.txt', 'w') as f:

            f.write("Index table:\n")
            for i in range(len(idx_row_chosen)):
                f.write("\t[")
                for j in range(0, len(idx_row_chosen[0])):
                    f.write(str(hex(int(round(idx_row_chosen[i][j], 0)))))
                    if j < len(idx_row_chosen[0]) - 1:
                        f.write(", ")
                f.write("]\n")

            f.write("\nStock torqueBP:\n")
            for i in range(len(stock_table_rows)):
                f.write("\t[")
                for j in range(0, len(stock_table_rows[0])):
                    f.write(str(stock_table_rows[i][j]))
                    if j < len(stock_table_rows[0]) - 1:
                        f.write(", ")
                f.write("]\n")

            f.write("\nModded torqueBP:\n")
            for i in range(len(mod_table_rows)):
                f.write("\t[")
                for j in range(0, len(mod_table_rows[0])):
                    f.write(str(mod_table_rows[i][j]))
                    if j < len(mod_table_rows[0]) - 1:
                        f.write(", ")
                f.write("]\n")

            f.write("\n3 point breakpoints")
            f.write("\n\t[[0, ")
            f.write(str((int(round(idx_row_chosen[use_idx_row][5] / math.sqrt(3), 0)) << 2)))
            f.write(", 12000],[0, ")
            f.write(str((int(round(idx_row_chosen[use_idx_row][5] / math.sqrt(3), 0)) << 2)) + ", ")
            f.write(str((int(round(idx_row_chosen[use_idx_row][8] / math.sqrt(3), 0)) << 2)))
            f.write("]]\n")
            f.write("\n9 point breakpoints")
            f.write("\n\t[[")
            for j in range(0, len(mod_table_rows[0])):
                f.write(str((mod_table_rows[use_idx_row][j])))
                if j < 8:
                    f.write(",")
            f.write("],[")
            for j in range(0, len(idx_row_chosen[0])):
                f.write(str(hex(int(round(idx_row_chosen[use_idx_row][j] / math.sqrt(3), 0)) << 2)))
                if j < 8:
                    f.write(",")
            f.write("]]\n")

            f.write("\nSteer to " + str(int(mod_speed_clamp[0],16)) + "km/h, (" + str(int(int(mod_speed_clamp[0],16) * 0.621371)) + "mph)\n")

            show_chart = "http://www.plotvar.com/line.php?title=&yaxis=&xvalues=&serie1=Stock&values_serie1=" + stock_table_rows[use_idx_row][0] + "%2C" + stock_table_rows[use_idx_row][1] + "%2C" + stock_table_rows[use_idx_row][2] + "%2C" + stock_table_rows[use_idx_row][3] + "%2C" + stock_table_rows[use_idx_row][4] + "%2C" + stock_table_rows[use_idx_row][5] + "%2C" + stock_table_rows[use_idx_row][6] + "%2C" + stock_table_rows[use_idx_row][7] + "%2C" + stock_table_rows[use_idx_row][8] + "&serie3=Modded&values_serie3=" + mod_table_rows[use_idx_row][0] + "%2C" + mod_table_rows[use_idx_row][1] + "%2C" + mod_table_rows[use_idx_row][2] + "%2C" + mod_table_rows[use_idx_row][3] + "%2C" + mod_table_rows[use_idx_row][4] + "%2C" + mod_table_rows[use_idx_row][5] + "%2C" + mod_table_rows[use_idx_row][6] + "%2C" + mod_table_rows[use_idx_row][7] + "%2C" + mod_table_rows[use_idx_row][8]
            f.write("\nLine plot:\n" + show_chart)

        autoecu.user_input = ""
        autoecu.get_input_key()
        while autoecu.user_input == "":
            autoecu.user_input = autoecu.input_get()
        autoecu.user_input = ""
        shutil.copy("/data/autotuner/user_patched.rwd", "/sdcard/autotuner.rwd")

    if autoecu.user_input == "V":
        system('clear')
        subprocess.call(["cat", "/data/autotuner/last_rwd.txt"])
        print ("\n\nPress any key to return to menu...")
        autoecu.user_input = ""
        autoecu.get_input_key()
        while autoecu.user_input == "":
            autoecu.user_input = autoecu.input_get()
        autoecu.user_input = ""
 
    if autoecu.user_input == "x":
        os.system('stty sane')
        sys.exit(0)
    print ("\033[0m")
    generate_eps_tool()




def torquevindextables_screen():
    if autoecu.user_input == "":
        autoecu.get_input_key()

    system('clear')
    print ("\n\r\t\t\033[32m\033[4mWelcome to the TMG Firmware tuner!\n\033[0m\033[32m\r")
    print ("\t\tDetected Firmware: " + detected_model[0] + "\n\r")



    print ("\t\033[32m\033[4mIndex table:\033[0m\033[32m\n\r")
    for i in range(len(idx_row_chosen)):
        print ("\t[", end='')
        for j in range(0, len(idx_row_chosen[0])):
            print (str(hex(int(round(idx_row_chosen[i][j], 0)))), end='')
            if j < len(idx_row_chosen[0]) - 1:
                print (", ", end='')
        print ("]\r")
    print ("\n\t\t\t1) Toggle for 0x67f or 0x6ee\n\r")

    print ("\t\033[32m\033[4mTorqueV table:\033[0m\033[32m\n\r")
    for i in range(len(idx_row_chosen)):
        print ("\t[", end='')
        for j in range(0, len(idx_row_chosen[0])):
            print (str(hex(int(round(idx_row_chosen[i][j] / math.sqrt(3), 0)) << 2)), end='')
            if j < len(idx_row_chosen[0]) - 1:
                print (", ", end='')
        print ("]\r")
    print ("\n\t\t\tx) exit\n\r")



    while autoecu.user_input == "":
        autoecu.user_input = autoecu.input_get()

    if autoecu.user_input == "1":
        if idx_row_chosen[0][8] == 0x67f:
            toggle_value = 0x6ee
        else:
            toggle_value = 0x67f
        for i in range(len(idx_row_chosen)):
            idx_row_chosen[i][8] = toggle_value
        if mod_type == "kiril":
            kiril_mod()

    if autoecu.user_input == "x":
        autoecu.menuscreen = "main"


    print ("\033[0m\r")
    generate_eps_tool()




if __name__ == '__main__':

    autoecu = TMGTuner_autoecu()
    finished_processing = False

    while not finished_processing:

        while autoecu.menuscreen == "main":
            autoecu.user_input = ""
            main_screen()

        while autoecu.menuscreen == "torquevindextables":
            autoecu.user_input = ""
            torquevindextables_screen()


