"""Prim: a view onto a prim in a stage.

A Prim is always bound to ``(stage, path)``. It reads composed results and authors
into the stage's edit layer, so the same class serves both a Layer (a single-layer
stage over that layer) and a Stage (the full composition). Schema subclasses such
as ``Xform`` and ``Mesh`` are dispatched by ``Prim.__new__`` from the composed
typeName, which is what makes ``isinstance`` and IDE completion work.

The internal, materialised form of one layer's opinion is ``PrimSpec``; reach it
through :attr:`Prim.resolved_prim`, :attr:`Prim.authored_prim` or
``Layer.prim_spec_at``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, List, Optional, Type, TypeVar, Union, cast

from .composition import normalize_prim_path, path_items, prim_at
from .prim_spec import PrimSpec
from .property import Property
from .sdf import Specifier
from .stage_metadata import StageMetadata
from .stage_variant_sets import StageVariantSets
from .utils import join_relative_path

if TYPE_CHECKING:
    from .clips_api import ClipsAPI
    from .collection_api import CollectionAPI
    from .color_space_api import ColorSpaceAPI
    from .color_space_definition_api import ColorSpaceDefinitionAPI
    from .geom.geom_model_api import GeomModelAPI
    from .geom.motion_api import MotionAPI
    from .geom.primvars_api import PrimvarsAPI
    from .geom.xform_common_api import XformCommonAPI
    from .layer import Layer
    from .lux.light_api import LightAPI
    from .lux.light_list_api import LightListAPI
    from .lux.list_api import ListAPI
    from .lux.mesh_light_api import MeshLightAPI
    from .lux.shadow_api import ShadowAPI
    from .lux.shaping_api import ShapingAPI
    from .lux.volume_light_api import VolumeLightAPI
    from .media.asset_previews_api import AssetPreviewsAPI

    # --- BEGIN generated api imports ---
    from .model_api import ModelAPI
    from .physics.physics_articulation_root_api import PhysicsArticulationRootAPI
    from .physics.physics_collision_api import PhysicsCollisionAPI
    from .physics.physics_drive_api import PhysicsDriveAPI
    from .physics.physics_filtered_pairs_api import PhysicsFilteredPairsAPI
    from .physics.physics_limit_api import PhysicsLimitAPI
    from .physics.physics_mass_api import PhysicsMassAPI
    from .physics.physics_material_api import PhysicsMaterialAPI
    from .physics.physics_mesh_collision_api import PhysicsMeshCollisionAPI
    from .physics.physics_rigid_body_api import PhysicsRigidBodyAPI
    from .ri.ri_material_api import RiMaterialAPI
    from .ri.ri_spline_api import RiSplineAPI
    from .ri.statements_api import StatementsAPI
    from .semantics.semantics_labels_api import SemanticsLabelsAPI
    from .shade.connectable_api import ConnectableAPI
    from .shade.coord_sys_api import CoordSysAPI
    from .shade.material_binding_api import MaterialBindingAPI
    from .shade.node_def_api import NodeDefAPI
    from .skel.skel_binding_api import SkelBindingAPI
    from .stage import Stage
    from .ui.accessibility_api import AccessibilityAPI
    from .ui.node_graph_node_api import NodeGraphNodeAPI
    from .ui.scene_graph_prim_api import SceneGraphPrimAPI
    from .vol.particle_field_kernel_base_api import ParticleFieldKernelBaseAPI
    from .vol.particle_field_position_base_api import ParticleFieldPositionBaseAPI
    from .vol.particle_field_radiance_base_api import ParticleFieldRadianceBaseAPI
    # --- END generated api imports ---



class Prim:
    _stage: Stage
    _path: str

    def __new__(cls, stage: Stage, path: str, _type_name: Optional[str] = None) -> Prim:
        """Dispatch to the schema class that models this prim's typeName.

        A plain ``Prim(stage, path)`` looks the composed typeName up in the schema
        registry and becomes a ``Mesh``, ``Xform`` and so on. Passing a concrete
        class (``def_``) skips the lookup. Either way ``__init__`` keeps the single
        ``(stage, path)`` shape, so there is no bound-vs-unbound mode to track.

        ``_type_name`` lets a caller that already resolved it pass the answer down.
        ``Stage.__getitem__`` has to know the typeName anyway, to tell a missing prim
        from an untyped one, and resolving it twice means paying for two prim index
        fetches -- each of which rebuilds a key holding a signature of the whole layer
        stack. The parameter is private because it is an optimisation, not an API.

        Views are interned per stage, so ``stage["/M"] is stage["/M"]``: asking twice
        for the same path means asking for the same thing, and a handle that compares
        unequal to itself by ``is`` reads as a bug even though ``==`` agrees. The
        lookup was already being done to pick the class, so this only trades one small
        allocation for one dict hit rather than adding work. ``pxr`` cannot offer this:
        its ``UsdPrim`` wraps a shared ``UsdPrimImpl`` but every Python binding call
        still builds a fresh wrapper, so there ``is`` is always False.

        Keyed by class as well as path, so a prim retyped by a stronger layer gets a
        new view instead of the one built for its previous type. ``__init__`` then runs
        again on the cached object; that is harmless because it only re-assigns the
        same two attributes and no schema class overrides ``__init__``.
        """
        if cls is Prim:
            from .schema_registry import prim_class

            if _type_name is None:
                _type_name = stage._engine.resolve_type_name(path)

            resolved = prim_class(_type_name)
            if resolved is not None:
                cls = resolved

        # cls was narrowed to the schema class modelling this prim's typeName,
        # so the allocation is a Prim even though object.__new__ is typed loosely.
        key = (normalize_prim_path(path), cls)
        views = stage.prim_views
        view = views.get(key)
        if view is None:
            view = cast(Prim, object.__new__(cls))
            views[key] = view
        return view

    def __init__(self, stage: Stage, path: str, _type_name: Optional[str] = None) -> None:
        # _type_name is accepted only so that it reaches __new__ without error: Python
        # passes the same arguments to both. The instance holds (stage, path) and
        # nothing else, which is what lets a cached view be handed straight back.
        object.__setattr__(self, "_stage", stage)
        object.__setattr__(self, "_path", normalize_prim_path(path))

    @property
    def stage(self) -> Stage:
        return self._stage

    @property
    def path(self) -> str:
        return self._path

    @property
    def name(self) -> str:
        items = path_items(self._path)
        return items[-1] if items else ""

    @property
    def variant_sets(self) -> StageVariantSets:
        return StageVariantSets(self)

    @property
    def metadata(self) -> StageMetadata:
        return StageMetadata(self._stage, self._path)

    @property
    def resolved_prim(self) -> Optional[PrimSpec]:
        """The strongest contributing spec, i.e. where the composed value came from."""
        strongest = self._stage._engine.prim_index(self._path).strongest_spec
        return strongest.prim if strongest is not None else None

    @property
    def authored_prim(self) -> Optional[PrimSpec]:
        """The spec for this prim in the edit layer, or None if not authored there.

        The low-level counterpart to :attr:`resolved_prim`: the escape hatch for
        operations that shape stored data itself. Authoring goes through the view.
        """
        return prim_at(self._stage.edit_layer, self._path)

    @property
    def specifier(self) -> Optional[Specifier]:
        prim = self.resolved_prim
        return prim.specifier if prim is not None else None

    @property
    def type_name(self) -> Optional[str]:
        return self._stage._engine.resolve_metadata(self._path, "typeName")

    @property
    def child_names(self) -> List[str]:
        return self._stage.child_names(self._path)

    @property
    def children(self) -> List[Prim]:
        return [self.child(name) for name in self.child_names]

    @property
    def prop_names(self) -> List[str]:
        # Namespaced names are real properties: Gprim declares
        # primvars:displayColor and primvars:displayOpacity, Material declares
        # outputs:surface, Camera declares exposure:* and shutter:*. UsdPrim's own
        # GetPropertyNames has no such filter, so neither does this. The op
        # attributes under xformOp: are absent because nothing declares them -- they
        # are created on demand by AddXformOp -- not because they were filtered out.
        return self._stage._engine.property_names(self._path)

    @property
    def props(self) -> List[Property]:
        return [Property.wrap(self._stage, self._path, name) for name in self.prop_names]

    def has_prop(self, name: str) -> bool:
        return self._stage._engine.resolve_property(self._path, name) is not None

    def prop(self, name: str) -> Property:
        if not self.has_prop(name):
            raise KeyError(name)

        return Property.wrap(self._stage, self._path, name)

    def child(self, name: str) -> Prim:
        return self[join_relative_path("", name)]

    def _edit_spec(self) -> PrimSpec:
        return self._stage._ensure_edit_prim(self._path)

    def _add_arc(self, attr_name: str, target: Any, prepend: bool) -> None:
        spec = self._edit_spec()
        arcs = getattr(spec, attr_name)
        if target in arcs:
            return

        if prepend:
            arcs.insert(0, target)
        else:
            arcs.append(target)

        self._stage.invalidate()

    def _remove_arc(self, attr_name: str, target: Any) -> None:
        spec = self._edit_spec()
        arcs = getattr(spec, attr_name)
        if target in arcs:
            arcs.remove(target)

        self._stage.invalidate()

    def inherit(self, target: Union[PrimSpec, Layer], prepend: bool = True) -> None:
        self._add_arc("_inherits", target, prepend)

    def remove_inherit(self, target: Union[PrimSpec, Layer]) -> None:
        self._remove_arc("_inherits", target)

    def reference(self, target: Union[PrimSpec, Layer], prepend: bool = True) -> None:
        self._add_arc("_references", target, prepend)

    def remove_reference(self, target: Union[PrimSpec, Layer]) -> None:
        self._remove_arc("_references", target)

    def payload(self, target: Union[PrimSpec, Layer], prepend: bool = True) -> None:
        self._add_arc("_payloads", target, prepend)

    def remove_payload(self, target: Union[PrimSpec, Layer]) -> None:
        self._remove_arc("_payloads", target)

    def specialize(self, target: Union[PrimSpec, Layer], prepend: bool = True) -> None:
        self._add_arc("_specializes", target, prepend)

    def remove_specialize(self, target: Union[PrimSpec, Layer])->None:
        self._remove_arc("_specializes", target)

    def def_(self, prim_type: Type[PrimType], path: str) -> PrimType:
        return self._stage.def_(prim_type, join_relative_path(self._path, path))

    def class_(self, path: str) -> Prim:
        return self._stage.class_(join_relative_path(self._path, path))

    def over_(self, path: str) -> Prim:
        return self._stage.over_(join_relative_path(self._path, path))

    def __getitem__(self, path: str) -> Prim:
        return self._stage[join_relative_path(self._path, path)]

    def __setitem__(self, path: str, prim: PrimSpec) -> None:
        self._stage[join_relative_path(self._path, path)] = prim

    def __delitem__(self, path: str) -> None:
        del self._stage[join_relative_path(self._path, path)]

    def __getattr__(self, name: str) -> Any:
        if name.startswith("_"):
            # Prim is the base of every schema class, so in_annotations would pick
            # up their property declarations and mistake authored names for
            # internal fields. Internal state is underscore-prefixed by definition.
            raise AttributeError(name)

        # An API schema is not a property. PrimSpec.__getattr__ is what consults the
        # API registry, checks apiSchemaCanOnlyApplyTo, and hands back the schema
        # object (or an APIWrapper for multiple-apply), so route _api names there
        # instead of fabricating a property handle that resolves to nothing.
        if name.endswith("_api"):
            return getattr(self._edit_spec(), name)

        return Property.wrap(self._stage, self._path, name)

    def __setattr__(self, name: str, value: Any) -> None:
        if name.startswith("_"):
            object.__setattr__(self, name, value)
            return

        self._stage._set_property(self._path, name, value)

    def __str__(self) -> str:
        return f"Prim(<{self._path}>)"

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Prim):
            return self._stage is other._stage and self._path == other._path

        if isinstance(other, str):
            return self._path == normalize_prim_path(other)

        return False

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        return hash((id(self._stage), self._path))

    # The accessors below are the one generated region in this hand-written module.
    # They used to live in a pyusd/prim.pyi, but a module that ships both a .py and a
    # .pyi gives `ty` two unrelated `Prim` types, so every module annotating a Prim
    # parameter reported invalid-argument-type. PrimSpec.__getattr__ stays the single
    # runtime path; these are typed forwarders onto it, and __getattr__ still covers
    # any API schema that appears without a regeneration.
    # --- BEGIN generated api accessors ---
    @property
    def model_api(self)->ModelAPI:
        api:Any = self._edit_spec().model_api
        result:ModelAPI = api
        return result
    @property
    def color_space_api(self)->ColorSpaceAPI:
        api:Any = self._edit_spec().color_space_api
        result:ColorSpaceAPI = api
        return result
    def color_space_definition_api(self, instance_name:str)->ColorSpaceDefinitionAPI:
        api:Any = self._edit_spec().color_space_definition_api
        result:ColorSpaceDefinitionAPI = api(instance_name)
        return result
    def collection_api(self, instance_name:str)->CollectionAPI:
        api:Any = self._edit_spec().collection_api
        result:CollectionAPI = api(instance_name)
        return result
    @property
    def clips_api(self)->ClipsAPI:
        api:Any = self._edit_spec().clips_api
        result:ClipsAPI = api
        return result
    @property
    def primvars_api(self)->PrimvarsAPI:
        api:Any = self._edit_spec().primvars_api
        result:PrimvarsAPI = api
        return result
    @property
    def geom_model_api(self)->GeomModelAPI:
        api:Any = self._edit_spec().geom_model_api
        result:GeomModelAPI = api
        return result
    @property
    def motion_api(self)->MotionAPI:
        api:Any = self._edit_spec().motion_api
        result:MotionAPI = api
        return result
    @property
    def xform_common_api(self)->XformCommonAPI:
        api:Any = self._edit_spec().xform_common_api
        result:XformCommonAPI = api
        return result
    @property
    def light_api(self)->LightAPI:
        api:Any = self._edit_spec().light_api
        result:LightAPI = api
        return result
    @property
    def mesh_light_api(self)->MeshLightAPI:
        api:Any = self._edit_spec().mesh_light_api
        result:MeshLightAPI = api
        return result
    @property
    def volume_light_api(self)->VolumeLightAPI:
        api:Any = self._edit_spec().volume_light_api
        result:VolumeLightAPI = api
        return result
    @property
    def light_list_api(self)->LightListAPI:
        api:Any = self._edit_spec().light_list_api
        result:LightListAPI = api
        return result
    @property
    def list_api(self)->ListAPI:
        api:Any = self._edit_spec().list_api
        result:ListAPI = api
        return result
    @property
    def shaping_api(self)->ShapingAPI:
        api:Any = self._edit_spec().shaping_api
        result:ShapingAPI = api
        return result
    @property
    def shadow_api(self)->ShadowAPI:
        api:Any = self._edit_spec().shadow_api
        result:ShadowAPI = api
        return result
    @property
    def asset_previews_api(self)->AssetPreviewsAPI:
        api:Any = self._edit_spec().asset_previews_api
        result:AssetPreviewsAPI = api
        return result
    @property
    def node_def_api(self)->NodeDefAPI:
        api:Any = self._edit_spec().node_def_api
        result:NodeDefAPI = api
        return result
    @property
    def connectable_api(self)->ConnectableAPI:
        api:Any = self._edit_spec().connectable_api
        result:ConnectableAPI = api
        return result
    @property
    def material_binding_api(self)->MaterialBindingAPI:
        api:Any = self._edit_spec().material_binding_api
        result:MaterialBindingAPI = api
        return result
    def coord_sys_api(self, instance_name:str)->CoordSysAPI:
        api:Any = self._edit_spec().coord_sys_api
        result:CoordSysAPI = api(instance_name)
        return result
    @property
    def physics_rigid_body_api(self)->PhysicsRigidBodyAPI:
        api:Any = self._edit_spec().physics_rigid_body_api
        result:PhysicsRigidBodyAPI = api
        return result
    @property
    def physics_mass_api(self)->PhysicsMassAPI:
        api:Any = self._edit_spec().physics_mass_api
        result:PhysicsMassAPI = api
        return result
    @property
    def physics_collision_api(self)->PhysicsCollisionAPI:
        api:Any = self._edit_spec().physics_collision_api
        result:PhysicsCollisionAPI = api
        return result
    @property
    def physics_mesh_collision_api(self)->PhysicsMeshCollisionAPI:
        api:Any = self._edit_spec().physics_mesh_collision_api
        result:PhysicsMeshCollisionAPI = api
        return result
    @property
    def physics_material_api(self)->PhysicsMaterialAPI:
        api:Any = self._edit_spec().physics_material_api
        result:PhysicsMaterialAPI = api
        return result
    @property
    def physics_filtered_pairs_api(self)->PhysicsFilteredPairsAPI:
        api:Any = self._edit_spec().physics_filtered_pairs_api
        result:PhysicsFilteredPairsAPI = api
        return result
    def physics_limit_api(self, instance_name:str)->PhysicsLimitAPI:
        api:Any = self._edit_spec().physics_limit_api
        result:PhysicsLimitAPI = api(instance_name)
        return result
    def physics_drive_api(self, instance_name:str)->PhysicsDriveAPI:
        api:Any = self._edit_spec().physics_drive_api
        result:PhysicsDriveAPI = api(instance_name)
        return result
    @property
    def physics_articulation_root_api(self)->PhysicsArticulationRootAPI:
        api:Any = self._edit_spec().physics_articulation_root_api
        result:PhysicsArticulationRootAPI = api
        return result
    @property
    def statements_api(self)->StatementsAPI:
        api:Any = self._edit_spec().statements_api
        result:StatementsAPI = api
        return result
    @property
    def ri_material_api(self)->RiMaterialAPI:
        api:Any = self._edit_spec().ri_material_api
        result:RiMaterialAPI = api
        return result
    @property
    def ri_spline_api(self)->RiSplineAPI:
        api:Any = self._edit_spec().ri_spline_api
        result:RiSplineAPI = api
        return result
    def semantics_labels_api(self, instance_name:str)->SemanticsLabelsAPI:
        api:Any = self._edit_spec().semantics_labels_api
        result:SemanticsLabelsAPI = api(instance_name)
        return result
    @property
    def skel_binding_api(self)->SkelBindingAPI:
        api:Any = self._edit_spec().skel_binding_api
        result:SkelBindingAPI = api
        return result
    @property
    def node_graph_node_api(self)->NodeGraphNodeAPI:
        api:Any = self._edit_spec().node_graph_node_api
        result:NodeGraphNodeAPI = api
        return result
    @property
    def scene_graph_prim_api(self)->SceneGraphPrimAPI:
        api:Any = self._edit_spec().scene_graph_prim_api
        result:SceneGraphPrimAPI = api
        return result
    def accessibility_api(self, instance_name:str)->AccessibilityAPI:
        api:Any = self._edit_spec().accessibility_api
        result:AccessibilityAPI = api(instance_name)
        return result
    @property
    def particle_field_position_base_api(self)->ParticleFieldPositionBaseAPI:
        api:Any = self._edit_spec().particle_field_position_base_api
        result:ParticleFieldPositionBaseAPI = api
        return result
    @property
    def particle_field_kernel_base_api(self)->ParticleFieldKernelBaseAPI:
        api:Any = self._edit_spec().particle_field_kernel_base_api
        result:ParticleFieldKernelBaseAPI = api
        return result
    @property
    def particle_field_radiance_base_api(self)->ParticleFieldRadianceBaseAPI:
        api:Any = self._edit_spec().particle_field_radiance_base_api
        result:ParticleFieldRadianceBaseAPI = api
        return result
    # --- END generated api accessors ---

# Declared after the class so the bound can name Prim without a forward ref; a string
# bound leaves the type variable unsolvable across Stage.def_.
PrimType = TypeVar("PrimType", bound=Prim)
