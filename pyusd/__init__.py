from .api_schema_base import APISchemaBase
from .attribute import Attribute
from .attribute_spec import AttributeSpec
from .clips_api import ClipsAPI
from .collection_api import CollectionAPI
from .color_space_api import ColorSpaceAPI
from .color_space_definition_api import ColorSpaceDefinitionAPI
from .common import Axis, Kind, SchemaKind
from .data import Data
from .dtypes import (
    asset,
    dictionary,
    double,
    group,
    half,
    int64,
    namespace,
    opaque,
    pathExpression,
    string,
    timecode,
    uchar,
    uint,
    uint64,
)
from .layer import Layer
from .model_api import ModelAPI
from .prim import Prim, PrimType
from .prim_spec import PrimSpec
from .property import Property
from .property_spec import PropertySpec
from .relationship import Relationship
from .relationship_spec import RelationshipSpec
from .stage import Stage
from .stage_metadata import StageMetadata
from .stage_variant_sets import StageVariantSets
from .typed import Typed
from .utils import abspath

__all__ = [
    "Layer",
    "Prim",
    # Internal storage, kept exported for compatibility. Reach it through
    # Prim.resolved_prim / Prim.authored_prim / Layer.prim_spec_at instead.
    "PrimSpec",
    "PrimType",
    "Attribute",
    "AttributeSpec",
    "Property",
    "PropertySpec",
    "Relationship",
    "RelationshipSpec",
    "Stage",
    "StageMetadata",
    "StageVariantSets",
    "Data",
    "double",
    "half",
    "uint",
    "uint64",
    "int64",
    "namespace",
    "string",
    "uchar",
    "opaque",
    "group",
    "asset",
    "timecode",
    "dictionary",
    "pathExpression",
    "generate_schema",
    "Typed",
    "APISchemaBase",
    "ModelAPI",
    "ColorSpaceAPI",
    "ColorSpaceDefinitionAPI",
    "CollectionAPI",
    "ClipsAPI",
    "abspath",
    "SchemaKind",
    "Kind",
    "Axis"
]

# Built last: the registry walks the submodules above, which are only fully
# bound once this module's imports have resolved.
from . import schema_registry as _schema_registry

_schema_registry._build()
