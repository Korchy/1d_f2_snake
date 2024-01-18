# Nikita Akimov
# interplanety@interplanety.org
#
# GitHub
#    https://github.com/Korchy/1d_f2_snake

import bmesh
import bpy
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
        # get data loop from source mesh
        bm = bmesh.new()
        bm.from_mesh(context.object.data)
        bm.verts.ensure_lookup_table()
        bm.edges.ensure_lookup_table()
        src_vertices = [vertex for vertex in bm.verts if vertex.select]
        if src_vertices:
            first_vertex = next((vertex for vertex in src_vertices
                                 if len(vertex.link_edges) == 1), None)
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
                    bm.faces.new(chunk)
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
                # alarm break
                i += 1
                if i > _l:
                    print('vertices_loop_sorted() err exit')
                    break
        # return sorted sequence
        return vertices_sorted


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
