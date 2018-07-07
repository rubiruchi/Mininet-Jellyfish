#!/usr/bin/python

from functools import partial
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import set1LogLevel
from mininet.net import Mininet
from mininet.node import OVSKernelSwitch
from mininet.node import RemoteController
from mininet.topo import Topo
from mininet.util import dumpNodeConnections


class MyNet( Topo ):    
    def __init__( self ):
        "Create custom topo."

        # Initialize topology
        Topo.__init__( self )

        # Add hosts
        h1 = self.addHost( 'h1' )
        h2 = self.addHost( 'h2' )
	      
    	# Add switches
        s1 = self.addSwitch( 's1' )
	   
        # Add links
        self.addLink( s1, h1 ,bw=1)
        self.addLink( s1, h2 ,bw=1)
        

topos = { 'MyNet': ( lambda: MyNet() ) }
