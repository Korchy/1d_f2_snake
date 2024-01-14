# Nikita Akimov
# interplanety@interplanety.org
#
# GitHub
#    https://github.com/Korchy/1d_f2_snake

# import bmesh
# import bpy
from bpy.types import Operator, Panel
from bpy.utils import register_class, unregister_class

bl_info = {
    "name": "F2 Snake",
    "description": "Fills snake-like loop of vertices with polygons",
    "author": "Nikita Akimov, Paul Kotelevets",
    "version": (1, 0, 0),
    "blender": (2, 79, 0),
    "location": "View3D > Tool panel > 1D > F2 Snake",
    "doc_url": "https://github.com/Korchy/1d_f2_snake",
    "tracker_url": "https://github.com/Korchy/1d_f2_snake",
    "category": "All"
}


# MAIN CLASS

class F2Snake:

    @staticmethod
    def fill(context):
        pass


# OPERATORS

class F2Snake_OT_fill(Operator):
    bl_idname = 'f2snake.fill'
    bl_label = 'Fill'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        F2Snake.fill(
            context=context
        )
        return {'FINISHED'}


# PANELS

class F2Snake_PT_panel(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_label = "F2 Snake"
    bl_category = '1D'

    def draw(self, context):
        self.layout.operator(
            operator='f2snake.fill',
            icon='SURFACE_DATA'
        )


# REGISTER

def register():
    register_class(F2Snake_OT_fill)
    register_class(F2Snake_PT_panel)


def unregister():
    unregister_class(F2Snake_PT_panel)
    unregister_class(F2Snake_OT_fill)


if __name__ == "__main__":
    register()
