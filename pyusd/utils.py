import os
from typing import List, Any, Set, get_origin, get_args, Optional
from types import ModuleType
from typeguard import typechecked

import numpy as np

from .gf import (
    double2, double3, double4,
    vector3d, color3d, color4d,
    float2, float3, float4,
    vector3f, color3f, color4f,
    texCoord2d, texCoord3d,
    texCoord2f, texCoord3f,
    point3f, point3d, normal3d, normal3f,
    int2, int3, int4,
    matrix2d, matrix3d, matrix4d, frame4d,
    quath, quatf, quatd, MathForm
)

from .dtypes import double, half, int64, string, token, pathExpression, timecode, uchar, uint, uint64, namespace, asset, dictionary


usd_scalar_types = (
    bool,
    double,
    float,
    half,
    int,
    int64,
    asset,
    str,
    string,
    token,
    pathExpression,
    timecode,
    uchar,
    uint,
    uint64
)

usd_vector_types = (
    double2, texCoord2d,
    double3, color3d, vector3d, point3d, normal3d, texCoord3d,
    double4, color4d, 
    float2, texCoord2f,
    float3, vector3f, point3f, normal3f, texCoord3f, color3f,
    float4, color4f,
    int2,
    int3,
    int4
)

usd_matrix_types = (
    matrix2d,
    matrix3d,
    matrix4d, frame4d
)

usd_quat_types = (
    quath,
    quatf,
    quatd
)

usd_dtypes = (
    namespace,
    dictionary,
    dict,
    *usd_scalar_types,
    *usd_vector_types,
    *usd_matrix_types,
    *usd_quat_types
)

allowed_types = usd_dtypes + (tuple,)

TYPE_PRIORITY = { int: 1, float: 2 }
NUMPY_TO_PY_TYPE_MAP = {
    np.int8: int, np.int16: int, np.int32: int, np.int64: int,
    np.uint8: int, np.uint16: int, np.uint32: int, np.uint64: int,
    np.float16: float, np.float32: float, np.float64: float,
    np.bool_: bool
}

def usd_value_str(value:Any, indents:int=0, degenerate_list:bool=False)->str:
    from .gf import genType
    from .prim import Prim

    tabs = "    " * indents
    next_tabs = "    " * (indents + 1)

    if isinstance(value, genType):
        if value.math_form == MathForm.Mat:
            result = f"(\n"
            for i in range(value.shape[0]):
                result += f"{next_tabs}("
                for j in range(value.shape[1]):
                    result += str(value[i, j])
                    if j != value.shape[1] - 1:
                        result += ", "
                result += f")"
                if i != value.shape[0] - 1:
                    result += ",\n"
                else:
                    result += "\n"
            result += f"{tabs})"
            return result
        else:
            return f"({', '.join([usd_value_str(sub_value) for sub_value in value])})"
    elif isinstance(value, dict):
        if len(value) == 0:
            return "{}"

        result = "{\n"
        for key, subvalue in value.items():
            subvalue_str = usd_value_str(subvalue, indents + 1)
            if isinstance(key, str):
                result += f"{next_tabs}{usd_type_str(infer_type(subvalue))} {key} = {subvalue_str}\n"
            else:
                result += f"{next_tabs}{key}: {subvalue_str}\n"
        result += f"{tabs}}}"
        return result
    elif isinstance(value, list) or isinstance(value, tuple):
        if isinstance(value, list):
            left_bracket = "["
            right_bracket = "]"
        elif isinstance(value, tuple):
            left_bracket = "("
            right_bracket = ")"

        if len(value) == 0:
            return f"{left_bracket}{right_bracket}"
        
        tabs = "    " * indents
        next_tabs = "    " * (indents + 1)
        if len(value) == 1:
            result = usd_value_str(value[0], 0)
            if degenerate_list:
                return result
            else:
                if "\n" not in result and len(result) < 100:
                    return f"{left_bracket}{result}{right_bracket}"
                else:
                    return f"{left_bracket}\n{usd_value_str(value[0], indents+1)}\n{right_bracket}"
        else:
            result = ", ".join([usd_value_str(subvalue, 0) for subvalue in value])
            if "\n" not in result and len(result) < 100:
                return f"{left_bracket}{result}{right_bracket}"
             
            result = f"{left_bracket}\n"
            result += f",\n{next_tabs}".join([usd_value_str(subvalue, indents+1) for subvalue in value])
            result += f"\n{tabs}{right_bracket}"
        return result
    elif isinstance(value, asset):
        return f'@{value}@'
    elif isinstance(value, Prim):
        return f"<{value.path}>"
    elif isinstance(value, float):
        if value.is_integer():
            return str(int(value))
        else:
            return str(value)
    elif isinstance(value, bool):
        return ("true" if value else "false")
    elif isinstance(value, str):
        value = value.replace("\\", "\\\\")
        if "\n" in value:
            return f'"""{value}"""'
        else:
            return f'"{value}"'
    else:
        return str(value)
    
def usd_type_str(type_:type, array_dim:int=0)->str:
    dtype, dim = analyze_list_type(type_)
    array_dim += dim

    result = ""
    if dtype == str:
        result = "string"
    elif dtype == dict:
        result = "dictionary"
    elif issubclass(dtype, token):
        result = "token"
    else:
        result = dtype.__name__

    result += "[]" * array_dim
    return result

def analyze_list_type(type_hint):
    depth = 0
    current_type = type_hint
    
    while True:
        origin = get_origin(current_type)
        
        if origin is list:
            args = get_args(current_type)
            if not args:
                raise TypeError(f"no element type int List")
            
            inner_type = args[0]
            inner_origin = get_origin(inner_type)
            
            if inner_origin is not None and inner_origin is not list:
                if inner_origin in [dict, tuple, set, frozenset]:
                    raise TypeError(f"not support type {inner_origin}")
            
            depth += 1
            current_type = inner_type
        else:
            break

    return current_type, depth

