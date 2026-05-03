from enum import Enum
from .dtypes import token


class SchemaKind(Enum):
    # Invalid or unknown schema kind.
    Invalid = 0

    # Represents abstract or base schema types that are interface-only
    # and cannot be instantiated. These are reserved for core base classes
    # known to the usdGenSchema system, so this should never be assigned to
    # generated schema classes.
    AbstractBase = 1
    
    # Represents a non-concrete typed schema
    AbstractTyped = 2

    # Represents a concrete typed schema
    ConcreteTyped = 3

    # Non-applied API schema
    NonAppliedAPI = 4

    # Single Apply API schema
    SingleApplyAPI = 5

    # Multiple Apply API Schema
    MultipleApplyAPI = 6


class Kind(token):
    # base class for all model kinds. model is considered an abstract type and should not be assigned as any prim’s kind
    Model = "model"

    # models that simply group other models
    Group = "group"

    # an important group model, often a published asset or reference to a published asset
    Assembly = "assembly"

    # a "leaf model" that can contain no other models
    Component = "component"

    # an identified, important "sub part" of a component model
    Subcomponent = "subcomponent"


class Axis(token):
    X = "X"
    Y = "Y"
    Z = "Z"
    