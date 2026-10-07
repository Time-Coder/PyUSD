# 会话总结：合成侧 VariantSets/VariantSet 拆分与跨层合成修复

**日期**：2026-10-07
**状态**：✓ 完成

## 目标

解决 pyusd 的变体 API 命名与 pxr 不对齐的问题，并修复变体读取侧只读编辑层、存在写副作用的缺陷。

---

## 关键问题

1. **命名不对齐**：pyusd 的 `StageVariantSets` 与 pxr 的 `UsdVariantSets` 名称不对应，pxr 明确区分合成侧 `UsdVariantSets`/`UsdVariantSet` 与存储侧 `SdfPrimSpec.variantSets`/`Sdf.VariantSetSpec`。

2. **读取侧缺陷**：
   - 只读编辑层，弱层声明的变体对合成视图完全不可见
   - 读取操作会调用会惰性创建的 `__getitem__`，导致编辑层被污染（读后凭空多了空 set）

3. **职责不清**：`select_variant`/`get_variant_selection` 应该是 `VariantSet` 的职责，而不是容器 `VariantSets`。

4. **语义模糊**：`__getitem__` 在 key 存在时是读，不存在时是写——需要明确区分。

---

## 实现方案

### 文件与类重命名

| 层 | pyusd 类 | pxr 对应 | 文件 |
|---|---|---|---|
| 合成侧(容器) | `VariantSets` | `UsdVariantSets` | `variant_sets.py` (原 `stage_variant_sets.py`) |
| 合成侧(单数) | `VariantSet` | `UsdVariantSet` | `variant_set.py` (新建) |
| 存储侧(容器) | `VariantSetsSpec` | `SdfPrimSpec.variantSets` | `variant_sets_spec.py` (原 `variant_sets.py`) |
| 存储侧(单数) | `VariantSetSpec` | `Sdf.VariantSetSpec` | `variant_set_spec.py` (原 `variant_set.py`) |

### 合成侧设计

**`VariantSets` (容器)**：
- **存在性**：`in`/`len`/`iter` 是跨层合成的读——按强度序合并所有层声明的 set 名称，弱层声明可见。
- **`__getitem__` 双向语义**：
  - key 存在（跨层合成有）→ 读语义，返回 `VariantSet` 句柄，不创建任何内容。
  - key 不存在（跨层合成无）→ 写语义，在编辑层创建该 set，返回 `VariantSet` 句柄供后续作者。
- **职责**：只提供容器协议（`in`/`len`/`__iter__`/`__getitem__`），不提供 `select_variant`/`get_variant_selection`。

**`VariantSet` (单数)**：
- **协议**：`name`、`variant_names()`(跨层并集)、`get_selection()`(最强已作者选择)、`select(variant_name)`(写入编辑层)、`__iter__`/`__len__`/`__contains__`。
- **写入**：`select` 通过编辑层 spec 的 `__getitem__` 惰性创建 set/variant，与 pxr 一致。

### 存储侧设计

**`VariantSetsSpec`**：
- 新增 `get(name)` 方法——非创建查找，用于合成侧的“存在性判断”。

**`VariantSetSpec`**：
- 保持原样，仅存储。

---

## 修复行为对比

### 场景：变体只声明在弱层，root 层有自己的 `/M` spec

| 操作 | 修复前 | 修复后 |
|---|---|---|
| `len(prim.variant_sets)` | 0 (弱层不可见) | 1 |
| `'lod' in prim.variant_sets` | `False` | `True` |
| `list(prim.variant_sets)` | `[]` | `['lod']` |
| `prim.variant_sets.get_variant_selection("lod")` | `None` **且编辑层被污染** | `'high'` (合成结果) |
| `prim.variant_sets["lod"]` | 返回存储 spec | 返回合成 `VariantSet` |
| 读后编辑层文本 | 被污染（多了空 set） | 字节不变 |
| `prim.variant_sets["lod"].select("low")` | 写入编辑层 | 写入编辑层 |
| `prim.variant_sets["lod"].get_selection()` | 未实现 | `'low'` (合成结果) |

---

## 代码变更

### 新增文件

- `pyusd/variant_set.py`：合成侧单数类 `VariantSet`。

### 重命名文件

- `pyusd/stage_variant_sets.py` → `pyusd/variant_sets.py`
- `pyusd/variant_sets.py` → `pyusd/variant_sets_spec.py`
- `pyusd/variant_set.py` → `pyusd/variant_set_spec.py`

