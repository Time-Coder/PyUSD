from ..typed import Typed
from .info import Info
from .outputs import Outputs


class NodeGraph(Typed):
    """A node-graph is a container for shading nodes, as well as other 
    node-graphs. It has a public input interface and provides a list of public 
    outputs.
    
    <b>Node Graph Interfaces</b>
    
    One of the most important functions of a node-graph is to host the "interface"
    with which clients of already-built shading networks will interact.  Please
    see \\ref UsdShadeNodeGraph_Interfaces "Interface Inputs" for a detailed
    explanation of what the interface provides, and how to construct and
    use it, to effectively share/instance shader networks.
    
    <b>Node Graph Outputs</b>
    
    These behave like outputs on a shader and are typically connected to an 
    output on a shader inside the node-graph.
    
    """

