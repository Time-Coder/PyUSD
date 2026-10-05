from enum import ReprEnum

from ..api_schema_base import APISchemaBase
from ..attribute_spec import AttributeSpec
from ..common import SchemaKind
from ..dtypes import namespace, token


class ListAPI(APISchemaBase):
    """
    \\deprecated
    Use LightListAPI instead

    """

    schema_kind: SchemaKind = SchemaKind.NonAppliedAPI

    class CacheBehavior(token, ReprEnum):
        ConsumeAndHalt = "consumeAndHalt"
        ConsumeAndContinue = "consumeAndContinue"
        Ignore = "ignore"


    lightList: AttributeSpec[namespace] = AttributeSpec(namespace, is_leaf=False)
    lightList.cacheBehavior = AttributeSpec(CacheBehavior,
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
