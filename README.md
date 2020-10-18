New tuning script for openpilot, early stages.

Features:

* Patches required files, not fork dependant. Patching requires reboot to take effect. Any patches are followed by automatic reboot.
* Automatically stores keys that don't exist, while falling back to default stock values in openpilot.
* Atomic writes done by bash, openpilot is not allowed to write, except queues
* Automatic keys are generated if not in the json, and OP stores them as individual key queues.
    When the 'bash autotuner.sh' detects new key queues, it services them to the json file.
* Deleting the json accidentally, openpilot will regenerate new queues immediately for the respective keys, and 'autotuner.sh' will
    re-fill the new json with those entries. Any time the key doesn't appear inside the json, openpilot uses the default (on boot)
    or last one (when deleted) to continue operation. This makes json file manipulation streamlined.


Installation:
```rm -rf /data/autotuner/; git clone https://github.com/tonton81/autotuner.git /data/autotuner; bash /data/autotuner/install.sh```

The first time you run ```bash /data/autotuner.sh``` it will patch the necessary files then reboot automatically.
Make sure comma is installed in the car and the car is detected. This will generate new entries automatically for the json file.

Tunes: (1 currently)

* This tune can take an input of Kp, and compute BP and Ki from it. The changes are live.
  Usage: ```bash autotuner.sh TUNEKP 0.15```
  This will configure BP to 20480, and Ki to 0.5. The changes will be made live as the json is updated.
