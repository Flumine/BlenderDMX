import bpy
import bmesh
from bpy.props import IntProperty
from bpy.app.handlers import persistent
    
class NODE_PT_MAINPANEL(bpy.types.Panel):
    bl_label = "Custom Node Group"
    bl_idname = "NODE_PT_MAINPANEL"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'New Tab' 
 
    def draw(self, context):
        
        scn = context.scene
        layout = self.layout
 
        row = layout.row()
        row.prop(context.scene, "my_int_prop")
        row.prop(context.scene, "start_channel")
        row.operator('node.test_operator')
        
 
 
def create_test_group(context, operator, group_name, interger, startChannel):
    print(interger)
    print(startChannel)

    test_group = bpy.data.node_groups.new(group_name, 'GeometryNodeTree')
    
    group_in = test_group.nodes.new('NodeGroupInput')
    group_in.location = (-400,0)
     
    
    group_out = test_group.nodes.new('NodeGroupOutput')
    group_out.location = (200* (interger + 2),0)
    test_group.outputs.new('NodeSocketGeometry','Output')
    
    link = test_group.links.new

    join_node = test_group.nodes.new(type= 'GeometryNodeJoinGeometry')
    join_node.location = (200 * (interger + 1),0) 
    
    i = 0
    for i in range(interger):
        print(i)
        
        vec_node = test_group.nodes.new(type= 'ShaderNodeCombineXYZ')
        vec_node.location = (200 * i,200)
        vec_node.inputs[2].default_value = i + startChannel
        line_node = test_group.nodes.new(type= 'GeometryNodeMeshLine')
        line_node.location = (200 * i,0)
        line_node.inputs[0].default_value = 1
        link(vec_node.outputs[0], line_node.inputs[2])
        test_group.inputs.new('NodeSocketInt','Channel ' + str(i + startChannel))
        test_group.inputs[i].max_value = 255;
        test_group.inputs[i].min_value = 0;
        link(group_in.outputs[i], vec_node.inputs[0])
        link(line_node.outputs[0],join_node.inputs[0])
        i += 1
    
    link(join_node.outputs[0], group_out.inputs[0])
    
    return test_group

class NODE_OT_TEST(bpy.types.Operator):
    bl_label = "Add Custom Node Group"
    bl_idname = "node.test_operator"
        
    def execute(self, context):
        
        startChannel = context.scene.start_channel 
        interger = context.scene.my_int_prop 
        custom_node_name = "hallo"
       
        my_group = create_test_group(self, context, custom_node_name, interger, startChannel)
        test_node = bpy.data.node_groups['Geometry Nodes'].nodes.new('GeometryNodeGroup')
        test_node.node_tree = bpy.data.node_groups[my_group.name]
        
        
        return {'FINISHED'}

# Locaton Checker
@persistent
def mainChange(scene):
    depsgraphTool = bpy.context.evaluated_depsgraph_get()

    obj = bpy.data.objects['Plane']

    bm = bmesh.new()

    bm.from_object( obj, depsgraphTool )

    bm.verts.ensure_lookup_table()
    print(bm.verts[0].co.x)
    print( "----" )
    for v in bm.verts:
        print("Level:", end =" ")
        print(int( v.co.x ), end =" ")
        print("channel:", end =" ")
        print(int(v.co.z))
    bm.free()           

bpy.app.handlers.frame_change_post.append(mainChange)
    
def register():
    
    bpy.app.handlers.depsgraph_update_post.append(mainChange)
    bpy.utils.register_class(NODE_PT_MAINPANEL)
    bpy.utils.register_class(NODE_OT_TEST)

    bpy.types.Scene.my_int_prop = bpy.props.IntProperty \
      (
        name = "Channel Amount",
        description = "My description",
        min = 1,
        max = 512,
        default = 0
      )
    bpy.types.Scene.start_channel = bpy.props.IntProperty \
      (
        name = "Start Amount",
        description = "My description",
        min = 1,
        max = 512,
        default = 0
      )
 
def unregister():
    bpy.utils.unregister_class(NODE_PT_MAINPANEL)
    bpy.utils.unregister_class(NODE_OT_TEST)
    del bpy.types.Scene.my_int_prop
    del bpy.types.Scene.start_channel

if __name__ == "__main__":
    register()