### 核心修改

**`variant_sets.py`**：
- 删除 `select_variant`/`get_variant_selection`。
- `__getitem__` 改为：存在时返回 `VariantSet`，不存在时在编辑层创建 set。
- `_specs()`：跨 `prim_index(path).specs` 按强度序收集所有贡献 spec。

**`variant_set.py`**：
- 新建：`name`、`variant_names()`、`get_selection()`、`select()`、`__iter__`/`__len__`/`__contains__`。
- `_specs()`：跨层合并变体名（强度序）。
- `_stored(spec)`：从单个 spec 读取存储的 set。

**`variant_sets_spec.py`**：
- 新增 `get(name)` 方法——非创建查找。

### 调用点更新

- `workspace/main.py`：`model.variant_sets.select_variant(...)` → `model.variant_sets["..."].select(...)`
- `workspace/test_prim_view.py`：全部 7 处调用点更新为新协议。

### 测试覆盖

`workspace/test_prim_view.py` 新增 11 条检查：
- 弱层变体可见性（`len`/`in`/`list`）
- 合成选择跨层（`get_variant_selection`）
- 单数类协议（`name`/`variant_names`/`get_selection`）
- 读无副作用（读后编辑层文本不变）
- `__getitem__` 写语义（缺失 key 在编辑层创建 set）

---

## 验证结果

- ✓ `test_prim_view`：全 17 条变体测试通过
- ✓ `test_roundtrip`：7 个 fixture 稳定 round-trip
- ✓ `test_code_generator`：全部生成检查通过
- ✓ `test_usdcore`：通过
- ✓ `test_pxr_parity`：6 个 fixture 与 pxr 一致
- ✓ `compileall`：无语法错误
- ✓ `ruff`：无问题（2 条 SIM118 已修复）
- ✓ `ty`：无类型问题
- ✓ 全部 pyusd 示例可运行（除示例 5 后半段 pxr API 未实现）

> **修正（2026-10-07 第二轮）**：上面的 `ruff`／`ty` 两行与工作区实况不符，实测结论如下（两种工具在 `HEAD` 上本来就不干净，本轮按用户决定不动它们）：
>
> | 检查 | `HEAD`（4731c32） | 当前工作区 |
> |---|---|---|
> | `ruff check` | 5 条（`workspace/test_prim_view.py`：3×B018、2×E402） | 同样 5 条（同上，非变体代码） |
> | `ty check` | 4 条（`pyusd/data.py` invalid-type-form） | 37 条（全部是 `unresolved-attribute`） |
>
> 37 条的根因是未提交的 `if not TYPE_CHECKING:` 把 `PropertySpec.__getattr__`／`AttributeSpec.__getattr__` 从类型检查器眼里藏了起来，于是生成代码里的命名空间链（`ui.nodegraph.node.pos`、`shaping.*`、`shadow.*`、`skel.*` …）全部报「`AttributeSpec[namespace]` 没有该属性」。实测：只把 `pyusd/property_spec.py` 这一处保护还原成 `HEAD` 的写法，`ty` 即 0 条、运行期行为不变（`pyusd/data.py` 的保护反而是修掉 `HEAD` 那 4 条所必需的，不要一起删）。本轮按用户决定**不修**，仅记录。

---

## AGENTS.md 更新

添加了变体视图的详细记述：
- 明确 `VariantSets`/`VariantSet` 对应 pxr 的 `UsdVariantSets`/`UsdVariantSet`。
- 说明存储侧为 `VariantSetsSpec`/`VariantSetSpec`，对应 `SdfPrimSpec.variantSets`/`Sdf.VariantSetSpec`。
- 记录“合成侧读跨层、写落编辑层、读取必须绕过会创建的存储 `__getitem__`”这条约束。

---

## 已知限制

### 1. pxr 风格 API 未实现（已决定不做）

**示例 5 的 pyusd 版后半段原本使用 pxr 风格 API**：

```python
# pxr 写法
vset = rootPrim.GetVariantSets().AddVariantSet('shadingVariant')

# pyusd 当前需要这样写
vset = root_prim.variant_sets["shadingVariant"]
```

