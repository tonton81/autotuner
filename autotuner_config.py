import json
import os.path
import sys
import shutil

class autotuner_config:

  def __init__(self):
    self.file_path = '/data/autotuner.json'


  def get(self, key, default):
    if not os.path.exists(self.file_path): #create dictionary if it doesn't exist
      dictionary = {
                   }
      with open(self.file_path, 'w', encoding='utf8') as file:
        json.dump(dictionary, file, indent=2, sort_keys=True, separators=(',', ': '), ensure_ascii=False)

    with open(self.file_path, 'r') as file:
      config_data = json.loads(file.read())
      try:
        if len(config_data[key]) == 0: #if key is empty, use default from OP
          return default
        return config_data[key]

      except KeyError: # if key doesn't exist, use default
        if not os.path.exists('/data/autotuner/queues/'):
          os.mkdir('/data/autotuner/queues/')
        new_queue_file = "/data/autotuner/queues/" + str(key) + ".queue"  #also queue it in a separate file, to be processed via bash
        if not os.path.exists(new_queue_file): #make sure it wasn't already created for queue
          dictionary = {
                       }
          dictionary[str(key)] = str(default)
          with open(new_queue_file, 'w', encoding='utf8') as file:
            json.dump(dictionary, file, indent=2, sort_keys=True, separators=(',', ': '), ensure_ascii=False)
        return default


  def bash_new_queue(self, from_file):
    with open(self.file_path, 'r') as file: #read our configuration
      config_data = json.loads(file.read())

    with open(from_file, 'r') as file: #get the queue to append
      new_data = json.loads(file.read())
      new_dictionary = dict(list(config_data.items()) + list(new_data.items()))

    with open('/data/autotuner.tmp', 'w', encoding='utf8') as file: #write new config to a temporary file
      json.dump(new_dictionary, file, indent=2, sort_keys=True, separators=(',', ': '), ensure_ascii=False)

      shutil.move('/data/autotuner.tmp', '/data/autotuner.json') #change it as main config file


  def resetall_config(self):
    dictionary = {
                   "reset_defaults": "1"
                 }
    with open('/data/autotuner.tmp', 'w', encoding='utf8') as file: #write new config to a temporary file
      json.dump(dictionary, file, indent=2, sort_keys=True, separators=(',', ': '), ensure_ascii=False)
      file.flush()
    shutil.move('/data/autotuner.tmp', '/data/autotuner.json') #change it as main config file




