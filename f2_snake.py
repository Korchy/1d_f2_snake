# Nikita Akimov
# interplanety@interplanety.org
#
# GitHub
#    https://github.com/Korchy/1d_f2_snake

import bmesh
import bpy
from bpy.props import EnumProperty, PointerProperty
from bpy.types import Operator, Panel, PropertyGroup, WindowManager
from bpy.utils import register_class, unregister_class

bl_info = {
    "name": "F2 Snake",
    "description": "Fills snake-like loop of vertices with polygons",
    "author": "Nikita Akimov, Paul Kotelevets",
    "version": (1, 0, 2),
    "blender": (2, 79, 0),
    "location": "View3D > Tool panel > 1D > F2 Snake",
    "doc_url": "https://github.com/Korchy/1d_f2_snake",
    "tracker_url": "https://github.com/Korchy/1d_f2_snake",
    "category": "All"
}


# MAIN CLASS

class F2Snake:

    @classmethod
    def fill(cls, context):
        # fill snake-like vertices loop with polygons
        src_obj = context.active_object
        # current mode
        mode = src_obj.mode
        # switch to OBJECT mode
        if src_obj.mode == 'EDIT':
            bpy.ops.object.mode_set(mode='OBJECT')
        # process object
        # get data from source mesh
        bm = bmesh.new()
        bm.from_mesh(context.object.data)
        bm.verts.ensure_lookup_table()
        bm.edges.ensure_lookup_table()
        # get loop starting from active vertex
        src_vertices = [vertex for vertex in bm.verts]
        if src_vertices:
            first_vertex = bm.select_history.active     # get active vertex as first
            selection_loop_sorted = cls.vertices_loop_sorted(
                bmesh_vertices_list=src_vertices,
                bmesh_first_vertex=first_vertex
            )
            # create faces by following selection loop
            for chunk in cls.chunks(
                    lst=selection_loop_sorted,
                    n=4,        # quad faces (4 vertices)
                    offset=2    # offset =-2 because snake-line line has 2 same vertices in each polygon
            ):
                if len(chunk) == 4:     # don't create non quad faces
                    if context.window_manager.f2snake_interface_vars.algorithm == 'snake':
                        # snake algorithm
                        bm.faces.new(chunk)
                    elif context.window_manager.f2snake_interface_vars.algorithm == 'saw':
                        # saw algorithm
                        # remove edge between 2-nd and 3-rd vertices
                        edge = next(iter(set(chunk[1].link_edges) & set(chunk[2].link_edges)), None)
                        if edge:
                            bm.edges.remove(edge)
                        bm.faces.new([chunk[0], chunk[2], chunk[3], chunk[1]])
        # recalculate normals
        bmesh.ops.recalc_face_normals(bm, faces=[face for face in bm.faces])
        # save changed data to mesh
        bm.to_mesh(src_obj.data)
        bm.free()
        # return mode back
        context.scene.objects.active = src_obj
        bpy.ops.object.mode_set(mode=mode)

    @staticmethod
    def chunks(lst, n, offset=0):
        # split list 'lst' to chunks each of 'n' elements with offset
        for i in range(0, len(lst), n - offset):
            yield lst[i:i + n]

    @staticmethod
    def vertices_loop_sorted(bmesh_vertices_list, bmesh_first_vertex):
        # return list with vertices sorted by following each other in the loop
        # breaks if loop ends with polygon
        vertices_sorted = []
        if bmesh_vertices_list and bmesh_first_vertex:
            vertex = bmesh_first_vertex
            _l = len(bmesh_vertices_list)
            i = 0
            while vertex is not None:
                vertices_sorted.append(vertex)
                edge = next((_edge for _edge in vertex.link_edges
                             if _edge.other_vert(vertex) not in vertices_sorted), None)
                vertex = edge.other_vert(vertex) if edge else None
                # stop loop if vertex has linked polygons
                vertex = vertex if vertex and len(vertex.link_faces) == 0 else None
                # alarm break
                i += 1
                if i > _l:
                    print('vertices_loop_sorted() err exit')
                    break
        # return sorted sequence
        return vertices_sorted


# INTERFACE VARS

class F2SnakeInterfaceVars(PropertyGroup):
    algorithm = EnumProperty(
        items=[
            ('snake', 'Snake', 'Snake', '', 0),
            ('saw', 'Saw', 'Saw', '', 1)
        ],
        default='saw'
    )


# OPERATORS

class F2Snake_OT_fill(Operator):
    bl_idname = 'f2snake.fill'
    bl_label = 'Fill'
    bl_description = 'Fill wiremesh loop with quads'
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
    bl_label = 'F2 Snake'
    bl_category = '1D'

    def draw(self, context):
        layout = self.layout
        layout.operator(
            operator='f2snake.fill',
            icon='SURFACE_DATA'
        )
        layout.prop(
            data=context.window_manager.f2snake_interface_vars,
            property='algorithm',
            expand=True
        )


# REGISTER

def register():
    register_class(F2SnakeInterfaceVars)
    WindowManager.f2snake_interface_vars = PointerProperty(
        type=F2SnakeInterfaceVars
    )
    register_class(F2Snake_OT_fill)
    register_class(F2Snake_PT_panel)


def unregister():
    unregister_class(F2Snake_PT_panel)
    unregister_class(F2Snake_OT_fill)
    del WindowManager.f2snake_interface_vars
    unregister_class(F2SnakeInterfaceVars)


if __name__ == "__main__":
    register()