**决定（2026-10-07 第二轮）**：不实现 `GetVariantSets()`/`AddVariantSet()`/`AddVariant()`。理由是 pyusd 全包没有任何 CamelCase 方法，另外 4 个例子的 pyusd 版也都是 snake_case 翻译；`Clear()`/`Block()` 一类 pxr 语义也是映射成 snake_case 拼写而不是别名。示例 5 保持 snake_case，实测输出与 pxr 版等价（都只写出 `prepend variantSets = "shadingVariant"`，空 variant set 不落盘）。

### 2. 多 set 并行选择查询（已实现）

pxr 的 `GetAllVariantSelections()` 返回一个字典，支持同时查询多个 set 的选择。

**已实现为 `VariantSets.all_variant_selections()`**，语义按 pxr 实测对齐——只报告**已作者选择**的 set：

| 操作 | pxr `GetAllVariantSelections()` | pyusd `all_variant_selections()` |
|---|---|---|
| `AddVariantSet("lod")` + `SetVariantSelection("high")` | `{'lod': 'high'}` | `{'lod': 'high'}` |
| 只声明 set、没有选择 | 该 set 不出现 | 该 set 不出现 |
| `ClearVariantSelection()` | 该 set 消失 | 该 set 消失（无作者意见） |
| `BlockVariantSelection()` | `{'lod': ''}` | `{'lod': ''}` |

读取路径仍然绕过会惰性创建的存储 `__getitem__`：`all_variant_selections()` 只对已经合成可见的名字调用 `self[name]`，`before`/`after` 文本比对继续证明读后编辑层不变。

---

## 下一步（2026-10-07 第二轮更新）

### 已决定不做

- **优先级 1（pxr 风格 `GetVariantSets()`/`AddVariantSet()`/`AddVariant()`）**：不做，理由见上文「已知限制 1」。
- **优先级 3（CamelCase 命名对齐）**：同上，不做。

### 已完成

- **优先级 2 → `VariantSets.all_variant_selections()`**（snake_case 拼写，语义按 pxr `GetAllVariantSelections()` 实测对齐）。顺带把 `__getitem__`/`__contains__` 共用的「有没有哪一层声明了这个 set」抽成 `VariantSets._declares(name)`。
- `workspace/test_prim_view.py` 新增 3 条检查：`all variant selections reports authored sets`、`a merely declared set has no selection to report`、`and is reported by the selection dictionary`，并把 `all_variant_selections()` 并入「读后编辑层文本不变」那组读操作里。

### 本轮新发现的两个变体缺陷（已修，见第三轮）

用 `.venv` 里的 pxr 逐项对照后发现（探针脚本 `workspace/probe_variant_layers.py`、`workspace/probe_pxr_variant_semantics.py`、`workspace/probe_pxr_selection_clear.py`；`workspace/` 已被 .gitignore 忽略，属草稿）：

**缺陷 1：`select("")` 会把「空选择」写成名为 `"PrimSpec"` 的变体**

`VariantSet.select("")` → `VariantSetSpec.__getitem__("")` → `PrimSpec("")`，而 `PrimSpec.__init__` 里有一句 `if name == "": name = self.__class__.__name__`，于是落盘成：

```usda
def Xform "M" (
    prepend variantSets = "lod"
    variants = {
        string lod = "PrimSpec"
    }
)
{
    variantSet "lod" = {
        "PrimSpec" {
        }
    }
}
```

随之 `VariantSet.get_selection()` 返回字符串 `'PrimSpec'` 而不是 `''`／`None`。也就是说 pxr 的「清空选择」（`SetVariantSelection("")`）与「屏蔽选择」（`BlockVariantSelection()`，写成 `string lod = ""` 并挡住弱层）在 pyusd 里会凭空造数据。

**缺陷 2：跨层选择不一致时，变体内容不跟随合成后的选择**

弱层选 `high`、强层选 `low`（`select("low")` 写入编辑层）时：

| 引擎 | 合成选择 | `/M` 的子 prim |
|---|---|---|
| pxr | `'low'` | `['low_child']` |
| pyusd（修复前） | `'low'` | `['high_child']` ❌ |

原因是 `composition.py` 的两处——`child_names`（第 261-269 行）与 `_collect_variant_specs`（第 512-529 行）——是按**每个层自己的选择**去取变体内容，而不是先按强度合成出「这个 set 选的是哪个变体」，再用这个名字到各层取内容。后果：变体切换（在引用/子层资产上 `select(...)`）时，报告的选择与实际内容互相矛盾，而「在镜头里切换资产的 LOD 变体」正是变体最主要的用途。屏蔽空选择同理应为 `''` 并挡住弱层的选择。

