from ..gprim import Gprim
from ..common import SchemaKind


class Volume(Gprim):
    """A renderable volume primitive. A volume is made up of any number
             of FieldBase primitives bound together in this volume. Each
             FieldBase primitive is specified as a relationship with a
             namespace prefix of "field".

             The relationship name is used by the renderer to associate
             individual fields with the named input parameters on the volume
             shader. Using this indirect approach to connecting fields to
             shader parameters (rather than using the field prim's name)
             allows a single field to be reused for different shader inputs, or
             to be used as different shader parameters when rendering different
             Volumes. This means that the name of the field prim is not
             relevant to its contribution to the volume prims which refer to
             it. Nor does the field prim's location in the scene graph have
             any relevance, and Volumes may refer to fields anywhere in the
             scene graph.  **However**, unless Field prims need to be shared
             by multiple Volumes, a Volume's Field prims should be located
             under the Volume in namespace, for enhanced organization."""
    schema_kind: SchemaKind = SchemaKind.ConcreteTyped
