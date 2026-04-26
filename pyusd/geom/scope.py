from .imageable import Imageable


class Scope(Imageable):
    """Scope is the simplest grouping primitive, and does not carry the
    baggage of transformability.  Note that transforms should inherit down
    through a Scope successfully - it is just a guaranteed no-op from a
    transformability perspective."""

    def __init__(self, name:str="")->None:
        Imageable.__init__(self, name)