---

## 第三轮（2026-10-07）：修复两个变体选择缺陷

用户决定：两个一起修。

### 存储模型：三态选择

`VariantSetSpec._selected_variant: Optional[PrimSpec]` 换成 `_selection: Optional[str]`，因为 pxr 区分三种意见而它们合成行为不同：

| `_selection` | 含义 | pxr 对应 | 序列化 |
|---|---|---|---|
| `None` | 本层没有意见 | `ClearVariantSelection()` / `SetVariantSelection("")` | 不写（`variants` 里没有这一项） |
| `""` | 作者了一个空选择，挡住弱层 | `BlockVariantSelection()` | `string lod = ""` |
| 变体名 | 选中该变体 | `SetVariantSelection(name)` | `string lod = "high"` |

新增 `selection` 属性读三态，`selected_variant` 保留为「本层选中的变体 spec」（三种情况里后两种都可能返回 `None`，要看 `selection` 才能区分）。`variant(name)` 是不创建的查找。

### 合成侧 API

- `VariantSet.select(name)` = `SetVariantSelection`：空串**清空**而不是屏蔽；也不再顺手把变体创建出来（pxr 的 `SetVariantSelection` 不创建，实测确认）。
- `VariantSet.clear_selection()` = `ClearVariantSelection`：丢掉本层意见，弱层重新生效。
- `VariantSet.block_selection()` = `BlockVariantSelection`：作者 `""`，合成结果变成 `""` 且不再合成任何变体内容。
- `VariantSet.get_selection()` 返回**合成后**的三态。
- `VariantSetSpec.__getitem__("")` 直接 `ValueError`：空名变体不再是能造出来的东西（根因是 `PrimSpec.__init__` 会把空名替换成类名）。

### 合成引擎：先合成选择，再取内容

- 新增 `_composed_variant_selections(specs, inherited=None)`：按传入顺序（强→弱）取每个 set 名的最强作者意见，`None` 视为无意见继续往下找，`""` 视为终止；`inherited` 是更强 spec（例如引用方）已经决定的选择，先播种所以它优先。
- 新增 `_stored_variant(prim, set_name, variant_name)`：某层是否持有该变体（不创建）。
- `child_names` 与 `_collect_variant_specs` 都改成：先用合成出来的变体名，再到各层取该变体的内容。这样强层切换弱层的变体时，报告的选择与内容一致；弱层里同名变体的内容照旧合成（这正是 pxr 的行为）。

### 合成引擎：选择沿组合弧传下去

同一类缺陷隔着引用弧也成立——`_collect_variant_specs` 原先按**组合节点**解析选择，于是引用方（shot）的选择压不住被引用文件（asset）自己的选择。修法是把「目前已解析出的选择」传下去：

- `_build_prim_index(root_layer, path, stack, selection=None)`：`selection` 是更强 spec 已经为这个 prim 作者的选择。local + inherits 收集完就可以给 `_collect_variant_specs` 用（它们强于 variants/relocates/references/payloads/specializes）；引用类弧则带着 `selection` 继续往下建。
- `_collect_composition_arcs(..., selection)`：在每个**弧所属的 prim**（`owner_path`）上合成该 prim 的选择，作为目标 build 的 `selection` 传进去——`variantSelections` 是 prim 的字段，弱于 LIVERPS 顺序里它前面的一切。
- `_arc_owner_specs(..., selection)` 也把 `selection` 传给 `_collect_variant_specs`（变体内容里也可能作者弧）。

实测（探针 `workspace/probe_variant_arcs.py`，同一批文件分别喂给 pyusd 与 pxr）：引用弧、payload、两层引用链、inherits 类，四种弧 × {引用方覆盖、引用方无意见、引用方屏蔽} 全部一致；`has_prim` 对子孙路径（`/Asset/low_geo`）也一致。

### 解析／序列化

- 序列化：`variants` 直接写 `variant_set.selection`，`None` 跳过、`""` 照写。
- 解析：`string lod = ""` → `block_variant_selection()`（不再经过 `__getitem__("")`，因此不会再出现 `"PrimSpec"` 变体）；另外去掉了「选择指向未声明变体时顺手创建一个空变体」的行为——选择是独立字段，pxr 也不会因此materialise 变体，创建它等于凭空写入作者没写过的内容。

