# -*- coding: UTF-8 -*-
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import bpy.utils.previews
from bpy.props import StringProperty, EnumProperty
from bpy.types import Operator, Menu
from bpy.app.handlers import persistent
import os
import bpy
import json
bl_info = {
    "name": "Nodes_SN",
    "author": "WXZ",
    "description": "",
    "blender": (3, 0, 0),
    "version": (1, 0, 0),
    "location": "",
    "warning": "",
    "category": "Node",
    "doc_url": "",
    "tracker_url": "",
}


def add_generators_button(self, context):
    if context.area.ui_type == 'ShaderNodeTree':
        self.layout.menu('NODE_MT_custom_SN_menu',
                         text="Custom_SN", icon='FUND')


shader_node_group_cache = {}
shader_cat_list = []

# adapted code from https://github.com/blender/blender/blob/master/release/scripts/modules/nodeitems_utils.py


def shader_cat_generator():
    global shader_cat_list
    shader_cat_list = []
    for item in shader_node_group_cache.items():

        def custom_draw(self, context):
            layout = self.layout
            for group_name in shader_node_group_cache[self.bl_label]:
                props = layout.operator(
                    NODE_OT_SN_group_add.bl_idname,
                    text=group_name,
                )
                props.group_name = group_name

        menu_type = type(
            "category_" + item[0],
            (bpy.types.Menu,),
            {
                "bl_idname": "category_"
                + item[0].replace(
                    " ", "_"
                ),  # replace whitespace with uderscore to avoid alpha-numeric suffix warning
                "bl_space_type": 'NODE_EDITOR',
                "bl_label": item[0],
                "draw": custom_draw,
            },
        )
        if menu_type not in shader_cat_list:
            shader_cat_list.append(menu_type)
            bpy.utils.register_class(menu_type)


class NODE_MT_custom_SN_menu(Menu):
    bl_label = "SN Custom Nodes"
    bl_idname = 'NODE_MT_custom_SN_menu'

    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'ShaderNodeTree'

    def draw(self, context):
        layout = self.layout
        for cat in shader_cat_list:
            layout.menu(cat.bl_idname)


class NODE_OT_SN_group_add(Operator):
    """Add a node template"""

    bl_idname = "custom_sn_nodes.template_add"
    bl_label = "Add node group"
    bl_description = "Append Node Group"
    bl_options = {'REGISTER', 'UNDO'}

    group_name: StringProperty()

    @classmethod
    def poll(cls, context):
        return context.space_data.node_tree

    def execute(self, context):
        old_groups = set(bpy.data.node_groups)
        filepath = os.path.join(os.path.dirname(__file__), "SN_Nodes.blend")
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

        bpy.ops.node.add_node(type="ShaderNodeGroup")

        node = context.selected_nodes[0]
        node.node_tree = bpy.data.node_groups[self.group_name]
        bpy.ops.transform.translate('INVOKE_DEFAULT')

        return {'FINISHED'}


classes = (NODE_MT_custom_SN_menu, NODE_OT_SN_group_add)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.NODE_MT_add.append(add_generators_button)
    global shader_node_group_cache

    for key in shader_node_group_cache:
        shader_node_group_cache[key] = []

    with open(os.path.join(os.path.dirname(__file__), "SN_Nodes.json"), 'r') as f:
        shader_node_group_cache = json.loads(f.read())

    shader_cat_generator()


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    bpy.types.NODE_MT_add.remove(add_generators_button)


if __name__ == "__main__":
    register()
