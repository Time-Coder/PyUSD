from typing import List
from .attribute import Attribute


class AttributePrefix:

    def __init__(self, name:str)->None:
        self._prop_names:List[str] = []
        self._name:str = name

    @property
    def name(self)->str:
        return self._name
    
    def to_str(self, indents:int=0)->str:
        from .prim import Prim

        tabs = "    " * indents
        results = []
        for prop_name in self._prop_names:
            prop = getattr(self, prop_name)
            if isinstance(prop, Attribute):
                if prop.value is not None:
                    results.append(prop.to_str(indents))
            elif isinstance(prop, Prim):
                results.append(f'{tabs}rel {prop_name} = <{prop.path}>')

        return "\n".join(results)