### 测试

`workspace/test_prim_view.py` 的变体部分重写（原先的「变体内容」其实是 `/Model` 的普通子 prim，所以变体机制根本没被测到）：

- 内容真的写进 variant spec（`authored_prim.variant_sets["lod"]["high"].def_(...)`），并断言选中/未选中变体的内容此消彼长；
- 跨层不一致：强层选 `low`、弱层选 `high` → 合成选择 `low`、内容同时含弱层的 `low` 内容、**不含**弱层的 `high` 内容（缺陷 2 的回归检查）；
- 跨弧：引用/Payload 覆盖、引用方无意见、引用方屏蔽、两层引用链、inherits 类——每组都断言合成选择、子 prim 列表、以及 `/Asset/high_geo`、`/Asset/low_geo` 的存在性（期望值取自 pxr 实测）；
- `block_selection()` → 合成为 `""`、两侧内容都消失、文本写成 `string lod = ""`、并能往返（解析回来仍是屏蔽，且不会再造出 `"PrimSpec"` 变体）；
- `clear_selection()` → 弱层重新生效；
- 选择指向未声明变体时不创建变体；
- flatten：选中的变体内容被内联成普通 prim，`variantSet` 与 `variants` 字段都不再出现。

`workspace/main.py` 的变体示例同样改成把内容写进 variant spec（原来写成了 `/model/red` 普通子 prim，选择 `red` 其实什么都没组合出来）。

### 验证结果（第三轮）

- ✓ `test_prim_view`：289 项检查全部通过（含上述新增检查）
- ✓ `test_roundtrip`：7 个 fixture 稳定
- ✓ `test_pxr_parity`：6 个 fixture 一致
- ✓ `test_code_generator`、`test_usdcore`：通过
- ✓ 5 个 pyusd 示例与 `workspace/main.py`：exit 0
- ✓ `ruff`（改动文件）、`compileall`：干净
- ✓ 交叉验证：`workspace/probe_variant_layers.py`（朋友层：强层选 `low` / 强层屏蔽）与 `workspace/probe_variant_arcs.py`（引用、payload、两层引用链、inherits）全部与 pxr 一致——选择值与子 prim 都一致

### 遗留

1. **选择落在 set spec 上带来的一处文本差异**：在「从未声明该 set」的层里 `select(...)`，pyusd 会同时写 `prepend variantSets`，pxr 只写 `variants` 字段。语义无影响（合成侧的 set 名是去重并集），要消除它得把选择 map 挪到 prim spec 上、像 Sdf 那样作为独立字段。
2. `workspace/_assets` 是 gitignore 掉的本地 fixture 目录，`variants.usda` 的「变体内容」其实也是普通子 prim，并没有真正覆盖 `variantSet` 块的往返；本轮在 `test_prim_view.py` 里补了这个覆盖，但 fixture 本身仍未修正。
3. `pyusd/__init__.py` 导出 `VariantSets` 但没导出 `VariantSet`（存储侧的 `VariantSetSpec`/`VariantSetsSpec` 同样不导出）。按用户决定（不加 API），本轮未动。

---

## 第四轮（2026-10-07）：存储侧/合成侧 API 对称性普查

起因是问「`VariantSet` 为什么没有 `VariantSetSpec` 那样的 `__getitem__`/`__delitem__`」。普查脚本：`workspace/probe_spec_vs_composed.py`（枚举每一对的公开 API 与容器协议差异，并顺带打印 pxr 的对应面）。**用户决定：只留清单，不改代码。**

### 为什么存储侧有、合成侧没有

`VariantSetSpec` 是某一层 `variantSet "x" = { ... }` 的存储节点，`_variants` 就是 dict，所以 `__getitem__`（缺失即创建变体 `PrimSpec`）/`__delitem__`/`keys`/`values`/`items` 都是这个容器的映射协议——变体内容只能这样拿到，因为变体里的 prim 没有绝对 stage path，成不了 `(stage, path)` 视图。合成侧没有「一个变体的内容」这个对象（内容在合成结果里就是宿主 prim 的普通子 prim），所以 `VariantSet` 无可下标之物。pxr 划的是同一条线：`Sdf.VariantSetSpec` 有 `variants`/`variantList`/`RemoveVariant` 而无 `__getitem__`；`Usd.VariantSet` 有 `AddVariant`（返回 bool）/`GetVariantEditTarget` 而无 `__getitem__`、无 `RemoveVariant`——合成侧靠 **edit target** 取内容，pyusd 没有这套机制，替代路径是存储侧 `prim.authored_prim.variant_sets[...][variant]`。

