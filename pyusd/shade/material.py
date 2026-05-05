from .node_graph import NodeGraph
from ..attribute import Attribute
from ..dtypes import namespace
from ..dtypes import token
from ..common import SchemaKind


class Material(NodeGraph):
    """A Material provides a container into which multiple "render contexts"
    can add data that defines a "shading material" for a renderer. Typically 
    this consists of one or more UsdShadeOutput properties connected to outputs 
    of nested Shader prims - though a context/client is free to add
    any data that is suitable. We <b>strongly advise</b> that all contexts
    adopt the convention that all properties be prefixed with a namespace
    that identifies the context e.g. "token outputs:ri:surface.connect = 
    </MyselfMaterial/previewSurface.outputs:surface". 
    
    ## Binding Materials
    
    In the UsdShading model, geometry expresses a binding to a single Material or
    to a set of Materials partitioned by UsdGeomSubsets defined beneath the
    geometry; it is legal to bind a Material at the root (or other sub-prim) of 
    a model, and then bind a different Material to individual gprims, but the
    meaning of inheritance and "ancestral overriding" of Material bindings is 
    left to each render-target to determine.  Since UsdGeom has no concept of 
    shading, we provide the API for binding and unbinding geometry on the API 
    schema UsdShadeMaterialBindingAPI.
    
    ## Material Variation
    
    The entire power of USD VariantSets and all the other composition 
    operators can leveraged when encoding shading variation.  
    UsdShadeMaterial provides facilities for a particular way of building
    "Material variants" in which neither the identity of the Materials themselves
    nor the geometry Material-bindings need to change - instead we vary the
    targeted networks, interface values, and even parameter values within
    a single variantSet.  
    See \\ref UsdShadeMaterial_Variations "Authoring Material Variations" 
    for more details.
    
    ## Materials Encapsulate their Networks in Namespace
    
    UsdShade requires that all of the shaders that "belong" to the Material 
    live under the Material in namespace. This supports powerful, easy reuse
    of Materials, because it allows us to *reference* a Material from one
    asset (the asset might be a library of Materials) into another asset: USD 
    references compose all descendant prims of the reference target into the 
    referencer's namespace, which means that all of the referenced Material's 
    shader networks will come along with the Material. When referenced in this
    way, Materials can also be [instanced](http://openusd.org/docs/USD-Glossary.html#USDGlossary-Instancing), for ease of deduplication and compactness.
    Finally, Material encapsulation also allows us to 
    \\ref UsdShadeMaterial_BaseMaterial "specialize" child materials from 
    parent materials.
    
    For UsdShade schema domain any connectable child prim of UsdShadeMaterial 
    must be either UsdShadeShader derived or UsdShadeNodeGraph derived but not 
    UsdShadeMaterial, that is, UsdShadeMaterial can not be nested. It also must
    not contain any imageable prims as its descendants (UsdGeomScope,
    UsdGeomCamera, UsdGeomMesh etc).
    
    Other derived classes of UsdShadeNodeGraph from other schema domains may 
    define their own stricter rules.
    
    """

    schema_kind: SchemaKind = SchemaKind.ConcreteTyped

    meta = {
        "customData": {
            "extraPlugInfo": {
                "providesUsdShadeConnectableAPIBehavior": None
            },
            "extraIncludes": """'''
    #include "pxr/usd/usd/variantSets.h"
    #include "pxr/usd/usdGeom/subset.h"
    #include "pxr/usd/usdShade/connectableAPI.h"'''""",
            "schemaTokens": {
                "materialVariant": {"doc": """The variant name of material variation
                    described on a UsdShadeMaterial.
                    """},
                "surface": {"doc": """Describes the <i>surface</i> output 
                    terminal on a UsdShadeMaterial. It is used to define the 
                    terminal UsdShadeShader describing the surface of a 
                    UsdShadeMaterial.
                    """},
                "displacement": {"doc": """Describes the <i>displacement</i> output 
                    terminal on a UsdShadeMaterial. It is used to define the 
                    terminal UsdShadeShader describing the displacement of a 
                    UsdShadeMaterial.
                    """},
                "volume": {"doc": """Describes the <i>volume</i> output 
                    terminal on a UsdShadeMaterial. It is used to define the 
                    terminal UsdShadeShader describing the volume of a 
                    UsdShadeMaterial.
                    """},
                "universalRenderContext": {"value": "", "doc": """Possible value for the "renderContext" parameter
                    in \\ref UsdShadeMaterial_Outputs API. Represents the universal
                    renderContext. An output with a universal renderContext is 
                    applicable to all possible rendering contexts.
                    """}
            }
        }
    }

    outputs: Attribute[namespace] = Attribute(namespace, is_leaf=False)
    outputs.surface = Attribute(token,
        doc="""Represents the universal "surface" output terminal of a
        material.
        """,
        metadata={
            "displayGroup": "Outputs",
            "customData": {
                "apiName": "surface"
            }
        }
    )
    outputs.displacement = Attribute(token,
        doc="""Represents the universal "displacement" output terminal of a 
        material.
        """,
        metadata={
            "displayGroup": "Outputs",
            "customData": {
                "apiName": "displacement"
            }
        }
    )
    outputs.volume = Attribute(token,
        doc="""Represents the universal "volume" output terminal of a
        material.
        """,
        metadata={
            "displayGroup": "Outputs",
            "customData": {
                "apiName": "volume"
            }
        }
    )