#FROM BASH ARGUMENTS
if len(sys.argv) > 1:
  autotuner_config = autotuner_config()

  if not os.path.exists('/data/autotuner.json'):
    dictionary = {
                 }
    with open('/data/autotuner.json', 'w', encoding='utf8') as file:
      json.dump(dictionary, file, indent=2, sort_keys=True, separators=(',', ': '), ensure_ascii=False)


  with open('/data/autotuner.json', 'r') as file: #read our configuration
    config_data = json.loads(file.read())



  for i in range(1, len(sys.argv)):

    if sys.argv[i] == "DEFAULT_LIST":
      try:
        BPV_list = "[[0, 2560, 8000], [0, 2560, 3840]]"
        config_data['torqueBPV'] = str(BPV_list)
      except KeyError:
        continue

    if sys.argv[i] == "SET.TONY":
      try:
        BPV_list = "[[0, 2327, 3525, 4119, 4511, 5131, 10435, 21091, 23755], [0, 512, 768, 1144, 1516, 2048, 2560, 3584, 3840]]"
        config_data['torqueBPV'] = str(BPV_list)
      except KeyError:
        continue

    if sys.argv[i] == "RESET":
      autotuner_config.resetall_config()
      raise SystemExit()

    if sys.argv[i] == "BASH_NEW_QUEUE":
      autotuner_config.bash_new_queue(sys.argv[2])
      raise SystemExit()

    if sys.argv[i] == "SET.BP":
      try:
        BPV_list = eval(config_data['torqueBPV'])
        BPV_list[0][-1] = round(float(sys.argv[i+1]))
        config_data['torqueBPV'] = str(BPV_list)
      except KeyError:
        continue

    if sys.argv[i] == "SET.V":
      try:
        BPV_list = eval(config_data['torqueBPV'])
        BPV_list[1][-1] = round(float(sys.argv[i+1]))
        config_data['torqueBPV'] = str(BPV_list)
      except KeyError:
        continue

    if sys.argv[i] == "SET.MP":
      try:
        BPV_list = eval(config_data['torqueBPV'])
        if ( len(BPV_list[0]) != 3 ):
          print ("Only 3 value lists are supported")
          continue
        if ( len(BPV_list[1]) != 3 ):
          print ("Only 3 value lists are supported")
          continue
        BPV_list[0][1] = round(float(sys.argv[i+1]))
        BPV_list[1][1] = round(float(sys.argv[i+1]))
        config_data['torqueBPV'] = str(BPV_list)
      except KeyError:
        continue

    if sys.argv[i] == "SET.MP1":
      BPV_list = eval(config_data['torqueBPV'])
      try:
        if ( len(BPV_list[0]) != 3 ):
          print ("Only 3 value lists are supported")
          continue
        BPV_list[0][1] = round(float(sys.argv[i+1]))
        config_data['torqueBPV'] = str(BPV_list)
      except KeyError:
        continue

    if sys.argv[i] == "SET.MP2":
      BPV_list = eval(config_data['torqueBPV'])
      try:
        if ( len(BPV_list[1]) != 3 ):
          print ("Only 3 value lists are supported")
          continue
        BPV_list[1][1] = round(float(sys.argv[i+1]))
        config_data['torqueBPV'] = str(BPV_list)
      except KeyError:
        continue


    if sys.argv[i] == "INC.MP1":
      try:
        BPV_list = eval(config_data['torqueBPV'])
        if ( len(BPV_list[0]) != 3 ):
          print ("Only 3 value lists are supported")
          continue
        BPV_list[0][1] = BPV_list[0][1] + int(sys.argv[i+1])
        config_data['torqueBPV'] = str(BPV_list)
        KpKi_list = eval(config_data['pidKpKi'])
        print ("\n  New tune set!\n    " + str(BPV_list) + "\n    " + str(KpKi_list) + "\n")
      except KeyError:
        continue




    if sys.argv[i] == "SET.KP":
      try:
        KpKi_list = eval(config_data['pidKpKi'])
        KpKi_list[0][0] = float(sys.argv[i+1])
        config_data['pidKpKi'] = str(KpKi_list)
      except KeyError:
        continue

    if sys.argv[i] == "SET.KI":
      try:
        KpKi_list = eval(config_data['pidKpKi'])
        KpKi_list[1][0] = float(sys.argv[i+1])
        config_data['pidKpKi'] = str(KpKi_list)
      except KeyError:
        continue

    if sys.argv[i] == "SET.KPDIV":
      try:
        KpDIV = float(sys.argv[i+1])
      except KeyError:
        continue

    if sys.argv[i] == "TUNEKP":
      try:
        KpKi_list = eval(config_data['pidKpKi'])
        KpKi_list[0][0] = float(sys.argv[i+1])
        config_data['pidKpKi'] = str(KpKi_list)
      except KeyError:
        continue

    if sys.argv[i] == "SET.KF":
      try:
        config_data['kf'] = str(sys.argv[i+1])
      except KeyError:
        continue



###############################################################################################
  try:                                                                 # CONFIGURE BP/V/Kp/Ki #
    if "TUNEKP" in str(sys.argv):                                      #    THEN PRINT RESULT #
      BPV_list = eval(config_data['torqueBPV'])                        ########################
      KpKi_list = eval(config_data['pidKpKi'])
      KP_DIV = float(KpDIV) if "KPDIV" in str(sys.argv) else float(3)
      if not "SET.BP" in str(sys.argv):
        if ( len(BPV_list[0]) == 3 ):
          BPV_list[0][-1] = round(float(BPV_list[1][-1]) * 0.8 / float(KpKi_list[0][0]))
          config_data['torqueBPV'] = str(BPV_list)
      KpKi_list[1][0] = round(float(KpKi_list[0][0]) / KP_DIV, 5)
      config_data['pidKpKi'] = str(KpKi_list)
    if "SET.BP" in str(sys.argv) or \
       "SET.V" in str(sys.argv) or \
       "SET.MP" in str(sys.argv) or \
       "SET.KP" in str(sys.argv) or \
       "SET.KI" in str(sys.argv) or \
       "SET.KPDIV" in str(sys.argv) or \
       "TUNEKP" in str(sys.argv):
       BPV_list = eval(config_data['torqueBPV'])
       KpKi_list = eval(config_data['pidKpKi'])
       print ("\n  New tune set!\n    " + str(BPV_list) + "\n    " + str(KpKi_list) + "\n")
###############################################################################################
  except KeyError:
    print ("\x1b[1;31m\n  Missing torqueBP, torqueV, kpV, kiV sets, make sure engine is")
    print ("    running so keys will be generated\n\x1b[0m")
###############################################################################################


######################################################################################################################
  with open('/data/autotuner.tmp', 'w', encoding='utf8') as file:                                      # UPDATE JSON #
    json.dump(config_data, file, indent=2, sort_keys=True, separators=(',', ': '), ensure_ascii=False) ###############
    file.flush()
  shutil.move("/data/autotuner.tmp", "/data/autotuner.json") #change it as main config file
######################################################################################################################
######################################################################################################################

