from ..api_schema_base import APISchemaBase
from ..attribute import Attribute
from ..dtypes import namespace
from ..gf import color3f, float2
from ..dtypes import asset, string, token
from ..common import SchemaKind


class NodeGraphNodeAPI(APISchemaBase):
    """
    This api helps storing information about nodes in node graphs.
    
    """

    schema_kind: SchemaKind = SchemaKind.NonAppliedAPI

    class ExpansionState(token):
        Open = "open"
        Closed = "closed"
        Minimized = "minimized"


    ui: Attribute[namespace] = Attribute(namespace, is_leaf=False)
    ui.nodegraph.node.pos = Attribute(float2,
        uniform=True,
        doc="""
        Declared relative position to the parent in a node graph.
        X is the horizontal position.
        Y is the vertical position. Higher numbers correspond to lower positions 
        (coordinates are Qt style, not cartesian).

        These positions are not explicitly meant in pixel space, but rather
        assume that the size of a node is approximately 1.0x1.0. Where size-x is
        the node width and size-y height of the node. Depending on 
        graph UI implementation, the size of a node may vary in each direction.

        Example: If a node's width is 300 and it is position is at 1000, we
        store for x-position: 1000 * (1.0/300)

        """,
        metadata={
            "customData": {
                "apiName": "pos"
            }
        }
    )
    ui.nodegraph.node.stackingOrder = Attribute(int,
        uniform=True,
        doc="""
        This optional value is a useful hint when an application cares about 
        the visibility of a node and whether each node overlaps another.

        Nodes with lower stacking order values are meant to be drawn below 
        higher ones. Negative values are meant as background. Positive values
        are meant as foreground.
        Undefined values should be treated as 0. 

        There are no set limits in these values.

        """,
        metadata={
            "customData": {
                "apiName": "stackingOrder"
            }
        }
    )
    ui.nodegraph.node.displayColor = Attribute(color3f,
        uniform=True,
        doc="""
        This hint defines what tint the node should have in the node graph.

        """,
        metadata={
            "customData": {
                "apiName": "displayColor"
            }
        }
    )
    ui.nodegraph.node.icon = Attribute(asset,
        uniform=True,
        doc="""
        This points to an image that should be displayed on the node.  It is 
        intended to be useful for summary visual classification of nodes, rather
        than a thumbnail preview of the computed result of the node in some
        computational system.

        """,
        metadata={
            "customData": {
                "apiName": "icon"
            }
        }
    )
    ui.nodegraph.node.expansionState = Attribute(ExpansionState,
        uniform=True,
        doc=""" 
        The current expansionState of the node in the ui. 
        'open' = fully expanded
        'closed' = fully collapsed
        'minimized' = should take the least space possible

        """,
        metadata={
            "customData": {
                "apiName": "expansionState"
            }
        }
    )
    ui.nodegraph.node.size = Attribute(float2,
        uniform=True,
        doc="""
        Optional size hint for a node in a node graph.
        X is the width.
        Y is the height.

        This value is optional, because node size is often determined 
        based on the number of in- and outputs of a node.

        """,
        metadata={
            "customData": {
                "apiName": "size"
            }
        }
    )
    ui.nodegraph.node.docURI = Attribute(string,
        uniform=True,
        doc=""" 
        A URI pointing to additional detailed documentation for this 
        node or node type.

        """,
        metadata={
            "displayName": "Doc Link",
            "customData": {
                "apiName": "docURI"
            }
        }
    )
