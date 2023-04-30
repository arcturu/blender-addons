"""
Awesome Picker
"""
from datetime import datetime
import re
import bpy
bl_info = {
    "name": "Awesome Picker",
    "blender": (3, 3, 0),
    "category": "3D View",
}


class ActivateObjectByNameOperator(bpy.types.Operator):
    """Activate object by name"""
    bl_idname = "awesome_picker.activate_by_name"
    bl_label = "Activate object by name"
    bl_options = {'UNDO'}

    name: bpy.props.StringProperty(name="name")

    def execute(self, context):
        obj = bpy.data.objects[self.name]
        bpy.ops.object.select_pattern(pattern=self.name, extend=False)
        bpy.context.view_layer.objects.active = obj
        return {'FINISHED'}


class ActivateBoneByNameOperator(bpy.types.Operator):
    """Activate bone by name"""
    bl_idname = "awesome_picker.activate_bone_by_name"
    bl_label = "Activate bone by name"
    bl_options = {'UNDO'}

    name: bpy.props.StringProperty(name="name")

    def execute(self, context):
        """Execute"""
        pose = context.object.pose
        self.unselect_all_bones(pose.bones)
        pose.bones[self.name].bone.select = True
        return {'FINISHED'}

    def unselect_all_bones(self, pose_bones):
        """Unselect all bones"""
        for pose_bone in pose_bones:
            pose_bone.bone.select = False


class ToggleIkInfluenceOperator(bpy.types.Operator):
    """Toggle influence parameter 0/1 of IK constraint"""
    bl_idname = "awesome_picker.toggle_ik_influence"
    bl_label = "Toggle IK Influence"
    bl_options = {'UNDO'}

    name: bpy.props.StringProperty(name="name")

    def execute(self, context):
        "Execute toggle ik influence"
        pose_bone = context.object.pose.bones[self.name]
        for c in pose_bone.constraints:
            if c.type != "IK":
                continue
            c.influence = 1.0 if c.influence < 0.5 else 0.0
        return {'FINISHED'}


class AwesomePickerSideBar(bpy.types.Panel):
    """Body of Awesome Picker side bar"""
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'  # sidebar
    bl_category = "Picker"
    bl_label = "Picker"

    def draw(self, context):
        """Draw side bar content"""
        layout = self.layout

        row = layout.row()
        row.label(text=str(datetime.now()))

        obj = context.object
        if context.mode != "POSE" or obj.type != "ARMATURE":
            return

        row = layout.row()
        row.label(text="Active:" + obj.name)

        pose = obj.pose

        row = layout.row()
        row.label(text="IK Pickers")
        self.show_pickers(layout, pose)

        row = layout.row()
        row.label(text="Toggle IK")

        split = layout.split()

        col = split.column()
        for bone in pose.bones:
            if not re.match(r'.*[_.]R$', bone.name):
                continue
            ikc = next((c for c in bone.constraints if c.type == "IK"), None)
            if ikc is None:
                continue
            split_inner = col.split(factor=0.1)
            col_inner = split_inner.column()
            col_inner.label(text=str(ikc.influence))
            col_inner = split_inner.column()
            col_inner.operator(operator="awesome_picker.toggle_ik_influence",
                               text=bone.name).name = bone.name

        col = split.column()
        for bone in pose.bones:
            if not re.match(r'.*[_.]L$', bone.name):
                continue
            ikc = next((c for c in bone.constraints if c.type == "IK"), None)
            if ikc is None:
                continue
            split_inner = col.split(factor=0.1)
            col_inner = split_inner.column()
            col_inner.label(text=str(ikc.influence))
            col_inner = split_inner.column()
            col_inner.operator(operator="awesome_picker.toggle_ik_influence",
                               text=bone.name).name = bone.name

    def show_pickers(self, layout, pose):
        iks = [b.name for b in pose.bones if re.match(
            r'^IK_.*[^RL]$', b.name)]
        iks = sorted(iks)
        ik_rights = [b.name for b in pose.bones if re.match(
            r'^IK_.*[_.]R', b.name)]
        ik_rights = sorted(ik_rights)
        ik_lefts = [b.name for b in pose.bones if re.match(
            r'^IK_.*[_.]L', b.name)]
        ik_lefts = sorted(ik_lefts)

        for ik in iks:
            row = layout.row()
            self.show_activate_button(row, ik)

        split = layout.split()
        col = split.column()
        for ik in ik_rights:
            self.show_activate_button(col, ik)
        col = split.column()
        for ik in ik_lefts:
            self.show_activate_button(col, ik)

    def show_activate_button(self, layout, name):
        """Show activate button"""
        layout.operator(operator="awesome_picker.activate_bone_by_name",
                        text=name).name = name


classes = [
    ActivateObjectByNameOperator,
    ActivateBoneByNameOperator,
    ToggleIkInfluenceOperator,
    AwesomePickerSideBar,
]


def register():
    """Register AwesomePickerSideBar to Blender"""
    for c in classes:
        bpy.utils.register_class(c)


def unregister():
    """Unregister AwesomePickerSideBar from Blender"""
    for c in reversed(classes):
        bpy.utils.unregister_class(c)