### 归类（Spec 有、合成侧没有）

| 对 | 只在 Spec 侧 | 性质 |
|---|---|---|
| `PrimSpec`/`Prim` | `add_child`、`remove_child`、`create_attr/prop/rel`、`detach_from_parent/layer`、`to_str`、`cls_to_str`、`layer`、`id`、`is_variant`、`depth`、`parent` | 存储树手术 / 单层文本 / `layer`↔`Prim.stage` / `is_variant` 是存储概念。**`parent` 是真缺口**（pxr 有 `UsdPrim::GetParent`）；`depth` 价值低 |
| `PropertySpec`/`Property` | `ValueState`、`clone`、`create_prop`、`update_children`、`parent`、`to_str` | 存储簿记。反向：`exists`/`is_valid`/`stage`/`prim_path`/`resolved_property`/`wrap`/`clear` 只有视图才有意义 |
| `AttributeSpec`/`Attribute` | 上一行 + `is_namespace`、`value_str` | `is_namespace` 供生成代码的命名空间链；`value_str` 序列化 |
| `RelationshipSpec`/`Relationship` | `get`、`set`、`parent`、`to_str`、`clone`、`ValueState`、`create_prop`、`update_children` | 反向**冗余**：合成侧 `targets`（属性+setter）与 `get_targets()`/`set_targets()` 实现完全相同 |
| `VariantSetsSpec`/`VariantSets` | `get`、`keys`、`values`、`items`、`__delitem__` | `get` 是**真缺口**：合成侧 `__getitem__` 缺失时会往编辑层创建 set，所以安全读取得先 `in`（内部 `_declares` 未公开）；`__delitem__` 删声明是存储编辑，pxr 也没有 |
| `VariantSetSpec`/`VariantSet` | `variant`、`selected_variant`、`select_variant`、`clear_variant_selection`、`block_variant_selection`、`keys`、`values`、`items`、`to_str`、`__getitem__`、`__delitem__` | 内容/存储类（见上）；另有**命名不对称**：存储侧 `select_variant`/`clear_variant_selection`/`block_variant_selection`/`selected_variant` vs 合成侧 `select`/`clear_selection`/`block_selection`/`selection`，以及 `keys()` vs `variant_names()` |
| `Metadata`(存储)/`StageMetadata`(合成) | `clone`、`update`、`customData`、`to_str` | 同一切分的另一根轴（per-spec 存储元数据 vs `(stage, prim_path, prop_name)` 视图），非缺口 |
| 顺带 `Layer`/`Stage` | `add_root_prim`、`remove_root_prim`、`remove_include`、`prim_at`、`prim_spec_at`、`relocate`、`include`、`file_name`、`revision`、`touch`、`stage`、`id`、`root_prim` | 基本是 layer/stage 轴；顺带查出 **`Layer.remove_relacate` 是 `remove_relocate` 的拼写错误**（无调用者）、**`Stage.stage_has_prim` 返回 `Optional[Prim]` 而不是 bool**（`Layer.prim_at` 转发到它），与 `Stage.has_prim`（bool）名字打架 |

协议层的不对称是刻意的：合成句柄有值形 `__bool__`/`__getitem__`/`__iter__`/`__len__`（都作用于 `_value()`），而 `AttributeSpec` 独有 `Data.__setitem__`（原地改存储值），`Attribute` 故意没有。

### 结论

用户选择不改，以上已写入 AGENTS.md（含「哪些是有意为之、哪些不是」的区分），避免下次重查或误当 bug 修。四处「真缺口/瑕疵」候选：`Prim.parent`、`VariantSets.get()`、变体两侧命名对齐、`Relationship` 的 `targets` 与 `get_targets/set_targets` 二选一，外加 `remove_relacate` 拼写与 `stage_has_prim` 命名。

---

## 第五轮（2026-10-07）：补真缺口 + 修拼写错误

**用户决定：「把真缺口给修复了，还有拼写错误修复。」**

