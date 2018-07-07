#!/usr/bin/python

"""
Test bandwidth (using iperf) on linear networks of varying size,
using both kernel and user datapaths.
Use Dichotomy to evaluate the max bandwidth usable without loosing any packet.

Look to the result in stats.txt file produced which contains 3 cols with:
1: the number of nodes,
2: the bandwidth in Mbps
3: the number of packets exchanged during the exp (10 secondes).

We construct a network of N hosts and N-1 switches, connected as follows:

h1 <-> s1 <-> s2 .. sN-1
       |       |    |
       h2      h3   hN

WARNING: by default, the reference controller only supports 16
switches, so this test WILL NOT WORK unless you have recompiled
your controller to support 100 switches (or more.)

In addition to testing the bandwidth across varying numbers
of switches, this example demonstrates:

- creating a custom topology, LinearTestTopo
- using the ping() and iperf() tests from Mininet()
- testing both the kernel and user switches

"""
import time
from mininet.net import Mininet
from mininet.node import UserSwitch, OVSKernelSwitch
from mininet.topo import Topo
from mininet.log import lg
from mininet.util import irange
from time import sleep
from mininet.link import TCLink
from mininet.node import CPULimitedHost
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel

import sys
flush = sys.stdout.flush

def GetLastPPS(fichier):
    fp = open (fichier, "r")
    for l in fp.readlines ():
        list_values = l.split ()
        bw = list_values[0]
        nodes = list_values[1]
        packets = list_values[2]
    fp.close ()
#    print "Dernier bw=",bw," nodes=",nodes," packets=",packets
    return int (packets)

# Extract the number of packets returned by the execution of udp-perf

class LinearTestTopo( Topo ):
    "Topology for a string of N hosts and N-1 switches."

    def __init__( self, N, bw, **params ):

        # Initialize topology
        Topo.__init__( self, **params )

        # Create switches and hosts
        hosts = [ self.addHost( 'h%s' % h )
                  for h in irange( 1, N ) ]
        switches = [ self.addSwitch( 's%s' % s )
                     for s in irange( 1, N - 1 ) ]

        # Wire up switches
        last = None
        for switch in switches:
            if last:
                self.addLink( last, switch, 
                              bw=bw, delay='1ns', loss=0, use_htb=True)
            last = switch

        # Wire up hosts
        self.addLink( hosts[ 0 ], switches[ 0 ], 
                      bw=bw, delay='1ms', loss=0, use_htb=True)
        for host, switch in zip( hosts[ 1: ], switches ):
            self.addLink( host, switch, 
                          bw=bw, delay='1ms', loss=0, use_htb=True)

# use Dichotomy to evaluate the max bandwidth usable without loosing any packet.
def linearBandwidthTest( nodes, band, num ):

    results = {}

#    nodes = switchCount + hostCount
    switchCount = (nodes / 2) - 1
    hostCount = switchCount + 1

    switches = { 'reference user': UserSwitch}
#    switches = { 'Open vSwitch kernel': OVSKernelSwitch }
    datapath = 'reference user'
#    datapath = 'Open vSwitch kernel'
    Switch = UserSwitch

# Variables for dichotomy
    bw = band  # Actual bandwidth
    maxOk = 0  # Maximum bw without loose
    minKo = 0  # Minimum BW with loose
    running = 1  # loop condition
    packets = 0  # last packets received by the server
    newbw = bw   # new bandwidth to test

    topo = LinearTestTopo( hostCount, bw )
    net = Mininet( topo=topo, switch=Switch , link=TCLink)
    net.start()
    n = switchCount
    src, dst = net.hosts[ 0 ], net.hosts[ n ]
    print "testing", src.name,"(",src.IP(),") <->", dst.name,"(",dst.IP(),")"
    print ('sleeping:',str(nodes))
    # sleep in function of the number of the nodes to let the processes to start well...
    sleep (nodes)
    #print "-------------------------------- start time:",src.cmd('date')
    IPERFPATH = '/home/epmancini/dce-tests/tests/build/bin/iperf'
    #IPERFPATH = 'iperf'
    start_time = time.time()
    src.cmd( IPERFPATH + '  -s -P 1 -u > s.txt &')
    dst.cmd( IPERFPATH + ' -c '+src.IP()+'  -u -n 100000000 -b 500m > c.txt &')
    #dst.cmd( IPERFPATH + ' -c '+src.IP()+'  -u -b 500m > c.txt &')

    #dst.cmd( IPERFPATH + ' -c '+src.IP()+'  --time 10 -u > c.txt &')
    #dst.cmd('./udp-perf --client --bandwidth='+str(bw*1000000)+' --nodes='+str(nodes)+' --duration=10 --host='+src.IP()+' >c.txt &')
    #print "started. Waiting"
    src.cmd('wait %'+IPERFPATH)
    dst.cmd('wait %'+IPERFPATH)
    elapsed_time = time.time() - start_time
    print "Elapsed time time:", elapsed_time, " nodes:", nodes
    #sleep (15)
    #print "------------------------------ stop time:",src.cmd('date')
    net.stop()
    del net
    del topo
    running = 0
    #ackets = GetLastPPS("server.txt")
    print ('sleeping:',str(5)) # str(nodes))
    sleep (5) #nodes)
        
    print
    # write the result in the stats.txt file.
    return packets




if __name__ == '__main__':

    lg.setLogLevel( 'info' )
    argc = len(sys.argv)
    bw = 1.0
    num = 0
    precision = 1.0
    if (argc<4):
        nodes = 8
	bw = 20000
	num = 1
    else:
        nodes = int(sys.argv[1])
        bw = float(sys.argv[2])
    	num = int(sys.argv[3])        
    #precision = float(sys.argv[4]) 
    p  = linearBandwidthTest( nodes, bw , num )
    print "nodes:",nodes," packets: ",p


