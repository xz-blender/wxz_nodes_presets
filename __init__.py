from bpy.types import PropertyGroup, AddonPreferences, Operator
from bpy.props import BoolProperty, PointerProperty, StringProperty
import bpy
import os

bl_info = {
    "name": "wxz_nodes_presets",
    "author": "wxz",
    "version": (0, 1, 0),
    "blender": (2, 80, 0),
    "category": "Node",
}


sub_modules_names = [
    "CN_init",
    "GN_init",
    "SN_init"
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


def create_property(cls, name, prop):
    if not hasattr(cls, '__annotations__'):
        cls.__annotations__ = dict()
    cls.__annotations__[name] = prop


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
        CN_path = os.path.join(os.path.dirname(__file__), 'CN_Nodes.blend')
        GN_path = os.path.join(os.path.dirname(__file__), 'GN_Nodes.blend')
        SN_path = os.path.join(os.path.dirname(__file__), 'SN_Nodes.blend')

        layout = self.layout
        box = layout.box()
        row = box.row()
        op = row.operator(Open_File_With_New_Program.bl_idname,
                          text='打开Composite Nodes文件')
        op.path = CN_path
        op.hide_props_region = False
        op = row.operator(Open_File_With_New_Program.bl_idname,
                          text='打开Geometry Nodes文件')
        op.path = GN_path
        op = row.operator(Open_File_With_New_Program.bl_idname,
                          text='打开Shader Nodes文件')
        op.path = SN_path


class Open_File_With_New_Program(Operator):
    bl_label = ''
    bl_idname = 'file.open_file_with_new_program'
    bl_options = {'REGISTER', 'UNDO'}

    path: StringProperty()
    hide_props_region: BoolProperty()

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        path = self.path
        bpy.ops.wm.open_mainfile(filepath=path)
        return {'FINISHED'}


classes = [
    WXZ_Nodes_Presets_Preferences,
    Open_File_With_New_Program,

]


for mod in sub_modules:
    info = mod.bl_info
    mod_name = mod.__name__.split('.')[-1]

    def gen_update(mod):
        def update(self, context):
            enabled = getattr(self, 'use_' + mod.__name__.split('.')[-1])
            if enabled:
                register_submodule(mod)
            else:
                unregister_submodule(mod)
            mod.__addon_enabled__ = enabled

        return update


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    prefs = get_addon_preferences()
    for mod in sub_modules:
        if not hasattr(mod, '__addon_enabled__'):
            mod.__addon_enabled__ = False
        register_submodule(mod)


def unregister():
    for mod in sub_modules:
        if mod.__addon_enabled__:
            unregister_submodule(mod)

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
