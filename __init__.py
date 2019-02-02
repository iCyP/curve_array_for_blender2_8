import bpy
import math
import os,re
bl_info = {
    "name":"HAIR_GEN",
    "author": "iCyP",
    "version": (0, 1),
    "blender": (2, 80, 0),
    "location": "ObjectMode->Right click",
    "description": "simple setup curve to array_hair",
    "warning": "",
    "support": "TESTING",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Object"
}


class ICYP_OT_hair_generator(bpy.types.Operator):
    bl_idname = "object.icyp_curve_setup"
    bl_label = "setup curve to array and bevel taper"
    bl_description = "setup curve to array bevel taper"
    bl_options = {'REGISTER', 'UNDO'}
    
    
    def curve_import(self):
        filedir = os.path.join(os.path.dirname(os.path.dirname(__file__)),"hair_array","resources","curves.blend")
        with bpy.data.libraries.load(filedir, link=False) as (data_from, data_to):
            data_to.curves = data_from.curves
            return data_to.curves    
    def execute(self,context):
        target_obj = context.active_object
        origin_empty = bpy.data.objects.new("pos",None)
        array_offset_empty = bpy.data.objects.new("offset",None)
        colle = bpy.data.collections.new("pro_hair")
        bpy.context.scene.collection.children.link(colle)
        colle.objects.link(origin_empty)
        colle.objects.link(array_offset_empty)
        colle.objects.link(target_obj)
        for coll in target_obj.users_collection:
            if coll is not colle:
                coll.objects.unlink(target_obj)
        origin_empty.empty_display_type = "SPHERE"
        array_offset_empty.parent = origin_empty
        array_offset_empty.rotation_euler[2] = math.radians(10)
        target_obj.parent = origin_empty
        mod = target_obj.modifiers.new("arr","ARRAY")
        mod.use_relative_offset = False
        mod.use_object_offset = True
        mod.offset_object = array_offset_empty
        mod.count = 10
        curves = self.curve_import()
        for curve in curves:
            if re.match("bevel",curve.name):
                b = bpy.data.objects.new("bevel",curve)
                colle.objects.link(b)
                target_obj.data.bevel_object = b
                b.parent = origin_empty
            elif re.match("taper",curve.name):
                t = bpy.data.objects.new("taper",curve)
                colle.objects.link(t)
                target_obj.data.taper_object = t
                t.parent = origin_empty
        return {'FINISHED'}
    
# アドオン有効化時の処理
classes = [
    ICYP_OT_hair_generator
    ]
    
def add_button(self, context):
    self.layout.operator(ICYP_OT_hair_generator.bl_idname)
    
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.VIEW3D_MT_object_specials.append(add_button)
    
# アドオン無効化時の処理
def unregister():
    bpy.types.VIEW3D_MT_object_specials.remove(add_button)
    for cls in classes:
        bpy.utils.unregister_class(cls)

if "__main__" == __name__:
    register()
