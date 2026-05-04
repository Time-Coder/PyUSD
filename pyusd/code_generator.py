"""
USD Schema 代码生成器

通过解析 schema.usda 文件自动生成 Python 类。
"""

import os
import textwrap
from typing import List, Dict, Any, Set, Tuple, Optional
from tree_sitter import Node


class CodeGenerator:
    """USD Schema 代码生成器
    
    解析 schema.usda 文件并生成对应的 Python 类文件。
    
    Attributes:
        schema_path: schema.usda 文件的路径
        schema_dir: schema 文件所在目录
        classes_info: 存储所有类的信息
        class_names: 类名列表
    """
    
    def __init__(self, schema_path: str):
        """初始化代码生成器
        
        Args:
            schema_path: schema.usda 文件的路径
        """
        self.schema_path: str = schema_path
        self.schema_dir: str = os.path.dirname(schema_path)
        self.classes_info: Dict[str, Dict[str, Any]] = {}
        self.class_names: List[str] = []
        self._parsed: bool = False  # 标记是否已解析
        self._generated_ns_files: Set[str] = set()  # 已生成的命名空间文件
        
        # 初始化 parser
        from tree_sitter import Language, Parser
        import tree_sitter_usd
        
        lang = Language(tree_sitter_usd.language())
        self.parser: Parser = Parser(lang)
    
    def parse(self) -> None:
        """解析 schema.usda 文件，提取类信息
        
        如果已经解析过，则跳过解析过程。
        """
        if self._parsed:
            return
        
        # 读取并解析 schema 文件
        with open(self.schema_path, 'r', encoding='utf-8') as f:
            code = f.read().encode('utf-8')
        
        tree = self.parser.parse(code)
        
        # 遍历所有 prim_definition
        for child in tree.root_node.children:
            if child.type == 'prim_definition':
                class_info = self._parse_prim_definition(child)
                if class_info and class_info['name'].lower() != 'global':
                    self.classes_info[class_info['name']] = class_info
                    self.class_names.append(class_info['name'])
        
        self._parsed = True
    
    def generate_pyclasses(self) -> None:
        """生成所有 Python 类文件
        
        如果尚未解析，会自动调用 parse() 方法。
        为每个类生成对应的 .py 文件和 __init__.py。
        """
        # 如果没有解析过，自动调用 parse
        if not self._parsed:
            self.parse()
        
        # 第一步：为每个类生成 Python 文件
        for class_name in self.class_names:
            class_info = self.classes_info[class_name]
            self._generate_class_file(class_name, class_info)
        
        # 第二步：收集所有命名空间的成员
        namespace_members = self._collect_all_namespace_members()
        
        # 第三步：为每个命名空间生成 .pyi 文件
        for ns_prefix, members in namespace_members.items():
            ns_class_name = self._snake_to_pascal(ns_prefix)
            ns_file_name = self._camel_to_snake(ns_prefix) + '.pyi'
            ns_file_path = os.path.join(self.schema_dir, ns_file_name)
            
            # 生成命名空间类的 .pyi 文件
            ns_content = self._generate_namespace_pyi(ns_prefix, ns_class_name, members)
            with open(ns_file_path, 'w', encoding='utf-8') as f:
                f.write(ns_content)
            print(f"Generated namespace: {ns_file_path}")
            self._generated_ns_files.add(ns_prefix)
        
        # 第四步：重新生成所有类的 .pyi 文件（使用已生成的命名空间文件）
        for class_name in self.class_names:
            class_info = self.classes_info[class_name]
            base_class = self._determine_base_class(class_info)
            _, imported_token_classes = self._generate_token_classes(class_info['attributes'])
            self._regenerate_pyi_file(class_name, class_info, base_class, imported_token_classes)
        
        # 第五步：生成 __init__.py
        self._generate_init_file()
    
    def _collect_all_namespace_members(self) -> Dict[str, List[Dict[str, Any]]]:
        """收集所有类的命名空间成员"""
        namespace_members = {}
        
        for class_info in self.classes_info.values():
            # 收集属性
            for attr in class_info['attributes']:
                full_name = attr.get('full_name', attr['name'])
                if ':' in full_name:
                    ns_prefix = full_name.split(':')[0]
                    if ns_prefix not in namespace_members:
                        namespace_members[ns_prefix] = []
                    # 避免重复添加（使用 full_name 作为唯一标识）
                    if not any(m.get('full_name') == full_name for m in namespace_members[ns_prefix]):
                        namespace_members[ns_prefix].append(attr)
            
            # 收集关系
            for rel in class_info['relationships']:
                full_name = rel.get('full_name', rel['name'])
                if ':' in full_name:
                    ns_prefix = full_name.split(':')[0]
                    if ns_prefix not in namespace_members:
                        namespace_members[ns_prefix] = []
                    # 避免重复添加（使用 full_name 作为唯一标识）
                    if not any(m.get('full_name') == full_name for m in namespace_members[ns_prefix]):
                        namespace_members[ns_prefix].append(rel)
        
        return namespace_members
    
    def _regenerate_pyi_file(self, class_name: str, class_info: Dict[str, Any], base_class: str, imported_token_classes: List[str]) -> None:
        """重新生成 .pyi 文件（使用已生成的命名空间文件）"""
        # 生成主类的导入语句（不包含 SchemaKind）
        pyi_imports = self._generate_pyi_imports(base_class, class_info, imported_token_classes, self._generated_ns_files)
        
        # 生成类定义（只有签名，没有实现）
        pyi_class_def = self._generate_pyi_class_definition(class_name, base_class, class_info, self._generated_ns_files)
        
        # 组合内容
        content = pyi_imports + "\n\n" + pyi_class_def + "\n"
        
        # 写入 .pyi 文件
        file_name = self._camel_to_snake(class_name) + '.pyi'
        file_path = os.path.join(self.schema_dir, file_name)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _parse_prim_definition(self, node: Node) -> Dict[str, Any]:
        """解析 prim_definition 节点，提取类信息"""
        info = {
            'name': '',
            'kind': '',
            'has_explicit_name': False,
            'inherits': [],
            'doc': '',
            'custom_data': {},
            'metadata': {},
            'attributes': [],
            'relationships': [],
            'api_schemas': [],
        }
        
        for child in node.named_children:
            if child.type == 'prim_type':
                info['kind'] = child.text.decode('utf-8').strip()
            elif child.type == 'string':
                name = child.text.decode('utf-8').strip('"')
                info['name'] = name
                prev_sibling = child.prev_named_sibling
                if prev_sibling and prev_sibling.type == 'identifier':
                    info['has_explicit_name'] = True
            elif child.type == 'metadata':
                self._parse_metadata(child, info)
            elif child.type == 'block':
                self._parse_block(child, info)
        
        return info
    
    def _parse_metadata(self, node: Node, info: Dict[str, Any]) -> None:
        """解析元数据"""
        for child in node.named_children:
            if child.type == 'metadata_assignment':
                key = ''
                value = None
                value_dict = None
                for assign_child in child.named_children:
                    if assign_child.type == 'identifier':
                        key = assign_child.text.decode('utf-8')
                    elif assign_child.type == 'string':
                        value = assign_child.text.decode('utf-8').strip('"')
                    elif assign_child.type == 'dictionary':
                        value_dict = self._parse_usd_dictionary(assign_child)
                
                if key == 'documentation' or key == 'doc':
                    info['doc'] = value or ''
                elif key == 'customData' and value_dict:
                    info['custom_data'] = value_dict
                    # 同时保存到 metadata
                    if not info.get('metadata'):
                        info['metadata'] = {}
                    info['metadata']['customData'] = value_dict
            elif child.type == 'attribute_assignment':
                self._parse_attribute_assignment(child, info)
    
    def _parse_attribute_assignment(self, node: Node, info: Dict[str, Any]) -> None:
        """解析属性赋值"""
        key = ''
        value = None
        
        for child in node.named_children:
            if child.type == 'identifier':
                key = child.text.decode('utf-8')
            elif child.type == 'string':
                value = child.text.decode('utf-8').strip('"')
            elif child.type == 'array':
                value = self._parse_usd_array(child)
            elif child.type == 'dictionary':
                value = self._parse_usd_dictionary(child)
        
        if key == 'apiSchemas' and isinstance(value, list):
            info['api_schemas'] = value
    
    def _parse_block(self, node: Node, info: Dict[str, Any]) -> None:
        """解析块内容（属性、关系等）"""
        for child in node.named_children:
            if child.type in ['attribute_declaration', 'attribute_assignment']:
                attr_info = self._parse_attribute_declaration(child)
                if attr_info:
                    info['attributes'].append(attr_info)
            elif child.type == 'relationship_declaration':
                rel_info = self._parse_relationship_declaration(child)
                if rel_info:
                    info['relationships'].append(rel_info)
            elif child.type == 'metadata_assignment':
                self._parse_custom_data_assignment(child, info)
    
    def _parse_custom_data_assignment(self, node: Node, info: Dict[str, Any]) -> None:
        """解析 customData 赋值"""
        key = ''
        for child in node.named_children:
            if child.type == 'identifier':
                key = child.text.decode('utf-8')
            elif child.type == 'dictionary' and key == 'customData':
                info['custom_data'] = self._parse_usd_dictionary(child)
                # 同时保存到 metadata
                if info['custom_data']:
                    info['metadata']['customData'] = info['custom_data']
    
    def _parse_attribute_declaration(self, node: Node) -> Dict[str, Any]:
        """解析属性声明"""
        attr_info = {
            'name': '',
            'full_name': '',
            'type': '',
            'is_uniform': False,
            'default_value': None,
            'doc': '',
            'allowed_tokens': [],
            'api_name': '',
            'metadata': {},
        }
        
        for child in node.named_children:
            if child.type == 'attribute_type':
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
            elif child.type == 'uniform':
                attr_info['is_uniform'] = True
            elif child.type == 'default_value':
                attr_info['default_value'] = self._parse_default_value(child)
            elif child.type == 'metadata':
                self._parse_attribute_metadata(child, attr_info)
        
        return attr_info
    
    def _parse_default_value(self, node: Node) -> Any:
        """解析默认值"""
        for child in node.named_children:
            if child.type == 'string':
                return child.text.decode('utf-8').strip('"')
            elif child.type == 'bool':
                return child.text.decode('utf-8') == 'true'
            elif child.type == 'int':
                return int(child.text.decode('utf-8'))
            elif child.type == 'float':
                text = child.text.decode('utf-8')
                if text == 'inf':
                    return float('inf')
                elif text == '-inf':
                    return float('-inf')
                return float(text)
            elif child.type == 'array':
                return self._parse_usd_array(child)
            elif child.type == 'dictionary':
                return self._parse_usd_dictionary(child)
        return None
    
    def _parse_attribute_metadata(self, node: Node, attr_info: Dict[str, Any]) -> None:
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
                        custom_data = self._parse_usd_dictionary(assign_child)
                        if 'apiName' in custom_data:
                            attr_info['api_name'] = custom_data['apiName']
                        if custom_data:
                            attr_info['metadata']['customData'] = custom_data
                    elif key not in ['doc', 'allowedTokens']:
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
                            value = self._parse_usd_array(assign_child)
                        elif assign_child.type == 'dictionary':
                            value = self._parse_usd_dictionary(assign_child)
                        
                        if value is not None:
                            attr_info['metadata'][key] = value
    
    def _parse_relationship_declaration(self, node: Node) -> Dict[str, Any]:
        """解析关系声明"""
        rel_info = {
            'name': '',
            'full_name': '',
            'doc': '',
            'api_name': '',
            'metadata': {},
        }
        
        for child in node.named_children:
            if child.type == 'identifier' or child.type == 'qualified_identifier':
                full_name = child.text.decode('utf-8')
                rel_info['full_name'] = full_name
                # 如果有冒号，提取最后一部分作为 Python 关系名
                if ':' in full_name:
                    rel_info['name'] = full_name.split(':')[-1]
                else:
                    rel_info['name'] = full_name
            elif child.type == 'metadata':
                self._parse_relationship_metadata(child, rel_info)
        
        return rel_info
    
    def _parse_relationship_metadata(self, node: Node, rel_info: Dict[str, Any]) -> None:
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
                        custom_data = self._parse_usd_dictionary(assign_child)
                        if 'apiName' in custom_data:
                            rel_info['api_name'] = custom_data['apiName']
                        if custom_data:
                            rel_info['metadata']['customData'] = custom_data
                    elif key != 'doc':
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
                            value = self._parse_usd_array(assign_child)
                        elif assign_child.type == 'dictionary':
                            value = self._parse_usd_dictionary(assign_child)
                        
                        if value is not None:
                            rel_info['metadata'][key] = value
    
    def _parse_usd_array(self, node: Node) -> List[Any]:
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
                text = child.text.decode('utf-8')
                if text == 'inf':
                    result.append(float('inf'))
                elif text == '-inf':
                    result.append(float('-inf'))
                else:
                    result.append(float(text))
        return result
    
    def _parse_usd_dictionary(self, node: Node) -> Dict[str, Any]:
        """解析 USD 格式的字典"""
        result = {}
        
        for child in node.named_children:
            if child.type == 'dictionary_item':
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
                        text = item_child.text.decode('utf-8')
                        if text == 'inf':
                            value = float('inf')
                        elif text == '-inf':
                            value = float('-inf')
                        else:
                            value = float(text)
                    elif item_child.type == 'array':
                        value = self._parse_usd_array(item_child)
                    elif item_child.type == 'dictionary':
                        value = self._parse_usd_dictionary(item_child)
                
                if key:
                    result[key] = value
            elif child.type == 'attribute_type':
                attr_type = child.text.decode('utf-8')
                key = ''
                value = None
                
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
                        text = next_sibling.text.decode('utf-8')
                        if text == 'inf':
                            value = float('inf')
                        elif text == '-inf':
                            value = float('-inf')
                        else:
                            value = float(text)
                        break
                    elif next_sibling.type == 'array' and key and value is None:
                        value = self._parse_usd_array(next_sibling)
                        break
                    elif next_sibling.type == 'dictionary' and key and value is None:
                        value = self._parse_usd_dictionary(next_sibling)
                        break
                    
                    next_sibling = next_sibling.next_named_sibling
                
                if key:
                    result[key] = value
        
        return result
    
    def _determine_base_class(self, class_info: Dict[str, Any]) -> str:
        """确定基类"""
        kind = class_info['kind']
        has_explicit_name = class_info['has_explicit_name']
        api_schemas = class_info.get('api_schemas', [])
        
        # API schemas
        if kind == 'class' and not has_explicit_name:
            # AbstractTyped API schema
            api_schema_type = class_info.get('custom_data', {}).get('apiSchemaType', '')
            if api_schema_type == 'nonAppliedAPI':
                return 'APISchemaBase'
            elif api_schema_type == 'singleApplyAPI':
                return 'APISchemaBase'
            elif api_schema_type == 'multipleApplyAPI':
                return 'APISchemaBase'
            return 'APISchemaBase'
        
        # Typed schemas
        if kind == 'class' and has_explicit_name:
            return 'Typed'
        
        # Inherits
        inherits = class_info.get('inherits', [])
        if inherits:
            parent_name = inherits[0]
            if '/' in parent_name:
                parent_name = parent_name.split('/')[-1]
            
            # 特殊处理已知基类
            base_class_mapping = {
                'APISchemaBase': 'APISchemaBase',
                'Typed': 'Typed',
                'Imageable': 'Imageable',
                'Gprim': 'Gprim',
                'Boundable': 'Boundable',
                'Xformable': 'Xformable',
                'PointBased': 'PointBased',
                'GeomSubset': 'GeomSubset',
            }
            
            if parent_name in base_class_mapping:
                return base_class_mapping[parent_name]
            
            # 跨模块继承
            cross_module_bases = {
                'Imageable': ('geom', 'Imageable'),
                'Gprim': ('geom', 'Gprim'),
                'Boundable': ('geom', 'Boundable'),
                'Xformable': ('geom', 'Xformable'),
                'PointBased': ('geom', 'PointBased'),
                'GeomModelAPI': ('geom', 'GeomModelAPI'),
                'PrimvarsAPI': ('geom', 'PrimvarsAPI'),
                'VisibilityAPI': ('geom', 'VisibilityAPI'),
                'MotionAPI': ('geom', 'MotionAPI'),
                'XformCommonAPI': ('geom', 'XformCommonAPI'),
            }
            
            if parent_name in cross_module_bases:
                return parent_name
        
        return 'Typed'
    
    def _determine_schema_kind(self, class_info: Dict[str, Any]) -> str:
        """确定 schema_kind"""
        kind = class_info['kind']
        has_explicit_name = class_info['has_explicit_name']
        
        # API schemas
        if kind == 'class' and not has_explicit_name:
            api_schema_type = class_info.get('custom_data', {}).get('apiSchemaType', '')
            if api_schema_type == 'nonAppliedAPI':
                return 'SchemaKind.NonAppliedAPI'
            elif api_schema_type == 'singleApplyAPI':
                return 'SchemaKind.SingleApplyAPI'
            elif api_schema_type == 'multipleApplyAPI':
                return 'SchemaKind.MultipleApplyAPI'
            return 'SchemaKind.NonAppliedAPI'
        
        # Typed schemas
        if kind == 'class' and has_explicit_name:
            return 'SchemaKind.ConcreteTyped'
        
        return 'SchemaKind.AbstractTyped'
    
    def _generate_class_file(self, class_name: str, class_info: Dict[str, Any]) -> None:
        """生成单个类的 Python 文件和对应的 .pyi 文件"""
        base_class = self._determine_base_class(class_info)
        
        # 生成导入语句
        imports = self._generate_imports(base_class, class_info)
        
        # 检查是否有需要从 common.py 导入的枚举类
        _, imported_token_classes = self._generate_token_classes(class_info['attributes'])
        if imported_token_classes:
            imports += f"\nfrom ..common import {', '.join(sorted(set(imported_token_classes)))}"
        
        # 生成类定义
        class_def = self._generate_class_definition(class_info)
        
        # 组合完整内容
        content = imports + "\n\n" + class_def + "\n"
        
        # 写入 .py 文件
        file_name = self._camel_to_snake(class_name) + '.py'
        file_path = os.path.join(self.schema_dir, file_name)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Generated: {file_path}")
        
        # 生成对应的 .pyi 文件
        self._generate_pyi_file(class_name, class_info, base_class, imported_token_classes)
    
    def _generate_pyi_file(self, class_name: str, class_info: Dict[str, Any], base_class: str, imported_token_classes: List[str]) -> None:
        """生成类型存根文件 (.pyi) - 第一遍生成（不包含命名空间导入）"""
        # 生成主类的导入语句（不包含 SchemaKind 和命名空间导入）
        pyi_imports = self._generate_pyi_imports(base_class, class_info, imported_token_classes, set())
        
        # 生成类定义（只有签名，没有实现）
        pyi_class_def = self._generate_pyi_class_definition(class_name, base_class, class_info, set())
        
        # 组合内容
        content = pyi_imports + "\n\n" + pyi_class_def + "\n"
        
        # 写入 .pyi 文件
        file_name = self._camel_to_snake(class_name) + '.pyi'
        file_path = os.path.join(self.schema_dir, file_name)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _generate_namespace_pyi(self, ns_prefix: str, ns_class_name: str, members: List[Dict[str, Any]]) -> str:
        """生成命名空间类的 .pyi 文件内容"""
        lines = []
        
        # 收集需要的导入
        imports = ["from ..attribute import Attribute", "from ..relationship import Relationship"]
        needed_types = set()
        
        for member in members:
            if 'type' in member:  # 是属性
                py_type = self._usd_type_to_python_type(member['type'])
                self._collect_needed_types(py_type, needed_types)
        
        # 添加 gf 和 dtypes 导入
        gf_types = {
            'double2', 'double3', 'double4',
            'vector3d', 'color3d', 'color4d',
            'float2', 'float3', 'float4',
            'vector3f', 'color3f', 'color4f',
            'texCoord2d', 'texCoord3d',
            'texCoord2f', 'texCoord3f',
            'point3f', 'point3d', 'normal3d', 'normal3f',
            'int2', 'int3', 'int4',
            'matrix2d', 'matrix3d', 'matrix4d', 'frame4d',
            'quath', 'quatf', 'quatd',
        }
        dtypes_types = {'double', 'half', 'int64', 'string', 'token', 'pathExpression', 'timecode', 'uchar', 'uint', 'uint64', 'asset', 'dictionary'}
        
        gf_imports = sorted(needed_types & gf_types)
        dtypes_imports = sorted(needed_types & dtypes_types)
        
        if gf_imports:
            imports.append(f"from ..gf import {', '.join(gf_imports)}")
        if dtypes_imports:
            imports.append(f"from ..dtypes import {', '.join(dtypes_imports)}")
        
        imports.append("from typing import List")
        
        # 类声明
        lines.append("\n".join(imports))
        lines.append("")
        lines.append("")
        lines.append(f"class {ns_class_name}(Attribute):")
        
        # 生成 allowedTokens 对应的枚举类
        token_classes, _ = self._generate_token_classes(members)
        if token_classes:
            lines.append("")
            lines.extend(token_classes)
        
        lines.append("")
        
        # 生成子属性和关系的签名
        for member in members:
            if 'type' in member:  # 是属性
                lines.extend(self._generate_pyi_attribute_signature('', member, is_sub_attr=True))
            else:  # 是关系
                lines.extend(self._generate_pyi_relationship_signature(ns_prefix, member))
        
        return "\n".join(lines)
    
    def _generate_pyi_imports(self, base_class: str, class_info: Dict[str, Any], imported_token_classes: List[str], generated_ns_files: Set[str] = None) -> str:
        """生成 .pyi 文件的导入语句"""
        imports = []
        
        # 基类导入
        if base_class in ['Typed', 'APISchemaBase']:
            if base_class == 'Typed':
                imports.append("from ..typed import Typed")
            else:
                imports.append("from ..api_schema_base import APISchemaBase")
        else:
            # 跨模块继承
            cross_module_bases = {
                'Imageable': ('geom', 'Imageable'),
                'Gprim': ('geom', 'Gprim'),
                'Boundable': ('geom', 'Boundable'),
                'Xformable': ('geom', 'Xformable'),
                'PointBased': ('geom', 'PointBased'),
                'GeomModelAPI': ('geom', 'GeomModelAPI'),
                'PrimvarsAPI': ('geom', 'PrimvarsAPI'),
                'VisibilityAPI': ('geom', 'VisibilityAPI'),
                'MotionAPI': ('geom', 'MotionAPI'),
                'XformCommonAPI': ('geom', 'XformCommonAPI'),
            }
            
            if base_class in cross_module_bases:
                module, cls = cross_module_bases[base_class]
                imports.append(f"from ..{module}.{self._camel_to_snake(cls)} import {cls}")
            else:
                imports.append(f"from .{self._camel_to_snake(base_class)} import {base_class}")
        
        # 添加常用导入
        if class_info['attributes'] or class_info['relationships']:
            imports.append("from ..attribute import Attribute")
            if class_info['relationships']:
                imports.append("from ..relationship import Relationship")
            
            # 收集所有需要的类型
            needed_types = set()
            for attr in class_info['attributes']:
                py_type = self._usd_type_to_python_type(attr['type'])
                if attr.get('allowed_tokens'):
                    class_name = self._snake_to_pascal(attr['name'])
                    py_type = class_name
                self._collect_needed_types(py_type, needed_types)
            
            # 检查是否需要 namespace 类型
            has_namespace = any(attr.get('full_name', '').count(':') > 0 for attr in class_info['attributes'])
            if has_namespace:
                needed_types.add('namespace')
            
            # 检查是否有 allowedTokens，需要导入 token
            has_allowed_tokens = any(attr.get('allowed_tokens') for attr in class_info['attributes'])
            if has_allowed_tokens:
                needed_types.add('token')
            
            # 生成 gf 和 dtypes 导入
            gf_types = {'matrix2d', 'matrix3d', 'matrix4d', 'matrix2f', 'matrix3f', 'matrix4f',
                       'quatd', 'quatf', 'quath', 'double2', 'double3', 'double4',
                       'float2', 'float3', 'float4', 'int2', 'int3', 'int4',
                       'half', 'vector3f', 'vector3d'}
            dtypes_types = {'token', 'namespace', 'string', 'asset', 'timecode', 'dictionary'}
            
            gf_imports = sorted(needed_types & gf_types)
            dtypes_imports = sorted(needed_types & dtypes_types)
            
            if gf_imports:
                imports.append(f"from ..gf import {', '.join(gf_imports)}")
            if dtypes_imports:
                imports.append(f"from ..dtypes import {', '.join(dtypes_imports)}")
        
        # 添加从 common 导入的枚举类
        if imported_token_classes:
            imports.append(f"from ..common import {', '.join(sorted(set(imported_token_classes)))}")
        
        # 添加命名空间类的导入
        if generated_ns_files:
            for ns_prefix in sorted(generated_ns_files):
                ns_class_name = self._snake_to_pascal(ns_prefix)
                imports.append(f"from .{self._camel_to_snake(ns_prefix)} import {ns_class_name}")
        
        return "\n".join(imports)
    
    def _generate_imports(self, base_class: str, class_info: Dict[str, Any]) -> str:
        """生成导入语句"""
        imports = []
        
        # 基类导入
        if base_class in ['Typed', 'APISchemaBase']:
            if base_class == 'Typed':
                imports.append("from ..typed import Typed")
            else:
                imports.append("from ..api_schema_base import APISchemaBase")
        else:
            # 跨模块继承
            cross_module_bases = {
                'Imageable': ('geom', 'Imageable'),
                'Gprim': ('geom', 'Gprim'),
                'Boundable': ('geom', 'Boundable'),
                'Xformable': ('geom', 'Xformable'),
                'PointBased': ('geom', 'PointBased'),
                'GeomModelAPI': ('geom', 'GeomModelAPI'),
                'PrimvarsAPI': ('geom', 'PrimvarsAPI'),
                'VisibilityAPI': ('geom', 'VisibilityAPI'),
                'MotionAPI': ('geom', 'MotionAPI'),
                'XformCommonAPI': ('geom', 'XformCommonAPI'),
            }
            
            if base_class in cross_module_bases:
                module, cls = cross_module_bases[base_class]
                imports.append(f"from ..{module}.{self._camel_to_snake(cls)} import {cls}")
            else:
                imports.append(f"from .{self._camel_to_snake(base_class)} import {base_class}")
        
        # 添加常用导入
        if class_info['attributes'] or class_info['relationships']:
            imports.append("from ..attribute import Attribute")
            if class_info['relationships']:
                imports.append("from ..relationship import Relationship")
            
            # 检查是否需要 List（只有当有数组类型属性时才需要）
            has_array = any(attr['type'].endswith('[]') for attr in class_info['attributes'])
            if has_array:
                imports.append("from typing import List")
            
            # 检查是否需要 namespace 类型（属性或关系有命名空间前缀）
            has_namespace_attrs = any(attr.get('full_name', '').count(':') > 0 for attr in class_info['attributes'])
            has_namespace_rels = any(rel.get('full_name', '').count(':') > 0 for rel in class_info['relationships'])
            if has_namespace_attrs or has_namespace_rels:
                imports.append("from ..dtypes import namespace")
            
            # 收集所有需要的类型
            needed_types = set()
            for attr in class_info['attributes']:
                py_type = self._usd_type_to_python_type(attr['type'])
                if attr.get('allowed_tokens'):
                    class_name = self._snake_to_pascal(attr['name'])
                    py_type = class_name
                self._collect_needed_types(py_type, needed_types)
            
            # 检查是否有 allowedTokens，需要导入 token
            has_allowed_tokens = any(attr.get('allowed_tokens') for attr in class_info['attributes'])
            if has_allowed_tokens:
                needed_types.add('token')
            
            # 添加 gf 类型导入
            gf_types = {
                'double2', 'double3', 'double4',
                'vector3d', 'color3d', 'color4d',
                'float2', 'float3', 'float4',
                'vector3f', 'color3f', 'color4f',
                'texCoord2d', 'texCoord3d',
                'texCoord2f', 'texCoord3f',
                'point3f', 'point3d', 'normal3d', 'normal3f',
                'int2', 'int3', 'int4',
                'matrix2d', 'matrix3d', 'matrix4d', 'frame4d',
                'quath', 'quatf', 'quatd',
            }
            
            needed_gf_types = needed_types & gf_types
            if needed_gf_types:
                imports.append(f"from ..gf import {', '.join(sorted(needed_gf_types))}")
            
            # 添加 dtypes 导入
            dtypes_types = {'double', 'half', 'int64', 'string', 'token', 'pathExpression', 'timecode', 'uchar', 'uint', 'uint64', 'asset', 'dictionary', 'namespace'}
            needed_dtype_types = needed_types & dtypes_types
            if needed_dtype_types:
                imports.append(f"from ..dtypes import {', '.join(sorted(needed_dtype_types))}")
        
        # 添加 SchemaKind 导入
        imports.append("from ..common import SchemaKind")
        
        return "\n".join(imports)
    
    def _collect_needed_types(self, py_type: str, needed_types: Set[str]) -> None:
        """收集需要的类型"""
        if py_type.startswith('List['):
            inner_type = py_type[5:-1]
            self._collect_needed_types(inner_type, needed_types)
        else:
            needed_types.add(py_type)
    
    def _generate_class_definition(self, class_info: Dict[str, Any]) -> str:
        """生成类定义"""
        lines = []
        
        # 类声明
        lines.append(f"class {class_info['name']}({self._determine_base_class(class_info)}):")
        
        # docstring（类级别使用 4 空格缩进）
        if class_info['doc']:
            doc_str = self._format_class_doc_string(class_info['doc'])
            lines.append(doc_str)
            lines.append("")  # docstring 后加空行
        
        # schema_kind
        schema_kind = self._determine_schema_kind(class_info)
        lines.append(f"    schema_kind: SchemaKind = {schema_kind}")
        
        # 如果有 metadata，添加 meta
        if class_info.get('metadata'):
            lines.append("")
            meta_str = self._format_metadata(class_info['metadata'], indent_level=0)
            meta_lines = meta_str.split('\n')
            for i, line in enumerate(meta_lines):
                if i == 0:
                    lines.append(f"    meta = {line}")
                else:
                    lines.append(f"    {line}")
        
        # 生成 allowedTokens 对应的枚举类
        token_classes, imported_token_classes = self._generate_token_classes(class_info['attributes'])
        if token_classes:
            lines.append("")
            lines.extend(token_classes)
        
        # 按命名空间分组属性
        namespaced_attrs = {}
        regular_attrs = []
        
        for attr in class_info['attributes']:
            full_name = attr.get('full_name', attr['name'])
            if ':' in full_name:
                ns_prefix = full_name.split(':')[0]
                if ns_prefix not in namespaced_attrs:
                    namespaced_attrs[ns_prefix] = []
                namespaced_attrs[ns_prefix].append(attr)
            else:
                regular_attrs.append(attr)
        
        # 生成命名空间属性
        for ns_prefix, attrs in namespaced_attrs.items():
            lines.append("")
            lines.append(f"    {ns_prefix}: Attribute[namespace] = Attribute(namespace, is_leaf=False)")
            
            for attr in attrs:
                lines.append(self._generate_namespaced_attribute_definition(ns_prefix, attr))
        
        # 生成普通属性
        for attr in regular_attrs:
            lines.append("")
            lines.append(self._generate_attribute_definition(attr))
        
        # 按命名空间分组关系
        namespaced_rels = {}
        regular_rels = []
        
        for rel in class_info['relationships']:
            full_name = rel.get('full_name', rel['name'])
            if ':' in full_name:
                ns_prefix = full_name.split(':')[0]
                if ns_prefix not in namespaced_rels:
                    namespaced_rels[ns_prefix] = []
                namespaced_rels[ns_prefix].append(rel)
            else:
                regular_rels.append(rel)
        
        # 生成命名空间关系
        for ns_prefix, rels in namespaced_rels.items():
            # 检查是否已经生成了该命名空间的属性声明
            has_ns_attr = any(f"{ns_prefix}: Attribute[namespace]" in line for line in lines)
            if not has_ns_attr:
                lines.append("")
                lines.append(f"    {ns_prefix}: Attribute[namespace] = Attribute(namespace, is_leaf=False)")
            
            for rel in rels:
                lines.append(self._generate_namespaced_relationship_definition(ns_prefix, rel))
        
        # 生成普通关系
        for rel in regular_rels:
            lines.append("")
            lines.append(self._generate_relationship_definition(rel))
        
        return "\n".join(lines)
    
    def _generate_pyi_class_definition(self, class_name: str, base_class: str, class_info: Dict[str, Any], generated_ns_files: Set[str] = None) -> str:
        """生成 .pyi 文件的类定义（只有签名）"""
        lines = []
        
        # 类声明
        lines.append(f"class {class_name}({base_class}):")
        
        # docstring
        if class_info['doc']:
            doc_str = self._format_class_doc_string(class_info['doc'])
            lines.append(doc_str)
            lines.append("")  # docstring 后加空行
        
        # 生成 allowedTokens 对应的枚举类
        token_classes, _ = self._generate_token_classes(class_info['attributes'])
        if token_classes:
            lines.append("")
            lines.extend(token_classes)
        
        # 按命名空间分组属性和关系
        namespaced_attrs = {}
        regular_attrs = []
        namespaced_rels = {}
        regular_rels = []
        
        for attr in class_info['attributes']:
            full_name = attr.get('full_name', attr['name'])
            if ':' in full_name:
                ns_prefix = full_name.split(':')[0]
                if ns_prefix not in namespaced_attrs:
                    namespaced_attrs[ns_prefix] = []
                namespaced_attrs[ns_prefix].append(attr)
            else:
                regular_attrs.append(attr)
        
        for rel in class_info['relationships']:
            full_name = rel.get('full_name', rel['name'])
            if ':' in full_name:
                ns_prefix = full_name.split(':')[0]
                if ns_prefix not in namespaced_rels:
                    namespaced_rels[ns_prefix] = []
                namespaced_rels[ns_prefix].append(rel)
            else:
                regular_rels.append(rel)
        
        # 合并命名空间的属性和关系
        all_namespaced = set(list(namespaced_attrs.keys()) + list(namespaced_rels.keys()))
        
        # 生成命名空间属性的签名
        for ns_prefix in all_namespaced:
            attrs = namespaced_attrs.get(ns_prefix, [])
            rels = namespaced_rels.get(ns_prefix, [])
            
            # 如果生成了独立的命名空间文件，使用命名空间类进行注解
            if generated_ns_files and ns_prefix in generated_ns_files:
                ns_class_name = self._snake_to_pascal(ns_prefix)
                lines.append(f"    @property")
                lines.append(f"    def {ns_prefix}(self) -> {ns_class_name}: ...")
                lines.append("")
            else:
                # 否则为每个子属性/关系生成单独的签名
                for attr in attrs:
                    lines.extend(self._generate_pyi_attribute_signature(ns_prefix, attr))
                for rel in rels:
                    lines.extend(self._generate_pyi_relationship_signature(ns_prefix, rel))
        
        # 生成普通属性的签名
        for attr in regular_attrs:
            lines.extend(self._generate_pyi_attribute_signature('', attr))
        
        # 生成普通关系的签名
        for rel in regular_rels:
            lines.extend(self._generate_pyi_relationship_signature('', rel))
        
        # 如果类定义没有任何内容，添加 pass
        if len(lines) == 1:  # 只有类声明行
            lines.append("    pass")
        
        return "\n".join(lines)
    
    def _generate_pyi_attribute_signature(self, ns_prefix: str, attr: Dict[str, Any], is_sub_attr: bool = False) -> List[str]:
        """生成属性的 @property 和 setter 签名"""
        lines = []
        
        # 获取属性名
        full_name = attr.get('full_name', attr['name'])
        if ':' in full_name and ns_prefix:
            attr_name = ':'.join(full_name.split(':')[1:])
            attr_name = attr_name.replace(':', '.')
        else:
            attr_name = attr['name']
        
        # 转换类型
        py_type = self._usd_type_to_python_type(attr['type'])
        
        # 如果有 allowedTokens，使用生成的类名
        if attr.get('allowed_tokens'):
            class_name = self._snake_to_pascal(attr['name'])
            py_type = class_name
        
        # 检查是否与 Attribute/Property 类的属性名冲突
        reserved_attrs = {
            'type', 'name', 'value', 'uniform', 'metadata', 'parent_prim', 
            'parent_prop', 'is_leaf', 'full_name', 'path', 'value_state', 
            'custom', 'timeSamples', 'type_name', 'is_namespace'
        }
        is_reserved = attr_name in reserved_attrs
        
        # 如果是保留字，跳过（在 .pyi 中不生成）
        if is_reserved:
            return []
        
        # 生成 docstring
        doc_lines = []
        if attr['doc']:
            doc_lines.append(f'        """{attr["doc"]}"""')
        
        # 生成 @property getter
        lines.append(f"    @property")
        lines.append(f"    def {attr_name}(self)->Attribute[{py_type}]:")
        if doc_lines:
            lines.extend(doc_lines)
        else:
            lines.append("        ...")
        lines.append("")
        
        # 生成 setter
        lines.append(f"    @{attr_name}.setter")
        lines.append(f"    def {attr_name}(self, value:{py_type})->None: ...")
        lines.append("")
        
        return lines
    
    def _generate_pyi_relationship_signature(self, ns_prefix: str, rel: Dict[str, Any]) -> List[str]:
        """生成关系的 @property 和 setter 签名"""
        lines = []
        
        # 获取关系名
        full_name = rel.get('full_name', rel['name'])
        if ':' in full_name and ns_prefix:
            rel_name = ':'.join(full_name.split(':')[1:])
            rel_name = rel_name.replace(':', '.')
        else:
            rel_name = rel['name']
        
        # 生成 docstring
        doc_lines = []
        if rel['doc']:
            doc_lines.append(f'        """{rel["doc"]}"""')
        
        # 生成 @property getter
        lines.append(f"    @property")
        lines.append(f"    def {rel_name}(self)->Relationship:")
        if doc_lines:
            lines.extend(doc_lines)
        else:
            lines.append("        ...")
        lines.append("")
        
        # 生成 setter
        lines.append(f"    @{rel_name}.setter")
        lines.append(f"    def {rel_name}(self, value:Relationship)->None: ...")
        lines.append("")
        
        return lines
    
    def _generate_token_classes(self, attributes: List[Dict[str, Any]]) -> Tuple[List[str], List[str]]:
        """为有 allowedTokens 的属性生成 token 枚举类"""
        lines = []
        imported_classes = []
        
        # common.py 中已定义的枚举类
        common_enums = {'Axis', 'Kind'}
        
        for attr in attributes:
            if attr.get('allowed_tokens'):
                class_name = self._snake_to_pascal(attr['name'])
                
                if class_name in common_enums:
                    imported_classes.append(class_name)
                else:
                    lines.append(f"    class {class_name}(token):")
                    
                    for token_value in attr['allowed_tokens']:
                        const_name = self._token_to_constant(token_value)
                        lines.append(f"        {const_name} = \"{token_value}\"")
                    
                    lines.append("")
        
        return lines, imported_classes
    
    def _generate_namespaced_attribute_definition(self, ns_prefix: str, attr: Dict[str, Any]) -> str:
        """生成命名空间属性的子属性定义"""
        py_type = self._usd_type_to_python_type(attr['type'])
        
        # 如果有 allowedTokens，使用生成的类名
        if attr.get('allowed_tokens'):
            class_name = self._snake_to_pascal(attr['name'])
            py_type = class_name
        
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
        
        params_list = []
        if attr['is_uniform']:
            params_list.append("uniform=True")
        if attr['default_value'] is not None:
            py_value = self._usd_value_to_python(attr['default_value'])
            params_list.append(f"value={py_value}")
        if attr['doc']:
            doc_str = self._format_doc_string(attr['doc'])
            params_list.append(f"doc={doc_str}")
        if attr.get('metadata'):
            metadata_str = self._format_metadata(attr['metadata'], indent_level=2)
            params_list.append(f"metadata={metadata_str}")
        
        # 如果是保留字，使用 create_prop 方法
        if is_reserved:
            params_list.insert(0, f'name="{sub_attr_name}"')
            params = ', '.join(params_list)
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
            if '\n' in params or len(params) > 80:
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
                return f"    {ns_prefix}.{sub_attr_name.replace(':', '.')} = Attribute({py_type}{', ' + params if params else ''})"
    
    def _generate_attribute_definition(self, attr: Dict[str, Any]) -> str:
        """生成属性定义"""
        py_type = self._usd_type_to_python_type(attr['type'])
        
        # 如果有 allowedTokens，使用生成的类名
        if attr.get('allowed_tokens'):
            class_name = self._snake_to_pascal(attr['name'])
            py_type = class_name
        
        attr_name = attr['name']
        
        # 检查是否与 Attribute/Property 类的属性名冲突
        reserved_attrs = {
            'type', 'name', 'value', 'uniform', 'metadata', 'parent_prim', 
            'parent_prop', 'is_leaf', 'full_name', 'path', 'value_state', 
            'custom', 'timeSamples', 'type_name', 'is_namespace'
        }
        is_reserved = attr_name in reserved_attrs
        
        params_list = []
        if attr['is_uniform']:
            params_list.append("uniform=True")
        if attr['default_value'] is not None:
            py_value = self._usd_value_to_python(attr['default_value'])
            params_list.append(f"value={py_value}")
        if attr['doc']:
            doc_str = self._format_doc_string(attr['doc'])
            params_list.append(f"doc={doc_str}")
        if attr.get('metadata'):
            metadata_str = self._format_metadata(attr['metadata'], indent_level=2)
            params_list.append(f"metadata={metadata_str}")
        
        # 如果是保留字，使用 create_prop 方法
        if is_reserved:
            params_list.insert(0, f'name="{attr_name}"')
            params = ', '.join(params_list)
            if '\n' in params or len(params) > 80:
                result = f"    {attr_name}.create_prop(Attribute({py_type}"
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
                return f"    {attr_name}.create_prop(Attribute({py_type}, {params}))"
        else:
            params = ', '.join(params_list)
            if '\n' in params or len(params) > 80:
                result = f"    {attr_name} = Attribute({py_type}"
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
                return f"    {attr_name} = Attribute({py_type}{', ' + params if params else ''})"
    
    def _generate_relationship_definition(self, rel: Dict[str, Any]) -> str:
        """生成关系定义"""
        params_list = []
        
        if rel['doc']:
            doc_str = self._format_doc_string(rel['doc'])
            params_list.append(f"doc={doc_str}")
        
        if rel.get('metadata'):
            metadata_str = self._format_metadata(rel['metadata'], indent_level=2)
            params_list.append(f"metadata={metadata_str}")
        
        params = ', '.join(params_list)
        if '\n' in params or len(params) > 80:
            result = f"    {rel['name']} = Relationship("
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
            return f"    {rel['name']} = Relationship({params})"
    
    def _generate_namespaced_relationship_definition(self, ns_prefix: str, rel: Dict[str, Any]) -> str:
        """生成命名空间关系定义"""
        # 获取关系的 Python 名称（去掉前缀）
        full_name = rel.get('full_name', rel['name'])
        if ':' in full_name:
            rel_name = ':'.join(full_name.split(':')[1:])
            rel_name = rel_name.replace(':', '.')
        else:
            rel_name = rel['name']
        
        params_list = []
        
        if rel['doc']:
            doc_str = self._format_doc_string(rel['doc'])
            params_list.append(f"doc={doc_str}")
        
        if rel.get('metadata'):
            metadata_str = self._format_metadata(rel['metadata'], indent_level=2)
            params_list.append(f"metadata={metadata_str}")
        
        params = ', '.join(params_list)
        if '\n' in params or len(params) > 80:
            result = f"    {ns_prefix}.{rel_name} = Relationship("
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
            return f"    {ns_prefix}.{rel_name} = Relationship({params})"
    
    def _generate_init_file(self) -> None:
        """生成 __init__.py 文件"""
        lines = []
        
        # 添加主类的导入（不包含命名空间类）
        for class_name in self.class_names:
            file_name = self._camel_to_snake(class_name)
            lines.append(f"from .{file_name} import {class_name}")
        
        lines.append("")
        lines.append("__all__ = [")
        
        # 添加主类到 __all__（不包含命名空间类）
        for class_name in self.class_names:
            lines.append(f'    "{class_name}",')
        lines.append("]")
        
        init_path = os.path.join(self.schema_dir, '__init__.py')
        with open(init_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(lines) + "\n")
        
        print(f"Generated: {init_path}")
    
    def _usd_type_to_python_type(self, usd_type: str) -> str:
        """转换 USD 类型到 Python 类型"""
        # 处理数组类型
        if usd_type.endswith('[]'):
            base_type = usd_type[:-2]
            return f'List[{base_type}]'
        
        return usd_type
    
    def _usd_value_to_python(self, value: Any) -> str:
        """转换 USD 值到 Python 表达式"""
        if value is None:
            return 'None'
        elif isinstance(value, bool):
            return 'True' if value else 'False'
        elif isinstance(value, int):
            return str(value)
        elif isinstance(value, float):
            if value == float('inf'):
                return "float('inf')"
            elif value == float('-inf'):
                return "float('-inf')"
            return str(value)
        elif isinstance(value, str):
            if '\n' in value:
                # 多行字符串，使用三引号
                return f'"""{value}"""'
            else:
                return f'"{value}"'
        elif isinstance(value, list):
            items = [self._usd_value_to_python(item) for item in value]
            return f"[{', '.join(items)}]"
        elif isinstance(value, dict):
            items = [f'"{k}": {self._usd_value_to_python(v)}' for k, v in value.items()]
            return '{' + ', '.join(items) + '}'
        return str(value)
    
    def _format_class_doc_string(self, doc: str) -> str:
        """格式化类级别的 doc 字符串（4 空格缩进）"""
        if not doc:
            return '    ""'
        
        if '\n' in doc:
            # 多行 doc，使用三引号，并规范化缩进
            lines = doc.split('\n')
            # 找到最小的非空行缩进
            min_indent = float('inf')
            for line in lines[1:]:  # 跳过第一行
                stripped = line.lstrip()
                if stripped:  # 非空行
                    indent = len(line) - len(stripped)
                    min_indent = min(min_indent, indent)
            
            # 如果找到最小缩进，去除它
            if min_indent != float('inf') and min_indent > 0:
                normalized_lines = [lines[0]]  # 第一行保持不变
                for line in lines[1:]:
                    if line.strip():  # 非空行
                        normalized_lines.append(line[min_indent:])
                    else:  # 空行
                        normalized_lines.append('')
                dedented_doc = '\n'.join(normalized_lines)
            else:
                dedented_doc = doc
            
            # 为每行添加 4 个空格缩进（类级别）
            indented_lines = []
            for i, line in enumerate(dedented_doc.split('\n')):
                if i == 0:
                    # 第一行紧跟在三引号后面
                    indented_lines.append('    """' + line)
                else:
                    # 后续行添加 4 个空格缩进
                    indented_lines.append('    ' + line if line else '    ')
            indented_doc = '\n'.join(indented_lines)
            
            return f'{indented_doc}\n    """'
        else:
            # 单行 doc
            return f'    "{doc}"'
    
    def _format_doc_string(self, doc: str) -> str:
        """格式化 doc 字符串"""
        if not doc:
            return '""'
        
        if '\n' in doc:
            # 多行 doc，使用三引号，并规范化缩进
            lines = doc.split('\n')
            # 找到最小的非空行缩进
            min_indent = float('inf')
            for line in lines[1:]:  # 跳过第一行
                stripped = line.lstrip()
                if stripped:  # 非空行
                    indent = len(line) - len(stripped)
                    min_indent = min(min_indent, indent)
            
            # 如果找到最小缩进，去除它
            if min_indent != float('inf') and min_indent > 0:
                normalized_lines = [lines[0]]  # 第一行保持不变
                for line in lines[1:]:
                    if line.strip():  # 非空行
                        normalized_lines.append(line[min_indent:])
                    else:  # 空行
                        normalized_lines.append('')
                dedented_doc = '\n'.join(normalized_lines)
            else:
                dedented_doc = doc
            
            # 为每行添加 8 个空格缩进（与代码对齐）
            indented_lines = []
            for i, line in enumerate(dedented_doc.split('\n')):
                if i == 0:
                    # 第一行紧跟在三引号后面
                    indented_lines.append(line)
                else:
                    # 后续行添加 8 个空格缩进
                    indented_lines.append('        ' + line if line else '')
            indented_doc = '\n'.join(indented_lines)
            
            return f'"""{indented_doc}\n        """'
        else:
            # 单行 doc，使用双引号
            return f'"{doc}"'
    
    def _format_metadata(self, metadata: Dict[str, Any], indent_level: int = 0) -> str:
        """格式化 metadata 字典"""
        if not metadata:
            return '{}'
        
        lines = []
        base_indent = '    ' * indent_level
        inner_indent = '    ' * (indent_level + 1)
        
        lines.append('{')
        
        items = list(metadata.items())
        for i, (key, value) in enumerate(items):
            comma = ',' if i < len(items) - 1 else ''
            
            if isinstance(value, dict):
                lines.append(f'{inner_indent}"{key}": {{')
                nested_items = list(value.items())
                for j, (nested_key, nested_value) in enumerate(nested_items):
                    nested_comma = ',' if j < len(nested_items) - 1 else ''
                    if isinstance(nested_value, dict):
                        lines.append(f'{inner_indent}    "{nested_key}": {{')
                        deep_items = list(nested_value.items())
                        for k, (deep_key, deep_value) in enumerate(deep_items):
                            deep_comma = ',' if k < len(deep_items) - 1 else ''
                            lines.append(f'{inner_indent}        "{deep_key}": {self._usd_value_to_python(deep_value)}{deep_comma}')
                        lines.append(f'{inner_indent}    }}{nested_comma}')
                    else:
                        lines.append(f'{inner_indent}    "{nested_key}": {self._usd_value_to_python(nested_value)}{nested_comma}')
                lines.append(f'{inner_indent}}}{comma}')
            else:
                lines.append(f'{inner_indent}"{key}": {self._usd_value_to_python(value)}{comma}')
        
        lines.append(f'{base_indent}}}')
        
        return '\n'.join(lines)
    
    def _camel_to_snake(self, name: str) -> str:
        """将 CamelCase 转换为 snake_case"""
        import re
        s1 = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1_\2', name)
        s2 = re.sub(r'([a-z\d])([A-Z])', r'\1_\2', s1)
        return s2.lower()
    
    def _snake_to_pascal(self, name: str) -> str:
        """将 snake_case 或 camelCase 转换为 PascalCase"""
        import re
        name = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', name)
        return ''.join(word.capitalize() for word in name.split('_'))
    
    def _token_to_constant(self, token_value: str) -> str:
        """将 token 值转换为合法的 Python 常量名"""
        if not token_value:
            return 'Empty'
        
        result = token_value.replace(':', '_').replace('-', '_').replace('.', '_').replace('/', '_')
        
        if not result or result == '_':
            return 'Unknown'
        
        if result[0].isdigit():
            result = '_' + result
        
        import re
        result = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', result)
        
        parts = result.split('_')
        result = ''.join(word.capitalize() for word in parts if word)
        
        if not result:
            return 'Unknown'
        
        python_keywords = {'None', 'True', 'False', 'class', 'def', 'return', 'import', 'from', 'if', 'else', 'elif', 'for', 'while', 'try', 'except', 'finally', 'with', 'as', 'pass', 'break', 'continue', 'lambda', 'yield', 'global', 'nonlocal', 'assert', 'del', 'raise', 'in', 'is', 'not', 'and', 'or'}
        if result in python_keywords:
            result = result + '_'
        
        return result
