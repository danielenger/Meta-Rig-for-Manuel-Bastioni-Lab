#    Rigify Meta-Rig for ManuelBastioniLAB
#    Copyright (C) 2017-2018 Daniel Engler

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.

bl_info = {
    "name": "Rigify Meta-Rig for ManuelBastioniLAB",
    "author": "Daniel Engler",
    "version": (0, 4, 1),
    "blender": (2, 79, 0),
    "location": "View3D > ManuelBastioniLAB",
    "description": "Adds a new Rigify Meta-Rig for ManuelBastioniLAB Characters",
    "category": "Characters",
    }

import bpy
from mathutils import Vector

metarig_bone_names = { # metarig_bone : mlab_bone
    "spine":"pelvis",
    "spine.001":"spine01",
    "spine.002":"spine02",
    "spine.003":"spine03",
    "spine.006":"head",
    "spine.005":"neck",
    "breast.L":"breast_L",
    "foot.L":"foot_L",
    "toe.L":"toes_L",
    "shoulder.L":"clavicle_L",
    "hand.L":"hand_L",
    "thumb.01.L":"thumb01_L",
    "thumb.02.L":"thumb02_L",
    "thumb.03.L":"thumb03_L",
    "palm.01.L":"index00_L",
    "f_index.01.L":"index01_L",
    "f_index.02.L":"index02_L",
    "f_index.03.L":"index03_L",
    "palm.02.L":"middle00_L",
    "f_middle.01.L":"middle01_L",
    "f_middle.02.L":"middle02_L",
    "f_middle.03.L":"middle03_L",
    "palm.03.L":"ring00_L",
    "f_ring.01.L":"ring01_L",
    "f_ring.02.L":"ring02_L",
    "f_ring.03.L":"ring03_L",
    "palm.04.L":"pinky00_L",
    "f_pinky.01.L":"pinky01_L",
    "f_pinky.02.L":"pinky02_L",
    "f_pinky.03.L":"pinky03_L",
    "breast.R":"breast_R",
    "foot.R":"foot_R",
    "toe.R":"toes_R",
    "shoulder.R":"clavicle_R",
    "hand.R":"hand_R",
    "thumb.01.R":"thumb01_R",
    "thumb.02.R":"thumb02_R",
    "thumb.03.R":"thumb03_R",
    "palm.01.R":"index00_R",
    "f_index.01.R":"index01_R",
    "f_index.02.R":"index02_R",
    "f_index.03.R":"index03_R",
    "palm.02.R":"middle00_R",
    "f_middle.01.R":"middle01_R",
    "f_middle.02.R":"middle02_R",
    "f_middle.03.R":"middle03_R",
    "palm.03.R":"ring00_R",
    "f_ring.01.R":"ring01_R",
    "f_ring.02.R":"ring02_R",
    "f_ring.03.R":"ring03_R",
    "palm.04.R":"pinky00_R",
    "f_pinky.01.R":"pinky01_R",
    "f_pinky.02.R":"pinky02_R",
    "f_pinky.03.R":"pinky03_R",
}
metarig_bone_arm_names = { # metarig_bone : mlab_bone
    "upper_arm.L":"upperarm_L",
    "forearm.L":"lowerarm_L",
    "upper_arm.R":"upperarm_R",
    "forearm.R":"lowerarm_R",
}

metarig_bone_leg_names = { # metarig_bone : mlab_bone - only legs, no feet!
    "thigh.L":"thigh_L",
    "shin.L":"calf_L",
    "thigh.R":"thigh_R",
    "shin.R":"calf_R",
}

mlab_bone_names = { # mlab_bone : DEF-metarig_bone - for rename only
    "upperarm_twist_L":"DEF-upper_arm.L",
    "upperarm_L":"DEF-upper_arm.L.001",
    "lowerarm_twist_L":"DEF-forearm.L.001",
    "lowerarm_L":"DEF-forearm.L",
    "thigh_twist_L":"DEF-thigh.L",
    "thigh_L":"DEF-thigh.L.001",
    "calf_twist_L":"DEF-shin.L.001",
    "calf_L":"DEF-shin.L",
    "upperarm_twist_R":"DEF-upper_arm.R",
    "upperarm_R":"DEF-upper_arm.R.001",
    "lowerarm_twist_R":"DEF-forearm.R.001",
    "lowerarm_R":"DEF-forearm.R",
    "thigh_twist_R":"DEF-thigh.R",
    "thigh_R":"DEF-thigh.R.001",
    "calf_twist_R":"DEF-shin.R.001",
    "calf_R":"DEF-shin.R",
}

