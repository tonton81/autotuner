#!/bin/bash
#####################################################################################################################################################################
##### IN THIS RESET, THE JSON IS CLEARED, COMMA REBOOTS, AND OPENPILOT SETS CAR SPECIFIC DEFAULT VALUES AS WELL AS NEW KEYS ARE GENERATED FOR JSON AUTOMATICALLY ####
#####################################################################################################################################################################
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
#####################################################################################################################################################################
##### OPENPILOT GENERATES MISSING KEYS AUTOMATICALLY WITH CAR SPECIFIC DEFAULTS. WHILE DICTIONARY IS NOT SET, OPENPILOT WILL USE DEFAULT CONFIGURATION ##############
#####################################################################################################################################################################
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
#####################################################################################################################################################################
##### PATCH INCLUDES ################################################################################################################################################
#####################################################################################################################################################################
patchCounter=0
for f in /data/openpilot/selfdrive/car/honda/carcontroller.py \
         /data/openpilot/selfdrive/controls/lib/latcontrol_pid.py \
         /data/openpilot/selfdrive/controls/lib/pid.py \
         /data/openpilot/selfdrive/controls/lib/pathplanner.py \
         /data/openpilot/selfdrive/controls/lib/lateral_planner.py
do
  if [ -f $f ]
    then
      if ( ! grep -Fxq "from autotuner_config import autotuner_config" $f )
        then
          sed -i -e '2i\' -e "autotuner_config = autotuner_config()" $f
          sed -i -e '2i\' -e "from autotuner_config import autotuner_config" $f
          sed -i -e '2i\' -e "sys.path.append(\"/data/\")" $f
          sed -i -e '2i\' -e "import sys" $f
          printf "Patched file: %s\n" "$f"
          ((patchCounter+=1))
      fi
  fi
done
#####################################################################################################################################################################
##### PATCH BP/V/Ki/Kp ##############################################################################################################################################
#####################################################################################################################################################################
if ( ! grep -Fq "CP.lateralTuning.pid.kiV = eval(autotuner_config.get" /data/openpilot/selfdrive/controls/lib/latcontrol_pid.py )
  then
    sed -i '/def update(self/a \                            sat_limit=CP.steerLimitTimer)' /data/openpilot/selfdrive/controls/lib/latcontrol_pid.py
    sed -i '/def update(self/a \                            k_f=CP.lateralTuning.pid.kf, pos_limit=1.0, neg_limit=-1.0,' /data/openpilot/selfdrive/controls/lib/latcontrol_pid.py
    sed -i '/def update(self/a \                            (CP.lateralTuning.pid.kiBP, CP.lateralTuning.pid.kiV),' /data/openpilot/selfdrive/controls/lib/latcontrol_pid.py
    sed -i '/def update(self/a \    self.pid = PIController((CP.lateralTuning.pid.kpBP, CP.lateralTuning.pid.kpV),' /data/openpilot/selfdrive/controls/lib/latcontrol_pid.py
    sed -i '/def update(self/a \    CP.lateralTuning.pid.kpV, CP.lateralTuning.pid.kiV = eval(autotuner_config.get("pidKpKi", KpKi))' /data/openpilot/selfdrive/controls/lib/latcontrol_pid.py
    sed -i '/def update(self/a \    CP.lateralParams.torqueBP, CP.lateralParams.torqueV = eval(autotuner_config.get("torqueBPV", BPV))' /data/openpilot/selfdrive/controls/lib/latcontrol_pid.py
    sed -i '/def update(self/a \    KpKi = "[" + str(CP.lateralTuning.pid.kpV) + ", " + str(CP.lateralTuning.pid.kiV) + "]"' /data/openpilot/selfdrive/controls/lib/latcontrol_pid.py
    sed -i '/def update(self/a \    BPV = "[" + str(CP.lateralParams.torqueBP) + ", " + str(CP.lateralParams.torqueV) + "]"' /data/openpilot/selfdrive/controls/lib/latcontrol_pid.py
    ((patchCounter+=1))