def infer_type(data: Any) -> str:
    def _analyze(item: Any) -> tuple:
        if isinstance(item, list):
            if not item: return 1, Any, None
            
            children_results = [_analyze(elem) for elem in item]
            first_depth, first_type, _ = children_results[0]
            
            if any(depth != first_depth for depth, _, _ in children_results):
                raise TypeError("list dimension not match")
            
            child_types = [t for _, t, _ in children_results]
            unique_types = set(child_types)
            
            final_type = None
            if len(unique_types) == 1:
                final_type = child_types[0]
            elif unique_types.issubset({int, float}):
                final_type = max(unique_types, key=lambda t: TYPE_PRIORITY.get(t, 0))
            else:
                raise TypeError(f"list type not compatible: {unique_types}")
                
            return first_depth + 1, final_type, None

        elif isinstance(item, np.ndarray):
            py_equiv_type = NUMPY_TO_PY_TYPE_MAP.get(item.dtype.type, item.dtype.type)
            
            if not issubclass(py_equiv_type, allowed_types):
                 pass 
            
            return 0, py_equiv_type, item.dtype

        else:
            val_type = type(item)
            if not issubclass(val_type, allowed_types):
                raise TypeError(f"not supported type: {val_type}")
            
            if val_type == float:
                val_type = double

            return 0, val_type, None

    if isinstance(data, np.ndarray):
        if data.dtype == np.object_:
             pass 
        
        depth, elem_type, dtype_obj = _analyze(data)
        target_type = NUMPY_TO_PY_TYPE_MAP.get(data.dtype.type, data.dtype.type)
        
        ndim = data.ndim
        result = target_type
        for _ in range(ndim):
            result = List[result]
        return result

    depth, element_type, _ = _analyze(data)
    
    if depth == 0:
        return element_type
    
    current_type = element_type
    for _ in range(depth):
        current_type = List[current_type]
        
    return current_type

def nest_map(nested_list, func):
    if not isinstance(nested_list, list):
        return func(nested_list)

    result = []
    for item in nested_list:
        if isinstance(item, list):
            result.append(nest_map(item, func))
        else:
            result.append(func(item))

    return result


def in_annotations(name:str, cls:type)->bool:
    for klass in cls.__mro__:
        if hasattr(klass, '__annotations__'):
            if name in klass.__annotations__:
                return True
            
    return False

@typechecked
def generate_schema(module: ModuleType)->None:
    from .typed import Typed
    from .api_schema_base import APISchemaBase

    result_list = []
    for cls_name in module.__all__:
        cls = getattr(module, cls_name)
        if isinstance(cls, type) and issubclass(cls, (Typed, APISchemaBase)):
            result_list.append(cls.cls_to_str())

    result = "\n".join(result_list)
    target_file_path = os.path.join(os.path.dirname(module.__file__), "schema_generated.usda")
    with open(target_file_path, "w") as f:
        f.write(result)


def generate_pyclasses(schema_path: str) -> None:
    """
    通过解析 schema.usda 文件，在相同文件夹生成对应的 python 类。
    
    Args:
        schema_path: schema.usda 文件的路径
    """
    from tree_sitter import Language, Parser
    import tree_sitter_usd
    
    # 初始化 parser
    lang = Language(tree_sitter_usd.language())
    parser = Parser(lang)
    
    # 读取并解析 schema 文件
    with open(schema_path, 'r', encoding='utf-8') as f:
        code = f.read().encode('utf-8')
    
    tree = parser.parse(code)
    
    # 获取目录路径
    schema_dir = os.path.dirname(schema_path)
    
    # 存储所有类的信息
    classes_info = {}
    class_names = []
    
    # 遍历所有 prim_definition
    for child in tree.root_node.children:
        if child.type == 'prim_definition':
            class_info = _parse_prim_definition(child)
            if class_info and class_info['name'].lower() != 'global':
                classes_info[class_info['name']] = class_info
                class_names.append(class_info['name'])
    
    # 为每个类生成 Python 文件
    for class_name in class_names:
        class_info = classes_info[class_name]
        _generate_class_file(schema_dir, class_name, class_info, classes_info)
    
    # 生成 __init__.py
    _generate_init_file(schema_dir, class_names)


def _parse_prim_definition(node) -> dict:
    """
    解析 prim_definition 节点，提取类信息
    
    Returns:
        包含类信息的字典，包括名称、类型、继承、属性等
    """
    info = {
        'name': '',
        'kind': '',  # 'def', 'class', 'over'
        'has_explicit_name': False,  # 是否有明确的类名（如 class XXX "XXX"）
        'inherits': [],
        'doc': '',
        'custom_data': {},
        'metadata': {},  # 类的完整 metadata
        'attributes': [],
        'relationships': [],
        'api_schemas': [],
    }
    
    for child in node.named_children:
        if child.type == 'prim_type':
            info['kind'] = child.text.decode('utf-8').strip()
        elif child.type == 'string':
            # 类名
            name = child.text.decode('utf-8').strip('"')
            info['name'] = name
            # 检查是否有明确的类名（class XXX "XXX" 格式）
            # 如果 prim_type 后面紧跟 identifier，然后才是 string，则有明确类名
            prev_sibling = child.prev_named_sibling
            if prev_sibling and prev_sibling.type == 'identifier':
                info['has_explicit_name'] = True
        elif child.type == 'metadata':
            _parse_metadata(child, info)
        elif child.type == 'block':
            _parse_block(child, info)
    
    if not info['name']:
        return None
    
    return info


def _parse_metadata(node, info: dict) -> None:
    """解析 metadata 节点"""
    for child in node.named_children:
        if child.type == 'metadata_assignment':
            _parse_metadata_assignment(child, info)


