from ..api_schema_base import APISchemaBase
from ..attribute import Attribute
from ..dtypes import string, token
from ..common import SchemaKind


class AccessibilityAPI(APISchemaBase):
    """
    This API describes \\em Accessibility information on a Prim that may be
    surfaced to a given runtime's accessibility frameworks.
    This information may be used by assistive tooling such as voice controls
    or screen readers.
    Accessibility information is provided as a standard triplet of label,
    description and priority.
    
    OpenUSD does not provide an accessibility runtime itself, but endeavours
    to provide the information needed for compatible runtimes to extract and
    present this information.
    
    This is a multiple apply schema, and so may have multiple namespaced
    accessibility triplets, where an instance name may reflect a given purpose
    for that triplet. For example, you may desire to express different
    information for different aspects of the prim, such as size or color.
    
    There are several best practices for using this schema:
    
    \\li Most accessibility runtimes support a single accessibility description.
    Therefore we recommend using a namespace labeled "default" for any critical 
    information.
    
    \\li A default value should be authored if using time sampled accessibility
    information. This helps accessibility runtimes that do not currently
    support time sampled information.
    
    \\li Provide accessibility information of your scene on the default prim
    of the layer, and any top level prims. This allows accessibility systems to
    provide concise scene descriptions to a user, but also allows supporting
    accessibility systems that either do not support hierarchy information or
    when a user has turned off that level of granularity. Accessibility
    information may still be provided on other prims in the hierarchy.
    
    \\note The use of the default prim and top level prims for scene
    accessibility descriptions is a recommended convention. Outside of that,
    accessibility information is not implicitly inherited through a prim
    hierarchy. The inheritance should be left to the accessibility runtime to
    decide how best to surface information to users.
    """

    schema_kind: SchemaKind = SchemaKind.NonAppliedAPI

    meta = {
        "customData": {
            "apiSchemaType": "multipleApply",
            "propertyNamespacePrefix": "accessibility",
            "schemaTokens": {
                "label": {"value": "label", "doc": "Name of the label attribute"},
                "description": {"value": "description", "doc": "Name of the description attribute"},
                "priority": {"value": "priority", "doc": "Name of the priority attribute"}
            }
        }
    }

    class Priority(token):
        Low = "low"
        Standard = "standard"
        High = "high"


    label = Attribute(string,
        doc="""A short label to concisely describe the prim.
        It is not recommended to time vary the label unless the concise
        description changes substantially.

        There is no specific suggested length for the label, but it is
        recommended to keep it succinct.
        """
    )

    description = Attribute(string,
        doc="""An extended description of the prim to provide more details.
        If a label attribute is not authored in a given instance name,
        the description attribute should not be used in it its place. A
        description is an optional attribute, and some accessibility systems
        may only use the label.

        Descriptions may be time varying for runtimes that support it. For
        example, you may describe what a character is doing at a given time.

        """
    )

    priority = Attribute(Priority,
        doc="""A hint to the accessibility runtime of how to prioritize this
        instance's label and description, relative to others.

        This attribute is optional and is considered a hint that runtimes may
        ignore, if they feel there are other necessities that take precedence
        over the prioritization values.

        """
    )
