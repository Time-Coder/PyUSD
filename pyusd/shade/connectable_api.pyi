from ..api_schema_base import APISchemaBase
from .info import Info
from .outputs import Outputs


class ConnectableAPI(APISchemaBase):
    """UsdShadeConnectableAPI is an API schema that provides a common
    interface for creating outputs and making connections between shading 
    parameters and outputs. The interface is common to all UsdShade schemas
    that support Inputs and Outputs, which currently includes UsdShadeShader,
    UsdShadeNodeGraph, and UsdShadeMaterial .
    
    One can construct a UsdShadeConnectableAPI directly from a UsdPrim, or
    from objects of any of the schema classes listed above.  If it seems
    onerous to need to construct a secondary schema object to interact with
    Inputs and Outputs, keep in mind that any function whose purpose is either
    to walk material/shader networks via their connections, or to create such
    networks, can typically be written entirely in terms of 
    UsdShadeConnectableAPI objects, without needing to care what the underlying
    prim type is.
    
    Additionally, the most common UsdShadeConnectableAPI behaviors
    (creating Inputs and Outputs, and making connections) are wrapped as
    convenience methods on the prim schema classes (creation) and 
    UsdShadeInput and UsdShadeOutput.
    
    """

