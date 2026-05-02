from .attribute import Attribute
from .relationship import Relationship
from .dtypes import token, opaque, pathExpression
from .api_schema_base import APISchemaBase
from .common import SchemaKind


class CollectionAPI(APISchemaBase):
    """A general purpose API schema used to describe a collection of prims
    and properties within a scene. This API schema can be applied to a prim
    multiple times with different instance names to define several collections
    on a single prim.

    A collection's membership is specified one of two ways. The first way uses
    the built-in relationships `includes` and `excludes`, and the attribute
    `includeRoot` to determine membership. The second way is termed a
    pattern-based collection, and uses the built-in attribute
    `membershipExpression` to determine membership. Here we will refer to
    collections using `includes`, `excludes` and `includeRoot` as being in
    *relationship-mode* and those using the `membershipExpression` as being in
    *expression-mode*.

    The `mode` attribute controls which mode the collection uses.  When set to
    `relationship` the collection is explicitly in *relationship-mode*, and when
    set to `expression` it is explicitly in *expression-mode*.  Properties
    belonging to the non-selected mode are ignored.  When `mode` is `automatic`
    (the default), the mode is inferred from the collection's authored
    properties: the collection is in *relationship-mode* when either or both of
    its `includes` and `excludes` relationships have valid targets, or the
    `includeRoot` attribute is set to `true`; otherwise it is in
    *expression-mode* and the `membershipExpression` attribute applies.

    In *relationship-mode* the `includes` and `excludes` relationships specify
    the collection members as a set of paths to include and a set of paths to
    exclude.  Whether or not the descendants of an included path belong to a
    collection is decided by its expansion rule (see below).  If the collection
    excludes paths that are not descendent to included paths, the collection
    implicitly includes the root path `</>`.  If such a collection also
    includes paths that are not descendent to the excluded paths, it is
    considered invalid since the intent is ambiguous.

    In *expression-mode*, the pattern-based `membershipExpression` attribute is
    used with the `expansionRule` attribute to determine collection membership.
    See the detailed descriptions of the built-in properties below for more
    details.

    \\section usd_collectionapi_properties Collection API Properties

    The built-in properties for this schema are in the `collection:instanceName`
    namespace, where `instanceName` is the user-provided applied API schema
    instance name.

    <ul>
    <li>`uniform token collection:instanceName:expansionRule` - in
    *relationship-mode*, specifies how to expand the `includes` and `excludes`
    relationship targets to determine the collection's members.  In
    *expression-mode*, specifies how matching scene objects against the
    `membershipExpression` proceeds.  Possible values include:
        <ul>
        <li>`expandPrims` - in *relationship-mode*, all the prims descendent
        to the `includes` relationship targets (and not descendent to `excludes`
        relationship targets) belong to the collection.  Any `includes`-targeted
        property paths also belong to the collection. This is the default
        behavior. In *expression-mode*, the functions
        UsdComputeIncludedObjectsFromCollection() and
        UsdComputeIncludedPathsFromCollection() only test prims against the
        `membershipExpression` to determine membership.
        </li>
        <li>`expandPrimsAndProperties` - like `expandPrims`, but in
        *relationship-mode*, all properties on all included prims also belong to
        the collection. In *expression-mode*, the functions
        UsdComputeIncludedObjectsFromCollection() and
        UsdComputeIncludedPathsFromCollection() test both prims and
        properties against the `membershipExpression` to determine membership.
        </li>
        <li>`explicitOnly` - in *relationship-mode*, only paths in the
        `includes` relationship targets and not those in the `excludes`
        relationship targets belong to the collection. Does not apply to
        *expression-mode*. If set in *expression-mode*, the functions
        UsdComputeIncludedObjectsFromCollection() and
        UsdComputeIncludedPathsFromCollection() return no results.
        </li>
        </ul>
        </li>

    <li>`bool collection:instanceName:includeRoot` - boolean attribute
    indicating whether the pseudo-root path `</>` should be counted as one
    of the included target paths in *relationship-mode*. This separate attribute
    is required because relationships cannot directly target the root. When
    `expansionRule` is `explicitOnly`, this attribute is ignored. The fallback
    value is false. When set to `true`, this collection is in
    *relationship-mode*. This attribute is ignored in *expression-mode*.  </li>

    <li>`rel collection:instanceName:includes` - in *relationship-mode*,
    specifies a list of targets that are included in the collection. This can
    target prims or properties directly. A collection can insert the rules of
    another collection by making its `includes` relationship target the
    `collection:otherInstanceName` property from the collection to be included
    (see UsdCollectionAPI::GetCollectionAttr).  Note that including another
    collection does not guarantee the contents of that collection will be in the
    final collection; instead, the rules are merged.  This means, for example,
    an exclude entry may exclude a portion of the included collection.  When a
    collection includes one or more collections, the order in which targets are
    added to the includes relationship may become significant, if there are
    conflicting opinions about the same path. Targets that are added later are
    considered to be stronger than earlier targets for the same path.  This
    relationship is ignored in *expression-mode*.</li>

    <li>`rel collection:instanceName:excludes` - in *relationship-mode*,
    specifies a list of targets that are excluded below the <b>included</b>
    paths in this collection. This can target prims or properties directly, but
    <b>cannot target another collection</b>. This is to keep the membership
    determining logic simple, efficient and easier to reason about. Finally, it
    is invalid for a collection to exclude paths that are not included in
    it. The presence of such "orphaned" excluded paths will not affect the set
    of paths included in the collection, but may affect the performance of
    querying membership of a path in the collection (see
    UsdCollectionMembershipQuery::IsPathIncluded) or of enumerating the
    objects belonging to the collection (see
    UsdCollectionAPI::ComputeIncludedObjects).  This relationship is ignored in
    *expression-mode*.</li>

    <li>`uniform opaque collection:instanceName` - opaque
    attribute (meaning it can never have a value) that represents the collection
    for the purpose of allowing another collection to include it in
    *relationship-mode*. When this property is targeted by another collection's
    `includes` relationship, the rules of this collection will be inserted
    into the rules of the collection that includes it.</li>

    <li>`uniform pathExpression collection:instanceName:membershipExpression` -
    in *expression-mode*, defines the SdfPathExpression used to test
    objects for collection membership.</li>

    </ul>

    \\subsection usd_collectionapi_implicit_inclusion Implicit Inclusion

    In some scenarios it is useful to express a collection that includes
    everything except certain paths.  To support this, a *relationship-mode*
    collection that has an exclude that is not descendent to any include will
    include the root path `</>`.

    \\section usd_collectionapi_creating_cpp Creating Collections in C++
    
    \\snippet examples_usd.cpp ApplyCollections
    """
    
    schema_kind: SchemaKind = SchemaKind.MultipleApplyAPI

    meta = {
        "customData": {
            "extraIncludes": """
#include "pxr/usd/usd/collectionMembershipQuery.h"
#include "pxr/usd/usd/primFlags.h"
#include "pxr/usd/usd/tokens.h"
#include "pxr/usd/sdf/pathExpression.h"
""",
            "apiSchemaType": "multipleApply",
            "propertyNamespacePrefix": "collection",
            "schemaTokens": {
                "exclude": {
                    "doc": """
                    This is the token used to exclude a path from a collection. 
                    Although it is not a possible value for the "expansionRule"
                    attribute, it is used as the expansionRule for excluded paths 
                    in UsdCollectionAPI::MembershipQuery::IsPathIncluded.
                    """
                }
            }
        }
    }

    expansionRule: Attribute[token] = Attribute(token, value="expandPrims", uniform=True,
        metadata={
            "allowedTokens": ["explicitOnly", "expandPrims", "expandPrimsAndProperties"]
        },
        doc="""Specifies how the paths that are included in
        the collection must be expanded to determine its members."""
    )
    includeRoot: Attribute[bool] = Attribute(bool, uniform=True, doc=
        """Boolean attribute indicating whether the pseudo-root
        path `</>` should be counted as one of the included target
        paths.  The fallback is false.  This separate attribute is
        required because relationships cannot directly target the root."""
    )
    includes: Relationship = Relationship(doc=
        """Specifies a list of targets that are included in the collection.
        This can target prims or properties directly. A collection can insert
        the rules of another collection by making its <i>includes</i>
        relationship target the <b>collection:{collectionName}</b> property on
        the owning prim of the collection to be included"""
    )
    excludes: Relationship = Relationship("excludes", doc=
        """Specifies a list of targets that are excluded below
        the included paths in this collection. This can target prims or
        properties directly, but cannot target another collection. This is to
        keep the membership determining logic simple, efficient and easier to
        reason about. Finally, it is invalid for a collection to exclude
        paths that are not included in it. The presence of such "orphaned"
        excluded paths will not affect the set of paths included in the
        collection, but may affect the performance of querying membership of 
        a path in the collection (see
        UsdCollectionAPI::MembershipQuery::IsPathIncluded) 
        or of enumerating the objects belonging to the collection (see 
        UsdCollectionAPI::GetIncludedObjects)."""
    )
    membershipExpression: Attribute[pathExpression] = Attribute(pathExpression, uniform=True, doc=
        """Specifies a path expression that determines membership in this
        collection."""
    )
    mode: Attribute[token] = Attribute(token, value="automatic", uniform=True,
        metadata={
            "allowedTokens": ["automatic", "relationship", "expression"]
        },
        doc="""Specifies which mode the collection uses to determine
        membership: `automatic`, `relationship`, or `expression`.
        <ul>
        <li>`automatic` - the collection's mode is inferred from its authored
        properties.  If either or both of the `includes` and `excludes`
        relationships have valid targets, or the `includeRoot` attribute is set
        to `true`, the collection is in *relationship-mode* and the
        `membershipExpression` attribute is ignored.  Otherwise, the collection
        is in *expression-mode* and the `membershipExpression` attribute
        applies.  This is the default behavior and is backward compatible with
        collections that predate this attribute.</li>
        <li>`relationship` - the collection is explicitly in
        *relationship-mode*.  The `includes`, `excludes`, and `includeRoot`
        attributes determine membership, and `membershipExpression` is
        ignored.</li>
        <li>`expression` - the collection is explicitly in *expression-mode*.
        The `membershipExpression` attribute determines membership, and
        `includes`, `excludes`, and `includeRoot` are ignored.</li>
        </ul>
        The fallback value is `automatic`."""
    )
    __INSTANCE_NAME__: Attribute[opaque] = Attribute(opaque, uniform=True,
        metadata={
            "customData": {
                "apiName": "Collection"
            }
        },
        doc="""This property represents the collection for the purpose of 
        allowing another collection to include it. When this property is 
        targeted by another collection's <i>includes</i> relationship, the rules
        of this collection will be inserted into the rules of the collection
        that includes it.
        """
    )