def _parse_metadata_assignment(node, info: dict) -> None:
    """解析 metadata assignment"""
    key = ''
    for child in node.named_children:
        if child.type == 'identifier':
            key = child.text.decode('utf-8')
        elif child.type == 'string' and key == 'doc':
            info['doc'] = child.text.decode('utf-8').strip('"')
        elif child.type == 'dictionary' and key == 'customData':
            _parse_custom_data(child, info)
        elif child.type == 'arc_path' and key == 'inherits':
            inherits_path = child.text.decode('utf-8').strip('<>').strip('/')
            if inherits_path:
                info['inherits'].append(inherits_path)
        elif child.type == 'array' and key == 'prepend apiSchemas':
            # 解析 apiSchemas 数组
            for item in child.named_children:
                if item.type == 'string':
                    api_schema = item.text.decode('utf-8').strip('"')
                    info['api_schemas'].append(api_schema)


def _parse_custom_data(node, info: dict) -> None:
    """解析 customData 字典，提取完整的 metadata 结构"""
    custom_data = _parse_usd_dictionary(node)
    if custom_data:
        info['custom_data'] = custom_data
        # 同时添加到 metadata
        if 'customData' not in info['metadata']:
            info['metadata']['customData'] = {}
        info['metadata']['customData'] = custom_data


def _parse_usd_dictionary(node) -> dict:
    """解析 USD 格式的字典（可能是 dictionary_item 或直接是属性声明）"""
    result = {}
    
    for child in node.named_children:
        if child.type == 'dictionary_item':
            # 标准 dictionary_item 格式
            key = ''
            value = None
            for item_child in child.named_children:
                if item_child.type == 'identifier':
                    key = item_child.text.decode('utf-8')
                elif item_child.type == 'string':
                    value = item_child.text.decode('utf-8').strip('"')
                elif item_child.type == 'bool':
                    value = item_child.text.decode('utf-8') == 'true'
                elif item_child.type == 'int':
                    value = int(item_child.text.decode('utf-8'))
                elif item_child.type == 'float':
                    value = float(item_child.text.decode('utf-8'))
                elif item_child.type == 'array':
                    value = _parse_usd_array(item_child)
                elif item_child.type == 'dictionary':
                    value = _parse_usd_dictionary(item_child)
            
            if key:
                result[key] = value
        elif child.type == 'attribute_type':
            # USD 属性声明格式: type key = value
            attr_type = child.text.decode('utf-8')
            key = ''
            value = None
            
            # 查找后续的 identifier 和 value
            next_sibling = child.next_named_sibling
            while next_sibling:
                if next_sibling.type == 'identifier' and not key:
                    key = next_sibling.text.decode('utf-8')
                elif next_sibling.type == 'string' and key and value is None:
                    value = next_sibling.text.decode('utf-8').strip('"')
                    break
                elif next_sibling.type == 'bool' and key and value is None:
                    value = next_sibling.text.decode('utf-8') == 'true'
                    break
                elif next_sibling.type == 'int' and key and value is None:
                    value = int(next_sibling.text.decode('utf-8'))
                    break
                elif next_sibling.type == 'float' and key and value is None:
                    value = float(next_sibling.text.decode('utf-8'))
                    break
                elif next_sibling.type == 'array' and key and value is None:
                    value = _parse_usd_array(next_sibling)
                    break
                elif next_sibling.type == 'dictionary' and key and value is None:
                    value = _parse_usd_dictionary(next_sibling)
                    break
                next_sibling = next_sibling.next_named_sibling
            
            if key:
                result[key] = value
    
    return result


def _parse_usd_array(node) -> list:
    """解析 USD 数组"""
    result = []
    for child in node.named_children:
        if child.type == 'string':
            result.append(child.text.decode('utf-8').strip('"'))
        elif child.type == 'bool':
            result.append(child.text.decode('utf-8') == 'true')
        elif child.type == 'int':
            result.append(int(child.text.decode('utf-8')))
        elif child.type == 'float':
            result.append(float(child.text.decode('utf-8')))
    return result


def _parse_block(node, info: dict) -> None:
    """解析 block 节点，提取属性和关系"""
    for child in node.named_children:
        if child.type == 'attribute_declaration' or child.type == 'attribute_assignment':
            attr_info = _parse_attribute_declaration(child)
            if attr_info:
                info['attributes'].append(attr_info)
        elif child.type == 'relationship_declaration' or child.type == 'relationship_assignment':
            rel_info = _parse_relationship_declaration(child)
            if rel_info:
                info['relationships'].append(rel_info)


def _parse_attribute_declaration(node) -> dict:
    """解析属性声明或赋值"""
    attr_info = {
        'name': '',  # Python 属性名（不带命名空间）
        'full_name': '',  # 完整的 USD 属性名（带命名空间）
        'type': '',
        'is_uniform': False,
        'default_value': None,
        'doc': '',
        'allowed_tokens': [],
        'api_name': '',  # customData 中的 apiName
        'metadata': {},  # 属性的 metadata
    }
    
    for child in node.named_children:
        if child.type == 'uniform':
            attr_info['is_uniform'] = True
        elif child.type == 'attribute_type':
            attr_info['type'] = child.text.decode('utf-8')
        elif child.type == 'identifier' or child.type == 'qualified_identifier':
            # qualified_identifier 包含 namespace:name 格式
            full_name = child.text.decode('utf-8')
            attr_info['full_name'] = full_name
            # 如果有冒号，提取最后一部分作为 Python 属性名
            if ':' in full_name:
                attr_info['name'] = full_name.split(':')[-1]
            else:
                attr_info['name'] = full_name
        elif child.type in ['bool', 'int', 'float', 'string', 'array', 'dictionary']:
            # 默认值
            attr_info['default_value'] = child.text.decode('utf-8')
        elif child.type == 'metadata':
            _parse_attribute_metadata(child, attr_info)
    
    # 如果有 apiName，使用它作为 Python 属性名
    if attr_info['api_name']:
        attr_info['name'] = attr_info['api_name']
    
    if not attr_info['name']:
        return None
    
    return attr_info


