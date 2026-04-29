from enum import Enum


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