from .api_schema_base import APISchemaBase
from .common import SchemaKind


class ClipsAPI(APISchemaBase):
    """ UsdClipsAPI is an API schema that provides an interface to
    a prim's clip metadata. Clips are a "value resolution" feature that 
    allows one to specify a sequence of usd files (clips) to be consulted, 
    over time, as a source of varying overrides for the prims at and 
    beneath this prim in namespace.
            
    SetClipAssetPaths() establishes the set of clips that can be consulted.
    SetClipActive() specifies the ordering of clip application over time 
    (clips can be repeated), while SetClipTimes() specifies time-mapping
    from stage-time to clip-time for the clip active at a given stage-time,
    which allows for time-dilation and repetition of clips. 
    Finally, SetClipPrimPath() determines the path within each clip that will 
    map to this prim, i.e. the location within the clip at which we will look
    for opinions for this prim. 

    The clip asset paths, times and active metadata can also be specified 
    through template clip metadata. This can be desirable when your set of 
    assets is very large, as the template metadata is much more concise. 
    SetClipTemplateAssetPath() establishes the asset identifier pattern of the 
    set of clips to be consulted. SetClipTemplateStride(), 
    SetClipTemplateEndTime(), and SetClipTemplateStartTime() specify the range 
    in which USD will search, based on the template. From the set of resolved 
    asset paths, times and active will be derived internally.

    A prim may have multiple "clip sets" -- named sets of clips that each
    have their own values for the metadata described above. For example, 
    a prim might have a clip set named "Clips_1" that specifies some group
    of clip asset paths, and another clip set named "Clips_2" that uses
    an entirely different set of clip asset paths. These clip sets are 
    composed across composition arcs, so clip sets for a prim may be
    defined in multiple sublayers or references, for example. Individual
    metadata for a given clip set may be sparsely overridden.
                
    Important facts about clips:            
    \\li Within the layerstack in which clips are established, the           
    opinions within the clips will be \\em weaker than any local opinions
    in the layerstack, but \\em stronger than varying opinions coming across
    references and variants.            
    \\li We will never look for metadata or default opinions in clips            
    when performing value resolution on the owning stage, since these           
    quantities must be time-invariant.          
            
    This leads to the common structure in which we reference a model asset
    on a prim, and then author clips at the same site: the asset reference
    will provide the topology and unvarying data for the model, while the 
    clips will provide the time-sampled animation.

    For further information, see \\ref Usd_Page_ValueClips
    """

    schema_kind: SchemaKind = SchemaKind.NonAppliedAPI

    meta = {
        "customData": {
            "apiSchemaType": "nonApplied",
            "schemaTokens": {
                "clips": {
                    "doc": """
                    Dictionary that contains the definition of the clip sets on
                    this prim. See \\ref UsdClipsAPI::GetClips.
                    """
                },

                "clipSets": {
                    "doc": """
                    ListOp that may be used to affect how opinions from
                    clip sets are applied during value resolution. 
                    See \\ref UsdClipsAPI::GetClipSets.
                    """
                }
            }
        }
    }