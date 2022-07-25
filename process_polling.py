#!/usr/bin/python3
import subprocess

while(True):
    all_process = subprocess.check_output(['ps', '-ef']).decode('utf-8').split('\n')
    for x in all_process:
        p = x.lower()
        #if r"/opt/microsoft/mdatp/sbin/sensecm" in p:
        if "sensecm" in p:
            print(x)
            exit(0);
