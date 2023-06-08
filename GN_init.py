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

bl_info = {
    "name" : "GN_Nodes_Presets",
    "author" : "wxz",
    "description" : "A collection of useful nodegroups to enhance Geometry Nodes.",
    "blender" : (3, 4, 0),
    "version" : (0, 1, 0),
    "location" : "Geometry Nodes Editor > Add > GN_Nodes",
    "warning" : "Restart Blender after disabling/uninstalling",
    "doc_url" : "",
    "category" : "Node"
}
    
import json
import bpy
import os
import re
from bpy.types import (
    Operator,
    Menu,
)
from bpy.props import (
    StringProperty,
    EnumProperty,
    BoolProperty,
    PointerProperty
)


def add_gn_nodes_button(self, context):
    if context.area.ui_type == 'GeometryNodeTree':
        self.layout.menu('NODE_MT_GN_Nodes', text="GN_Nodes", icon='FUND')


higgsas_node_group_cache = {}
geo_cat_list = []

dir_path = os.path.dirname(__file__)

# adapted code from https://github.com/blender/blender/blob/master/release/scripts/modules/nodeitems_utils.py
def geo_cat_generator():
    global geo_cat_list
    geo_cat_list = []
    for item in higgsas_node_group_cache.items():
        def custom_draw(self,context):
            layout = self.layout
            for group_name in higgsas_node_group_cache[self.bl_label]:
                props = layout.operator(
                    NODE_OT_GN_Nodes_Group.bl_idname,
                    text=re.sub(r'.*?_', '', group_name), # filter prefix
                )
                props.group_name = group_name

        menu_type = type("NODE_MT_category_" + item[0], (bpy.types.Menu,),
        {
            # replace whitespace with uderscore to avoid alpha-numeric suffix warning 
            "bl_idname": "NODE_MT_category_" + item[0].replace(" ", "_"),   
            "bl_space_type": 'NODE_EDITOR',
            "bl_label": item[0],
            "draw": custom_draw,
        })
        if menu_type not in geo_cat_list:
            def generate_menu_draw(name,label): # Wrapper function to force unique references
                def draw_menu(self,context):
                    self.layout.menu(name, text=label)
                return draw_menu
            bpy.utils.register_class(menu_type)
            bpy.types.NODE_MT_GN_Nodes.append(generate_menu_draw(menu_type.bl_idname,menu_type.bl_label))
            geo_cat_list.append(menu_type)


class NODE_MT_GN_Nodes(Menu):
    bl_label = "GN_Nodes"
    bl_idname = 'NODE_MT_GN_Nodes'

    @classmethod
    def poll(cls,context):
        return context.space_data.tree_type == 'GeometryNodeTree'

    def draw(self, context):
        pass

class NODE_OT_GN_Nodes_Group(Operator):
    """Add a node group"""
    bl_idname = "gn." + os.path.basename(dir_path).lower()
    bl_label = "Add node group"
    bl_description = "Append Node Group"
    bl_options = {'REGISTER', 'UNDO'}

    group_name: StringProperty()

    @classmethod
    def poll(cls,context):
        return context.space_data.node_tree

    def execute(self, context):
        old_groups = set(bpy.data.node_groups)
        
        filepath = os.path.join(dir_path,'GN_Nodes.blend')
                
        with bpy.data.libraries.load(filepath, link=False) as (data_from, data_to):
            if self.group_name not in bpy.data.node_groups:
                data_to.node_groups.append(self.group_name)
        added_groups = list(set(bpy.data.node_groups)-old_groups)
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

def search_prop_group_by_ntree(self,context):
        for prop in context.scene.use_render:
            if prop.n_tree == context.space_data.node_tree:
                return prop


classes = (
    NODE_OT_GN_Nodes_Group,
    )


def register():
    global higgsas_node_group_cache

    with open(os.path.join(os.path.dirname(__file__), "GN_Nodes.json"), 'r') as h:
        higgsas_node_group_cache = json.loads(h.read())

    if not hasattr(bpy.types, "NODE_MT_GN_Nodes"):
        bpy.utils.register_class(NODE_MT_GN_Nodes)
        bpy.types.NODE_MT_add.append(add_gn_nodes_button)
    for cls in classes:
        bpy.utils.register_class(cls)

    geo_cat_generator()

def unregister():
    if hasattr(bpy.types, "NODE_MT_GN_Nodes"):
        bpy.types.NODE_MT_add.remove(add_gn_nodes_button)
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
