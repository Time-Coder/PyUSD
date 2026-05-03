from ..boundable import Boundable
from ..attribute import Attribute
from typing import List
from ..dtypes import token
from ..common import SchemaKind


class GenerativeProcedural(Boundable):
    """
    Represents an abstract generative procedural prim which delivers its input
    parameters via properties (including relationships) within the "primvars:"
    namespace.
 
    It does not itself have any awareness or participation in the execution of
    the procedural but rather serves as a means of delivering a procedural's
    definition and input parameters.
 
    The value of its "proceduralSystem" property (either authored or provided
    by API schema fallback) indicates to which system the procedural definition
    is meaningful.
    """
    schema_kind: SchemaKind = SchemaKind.ConcreteTyped

    proceduralSystem: Attribute[token] = Attribute(token,
        doc=
        """The name or convention of the system responsible for evaluating
        the procedural.
        NOTE: A fallback value for this is typically set via an API schema.
        """
    )
