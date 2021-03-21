import shutil
import os

def find_file(name, path):
    for root, dirs, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)

def find_all(name, path):
    result = []
    for root, dirs, files in os.walk(path):
        if name in files:
            result.append(os.path.join(root, name))
    return result

import os, fnmatch
def find_pattern(pattern, path):
    result = []
    for root, dirs, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result.append(os.path.join(root, name))
    return result




manager_file = find_file('manager.py', '/data/openpilot')
with open (manager_file.replace(".py", ".bak"), 'w') as manager_py_write:
    with open (manager_file, 'r') as manager_py_read:
        for line in manager_py_read:
            if "\"uploader\":" in line and "#" != line[0]:
                manager_py_write.write("#" + line)
            elif "\"loggerd\":" in line and "#" != line[0]:
                manager_py_write.write("#" + line)
            elif "\"logmessaged\":" in line and "#" != line[0]:
                manager_py_write.write("#" + line)
            elif "\"logcatd\":" in line and "#" != line[0]:
                manager_py_write.write("#" + line)
            elif "\"proclogd\":" in line and "#" != line[0]:
                manager_py_write.write("#" + line)
            elif "\"updated\":" in line and "#" != line[0]:
                manager_py_write.write("#" + line)
            elif "\"manage_athenad\":" in line and "#" != line[0]:
                manager_py_write.write("#" + line)
            elif "'logmessaged'," in line and "#" != line[0]:
                manager_py_write.write("#" + line)
            elif "'uploader'," in line and "#" != line[0]:
                manager_py_write.write("#" + line)
            elif "'updated'," in line and "#" != line[0]:
                manager_py_write.write("#" + line)
            elif "'loggerd'," in line and "#" != line[0]:
                manager_py_write.write("#" + line)
            elif "'proclogd'," in line and "#" != line[0]:
                manager_py_write.write("#" + line)
            elif "'logcatd'," in line and "#" != line[0]:
                manager_py_write.write("#" + line)
            elif "bootlog" in line and "subprocess.call" in line and "#" != line[0]:
                manager_py_write.write("#" + line)
            else:
                manager_py_write.write(line)
    shutil.move(manager_file.replace(".py", ".bak"), manager_file)
os.chmod(manager_file, 0o0777)
