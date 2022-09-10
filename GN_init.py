from bpy.props import StringProperty
from bpy.types import Operator, Menu
import os
import bpy
import json

bl_info = {
    "name": "GN_Nodes_Presets",
    "author": "wxz",
    "description": "A collection of 2D signed distance functions and utilities",
    "blender": (3, 0, 0),
    "version": (0, 0, 1),
    "location": "Shader Editor > Add > GN_Nodes",
    "tracker_url": "",
    "doc_url": "",
    "category": "Node",
}


def add_generators_button(self, context):
    if context.area.ui_type == 'GeometryNodeTree':
        self.layout.menu(NODE_MT_GN_Nodes_Menu.bl_idname,
                         text="GN_Nodes", icon='FUND')


geo_node_group_cache = {}
geo_cat_list = []


def geo_cat_generator():
    global geo_cat_list
    geo_cat_list = []
    for item in geo_node_group_cache.items():

        def custom_draw(self, context):
            layout = self.layout
            for group_name in geo_node_group_cache[self.bl_label]:
                props = layout.operator(
                    NODE_OT_GN_group_add.bl_idname,
                    text=group_name,
                )
                props.group_name = group_name

        menu_type = type(
            "GN_category_" + item[0],
            (bpy.types.Menu),
            {
                "bl_idname": "GN_category_" + item[0].replace(" ", "_"),
                "bl_space_type": 'NODE_EDITOR',
                "bl_label": item[0],
                "draw": custom_draw,
            },
        )
        if menu_type not in geo_cat_list:
            geo_cat_list.append(menu_type)
            bpy.utils.register_class(menu_type)


class NODE_MT_GN_Nodes_Menu(Menu):
    bl_idname = __qualname__

    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'GeometryNodeTree'

    def draw(self, context):
        layout = self.layout
        for cat in geo_cat_list:
            layout.menu(cat.bl_idname)


class NODE_OT_GN_Nodes_add(Operator):
    bl_idname = "node.gn_nodes_group_add"
    bl_label = "Add node group"
    bl_description = "Append Node Group"
    bl_options = {'REGISTER', 'UNDO'}

    group_name: StringProperty()

    @classmethod
    def poll(cls, context):
        return context.space_data.node_tree

    def execute(self, context):
        old_groups = set(bpy.data.node_groups)
        filepath = os.path.join(os.path.dirname(__file__), "GN_Nodes.blend")
        with bpy.data.libraries.load(filepath, link=False) as (data_from, data_to):
            if self.group_name not in bpy.data.node_groups:
                data_to.node_groups.append(self.group_name)
        added_groups = list(set(bpy.data.node_groups) - old_groups)
        for group in added_groups:
            for node in group.nodes:
                if node.type == "GROUP":
                    new_name = node.node_tree.name.split(".")[0]
                    node.node_tree = bpy.data.node_groups[new_name]
        for group in added_groups:
            if "." in group.name:
                bpy.data.node_groups.remove(group)

        bpy.ops.node.add_node(type="GeometryNodeGroup")

        node = context.selected_nodes[0]
        node.node_tree = bpy.data.node_groups[self.group_name]
        bpy.ops.transform.translate('INVOKE_DEFAULT')

        return {'FINISHED'}


classes = (NODE_MT_GN_Nodes_Menu, NODE_OT_GN_Nodes_add)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.NODE_MT_add.append(add_generators_button)
    global geo_node_group_cache

    for key in geo_node_group_cache:
        geo_node_group_cache[key] = []

    with open(os.path.join(os.path.dirname(__file__), "GN_Nodes.json"), 'r') as f:
        geo_node_group_cache = json.loads(f.read())

    geo_cat_generator()


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    bpy.types.NODE_MT_add.remove(add_generators_button)


if __name__ == "__main__":
    register()
