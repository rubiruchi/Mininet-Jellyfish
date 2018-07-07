#!/usr/bin/python
from random import choice
import os
import signal
import time as systime

if __name__ == '__main__':
	INPUT = int(input('input switches set: '))
	EXCLUDES = int( input('excludes a set of switches: '))
	sizes = [3, 5]

	try:	
		while True:
			host = choice([i for i in range(1,INPUT) if i not in [EXCLUDES]])
			cmd = "ping -c "+str(choice(sizes))+" 10.0."+str(host)+"."+str(host)+">> /home/floodlight/Desktop/script/RTT_TEST.txt" 
			print 'system input: ' + cmd	
			os.system(cmd)
			systime.sleep(0.5)
	except KeyboardInterrupt:
	    print('interrupted!')
