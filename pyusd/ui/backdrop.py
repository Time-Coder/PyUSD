from ..typed import Typed
from ..attribute import Attribute
from ..dtypes import namespace
from ..dtypes import token
from ..common import SchemaKind


class Backdrop(Typed):
    """Provides a 'group-box' for the purpose of node graph organization.
    
    Unlike containers, backdrops do not store the Shader nodes inside of them.
    Backdrops are an organizational tool that allows Shader nodes to be visually 
    grouped together in a node-graph UI, but there is no direct relationship 
    between a Shader node and a Backdrop. 
    
    The guideline for a node-graph UI is that a Shader node is considered part 
    of a Backdrop when the Backdrop is the smallest Backdrop a Shader node's 
    bounding-box fits inside.
    
    Backdrop objects are contained inside a NodeGraph, similar to how Shader 
    objects are contained inside a NodeGraph.
    
    Backdrops have no shading inputs or outputs that influence the rendered
    results of a NodeGraph. Therefore they can be safely ignored during import.
    
    Like Shaders and NodeGraphs, Backdrops subscribe to the NodeGraphNodeAPI to 
    specify position and size.
    
    """

    schema_kind: SchemaKind = SchemaKind.ConcreteTyped

    ui: Attribute[namespace] = Attribute(namespace, is_leaf=False)
    ui.description = Attribute(token,
        uniform=True,
        doc="""The text label that is displayed on the backdrop in the node
        graph. This help-description explains what the nodes in a backdrop do.

        """,
        metadata={
            "customData": {
                "apiName": "description"
            }
        }
    )