fi
if ( ! grep -Fq "tunedV = eval(autotuner_config.get(" /data/openpilot/selfdrive/car/honda/carcontroller.py )
  then
    sed -i '/P \= self.params/i \    BPV = "[" + str(CS.CP.lateralParams.torqueBP) + ", " + str(CS.CP.lateralParams.torqueV) + "]"' /data/openpilot/selfdrive/car/honda/carcontroller.py
    sed -i '/P \= self.params/i \    KpKi = "[" + str(CS.CP.lateralTuning.pid.kpV) + ", " + str(CS.CP.lateralTuning.pid.kiV) + "]"' /data/openpilot/selfdrive/car/honda/carcontroller.py
    sed -i '/P \= self.params/i \    tunedBP, tunedV = eval(autotuner_config.get("torqueBPV", BPV))' /data/openpilot/selfdrive/car/honda/carcontroller.py
    sed -i '/P \= self.params/i \    self.params.STEER_MAX = tunedBP[-1]' /data/openpilot/selfdrive/car/honda/carcontroller.py
    sed -i '/P \= self.params/i \    self.params.STEER_LOOKUP_BP = [v * -1 for v in tunedBP][1:][::-1] + list(tunedBP)' /data/openpilot/selfdrive/car/honda/carcontroller.py
    sed -i '/P \= self.params/i \    self.params.STEER_LOOKUP_V = [v * -1 for v in tunedV][1:][::-1] + list(tunedV)' /data/openpilot/selfdrive/car/honda/carcontroller.py
    ((patchCounter+=1))
fi
if ( ! grep -Fq "self.prev_act = 0." /data/openpilot/selfdrive/car/honda/carcontroller.py )
  then
    sed -i '/def __init__/a \    self.prev_act = 0.' /data/openpilot/selfdrive/car/honda/carcontroller.py
    sed -i '/hud_car = 0/a \      self.prev_act = actuators.steer' /data/openpilot/selfdrive/car/honda/carcontroller.py
    sed -i '/\*\*\*\* process the car messages \*\*\*\*/a \      self.prev_act = actuators.steer' /data/openpilot/selfdrive/car/honda/carcontroller.py
    sed -i '/\*\*\*\* process the car messages \*\*\*\*/a \    else:' /data/openpilot/selfdrive/car/honda/carcontroller.py
    sed -i '/\*\*\*\* process the car messages \*\*\*\*/a \      self.prev_act = self.prev_act + percent_limit' /data/openpilot/selfdrive/car/honda/carcontroller.py
    sed -i '/\*\*\*\* process the car messages \*\*\*\*/a \    elif actuators.steer > (self.prev_act + percent_limit):' /data/openpilot/selfdrive/car/honda/carcontroller.py
    sed -i '/\*\*\*\* process the car messages \*\*\*\*/a \      self.prev_act = self.prev_act - percent_limit' /data/openpilot/selfdrive/car/honda/carcontroller.py
    sed -i '/\*\*\*\* process the car messages \*\*\*\*/a \    if actuators.steer < (self.prev_act - percent_limit):' /data/openpilot/selfdrive/car/honda/carcontroller.py
    sed -i '/\*\*\*\* process the car messages \*\*\*\*/a \    percent_limit = float(format(eval(autotuner_config.get("actuator_steer_percent_limit", str(format(0.02, ".8f")))), "0.8f"))' /data/openpilot/selfdrive/car/honda/carcontroller.py
    sed -i 's/apply_steer = .*/apply_steer = int(interp(-self.prev_act * P.STEER_MAX, P.STEER_LOOKUP_BP, P.STEER_LOOKUP_V))/g' /data/openpilot/selfdrive/car/honda/carcontroller.py
    ((patchCounter+=1))
else
  if ( ! grep -Fq "actuator_steer_percent_limit" /data/openpilot/selfdrive/car/honda/carcontroller.py )
    then
      sed -i 's/percent_limit = .*/percent_limit = float(format(eval(autotuner_config.get("actuator_steer_percent_limit", str(format(0.02, ".8f")))), "0.8f"))/g' /data/openpilot/selfdrive/car/honda/carcontroller.py
      ((patchCounter+=1))
  fi
