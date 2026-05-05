from ..api_schema_base import APISchemaBase
from .info import Info
from .outputs import Outputs


class MaterialBindingAPI(APISchemaBase):
    """UsdShadeMaterialBindingAPI is an API schema that provides an 
    interface for binding materials to prims or collections of prims 
    (represented by UsdCollectionAPI objects). 
    
    In the USD shading model, each renderable gprim computes a single 
    <b>resolved Material</b> that will be used to shade the gprim (exceptions, 
    of course, for gprims that possess UsdGeomSubsets, as each subset can be 
    shaded by a different Material).  A gprim <b>and each of its ancestor 
    prims</b> can possess, through the MaterialBindingAPI, both a 
    <b>direct</b> binding to a Material, and any number of 
    <b>collection-based</b> bindings to Materials; each binding can be generic 
    or declared for a particular <b>purpose</b>, and given a specific <b>binding 
    strength</b>. It is the process of "material resolution" (see 
    \\ref UsdShadeMaterialBindingAPI_MaterialResolution) that examines all of 
    these bindings, and selects the one Material that best matches the 
    client's needs.
    
    The intent of <b>purpose</b> is that each gprim should be able to resolve a 
    Material for any given purpose, which implies it can have differently bound 
    materials for different purposes. There are two <i>special</i> values of 
    <b>purpose</b> defined in UsdShade, although the API fully supports 
    specifying arbitrary values for it, for the sake of extensibility:
    <ul><li><b>UsdShadeTokens->full</b>: to be used when the purpose of the 
    render is entirely to visualize the truest representation of a scene, 
    considering all lighting and material information, at highest fidelity.</li>  
    <li><b>UsdShadeTokens->preview</b>: to be used when the render is in 
    service of a goal other than a high fidelity "full" render (such as scene
    manipulation, modeling, or realtime playback). Latency and speed are 
    generally of greater concern for preview renders, therefore preview 
    materials are generally designed to be "lighterweight" compared to full
    materials.</li></ul>
    A binding can also have no specific purpose at all, in which 
    case, it is considered to be the fallback or all-purpose binding (denoted 
    by the empty-valued token <b>UsdShadeTokens->allPurpose</b>). 
    
    The <b>purpose</b> of a material binding is encoded in the name of the 
    binding relationship. 
    <ul><li>
    In the case of a direct binding, the <i>allPurpose</i> binding is 
    represented by the relationship named <b>material:binding</b>. 
    Special-purpose direct bindings are represented by relationships named
    <b>material:binding:<i>purpose</i></b>. A direct binding relationship 
    must have a single target path that points to a <b>UsdShadeMaterial</b>.</li>
    <li>
    In the case of a collection-based binding, the <i>allPurpose</i> binding is 
    represented by a relationship named 
    <b>material:binding:collection:<i>bindingName</i></b>, where 
    <b>bindingName</b> establishes an identity for the binding that is unique 
    on the prim. Attempting to establish two collection bindings of the same 
    name on the same prim will result in the first binding simply being 
    overridden. A special-purpose collection-based binding is represented by a 
    relationship named <b>material:binding:collection:<i>purpose:bindingName</i></b>.
    A collection-based binding relationship must have exacly two targets, one of 
    which should be a collection-path (see 
    \ref UsdCollectionAPI::GetCollectionPath()) and the other should point to a
    <b>UsdShadeMaterial</b>. In the future, we may allow a single collection 
    binding to target multiple collections, if we can establish a reasonable 
    round-tripping pattern for applications that only allow a single collection 
    to be associated with each Material.
    </li>
    </ul>
    
    <b>Note:</b> Both <b>bindingName</b> and <b>purpose</b> must be 
    non-namespaced tokens. This allows us to know the role of a binding 
    relationship simply from the number of tokens in it. 
    <ul><li><b>Two tokens</b>: the fallback, "all purpose", direct binding, 
    <i>material:binding</i></li>
    <li><b>Three tokens</b>: a purpose-restricted, direct, fallback binding, 
    e.g. material:binding:preview</li>
    <li><b>Four tokens</b>: an all-purpose, collection-based binding, e.g. 
    material:binding:collection:metalBits</li>
    <li><b>Five tokens</b>: a purpose-restricted, collection-based binding, 
    e.g. material:binding:collection:full:metalBits</li>
    </ul>
    
    A <b>binding-strength</b> value is used to specify whether a binding 
    authored on a prim should be weaker or stronger than bindings that appear 
    lower in namespace. We encode the binding strength with as token-valued 
    metadata <b>'bindMaterialAs'</b> for future flexibility, even though for 
    now, there are only two possible values:
    <i>UsdShadeTokens->weakerThanDescendants</i> and 
    <i>UsdShadeTokens->strongerThanDescendants</i>. When binding-strength is 
    not authored (i.e. empty) on a binding-relationship, the default behavior 
    matches UsdShadeTokens->weakerThanDescendants.
    
    \\note If a material binding relationship is a built-in property defined as 
    part of a typed prim's schema, a fallback value should not be provided for 
    it. This is because the "material resolution" algorithm only conisders 
    <i>authored</i> properties.
    
    """