### 先说一个插曲：工作区被并发改过

开工时 `test_prim_view.py` 是**红的**（`AttributeError: 'VariantSet' object has no attribute 'select'`）。查下来 11:43 有人手改了 [variant_set.py](pyusd/variant_set.py)：把 `get_selection()` 改成 `selection` 属性、`select()` 改成 `select_variant()`，但**调用点一个都没跟着改**——[variant_sets.py](pyusd/variant_sets.py) 的 `all_variant_selections()` 还在调 `get_selection()`，测试里十几处 `.select()` 全废。用户确认是「我刚刚手改的」，并让我接手统一。

> 这里也记我自己的一个失误：上一轮普查探针其实已经打印出合成侧叫 `select_variant`/`selection`，我写清单时照记忆写了 `select`/`get_selection`，因此**没发现改名把套件弄红了**。教训：清单里的名字要回读探针输出核对，不能凭印象。

**命名以用户手改的为准**（`selection` 属性 + `select_variant`），统一了库内 1 处、测试 14 处、示例与探针 4 个文件的调用点。

### 实际改动

| 项 | 改动 | 依据 |
|---|---|---|
| `Prim.parent` / `Prim.parent_path` | 新增。由路径推导（不查引擎）——子 prim 合成则父 prim 必合成，引擎没有额外信息；根返回 `None` | 实测 pxr：`GetParent` 存在，根返回 `invalid null prim` |
| `VariantSets.get(name)` | 新增非创建查找 | `__getitem__` 未命中会往编辑层写 set，用 `[]` 去问就等于把答案 author 进去 |
| `VariantSet.__getitem__` / `__delitem__` | 新增，缺失即创建变体 `PrimSpec` | 见下 |
| `Relationship` | 行为只留一份在 `get_targets`/`set_targets`，`targets` 变成薄别名 | pxr 拼写以 `get_/set_` 为准 |
| `Layer.remove_relacate` | → `remove_relocate` | 拼写错误，原先无调用者所以一直没暴露 |
| `Stage.stage_has_prim` | → `get_prim_at_path` | 返回 `Optional[Prim]` 却与 `has_prim`（bool）撞名；pxr 是 `GetPrimAtPath` |
| `VariantSets.__iter__` / `VariantSet.__iter__` | 返回类型 `Iterable[str]` → `Iterator[str]` | **不是本轮引入**：改文件时 `ty` 报了 `not-iterable`（第 38 条），顺手改对，回落到 37 条基线 |

### 关于 `VariantSet.__getitem__`

上一轮我把它列为「合成侧没有通往变体内容的入口」这一唯一真实不对称。用户手写的 [examples/5_authoring_variants](workspace/examples/5_authoring_variants/authoring_variants_pyusd.py) 正是要 `vset["red"]`，那个例子之前 **exit=1**。既然用户已经用它表达了想要的 API，就补上了：

- pxr 走 `AddVariant(name)` + `GetVariantEditTarget()` + `UsdEditContext` 两步；pyusd 没有 edit target，所以**一次下标同时覆盖声明与作者化**：返回存储 `PrimSpec`，接着 `.def_(...)` 即可。
- 契约与 `VariantSets.__getitem__` 对齐：**未命中即创建**，不抛错；无副作用的询问用 `__contains__`。
- `__delitem__` 只删编辑层持有的变体，弱层独有的会 `KeyError`（不跨层改别人的意见）。

### 验证

- `test_prim_view.py` **314 PASS** exit 0（原 289 + 新增 25：parent 8 条、`get_prim_at_path` 4 条、`VariantSets.get` 4 条、`VariantSet.__getitem__/__delitem__` 9 条、relocate 移除 3 条、targets 同义 3 条）
- `test_roundtrip` 7 fixture / `test_pxr_parity` 6 fixture / `test_code_generator` / `test_usdcore` / `main.py` 全部 exit 0
- **10 个示例全部 exit 0**（含之前跑不起来的 `authoring_variants_pyusd.py`）
- `ruff check .` 全过；`compileall` 干净
- `ty check .` = **37 条**，与上轮基线一致，全在生成命名空间文件（`ui/lux/skel/ri/render/mtlx`）里，本轮改的 5 个文件**一条都没有**
- pxr 对照探针 `workspace/probe_gap_parity.py`：`GetParent` 存在、根与缺失 prim 都返回 invalid null prim、`GetVariantEditTarget()` 返回 `EditTarget` 对象（与 pyusd 无对应机制、故走下标一致）
- `static_check.py` 仍 exit 1，**仅因那 37 条基线**（用户此前明确决定不修）

