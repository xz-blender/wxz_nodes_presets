from bpy.types import PropertyGroup, AddonPreferences, Operator
from bpy.props import BoolProperty, PointerProperty
import bpy
import os

bl_info = {
    "name": "wxz_nodes_presets",
    "description": "",
    "author": "wxz",
    "version": (0, 0, 1),
    "blender": (2, 9, 0),
    "location": "Node Editor",
    "warning": "",
    "wiki_url": "",
    "category": "Node"}


sub_modules_names = [
    # "CN_init",
    "GN_init",
    # "SN_init"
]
sub_modules = [
    __import__(__package__ + "." + submod, {}, {}, submod)
    for submod in sub_modules_names
]


def _get_pref_class(mod):
    import inspect

    for obj in vars(mod).values():
        if inspect.isclass(obj) and issubclass(obj, PropertyGroup):
            if hasattr(obj, 'bl_idname') and obj.bl_idname == mod.__name__:
                return obj


def get_addon_preferences(name=''):
    """Acquisition and registration"""
    addons = bpy.context.preferences.addons
    if __name__ not in addons:  # wm.read_factory_settings()
        return None
    addon_prefs = addons[__name__].preferences
    if name:
        if not hasattr(addon_prefs, name):
            for mod in sub_modules:
                if mod.__name__.split('.')[-1] == name:
                    cls = _get_pref_class(mod)
                    if cls:
                        prop = PointerProperty(type=cls)
                        create_property(
                            WXZ_Nodes_Presets_Preferences, name, prop)
                        bpy.utils.unregister_class(
                            WXZ_Nodes_Presets_Preferences)
                        bpy.utils.register_class(WXZ_Nodes_Presets_Preferences)
        return getattr(addon_prefs, name, None)
    else:
        return addon_prefs


def register_submodule(mod):
    mod.register()
    mod.__addon_enabled__ = True


def unregister_submodule(mod):
    if mod.__addon_enabled__:
        mod.unregister()
        mod.__addon_enabled__ = False

        prefs = get_addon_preferences()
        name = mod.__name__.split('.')[-1]
        if hasattr(WXZ_Nodes_Presets_Preferences, name):
            delattr(WXZ_Nodes_Presets_Preferences, name)
            if prefs:
                bpy.utils.unregister_class(WXZ_Nodes_Presets_Preferences)
                bpy.utils.register_class(WXZ_Nodes_Presets_Preferences)
                if name in prefs:
                    del prefs[name]


class WXZ_Nodes_Presets_Preferences(AddonPreferences):
    # bl_idname = 'wxz.nodes_presets_prefernses'
    bl_idname = __name__

    def draw(self, context):
        layout = self.layout

        CN_path = os.path.join(os.path.getcwd(), 'CN_Nodes.blend')
        GN_path = os.path.join(os.path.getcwd(), 'GN_Nodes.blend')
        SN_path = os.path.join(os.path.getcwd(), 'SN_Nodes.blend')

        row = layout.box().row()
        row.alignment = 'RIGHT'
        sub_row = row.row()
        sub_row.label(text=GN_path)
        sub_row = row.row()
        sub_row.scale_x = 1.4
        sub_row.operator('wm.open_mainfile', text='打开GN文件')


classes = [
    WXZ_Nodes_Presets_Preferences,

]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    prefs = get_addon_preferences()
    for mod in sub_modules:
        if not hasattr(mod, '__addon_enabled__'):
            mod.__addon_enabled__ = False
        name = mod.__name__.split('.')[-1]
        if getattr(prefs, 'use_' + name):
            register_submodule(mod)


def unregister():
    for mod in sub_modules:
        if mod.__addon_enabled__:
            unregister_submodule(mod)

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
