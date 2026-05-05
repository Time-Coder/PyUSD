from ..attribute import Attribute
from ..relationship import Relationship
from ..gf import color3f, float2
from ..dtypes import asset, string, token
from typing import List


class Ui(Attribute):

    class ExpansionState(token):
        Open = "open"
        Closed = "closed"
        Minimized = "minimized"


    @property
    def pos(self)->Attribute[float2]:
        """
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
        """

    @pos.setter
    def pos(self, value:float2)->None: ...

    @property
    def stackingOrder(self)->Attribute[int]:
        """
        This optional value is a useful hint when an application cares about 
        the visibility of a node and whether each node overlaps another.
        
        Nodes with lower stacking order values are meant to be drawn below 
        higher ones. Negative values are meant as background. Positive values
        are meant as foreground.
        Undefined values should be treated as 0. 

        There are no set limits in these values.
        """

    @stackingOrder.setter
    def stackingOrder(self, value:int)->None: ...

    @property
    def displayColor(self)->Attribute[color3f]:
        """
        This hint defines what tint the node should have in the node graph.
        """

    @displayColor.setter
    def displayColor(self, value:color3f)->None: ...

    @property
    def icon(self)->Attribute[asset]:
        """
        This points to an image that should be displayed on the node.  It is 
        intended to be useful for summary visual classification of nodes, rather
        than a thumbnail preview of the computed result of the node in some
        computational system.
        """

    @icon.setter
    def icon(self, value:asset)->None: ...

    @property
    def expansionState(self)->Attribute[ExpansionState]:
        """ 
        The current expansionState of the node in the ui. 
        'open' = fully expanded
        'closed' = fully collapsed
        'minimized' = should take the least space possible
        """

    @expansionState.setter
    def expansionState(self, value:ExpansionState)->None: ...

    @property
    def size(self)->Attribute[float2]:
        """
        Optional size hint for a node in a node graph.
        X is the width.
        Y is the height.

        This value is optional, because node size is often determined 
        based on the number of in- and outputs of a node.
        """

    @size.setter
    def size(self, value:float2)->None: ...

    @property
    def docURI(self)->Attribute[string]:
        """ 
        A URI pointing to additional detailed documentation for this 
        node or node type.
        """

    @docURI.setter
    def docURI(self, value:string)->None: ...

    @property
    def displayName(self)->Attribute[token]:
        """When publishing a nodegraph or a material, it can be useful to
        provide an optional display name, for readability.
        """

    @displayName.setter
    def displayName(self, value:token)->None: ...

    @property
    def displayGroup(self)->Attribute[token]:
        """When publishing a nodegraph or a material, it can be useful to
        provide an optional display group, for organizational purposes and 
        readability. This is because often the usd shading hierarchy is rather
        flat while we want to display it in organized groups.
        """

    @displayGroup.setter
    def displayGroup(self, value:token)->None: ...

    @property
    def description(self)->Attribute[token]:
        """The text label that is displayed on the backdrop in the node
        graph. This help-description explains what the nodes in a backdrop do.
        """

    @description.setter
    def description(self, value:token)->None: ...