class MetarigForMLAB(bpy.types.Operator):
    """Add new Meta-Rig for ManuelBastioniLAB Characters
    - MLAB Armature must be selected"""
    bl_idname = "object.metarig_for_mlab_operator"
    bl_label = "Rigify Meta-Rig for MLAB"
    bl_options = {'REGISTER', 'UNDO'}

    bool_straight_legs = bpy.props.BoolProperty(name="Straight Legs",
                                                    description="", 
                                                    default=True)
    knee_offset_y = bpy.props.FloatProperty(name="Knee y Offset", 
                                                default=0.0,#-0.01,
                                                step=0.3,
                                                precision=3)
                                                
    def execute(self, context):
        bone_data = {} # "name of meta rig bone" : (3 Vectors head, tail, roll)
        
        mlab_rig = context.active_object
        if mlab_rig.type == 'ARMATURE':
            ########
            # start mlab edit mode 
            bpy.ops.object.mode_set(mode='EDIT')
            # get bone data from mlab rig and store vectors (head, tail, roll) in bone_data dictionary
            for metarig_bone, mlab_bone in metarig_bone_names.items():
                b = mlab_rig.data.edit_bones[mlab_bone]
                bone_data[metarig_bone] = (b.head.copy(), b.tail.copy(), b.roll)
            # repeat for arm bones
            for metarig_bone, mlab_bone in metarig_bone_arm_names.items():
                b = mlab_rig.data.edit_bones[mlab_bone]
                bone_data[metarig_bone] = (b.head.copy(), b.tail.copy(), b.roll)
            
            # straight legs and knee offset fix for metarig
            # TODO: fix shin deformation/rotation
            if self.bool_straight_legs:
                tmp_leg_dict = {"thigh.L":"shin.L", "thigh.R":"shin.R", }
                for thigh_name, shin_name in tmp_leg_dict.items():
                    mlab_thigh_name = metarig_bone_leg_names[thigh_name] # "thigh_L/R"
                    mlab_shin_name = metarig_bone_leg_names[shin_name] # "calf_L/R"
                    
                    # new knee position for straight legs                    
                    tmp_thigh_head = mlab_rig.data.edit_bones[mlab_thigh_name].head.copy()
                    tmp_thigh_tail = mlab_rig.data.edit_bones[mlab_shin_name].tail.copy()
                    tmp_thigh_roll = mlab_rig.data.edit_bones[mlab_thigh_name].roll
                    tmp_shin_roll = mlab_rig.data.edit_bones[mlab_shin_name].roll
                    new_length = mlab_rig.data.edit_bones[mlab_thigh_name].length 
                    new_straight_legs_knee_pos = new_length * ( 
                                                    (tmp_thigh_tail - 
                                                    tmp_thigh_head).normalized() ) + tmp_thigh_head
                    # y from mlab knee
                    new_straight_legs_knee_pos.y = mlab_rig.data.edit_bones[mlab_shin_name].head.y
                    new_knee_pos = new_straight_legs_knee_pos
                    new_knee_pos.y = new_straight_legs_knee_pos.y + self.knee_offset_y
                    bone_data[thigh_name] = (   tmp_thigh_head, 
                                                new_knee_pos, 
                                                tmp_thigh_roll)
                    bone_data[shin_name] = (new_knee_pos,
                                            tmp_thigh_tail,
                                            tmp_shin_roll)
            else:
                for metarig_bone, mlab_bone in metarig_bone_leg_names.items():
                    b = mlab_rig.data.edit_bones[mlab_bone]
                    bone_data[metarig_bone] = (b.head.copy(), b.tail.copy(), b.roll)
                                
            # x location for metarig heels from mlab "foot_L/R" head
            foot_l_x = mlab_rig.data.edit_bones["foot_L"].head.x
            foot_r_x = mlab_rig.data.edit_bones["foot_R"].head.x
            
            ########
            # end mlab edit mode
            bpy.ops.object.mode_set(mode='OBJECT')
            
            # create meta rig
            #bpy.context.scene.cursor_location = mlab_rig.location
            bpy.ops.object.armature_human_metarig_add()
            meta_rig = context.active_object
            meta_rig.location = mlab_rig.location
            
            ########
            # start metarig edit mode 
            bpy.ops.object.mode_set(mode='EDIT')
            
            # metarig heels            
            foot_l_x = bone_data["foot.L"][0][0] # mlab_rig.data.edit_bones["foot_L"].head.x
            foot_r_x = bone_data["foot.R"][0][0] # mlab_rig.data.edit_bones["foot_R"].head.x
            # y and z from mlab object origin is the same for left and right
            heel_y = mlab_rig.location.y
            heel_z = mlab_rig.location.z            
            bone_name = "heel.02.L"
            bone_heel_l = meta_rig.data.edit_bones[bone_name]
            # metarig heel x location relative in middle to mlab foot head
            heel_l_head_x = (bone_heel_l.head.x - bone_heel_l.tail.x)/2 + foot_l_x
            heel_l_tail_x = (bone_heel_l.tail.x - bone_heel_l.head.x)/2 + foot_l_x
            # create new vectors from collected data
            bone_heel_l_head = Vector( (heel_l_head_x, heel_y, heel_z) )
            bone_heel_l_tail = Vector( (heel_l_tail_x, heel_y, heel_z) )
            bone_heel_l_roll = meta_rig.data.edit_bones[bone_name].roll
            # store data
            bone_data[bone_name] = (bone_heel_l_head, bone_heel_l_tail, bone_heel_l_roll)
            
            bone_name = "heel.02.R"
            bone_heel_r = meta_rig.data.edit_bones[bone_name]
            # metarig heel x location relative in middle to mlab foot head
            heel_r_head_x = (bone_heel_r.head.x - bone_heel_r.tail.x)/2 + foot_r_x
            heel_r_tail_x = (bone_heel_r.tail.x - bone_heel_r.head.x)/2 + foot_r_x
            # create new vectors from collected data
            bone_heel_r_head = Vector( (heel_r_head_x, heel_y, heel_z) )
            bone_heel_r_tail = Vector( (heel_r_tail_x, heel_y, heel_z) )
            bone_heel_r_roll = meta_rig.data.edit_bones[bone_name].roll
            # store data
            bone_data[bone_name] = (bone_heel_r_head, bone_heel_r_tail, bone_heel_r_roll)

            # meta rig pelvis
            new_pelvis_head = bone_data["spine"][0] # mlab_rig.data.edit_bones["pelvis"].head.copy()
            tmp_bone_list = ("pelvis.L", "pelvis.R")
            for bone_name in tmp_bone_list:
                pelvis_head = meta_rig.data.edit_bones[bone_name].head
                pelvis_tail = meta_rig.data.edit_bones[bone_name].tail
                new_pelvis_tail = (pelvis_tail - pelvis_head) + new_pelvis_head
                new_pelvis_roll = meta_rig.data.edit_bones[bone_name].roll            
                bone_data[bone_name] = (new_pelvis_head, new_pelvis_tail, new_pelvis_roll)
            
            # meta rig face rig
            relative_offset = meta_rig.data.edit_bones["face"].head.copy() - bone_data["spine.006"][0]            
            for bone in meta_rig.data.edit_bones["face"].parent.children_recursive:                
                bone_name = bone.name
                new_h = bone.head.copy() - relative_offset
                new_t = bone.tail.copy() - relative_offset
                new_r = meta_rig.data.edit_bones[bone_name].roll
                bone_data[bone_name] = (new_h, new_t, new_r)
                
            # go through all bones in meta rig, pass the ones not needed
            for b in meta_rig.data.edit_bones:
                try:
                    h, t, r = bone_data[b.name]
                    b.head = h
                    b.tail = t
                    b.roll = r # roll needed for rigify?
                except:
                    pass
            
            ########
            # end metarig edit mode
            bpy.ops.object.mode_set(mode='OBJECT')
            
        else:
            print("Error: '%s' is not an armature" % mlab_rig.name)
        return {'FINISHED'}