def _parse_relationship_declaration(node) -> dict:
    """解析关系声明或赋值"""
    rel_info = {
        'name': '',  # Python 属性名
        'full_name': '',  # 完整的 USD 关系名
        'doc': '',
        'metadata': {},  # 关系的 metadata
    }
    
    for child in node.named_children:
        if child.type == 'identifier' or child.type == 'qualified_identifier':
            full_name = child.text.decode('utf-8')
            rel_info['full_name'] = full_name
            # 如果有冒号，提取最后一部分作为 Python 属性名
            if ':' in full_name:
                rel_info['name'] = full_name.split(':')[-1]
            else:
                rel_info['name'] = full_name
        elif child.type == 'metadata':
            _parse_relationship_metadata(child, rel_info)
    
    if not rel_info['name']:
        return None
    
    return rel_info


def _parse_attribute_metadata(node, attr_info: dict) -> None:
    """解析属性元数据"""
    for child in node.named_children:
        if child.type == 'metadata_assignment':
            key = ''
            value_dict = {}
            for assign_child in child.named_children:
                if assign_child.type == 'identifier':
                    key = assign_child.text.decode('utf-8')
                elif assign_child.type == 'string' and key == 'doc':
                    attr_info['doc'] = assign_child.text.decode('utf-8').strip('"')
                elif (assign_child.type == 'array' or assign_child.type == 'list') and key == 'allowedTokens':
                    for item in assign_child.named_children:
                        if item.type == 'string':
                            attr_info['allowed_tokens'].append(item.text.decode('utf-8').strip('"'))
                elif assign_child.type == 'dictionary' and key == 'customData':
                    # 解析 customData 中的 apiName 和其他元数据
                    custom_data = _parse_usd_dictionary(assign_child)
                    # 提取 apiName 作为单独字段
                    if 'apiName' in custom_data:
                        attr_info['api_name'] = custom_data['apiName']
                    # 完整的 customData 都应该保存到 metadata 中
                    if custom_data:
                        attr_info['metadata']['customData'] = custom_data
                elif key not in ['doc', 'allowedTokens']:
                    # 其他 metadata 字段（如 displayName）
                    value = None
                    if assign_child.type == 'string':
                        value = assign_child.text.decode('utf-8').strip('"')
                    elif assign_child.type == 'bool':
                        value = assign_child.text.decode('utf-8') == 'true'
                    elif assign_child.type == 'int':
                        value = int(assign_child.text.decode('utf-8'))
                    elif assign_child.type == 'float':
                        value = float(assign_child.text.decode('utf-8'))
                    elif assign_child.type == 'array':
                        value = _parse_usd_array(assign_child)
                    elif assign_child.type == 'dictionary':
                        value = _parse_usd_dictionary(assign_child)
                    
                    if value is not None:
                        attr_info['metadata'][key] = value


def _parse_relationship_metadata(node, rel_info: dict) -> None:
    """解析关系元数据"""
    for child in node.named_children:
        if child.type == 'metadata_assignment':
            key = ''
            for assign_child in child.named_children:
                if assign_child.type == 'identifier':
                    key = assign_child.text.decode('utf-8')
                elif assign_child.type == 'string' and key == 'doc':
                    rel_info['doc'] = assign_child.text.decode('utf-8').strip('"')
                elif assign_child.type == 'dictionary' and key == 'customData':
                    # 解析 customData
                    custom_data = _parse_usd_dictionary(assign_child)
                    if custom_data:
                        rel_info['metadata']['customData'] = custom_data
                elif key != 'doc':
                    # 其他 metadata 字段
                    value = None
                    if assign_child.type == 'string':
                        value = assign_child.text.decode('utf-8').strip('"')
                    elif assign_child.type == 'bool':
                        value = assign_child.text.decode('utf-8') == 'true'
                    elif assign_child.type == 'int':
                        value = int(assign_child.text.decode('utf-8'))
                    elif assign_child.type == 'float':
                        value = float(assign_child.text.decode('utf-8'))
                    elif assign_child.type == 'array':
                        value = _parse_usd_array(assign_child)
                    elif assign_child.type == 'dictionary':
                        value = _parse_usd_dictionary(assign_child)
                    
                    if value is not None:
                        rel_info['metadata'][key] = value


def _generate_class_file(schema_dir: str, class_name: str, class_info: dict, all_classes: dict) -> None:
    """生成 Python 类文件"""
    # 确定基类
    base_class = _determine_base_class(class_info, all_classes)
    
    # 确定 schema_kind
    schema_kind = _determine_schema_kind(class_info)
    
    # 生成文件名（转换为 snake_case）
    file_name = _camel_to_snake(class_name) + '.py'
    file_path = os.path.join(schema_dir, file_name)
    
    # 如果文件已存在，跳过
    if os.path.exists(file_path):
        print(f"Skipping existing file: {file_path}")
        return
    
    # 生成导入语句
    imports = _generate_imports(base_class, class_info, schema_dir)
    
    # 检查是否有需要从 common.py 导入的枚举类
    _, imported_token_classes = _generate_token_classes(class_info['attributes'])
    if imported_token_classes:
        # 添加到导入语句中
        imports += f"\nfrom ..common import {', '.join(sorted(set(imported_token_classes)))}"
    
    # 生成类定义
    class_def = _generate_class_definition(class_name, base_class, schema_kind, class_info)
    
    # 写入文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(imports)
        f.write('\n\n')
        f.write(class_def)
        f.write('\n')
    
    print(f"Generated: {file_path}")


