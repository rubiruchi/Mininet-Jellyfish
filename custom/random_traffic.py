#!/usr/bin/python
from random import choice
import os
import signal
import time as systime

if __name__ == '__main__':
	INPUT = int(input('input switches set: '))
	#EXCLUDES = list(map(int, raw_input('excludes a set of switches: ').split()))
	EXCLUDES = int( input('excludes a set of switches: '))
	sizes = [ 100 ]
	time = [ 5, 10, 20, 30 ]

	try:	
		while True:
			systime.sleep(1)
			host = choice([i for i in range(1,INPUT) if i not in [EXCLUDES]])
			#os.system('iperf -c 10.0.0.4 -u -b 100M -t 6 -p 5566')
			cmd = "iperf -c 10.0."+str(host)+"."+str(host)+" -u -b "+str(choice(sizes))+"M"+" -t "+str(choice(time))+" -p 5566" 
			print 'system input: ' + cmd			
			os.system(cmd)	
	except KeyboardInterrupt:
	    print('interrupted!')

#cmd = "iperf -c 10.0.0."+str(host)+" -u -b "+str(choice(sizes))+"M"+" -t "+str(choice(time))+" -p 5566 >> /home/floodlight/Desktop/script/tmp.txt"
