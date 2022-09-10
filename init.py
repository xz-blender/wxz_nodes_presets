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


def main(context):
    for ob in context.scene.objects:
        print(ob)


class WXZ_Nodes_Presets_Preferences(AddonPreferences):
    bl_idname = 'wxz.nodes_presets_prefernses'

    def draw(self, context):
        layout = self.layout

        CN_path = os.path.join(os.path.getcwd(), 'CN', 'CN_Nodes.blend')
        GN_path = os.path.join(os.path.getcwd(), 'GN', 'GN_Nodes.blend')
        SN_path = os.path.join(os.path.getcwd(), 'SN', 'SN_Nodes.blend')

        row = layout.row()
        row.label


classes = [
    WXZ_Nodes_Presets_Preferences,

]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.register_class(cls)


if __name__ == "__main__":
    register()
