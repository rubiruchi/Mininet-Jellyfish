#!/usr/bin/python

from mininet.net import Mininet
from mininet.node import RemoteController,Host,Node
from mininet.cli import CLI
from mininet.log import setLogLevel, info

def emptyNet():

    net = Mininet( controller=RemoteController )

    info( '*** Adding controller\n' )
    net.addController( 'c0', 
                       controller=RemoteController, 
                       ip = "127.0.0.1", 
                       port=6653 )

    info( '*** Adding hosts\n' )
    #---------subnet1---------
    h1 = net.addHost( 'h1', 
                      ip='10.0.0.1', 
                      mac='00:00:00:00:00:01',
                      defaultRoute='via 10.0.0.254')
    h2 = net.addHost( 'h2', 
                      ip='10.0.0.2',
                      mac='00:00:00:00:00:02',
                      defaultRoute='via 10.0.0.254')
    
        
    info( '*** Adding switch\n' )
    s1 = net.addSwitch( 's1' )
    info( '*** Creating links\n' )
    #---------subnet1---------
    net.addLink( h1, s1 )
    net.addLink( h2, s1 )

    info( '*** Adding gateway\n')
    gateway = Host('gateway')

    net.addLink(s1, gateway)
    gateway.intf("gateway-eth0").setIP('10.0.0.254/24')
    
    info( '*** Starting network\n')
    net.start()

    info( '*** Running CLI\n' )
    CLI( net )

    info( '*** Stopping network' )
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    emptyNet()
