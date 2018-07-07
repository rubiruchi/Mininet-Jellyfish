import fnss

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
from mininet.node import OVSController

class mininet.topo import topo 

class customTopo(Topo):

  def __init__(self, linkopts1, linkopts2, linkopts3, fanout=2, **opts):
        Topo.__init__(self, **opts)

topos = { 'custom': ( lambda: CustomTopo() ) }