# add bone names from metarig_bone_names dict and add renamed to mlab_bone_names dict
def update_mlab_bone_names():
    for metarig_bone, mlab_bone in metarig_bone_names.items():
        mlab_bone_names[mlab_bone] = "DEF-" + metarig_bone

class RenameVertexGroupsFromMlabToRigify(bpy.types.Operator):
    """Rename Vertex Groups to match Rigify Meta-Rig
    - select the character mesh first"""
    bl_idname = "object.rename_vertex_groups_from_mlab_to_rigify_operator" # best name ever
    bl_label = "MLAB to Rigify"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        mlab_mesh = context.active_object
        if mlab_mesh.type == 'MESH':
            update_mlab_bone_names()
            # go through mlab_bone_names dictinary and try rename vertex groups
            for mlab_bone, metarig_bone in mlab_bone_names.items():
                try:
                    mlab_mesh.vertex_groups[mlab_bone].name = metarig_bone
                except:
                    print("Error: '%s' could not be found in vertex groups" % mlab_bone)
        else:
            print("Error: '%s' is not a mesh object" % mlab_mesh.name)
        return {'FINISHED'}

class RenameVertexGroupsFromRigifyToMlab(bpy.types.Operator):
    """Rename Vertex Groups to match MLAB rig
    - select the character mesh first"""
    bl_idname = "object.rename_vertex_groups_from_rigify_to_mlab_operator" # best name ever
    bl_label = "Rigify to MLAB"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        mlab_mesh = context.active_object
        if mlab_mesh.type == 'MESH':
            update_mlab_bone_names()
            # go through mlab_bone_names dictinary and try rename vertex groups
            for mlab_bone, metarig_bone in mlab_bone_names.items():
                try:
                    mlab_mesh.vertex_groups[metarig_bone].name = mlab_bone
                except:
                    print("Error: '%s' could not be found in vertex groups" % metarig_bone)
        else:
            print("Error: '%s' is not a mesh object" % mlab_mesh.name)
        return {'FINISHED'}