def _generate_init_file(schema_dir: str, class_names: list) -> None:
    """生成 __init__.py 文件"""
    init_path = os.path.join(schema_dir, '__init__.py')
    
    lines = []
    for class_name in class_names:
        file_name = _camel_to_snake(class_name)
        lines.append(f"from .{file_name} import {class_name}")
    
    # 添加 __all__
    lines.append('')
    lines.append('__all__ = [')
    for class_name in class_names:
        lines.append(f'    "{class_name}",')
    lines.append(']')
    
    with open(init_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
        f.write('\n')
    
    print(f"Generated: {init_path}")


def _determine_base_class(class_info: dict, all_classes: dict) -> str:
    """确定基类"""
    if class_info['inherits']:
        # 使用第一个继承的类
        parent_name = class_info['inherits'][0]
        
        # 提取路径的最后一部分（处理 /PhysicsJoint 这样的路径）
        if '/' in parent_name:
            parent_name = parent_name.split('/')[-1]
        
        # 特殊处理一些已知的基类
        if parent_name.lower() == 'apischemabase':
            return 'APISchemaBase'
        elif parent_name.lower() == 'typed':
            return 'Typed'
        elif parent_name.lower() == 'imageable':
            return 'Imageable'
        
        # 如果已经是 PascalCase，直接返回
        if parent_name[0].isupper():
            return parent_name
        
        # 转换为 PascalCase
        parent_name = _snake_to_pascal(parent_name)
        return parent_name
    
    # 默认基类
    if class_info['kind'] == 'class':
        # 检查是否是 API schema
        if 'apiSchemaType' in class_info['custom_data']:
            return 'APISchemaBase'
        return 'Typed'
    return 'object'


def _determine_schema_kind(class_info: dict) -> str:
    """确定 schema kind"""
    api_schema_type = class_info['custom_data'].get('apiSchemaType', '')
    
    # 检查是否继承自 APISchemaBase
    inherits_from_api = any('APISchemaBase' in inherit for inherit in class_info['inherits'])
    
    if api_schema_type:
        # API Schema with explicit type
        if api_schema_type == 'nonApplied':
            return 'NonAppliedAPI'
        elif api_schema_type == 'singleApply':
            return 'SingleApplyAPI'
        elif api_schema_type == 'multipleApply':
            return 'MultipleApplyAPI'
        else:
            return 'NonAppliedAPI'
    elif inherits_from_api:
        # 继承自 APISchemaBase 但没有明确指定 apiSchemaType，默认为 nonApplied
        return 'NonAppliedAPI'
    elif class_info['kind'] == 'class':
        # 非 API schema 的 class
        # class XXX "XXX" -> ConcreteTyped
        # class "XXX" -> AbstractTyped
        if class_info.get('has_explicit_name', False):
            return 'ConcreteTyped'
        else:
            return 'AbstractTyped'
    else:
        return 'ConcreteTyped'


def _generate_imports(base_class: str, class_info: dict, schema_dir: str) -> str:
    """生成导入语句"""
    imports = []
    
    # 根据基类确定导入
    if base_class in ['Typed', 'APISchemaBase']:
        # 这些可能在父模块中
        imports.append(f"from ..typed import Typed")
        imports.append(f"from ..api_schema_base import APISchemaBase")
    else:
        # 检查是否是已知的跨模块基类
        known_cross_module_classes = {
            'Imageable': 'geom',
            'Xformable': 'geom',
        }
        
        if base_class in known_cross_module_classes:
            module_name = known_cross_module_classes[base_class]
            imports.append(f"from pyusd.{module_name}.{_camel_to_snake(base_class)} import {base_class}")
        else:
            # 同级模块中的类
            base_file_name = _camel_to_snake(base_class)
            base_file = os.path.join(schema_dir, base_file_name + '.py')
            if os.path.exists(base_file):
                imports.append(f"from .{base_file_name} import {base_class}")
            else:
                # 可能来自父模块或其他模块
                imports.append(f"from ..{_camel_to_snake(base_class)} import {base_class}")
    
    # 检查需要的类型
    needed_types = set()
    for attr in class_info['attributes']:
        py_type = _usd_type_to_python_type(attr['type'])
        # 提取类型名称（处理 List[X] 的情况）
        if py_type.startswith('List['):
            inner_type = py_type[5:-1]
            needed_types.add(inner_type)
        else:
            needed_types.add(py_type)
    
    # 添加常用导入
    if class_info['attributes']:
        imports.append("from ..attribute import Attribute")
        imports.append("from typing import List")
        
        # 检查是否需要 namespace 类型
        has_namespace = any(attr.get('full_name', '').count(':') > 0 for attr in class_info['attributes'])
        if has_namespace:
            imports.append("from ..dtypes import namespace")
        
        # 检查是否有 allowedTokens，需要导入 token
        has_allowed_tokens = any(attr.get('allowed_tokens') for attr in class_info['attributes'])
        if has_allowed_tokens and "from ..dtypes import token" not in imports:
            imports.append("from ..dtypes import token")
            # 从 needed_types 中移除 token，避免重复导入
            needed_types.discard('token')
        
        # 添加需要的类型导入
        gf_types = {
            'vector3f', 'vector3d', 'point3f', 'point3d', 'normal3f', 'normal3d',
            'color3f', 'color3d', 'color4f', 'color4d',
            'float2', 'float3', 'float4', 'double2', 'double3', 'double4',
            'int2', 'int3', 'int4',
            'matrix2d', 'matrix3d', 'matrix4d',
            'quatf', 'quatd', 'quath'
        }
        
        dtypes_types = {
            'token', 'asset', 'path', 'timecode', 'half', 'double'
        }
        
        needed_gf_types = needed_types.intersection(gf_types)
        needed_dtype_types = needed_types.intersection(dtypes_types)
        
        if needed_gf_types:
            types_str = ', '.join(sorted(needed_gf_types))
            imports.append(f"from ..gf import {types_str}")
        
        if needed_dtype_types:
            types_str = ', '.join(sorted(needed_dtype_types))
            imports.append(f"from ..dtypes import {types_str}")
    
    if class_info['relationships']:
        if "from ..relationship import Relationship" not in imports:
            imports.append("from ..relationship import Relationship")
    
    # 添加 SchemaKind
    imports.append("from ..common import SchemaKind")
    
    return '\n'.join(imports)


def _generate_token_classes(attributes: list) -> tuple:
    """为有 allowedTokens 的属性生成 token 枚举类
    
    Returns:
        (lines, imported_classes): lines 是要生成的类定义，imported_classes 是需要从 common 导入的类名列表
    """
    lines = []
    imported_classes = []
    
    # common.py 中已定义的枚举类
    common_enums = {'Axis', 'Kind'}
    
    for attr in attributes:
        if attr.get('allowed_tokens'):
            # 生成类名：将属性名转换为 PascalCase
            class_name = _snake_to_pascal(attr['name'])
            
            # 检查是否在 common.py 中已定义
            if class_name in common_enums:
                imported_classes.append(class_name)
            else:
                # 生成新的枚举类
                lines.append(f"    class {class_name}(token):")
                
                # 为每个 token 生成常量
                for token_value in attr['allowed_tokens']:
                    # 将 token 值转换为合法的 Python 标识符
                    const_name = _token_to_constant(token_value)
                    lines.append(f"        {const_name} = \"{token_value}\"")
                
                lines.append("")
    
    return lines, imported_classes


def _token_to_constant(token_value: str) -> str:
    """将 token 值转换为合法的 Python 常量名"""
    # 替换特殊字符为下划线
    result = token_value.replace(':', '_').replace('-', '_').replace('.', '_').replace('/', '_')
    # 如果以数字开头，添加前缀
    if result[0].isdigit():
        result = '_' + result
    # 转换为 PascalCase
    parts = result.split('_')
    result = ''.join(word.capitalize() for word in parts if word)
    # 如果是 Python 关键字，添加后缀
    python_keywords = {'None', 'True', 'False', 'class', 'def', 'return', 'import', 'from', 'if', 'else', 'elif', 'for', 'while', 'try', 'except', 'finally', 'with', 'as', 'pass', 'break', 'continue', 'lambda', 'yield', 'global', 'nonlocal', 'assert', 'del', 'raise', 'in', 'is', 'not', 'and', 'or'}
    if result in python_keywords:
        result = result + '_'
    return result


def _generate_class_definition(class_name: str, base_class: str, schema_kind: str, class_info: dict) -> str:
    """生成类定义"""
    lines = []
    
    # 类定义和 docstring
    lines.append(f"\nclass {class_name}({base_class}):")
    
    if class_info['doc']:
        doc = class_info['doc'].replace('\\n', '\n').replace('\\"', '"')
        lines.append(f'    """{doc}"""')
    
    # schema_kind
    if schema_kind in ['NonAppliedAPI', 'SingleApplyAPI', 'MultipleApplyAPI']:
        lines.append(f"    schema_kind: SchemaKind = SchemaKind.{schema_kind}")
    elif schema_kind == 'AbstractTyped':
        lines.append(f"    schema_kind: SchemaKind = SchemaKind.AbstractTyped")
    else:
        lines.append(f"    schema_kind: SchemaKind = SchemaKind.ConcreteTyped")
    
    # 如果有 metadata，添加 meta
    if class_info.get('metadata'):
        lines.append("")
        meta_str = _format_metadata(class_info['metadata'], indent_level=0)
        # 调整缩进：每行添加 4 个空格，第一行添加 "meta = "
        meta_lines = meta_str.split('\n')
        for i, line in enumerate(meta_lines):
            if i == 0:
                lines.append(f"    meta = {line}")
            else:
                lines.append(f"    {line}")
    
    # 生成 allowedTokens 对应的枚举类
    token_classes, imported_token_classes = _generate_token_classes(class_info['attributes'])
    if imported_token_classes:
        # 添加到导入语句中（在函数外部处理）
        pass
    if token_classes:
        lines.append("")
        lines.extend(token_classes)
    
    # 按命名空间分组属性
    namespaces = {}
    regular_attrs = []
    
    for attr in class_info['attributes']:
        full_name = attr.get('full_name', attr['name'])
        if ':' in full_name:
            # 有命名空间的属性
            ns_prefix = full_name.split(':')[0]
            if ns_prefix not in namespaces:
                namespaces[ns_prefix] = []
            namespaces[ns_prefix].append(attr)
        else:
            regular_attrs.append(attr)
    
    # 先生成普通属性
    for attr in regular_attrs:
        attr_def = _generate_attribute_definition(attr)
        if attr_def:
            lines.append("")
            lines.append(attr_def)
    
    # 再生成命名空间属性和其子属性
    for ns_prefix, ns_attrs in namespaces.items():
        # 生成 namespace 属性
        lines.append("")
        lines.append(f"    {ns_prefix}: Attribute[namespace] = Attribute(namespace, is_leaf=False)")
        
        # 生成子属性
        for attr in ns_attrs:
            attr_def = _generate_namespaced_attribute_definition(ns_prefix, attr)
            if attr_def:
                lines.append(attr_def)
    
    # 添加关系
    for rel in class_info['relationships']:
        rel_def = _generate_relationship_definition(rel)
        if rel_def:
            lines.append("")
            lines.append(rel_def)
    
    return '\n'.join(lines)


def _generate_namespaced_attribute_definition(ns_prefix: str, attr: dict) -> str:
    """生成命名空间属性的子属性定义"""
    # 转换 USD 类型到 Python 类型
    py_type = _usd_type_to_python_type(attr['type'])
    
    # 如果有 allowedTokens，使用生成的类名
    if attr.get('allowed_tokens'):
        class_name = _snake_to_pascal(attr['name'])
        py_type = class_name
    
    # 获取子属性名（去掉命名空间前缀）
    full_name = attr.get('full_name', attr['name'])
    if ':' in full_name:
        sub_attr_name = ':'.join(full_name.split(':')[1:])
    else:
        sub_attr_name = attr['name']
    
    # 检查是否与 Attribute/Property 类的属性名冲突
    reserved_attrs = {
        'type', 'name', 'value', 'uniform', 'metadata', 'parent_prim', 
        'parent_prop', 'is_leaf', 'full_name', 'path', 'value_state', 
        'custom', 'timeSamples', 'type_name', 'is_namespace'
    }
    is_reserved = sub_attr_name in reserved_attrs
    if is_reserved:
        # 使用 create_prop 方法并传递 name 参数
        pass
    
    # 构建参数列表
    params_list = []
    
    # uniform 关键字
    if attr['is_uniform']:
        params_list.append("uniform=True")
    
    # default value - 转换为 Python 语法
    if attr['default_value'] is not None:
        py_value = _usd_value_to_python(attr['default_value'])
        params_list.append(f"value={py_value}")
    
    # doc
    if attr['doc']:
        doc_str = _format_doc_string(attr['doc'])
        params_list.append(f"doc={doc_str}")
    
    # metadata
    if attr.get('metadata'):
        # 在属性参数中使用，需要从 indent_level=2 开始
        metadata_str = _format_metadata(attr['metadata'], indent_level=2)
        params_list.append(f"metadata={metadata_str}")
    
    # 如果是保留字，需要添加 name 参数并使用 create_prop
    if is_reserved:
        params_list.insert(0, f'name="{sub_attr_name}"')
        params = ', '.join(params_list)
        
        # 如果有多行参数，需要换行格式化
        if '\n' in params or len(params) > 80:
            result = f"    {ns_prefix}.create_prop(Attribute({py_type}"
            result += ",\n"
            for i, param in enumerate(params_list):
                result += f"        {param}"
                if i < len(params_list) - 1:
                    result += ",\n"
                else:
                    result += "\n"
            result += "    ))"
            return result
        else:
            return f"    {ns_prefix}.create_prop(Attribute({py_type}, {params}))"
    else:
        params = ', '.join(params_list)
        
        # 如果有多行参数，需要换行格式化
        if '\n' in params or len(params) > 80:
            # 多行格式
            result = f"    {ns_prefix}.{sub_attr_name.replace(':', '.')} = Attribute({py_type}"
            if params_list:
                result += ",\n"
                for i, param in enumerate(params_list):
                    result += f"        {param}"
                    if i < len(params_list) - 1:
                        result += ",\n"
                    else:
                        result += "\n"
            result += "    )"
            return result
        else:
            # 单行格式
            return f"    {ns_prefix}.{sub_attr_name.replace(':', '.')} = Attribute({py_type}{', ' + params if params else ''})"


def _generate_attribute_definition(attr: dict) -> str:
    """生成属性定义"""
    # 转换 USD 类型到 Python 类型
    py_type = _usd_type_to_python_type(attr['type'])
    
    # 如果有 allowedTokens，使用生成的类名
    if attr.get('allowed_tokens'):
        class_name = _snake_to_pascal(attr['name'])
        py_type = class_name
    
    # 获取属性名
    attr_name = attr['name']
    
    # 检查是否与 Attribute/Property 类的属性名冲突
    reserved_attrs = {
        'type', 'name', 'value', 'uniform', 'metadata', 'parent_prim', 
        'parent_prop', 'is_leaf', 'full_name', 'path', 'value_state', 
        'custom', 'timeSamples', 'type_name', 'is_namespace'
    }
    is_reserved = attr_name in reserved_attrs
    if is_reserved:
        # 使用 create_prop 方法并传递 name 参数
        pass
    
    # 构建参数列表
    params_list = []
    
    # uniform 关键字
    if attr['is_uniform']:
        params_list.append("uniform=True")
    
    # default value - 转换为 Python 语法
    if attr['default_value'] is not None:
        py_value = _usd_value_to_python(attr['default_value'])
        params_list.append(f"value={py_value}")
    
    # doc
    if attr['doc']:
        doc_str = _format_doc_string(attr['doc'])
        params_list.append(f"doc={doc_str}")
    
    # metadata
    if attr.get('metadata'):
        # 在属性参数中使用，需要从 indent_level=2 开始
        metadata_str = _format_metadata(attr['metadata'], indent_level=2)
        params_list.append(f"metadata={metadata_str}")
    
    # 如果是保留字，需要添加 name 参数并使用 create_prop
    if is_reserved:
        params_list.insert(0, f'name="{attr_name}"')
        params = ', '.join(params_list)
        
        # 如果有多行参数，需要换行格式化
        if '\n' in params or len(params) > 80:
            result = f"    {attr_name}_ = create_prop(Attribute({py_type}"
            result += ",\n"
            for i, param in enumerate(params_list):
                result += f"        {param}"
                if i < len(params_list) - 1:
                    result += ",\n"
                else:
                    result += "\n"
            result += "    ))"
            return result
        else:
            return f"    {attr_name}_ = create_prop(Attribute({py_type}, {params}))"
    else:
        params = ', '.join(params_list)
        
        # 如果有多行参数，需要换行格式化
        if '\n' in params or len(params) > 80:
            # 多行格式
            result = f"    {attr_name}: Attribute[{py_type}] = Attribute({py_type}"
            if params_list:
                result += ",\n"
                for i, param in enumerate(params_list):
                    result += f"        {param}"
                    if i < len(params_list) - 1:
                        result += ",\n"
                    else:
                        result += "\n"
            result += "    )"
            return result
        else:
            # 单行格式
            return f"    {attr_name}: Attribute[{py_type}] = Attribute({py_type}{', ' + params if params else ''})"


def _generate_relationship_definition(rel: dict) -> str:
    """生成关系定义"""
    # 获取关系名
    rel_name = rel['name']
    
    # 检查是否与 Relationship/Property 类的属性名冲突
    reserved_attrs = {
        'type', 'name', 'value', 'uniform', 'metadata', 'parent_prim', 
        'parent_prop', 'is_leaf', 'full_name', 'path', 'value_state', 
        'custom', 'timeSamples', 'type_name', 'is_namespace'
    }
    if rel_name in reserved_attrs:
        # 添加下划线后缀避免冲突
        rel_name = rel_name + '_'
    
    params_list = []
    
    # doc
    if rel['doc']:
        doc_str = _format_doc_string(rel['doc'])
        params_list.append(f"doc={doc_str}")
    
    # metadata
    if rel.get('metadata'):
        # 在关系参数中使用，需要从 indent_level=2 开始
        metadata_str = _format_metadata(rel['metadata'], indent_level=2)
        params_list.append(f"metadata={metadata_str}")
    
    params = ', '.join(params_list)
    
    # 如果有多行参数，需要换行格式化
    if '\n' in params or len(params) > 80:
        # 多行格式
        result = f"    {rel_name}: Relationship = Relationship("
        if params_list:
            result += "\n"
            for i, param in enumerate(params_list):
                result += f"        {param}"
                if i < len(params_list) - 1:
                    result += ",\n"
                else:
                    result += "\n"
        result += "    )"
        return result
    else:
        # 单行格式
        return f"    {rel_name}: Relationship = Relationship({params})"


def _format_doc_string(doc: str) -> str:
    """格式化 doc 字符串"""
    # 处理转义字符
    doc = doc.replace('\\n', '\n').replace('\\"', '"')
    
    # 如果包含换行符，使用三引号并适当缩进
    if '\n' in doc:
        lines = doc.split('\n')
        result = '\n        """'
        for i, line in enumerate(lines):
            if i > 0:
                result += '\n'
            result += line
        result += '\n        """'
        return result
    else:
        # 单行使用双引号
        return f'"{doc}"'


def _format_metadata(metadata: dict, indent_level: int = 1) -> str:
    """格式化 metadata 字典为 Python 代码"""
    import json
    
    def format_value(value, current_indent_level=1):
        indent = '    ' * current_indent_level
        next_indent = '    ' * (current_indent_level + 1)
        
        if isinstance(value, dict):
            if not value:
                return '{}'
            items = []
            for k, v in value.items():
                formatted_v = format_value(v, current_indent_level + 1)
                items.append(f'{next_indent}"{k}": {formatted_v}')
            return '{\n' + ',\n'.join(items) + f'\n{indent}}}'
        elif isinstance(value, bool):
            return 'True' if value else 'False'
        elif isinstance(value, (int, float)):
            return str(value)
        elif isinstance(value, str):
            if '\n' in value:
                lines = value.split('\n')
                result = '"""'
                for i, line in enumerate(lines):
                    if i > 0:
                        result += '\n' + next_indent
                    result += line
                result += '"""'
                return result
            else:
                return f'"{value}"'
        elif isinstance(value, list):
            if not value:
                return '[]'
            items = [format_value(item, current_indent_level + 1) for item in value]
            return '[\n' + ',\n'.join([f'{next_indent}{item}' for item in items]) + f'\n{indent}]'
        else:
            return f'"{value}"'
    
    return format_value(metadata, indent_level)


def _usd_value_to_python(usd_value: str) -> str:
    """将 USD 值转换为 Python 值"""
    # 布尔值
    if usd_value == 'true':
        return 'True'
    elif usd_value == 'false':
        return 'False'
    
    # 无穷大
    if usd_value == 'inf' or usd_value == '-inf':
        return f"float('{usd_value}')"
    
    # 字符串
    if usd_value.startswith('"') or usd_value.startswith('"""'):
        return usd_value
    
    # 数组
    if usd_value.startswith('['):
        return usd_value
    
    # 数字和其他值
    return usd_value


def _usd_type_to_python_type(usd_type: str) -> str:
    """将 USD 类型转换为 Python 类型"""
    # 处理数组类型
    if usd_type.endswith('[]'):
        base_type = usd_type[:-2]
        py_base = _usd_scalar_type_to_python(base_type)
        return f"List[{py_base}]"
    
    return _usd_scalar_type_to_python(usd_type)


def _usd_scalar_type_to_python(usd_type: str) -> str:
    """将 USD 标量类型转换为 Python 类型"""
    type_map = {
        'bool': 'bool',
        'int': 'int',
        'float': 'float',
        'double': 'double',
        'half': 'half',
        'string': 'str',
        'token': 'token',
        'asset': 'asset',
        'path': 'path',
        'timecode': 'timecode',
        'matrix4d': 'matrix4d',
        'matrix3d': 'matrix3d',
        'quatd': 'quatd',
        'quatf': 'quatf',
        'vector3d': 'vector3d',
        'vector3f': 'vector3f',
        'point3d': 'point3d',
        'point3f': 'point3f',
        'normal3d': 'normal3d',
        'normal3f': 'normal3f',
        'color3d': 'color3d',
        'color3f': 'color3f',
        'color4d': 'color4d',
        'color4f': 'color4f',
        'float2': 'float2',
        'float3': 'float3',
        'float4': 'float4',
        'double2': 'double2',
        'double3': 'double3',
        'double4': 'double4',
        'int2': 'int2',
        'int3': 'int3',
        'int4': 'int4',
    }
    
    return type_map.get(usd_type, usd_type)


def _camel_to_snake(name: str) -> str:
    """将 CamelCase 转换为 snake_case"""
    import re
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def _snake_to_pascal(name: str) -> str:
    """将 snake_case 转换为 PascalCase"""
    return ''.join(word.capitalize() for word in name.split('_'))