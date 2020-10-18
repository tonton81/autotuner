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
        new_queue_file = "/data/" + str(key) + ".queue"  #also queue it in a separate file, to be processed via bash
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
      file.flush()
    shutil.move('/data/autotuner.tmp', '/data/autotuner.json') #change it as main config file




#BASH AREA: here we check for arguments (if any)
if len(sys.argv) > 1:
  autotuner_config = autotuner_config()


  if sys.argv[1] == "BASH_NEW_QUEUE": #append to our config file from queue
    autotuner_config.bash_new_queue(sys.argv[2])


  if sys.argv[1] == "COMPUTE_BP_KI_FROM_KP": #calculate BP based off Kp, and tune both BP and Ki proportionally
    with open('/data/autotuner.json', 'r') as file: #read our configuration
      config_data = json.loads(file.read())
    sys.argv[2] = (min(float(2), max(float(0), float(sys.argv[2]))))
    BPV_list = eval(config_data['torqueBPV'])
    KpKi_list = eval(config_data['pidKpKi'])
    BP_calc = float(BPV_list[1][2]) * 0.8 / float(sys.argv[2])
    Ki_calc = float(sys.argv[2]) / 3
    KpKi_list[0][0] = float(sys.argv[2]) #we store new Kp
    KpKi_list[1][0] = round(Ki_calc, 5) #we store new Ki
    BPV_list[0][2] = round(BP_calc) #we store new BP
    config_data['torqueBPV'] = str(BPV_list)
    config_data['pidKpKi'] = str(KpKi_list)
    with open('/data/autotuner.tmp', 'w', encoding='utf8') as file: #write new config to a temporary file
      json.dump(config_data, file, indent=2, sort_keys=True, separators=(',', ': '), ensure_ascii=False)
      file.flush()
    shutil.move('/data/autotuner.tmp', '/data/autotuner.json') #change it as main config file