class DeleteFaceRig(bpy.types.Operator):
    """Delete Face Rig from Rigify Meta-Rig
    - select the character mesh first"""
    bl_idname = "object.delete_face_rig_operator" # best name ever
    bl_label = "Delete Face Rig"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        meta_rig = context.active_object
        if meta_rig.type == 'ARMATURE':
            bone_name = "face"
            if bone_name in meta_rig.data.bones:
                bpy.ops.object.mode_set(mode='EDIT')
                for b in meta_rig.data.edit_bones:
                    b.select = False                
                for b in meta_rig.data.edit_bones[bone_name].parent.children_recursive:
                    b.select = True
                bpy.ops.armature.delete()
                bpy.ops.object.mode_set(mode='OBJECT')
            else:
                print("Error: '%s' not found in armature" % bone_name)
        return {'FINISHED'}

class MetarigForMLABPanel(bpy.types.Panel):
    bl_label = 'Rigify Meta-Rig for MLAB'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context = 'objectmode'
    bl_category = 'ManuelBastioniLAB'
    
    def draw(self, context):
        layout = self.layout
        layout.operator(MetarigForMLAB.bl_idname)
        layout.operator(DeleteFaceRig.bl_idname)
        layout.label(text="Rename Vertex Groups:")
        layout.operator(RenameVertexGroupsFromMlabToRigify.bl_idname)
        layout.operator(RenameVertexGroupsFromRigifyToMlab.bl_idname)

def register():
    bpy.utils.register_class(MetarigForMLAB)
    bpy.utils.register_class(DeleteFaceRig)
    bpy.utils.register_class(RenameVertexGroupsFromMlabToRigify)
    bpy.utils.register_class(RenameVertexGroupsFromRigifyToMlab)
    bpy.utils.register_class(MetarigForMLABPanel)

def unregister():
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()