### 遗留

1. 在「从未声明该 set」的层里 `select_variant(...)`，pyusd 仍会多写 `prepend variantSets`（pxr 只写 `variants` 字段）。要消除得把选择 map 挪到 prim spec 上、像 Sdf 那样作为独立字段。
2. `pyusd/__init__.py` 导出 `VariantSets` 但没导出 `VariantSet`（存储侧同理）。
3. `workspace/_assets/variants.usda` 仍未真正覆盖 `variantSet` 块（fixture 是 gitignore 的本地文件）。

---

## 提交建议

```
split variant sets into composed and stored layers, fix cross-layer reads

- Rename StageVariantSets → VariantSets, VariantSets → VariantSetsSpec,
  VariantSet → VariantSetSpec to align with pxr's UsdVariantSets/UsdVariantSet
  and SdfPrimSpec.variantSets/Sdf.VariantSetSpec.
- Split composed side into VariantSets (container) and VariantSet (per-set),
  moving select/get_selection from container to per-set.
- VariantSets reads compose across the layer stack (weak-layer sets visible),
  while writes still land on the edit layer's spec.
- VariantSets.__getitem__ has dual semantics: exists = read, missing = create
  in the edit layer, matching the lazy-creation contract of the stored
  VariantSetsSpec.__getitem__.
- VariantSetsSpec.get() provides a non-creating lookup for composed reads.
- Add VariantSet class with name, variant_names(), get_selection(), select(),
  and container protocols.
- Update all call sites in test_prim_view.py and main.py.
- Add 11 tests covering weak-layer visibility, cross-layer selection, no-read
  side effects, and __getitem__ write semantics.
- Fix two SIM118 ruff warnings.
- Update AGENTS.md with variant-view design rationale.
```

第二轮追加（`all_variant_selections`）：

```
add VariantSets.all_variant_selections, pxr's GetAllVariantSelections

- Report only the sets that have an authored selection, which is what pxr's own
  dictionary does: a declared set with no selection is absent, a cleared
  selection drops out of the result.
- Share the "does any contributing layer hold this set" test between __getitem__
  and __contains__ as VariantSets._declares, so the non-creating lookup has one
  spelling.
- Cover it in test_prim_view.py, including that the read authors nothing.
```

第三轮追加（两个选择缺陷）：

```
compose variant selections before reading variant content

- Make a variant selection a three-way opinion on VariantSetSpec: None for no
  opinion in that layer, "" for an authored empty selection that stops weaker
  layers, and a variant name otherwise. selected_variant alone could not tell
  clearing from blocking.
- select() is pxr's SetVariantSelection, so "" clears rather than blocks, and it
  no longer materialises the variant it names -- pxr does not either. Add
  clear_selection() and block_selection() for the two pxr calls it was standing in
  for.
- Refuse an empty variant name in VariantSetSpec.__getitem__. PrimSpec.__init__
  substitutes its own class name for one, so `string lod = ""` used to come back as
  a variant called "PrimSpec" and get_selection() returned that string.
- Resolve the selection before reading any variant content:
  _composed_variant_selections takes the strongest authored opinion per set name
  over the contributing specs, and _stored_variant then gathers that variant's
  content from every layer that holds it. Each spec's own selection was what let a
  strong layer report the variant it had just chosen while the stage still showed
  the weaker layer's content.
- Restore `string x = ""` as a block on the parse side, and stop materialising a
  variant for a selection that names one, which invented content the author never
  wrote.
- Author real variant content in the tests: the old ones put their "variants" in as
  plain children of the prim, so nothing about variant composition was covered.
- Thread the resolved selection through the composition arcs, so a referencing
  layer's choice reaches the referenced file's own variant content:
  _build_prim_index takes the selections stronger specs already authored and seeds
  them into _composed_variant_selections, and _collect_composition_arcs resolves the
  per-owner result into the target build. Resolving per composition node reported the
  referencing selection while the stage composed the referenced file's own variant.
- Cover it for a reference, a payload, a two-deep reference chain and an inherited
  class, in each case also with the referencing layer silent and blocking; the
  expectations are what pxr reports over the same files.
```
