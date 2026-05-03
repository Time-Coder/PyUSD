from .property import Property
from .common import SchemaKind
from .metadata import Metadata


class APISchemaBase:
    """The base class for all \\em API schemas.

    An API schema provides an interface to a prim's qualities, but does not
    specify a typeName for the underlying prim. The prim's qualities include 
    its inheritance structure, attributes, relationships etc. Since it cannot
    provide a typeName, an API schema is considered to be non-concrete. 
    
    To auto-generate an API schema using usdGenSchema, simply leave the 
    typeName empty and make it inherit from "/APISchemaBase" or from another 
    API schema. See UsdModelAPI, UsdClipsAPI and UsdCollectionAPI for examples.
    
    API schemas are classified into applied and non-applied API schemas. 
    The author of an API schema has to decide on the type of API schema 
    at the time of its creation by setting customData['apiSchemaType'] in the 
    schema definition (i.e. in  the associated primSpec inside the schema.usda 
    file).  UsdAPISchemaBase implements methods that are used to record the 
    application of an API schema on a USD prim.

    If an API schema only provides an interface to set certain core bits of 
    metadata (like UsdModelAPI, which sets model kind and UsdClipsAPI, which 
    sets clips-related metadata) OR if the API schema can apply to any type of 
    prim or only to a known fixed set of prim types OR if there is no use of 
    recording the application of the API schema, in such cases, it would be 
    better to make it a non-applied API schema. Examples of non-applied API 
    schemas include UsdModelAPI, UsdClipsAPI, UsdShadeConnectableAPI and
    UsdGeomPrimvarsAPI.

    If there is a need to discover (or record) whether a prim contains or 
    subscribes to a given API schema, it would be advantageous to make the API 
    schema be "applied". In general, API schemas that add one or more properties 
    to a prim should be tagged as applied API schemas. A public Apply() method 
    is generated for applied API schemas by usdGenSchema. An applied API schema 
    must be applied to a prim via a call to the generated Apply() method, for 
    the schema object to evaluate to true when converted to a bool using the 
    explicit bool conversion operator. Examples of applied API schemas include
    UsdCollectionAPI, UsdGeomModelAPI and UsdGeomMotionAPI

    \\subsection usd_apischemabase_single_vs_multiple_apply Single vs. Multiple Apply API Schemas
    
    Applied API schemas can further be classified into single-apply and 
    multiple-apply API schemas. As the name suggests, a single-apply API schema 
    can only be applied once to a prim. A multiple-apply API schema can be 
    applied multiple times with different 'instanceName' values. An example of 
    a multiple-apply API schema is UsdCollectionAPI, where the API schema is 
    applied to a prim once for every collection owned by the prim. 
    
    \\note An applied API schema must only inherit directly from APISchemaBase. 
    'usdGenSchema' will issue a warning if it detects applied API schemas
    that don't inherit from APISchemaBase, or inherit from something other than 
    APISchemaBase. 

    \\note When the bool-conversion operator is invoked on an applied API 
    schema, it evaluates to true only if the application of the API schema has
    been recorded on the prim via a call to the auto-generated Apply() method.
    
    """

    schema_kind: SchemaKind = SchemaKind.AbstractBase

    meta = {
        "customData": {
            "fileName": "apiSchemaBase"
        }
    }

    def __init__(self)->None:
        self.metadata.apiSchemas.append(self.__class__.__name__)
    
    @classmethod
    def cls_to_str(cls)->str:
        type_name = cls.__name__
        result = f'class "{type_name}"'

        if "meta" in cls.__dict__:
            metadata = Metadata(cls.meta)
        else:
            metadata = Metadata()

        update_metadata = {}

        if cls.__mro__[1] is not object:
            update_metadata["inherits"] = f"</{cls.__mro__[1].__name__}>"

        if cls.__doc__:
            update_metadata["doc"] = cls.__doc__

        metadata.update(update_metadata)

        metadata_str = metadata.to_str(0, True)
        if metadata_str:
            result += (" " + metadata_str)

        result += f'\n{{\n'
        
        props_str_list = []
        for name, prop in cls.__dict__.items():
            if not isinstance(prop, Property):
                continue

            prop._name = name
            prop_str = prop.to_str(1, full=True)
            if prop_str:
                props_str_list.append(prop_str)

        if props_str_list:
            result += "\n".join(props_str_list) + "\n"

        result += f'}}\n'
        return result