fi
#####################################################################################################################################################################
##### PATCH KF ######################################################################################################################################################
#####################################################################################################################################################################
if ( ! grep -Fq "self.k_f = float(format(eval(autotuner_config.get" /data/openpilot/selfdrive/controls/lib/pid.py )
  then
    sed -i '/def update(self/a \    self.k_f = float(format(eval(autotuner_config.get("kf", str(format(self.k_f, ".8f")))), ".8f"))' /data/openpilot/selfdrive/controls/lib/pid.py
    ((patchCounter+=1))
fi
if ( ! grep -Fq "CP.lateralTuning.pid.kf = float(format(eval(autotuner_config.get" /data/openpilot/selfdrive/controls/lib/latcontrol_pid.py )
  then
    sed -i '/def update(self/a \    CP.lateralTuning.pid.kf = float(format(eval(autotuner_config.get("kf", str(format(CP.lateralTuning.pid.kf, ".8f")))), ".8f"))' /data/openpilot/selfdrive/controls/lib/latcontrol_pid.py
    ((patchCounter+=1))
fi
#####################################################################################################################################################################
##### PATCH STEER RATIO #############################################################################################################################################
#####################################################################################################################################################################
if ( ! grep -Fq "CP.steerRatio = float(format(eval(autotuner_config.get" /data/openpilot/selfdrive/controls/lib/latcontrol_pid.py )
  then
    sed -i '/def update(self/a \    CP.steerRatio = float(format(eval(autotuner_config.get("steer_ratio", str(format(CP.steerRatio, ".8f")))), ".8f"))' /data/openpilot/selfdrive/controls/lib/latcontrol_pid.py
    ((patchCounter+=1))
fi
#####################################################################################################################################################################
##### PATCH STEER_RATE_COST #########################################################################################################################################
#####################################################################################################################################################################
if ( ! grep -Fq "CP.steerRateCost = float(format(eval(autotuner_config.get" /data/openpilot/selfdrive/controls/lib/latcontrol_pid.py )
  then
    sed -i '/def update(self/a \    CP.steerRateCost = float(format(eval(autotuner_config.get("steer_rate_cost", str(format(CP.steerRateCost, ".8f")))), ".8f"))' /data/openpilot/selfdrive/controls/lib/latcontrol_pid.py
    echo "UPDATED!!!!!!!!!!!!!!!!!"
    ((patchCounter+=1))
fi
#####################################################################################################################################################################
##### PATCH LANE_CHANGE_SPEED & TIME ################################################################################################################################
#####################################################################################################################################################################
if [ -f /data/openpilot/selfdrive/controls/lib/pathplanner.py ]
  then
    pathplanner='/data/openpilot/selfdrive/controls/lib/pathplanner.py'
fi
if [ -f /data/openpilot/selfdrive/controls/lib/lateral_planner.py ]
  then
    pathplanner='/data/openpilot/selfdrive/controls/lib/lateral_planner.py'
fi

if ( ! grep -Fq "LANE_CHANGE_SPEED_MIN = int(eval(autotuner_config.get" ${pathplanner} )
  then
    sed -i 's/LANE_CHANGE_SPEED_MIN = .*/LANE_CHANGE_SPEED_MIN = int(eval(autotuner_config.get("lane_change_speed", str(45)))) * CV.MPH_TO_MS/g' ${pathplanner}
    sed -i 's/LANE_CHANGE_TIME_MAX = .*/LANE_CHANGE_TIME_MAX = int(eval(autotuner_config.get("lane_change_time_max", str(10))))/g' ${pathplanner}
    ((patchCounter+=1))
fi
#####################################################################################################################################################################
##### REBOOT IF ANY PATCHES WERE MADE ###############################################################################################################################
#####################################################################################################################################################################
if [ $patchCounter != 0 ]
  then
    echo "Patches complete! Rebooting..."
    reboot
fi
#####################################################################################################################################################################
##### SEND REMAINING ARGUMENTS TO PYTHON SCRIPT FOR PROCESSING ######################################################################################################
#####################################################################################################################################################################
if [ ! -z "$1" ]
  then
    python autotuner_config.py $@
fi
