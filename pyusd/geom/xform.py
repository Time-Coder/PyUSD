from .xformable import Xformable


class Xform(Xformable):

    def __init__(self, name:str="")->None:
        Xformable.__init__(self, name)
        
        self.metadata.doc = """Concrete prim schema for a transform, which implements Xformable """
