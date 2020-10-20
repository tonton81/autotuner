#!/bin/bash


if [ ! -z "$1" ] && [ $1 == "RESET" ]
  then
    python autotuner_config.py $@
    sync
    printf "\n\n  Dictionary cleared. Rebooting to clear cache OP uses when entries are not set.\n"
    printf "  New keys will be generated from openpilot and automatically imported with the\n"
    printf "    default values, make sure your car is detected so keys can be generated\n"
    printf "\n  Rebooting...\n\n"
    reboot
fi



if [ -f /data/autotuner.json ] #remove stale queues after RESET
  then
    if ( grep -q "reset_defaults" /data/autotuner.json )
      then
        rm autotuner.json 2>/dev/nul
        rm /data/autotuner/queues/*.queue 2>/dev/nul
    fi
fi



#first, we append queued dictionary entries to main configuration (if any)
for filename in /data/autotuner/queues/*.queue
do
  if [ -f $filename ]
    then
      printf "New key added:"
      cat $filename | sed -n '2 p'
      python autotuner_config.py "BASH_NEW_QUEUE" $filename
      rm $filename
  fi
done



# make sure necessary files are patched
patchCounter=0

if ( ! grep -Fxq "from autotuner_config import autotuner_config" /data/openpilot/selfdrive/car/honda/carcontroller.py )
  then
    sed -i -e '2i\' -e "autotuner_config = autotuner_config()" /data/openpilot/selfdrive/car/honda/carcontroller.py
    sed -i -e '2i\' -e "from autotuner_config import autotuner_config" /data/openpilot/selfdrive/car/honda/carcontroller.py
    sed -i -e '2i\' -e "sys.path.append(\"/data/\")" /data/openpilot/selfdrive/car/honda/carcontroller.py
    sed -i -e '2i\' -e "import sys" /data/openpilot/selfdrive/car/honda/carcontroller.py
    sed -i -e '2i\' -e "import json" /data/openpilot/selfdrive/car/honda/carcontroller.py

    sed -i '/P \= self.params/i \    BPV = "[" + str(CS.CP.lateralParams.torqueBP) + ", " + str(CS.CP.lateralParams.torqueV) + "]"' /data/openpilot/selfdrive/car/honda/carcontroller.py
    sed -i '/P \= self.params/i \    KpKi = "[" + str(CS.CP.lateralTuning.pid.kpV) + ", " + str(CS.CP.lateralTuning.pid.kiV) + "]"' /data/openpilot/selfdrive/car/honda/carcontroller.py
    sed -i '/P \= self.params/i \    tunedBP, tunedV = eval(autotuner_config.get("torqueBPV", BPV))' /data/openpilot/selfdrive/car/honda/carcontroller.py
    sed -i '/P \= self.params/i \    self.params.STEER_MAX = tunedBP[-1]' /data/openpilot/selfdrive/car/honda/carcontroller.py
    sed -i '/P \= self.params/i \    self.params.STEER_LOOKUP_BP = [v * -1 for v in tunedBP][1:][::-1] + list(tunedBP)' /data/openpilot/selfdrive/car/honda/carcontroller.py
    sed -i '/P \= self.params/i \    self.params.STEER_LOOKUP_V = [v * -1 for v in tunedV][1:][::-1] + list(tunedV)' /data/openpilot/selfdrive/car/honda/carcontroller.py

    echo "Patched carcontroller.py"
    ((patchCounter+=1))
fi



if ( ! grep -Fxq "from autotuner_config import autotuner_config" /data/openpilot/selfdrive/controls/lib/latcontrol_pid.py )
  then
    sed -i -e '2i\' -e "autotuner_config = autotuner_config()" /data/openpilot/selfdrive/controls/lib/latcontrol_pid.py
    sed -i -e '2i\' -e "from autotuner_config import autotuner_config" /data/openpilot/selfdrive/controls/lib/latcontrol_pid.py
    sed -i -e '2i\' -e "sys.path.append(\"/data/\")" /data/openpilot/selfdrive/controls/lib/latcontrol_pid.py
    sed -i -e '2i\' -e "import sys" /data/openpilot/selfdrive/controls/lib/latcontrol_pid.py
    sed -i -e '2i\' -e "import json" /data/openpilot/selfdrive/controls/lib/latcontrol_pid.py

    sed -i '/pid_log \= log*/i \    BPV = "[" + str(CP.lateralParams.torqueBP) + ", " + str(CP.lateralParams.torqueV) + "]"' /data/openpilot/selfdrive/controls/lib/latcontrol_pid.py
    sed -i '/pid_log \= log*/i \    KpKi = "[" + str(CP.lateralTuning.pid.kpV) + ", " + str(CP.lateralTuning.pid.kiV) + "]"' /data/openpilot/selfdrive/controls/lib/latcontrol_pid.py
    sed -i '/pid_log \= log*/i \    CP.lateralParams.torqueBP, CP.lateralParams.torqueV = eval(autotuner_config.get("torqueBPV", BPV))' /data/openpilot/selfdrive/controls/lib/latcontrol_pid.py
    sed -i '/pid_log \= log*/i \    CP.lateralTuning.pid.kpV, CP.lateralTuning.pid.kiV = eval(autotuner_config.get("pidKpKi", KpKi))' /data/openpilot/selfdrive/controls/lib/latcontrol_pid.py
    sed -i '/pid_log \= log*/i \    self.pid = PIController((CP.lateralTuning.pid.kpBP, CP.lateralTuning.pid.kpV),' /data/openpilot/selfdrive/controls/lib/latcontrol_pid.py
    sed -i '/pid_log \= log*/i \                            (CP.lateralTuning.pid.kiBP, CP.lateralTuning.pid.kiV),' /data/openpilot/selfdrive/controls/lib/latcontrol_pid.py
    sed -i '/pid_log \= log*/i \                            k_f=CP.lateralTuning.pid.kf, pos_limit=1.0, neg_limit=-1.0,' /data/openpilot/selfdrive/controls/lib/latcontrol_pid.py
    sed -i '/pid_log \= log*/i \                            sat_limit=CP.steerLimitTimer)' /data/openpilot/selfdrive/controls/lib/latcontrol_pid.py

    echo "Patched latcontrol_pid.py"
    ((patchCounter+=1))
fi

if [ $patchCounter != 0 ]
  then
    echo "Patches complete! Rebooting..."
    reboot
fi



#Let's pass all further arguments to python

if [ ! -z "$1" ]
  then
    python autotuner_config.py $@
fi
