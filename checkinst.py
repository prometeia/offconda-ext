import subprocess
import sys
import re


found = ''
with open("Jenkinsfile") as jfile:
    for row in jfile:
        if 'defaultValue' in row:
            found = row.split("'")[1]
            break
assert found, "Components not found in Jenkinsfile!"

print("Dry-run installation of {}".format(found))
cmd = "conda install --dry-run {}".format(found)
if len(sys.argv) >= 1:
    cmd += ' -c ' + ' '.join(sys.argv[1:])

done = subprocess.check_output(cmd)
for module, channel, packet in re.findall(r"\s+(\S+)\s+(prometeia/\S+)::(\S+)\s*", done.decode('ascii')):
    print("{:20s} {:40s} {:40s}".format(module, packet, '/'.join(channel.split('/')[:-1])))
