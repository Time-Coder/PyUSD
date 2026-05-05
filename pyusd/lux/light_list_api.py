from ..api_schema_base import APISchemaBase
from ..attribute import Attribute
from ..relationship import Relationship
from ..dtypes import namespace
from ..dtypes import token
from ..common import SchemaKind


class LightListAPI(APISchemaBase):
    """API schema to support discovery and publishing of lights in a scene.
    
    \\section UsdLuxLightListAPI_Discovery Discovering Lights via Traversal
    
    To motivate this API, consider what is required to discover all
    lights in a scene.  We must load all payloads and traverse all prims:
    
    \\code
    01  // Load everything on the stage so we can find all lights,
    02  // including those inside payloads
    03  stage->Load();
    04  
    05  // Traverse all prims, checking if they have an applied UsdLuxLightAPI
    06  // (Note: ignoring instancing and a few other things for simplicity)
    07  SdfPathVector lights;
    08  for (UsdPrim prim: stage->Traverse()) {
    09      if (prim.HasAPI<UsdLuxLightAPI>()) {
    10          lights.push_back(i->GetPath());
    11      }
    12  }
    \\endcode
    
    This traversal -- suitably elaborated to handle certain details --
    is the first and simplest thing UsdLuxLightListAPI provides.
    UsdLuxLightListAPI::ComputeLightList() performs this traversal and returns
    all lights in the scene:
    
    \\code
    01  UsdLuxLightListAPI listAPI(stage->GetPseudoRoot());
    02  SdfPathVector lights = listAPI.ComputeLightList();
    \\endcode
    
    \\section UsdLuxLightListAPI_LightList Publishing a Cached Light List
    
    Consider a USD client that needs to quickly discover lights but
    wants to defer loading payloads and traversing the entire scene
    where possible, and is willing to do up-front computation and
    caching to achieve that.
    
    UsdLuxLightListAPI provides a way to cache the computed light list,
    by publishing the list of lights onto prims in the model
    hierarchy.  Consider a big set that contains lights:
    
    \\code
    01  def Xform "BigSetWithLights" (
    02      kind = "assembly"
    03      payload = @BigSetWithLights.usd@   // Heavy payload
    04  ) {
    05      // Pre-computed, cached list of lights inside payload
    06      rel lightList = [
    07          <./Lights/light_1>,
    08          <./Lights/light_2>,
    09          ...
    10      ]
    11      token lightList:cacheBehavior = "consumeAndContinue";
    12  }
    \\endcode
    
    The lightList relationship encodes a set of lights, and the
    lightList:cacheBehavior property provides fine-grained
    control over how to use that cache.  (See details below.)
    
    The cache can be created by first invoking
    ComputeLightList(ComputeModeIgnoreCache) to pre-compute the list
    and then storing the result with UsdLuxLightListAPI::StoreLightList().
    
    To enable efficient retrieval of the cache, it should be stored
    on a model hierarchy prim.  Furthermore, note that while you can
    use a UsdLuxLightListAPI bound to the pseudo-root prim to query the
    lights (as in the example above) because it will perform a
    traversal over descendants, you cannot store the cache back to the
    pseduo-root prim.
    
    To consult the cached list, we invoke
    ComputeLightList(ComputeModeConsultModelHierarchyCache):
    
    \\code
    01  // Find and load all lights, using lightList cache where available
    02  UsdLuxLightListAPI list(stage->GetPseudoRoot());
    03  SdfPathSet lights = list.ComputeLightList(
    04      UsdLuxLightListAPI::ComputeModeConsultModelHierarchyCache);
    05  stage.LoadAndUnload(lights, SdfPathSet());
    \\endcode
    
    In this mode, ComputeLightList() will traverse the model
    hierarchy, accumulating cached light lists.
    
    \\section UsdLuxLightListAPI_CacheBehavior Controlling Cache Behavior
    
    The lightList:cacheBehavior property gives additional fine-grained
    control over cache behavior:
    
    \\li The fallback value, "ignore", indicates that the lightList should
    be disregarded.  This provides a way to invalidate cache entries.
    Note that unless "ignore" is specified, a lightList with an empty
    list of targets is considered a cache indicating that no lights
    are present.
    
    \\li The value "consumeAndContinue" indicates that the cache should
    be consulted to contribute lights to the scene, and that recursion
    should continue down the model hierarchy in case additional lights
    are added as descedants. This is the default value established when
    StoreLightList() is invoked. This behavior allows the lights within
    a large model, such as the BigSetWithLights example above, to be
    published outside the payload, while also allowing referencing and
    layering to add additional lights over that set.
    
    \\li The value "consumeAndHalt" provides a way to terminate recursive
    traversal of the scene for light discovery. The cache will be
    consulted but no descendant prims will be examined.
    
    \\section UsdLuxLightListAPI_Instancing Instancing
    
    Where instances are present, UsdLuxLightListAPI::ComputeLightList() will
    return the instance-unique paths to any lights discovered within
    those instances.  Lights within a UsdGeomPointInstancer will
    not be returned, however, since they cannot be referred to
    solely via paths.
    
    """

    schema_kind: SchemaKind = SchemaKind.NonAppliedAPI

    class CacheBehavior(token):
        ConsumeAndHalt = "consumeAndHalt"
        ConsumeAndContinue = "consumeAndContinue"
        Ignore = "ignore"


    lightList: Attribute[namespace] = Attribute(namespace, is_leaf=False)
    lightList.cacheBehavior = Attribute(CacheBehavior,
        doc="""
        Controls how the lightList should be interpreted.
        Valid values are:
        - consumeAndHalt: The lightList should be consulted,
          and if it exists, treated as a final authoritative statement
          of any lights that exist at or below this prim, halting
          recursive discovery of lights.
        - consumeAndContinue: The lightList should be consulted,
          but recursive traversal over nameChildren should continue
          in case additional lights are added by descendants.
        - ignore: The lightList should be entirely ignored.  This
          provides a simple way to temporarily invalidate an existing
          cache.  This is the fallback behavior.

        """
    )

    lightList = Relationship(doc="Relationship to lights in the scene.")
