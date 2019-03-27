import bpy
import math
import os,re
bl_info = {
    "name":"Curve_array_bevel_taper_setup",
    "author": "iCyP",
    "version": (0, 1),
    "blender": (2, 80, 0),
    "location": "ObjectMode->Right click",
    "description": "simple setup curve to array, bevel, taper",
    "warning": "",
    "support": "TESTING",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Object"
}

def get_enum(data_kind):
    enum_obj = []
    filedir = os.path.join(os.path.dirname(__file__),"resources",f"{data_kind}s.blend")
    with bpy.data.libraries.load(filedir, link=False) as (data_from, data_to):
        enum_obj =  [ (curve,curve,"") for curve in data_from.curves]
    return enum_obj

def get_bevel_enum(scene, context):
    return get_enum("bevel")
def get_taper_enum(scene, context):
    return get_enum("taper")

class ICYP_OT_curve_array_setup(bpy.types.Operator):
    bl_idname = "object.icyp_curve_setup"
    bl_label = "setup curve to array and bevel taper"
    bl_description = "setup curve to array bevel taper"
    bl_options = {'REGISTER', 'UNDO'}
    
    add_array : bpy.props.BoolProperty(default = True)
    taper_type : bpy.props.EnumProperty(name = "Taper type",description ="Taper type",items = get_taper_enum)
    bevel_type : bpy.props.EnumProperty(name = "Bevel type",description ="Bevel type",items = get_bevel_enum)
    def curve_import(self):
        taper,bevel = None,None
        filedir = os.path.join(os.path.dirname(__file__),"resources","bevels.blend")
        with bpy.data.libraries.load(filedir, link=False) as (data_from, data_to):
            for curve_name in data_from.curves:
                if curve_name == self.bevel_type:
                    data_to.curves = [curve_name]
        bevel = data_to.curves[0]
        filedir = os.path.join(os.path.dirname(__file__),"resources","tapers.blend")
        with bpy.data.libraries.load(filedir, link=False) as (data_from, data_to):
            for curve_name in data_from.curves:
                if curve_name == self.taper_type:
                    data_to.curves = [curve_name]
        taper = data_to.curves[0]
        return taper,bevel
    def execute(self,context):   
        target_obj = context.active_object
        if self.add_array:
            origin_empty = bpy.data.objects.new("pos",None)
            array_offset_empty = bpy.data.objects.new("offset",None)
            colle = bpy.data.collections.new("pro_hair")
            bpy.context.scene.collection.children.link(colle)
            colle.objects.link(origin_empty)
            colle.objects.link(array_offset_empty)
            colle.objects.link(target_obj)
            origin_empty.location = target_obj.location
            origin_empty.empty_display_size = 0.3
            origin_empty.show_name = True
            array_offset_empty.show_name = True
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
            target_obj.location = (0,0,0)
        else:
            colle = bpy.data.collections.new("curve_set")
            colle.objects.link(target_obj)
            bpy.context.scene.collection.children.link(colle)
            for coll in target_obj.users_collection:
                if coll is not colle:
                    coll.objects.unlink(target_obj)
            
        def curve_setup(isTaper,curve,difPos,parent_obj):
            c = bpy.data.objects.new("taper" if isTaper else "bevel",curve)
            colle.objects.link(c)
            c.parent = parent_obj
            if isTaper:
                target_obj.data.taper_object = c
            else: #isBevel
                target_obj.data.bevel_object = c
            c.location[2] += difPos
            c.show_name = True
            c.data.dimensions = "2D"            

        taper,bevel = self.curve_import()
        parent_object = origin_empty if self.add_array else target_obj 
        curve_setup(False,bevel,0.45,parent_object)
        curve_setup(True,taper,0.6,parent_object)
        return {'FINISHED'}
    
# アドオン有効化時の処理
classes = [
    ICYP_OT_curve_array_setup
    ]
    
def add_button(self, context):
    if context.active_object.type == "CURVE":
        self.layout.operator(ICYP_OT_curve_array_setup.bl_idname)
    
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.VIEW3D_MT_object_context_menu.append(add_button)
    
# アドオン無効化時の処理
def unregister():
    bpy.types.VIEW3D_MT_object_context_menu.remove(add_button)
    for cls in classes:
        bpy.utils.unregister_class(cls)

if "__main__" == __name__:
    register()
