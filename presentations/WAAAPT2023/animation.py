import pybind11 as pyb11
import numpy as np
import bpy


# remove all objects from the scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)


focal_length = 44.95


#add stl to the scene
bpy.ops.import_mesh.stl(filepath='../../stl/aluminum_G.stl')
bpy.context.object.location = (0, 0, -focal_length)
# create red metal material
bpy.ops.material.new()
bpy.data.materials['Material'].name = 'Red Metal'
bpy.data.materials['Red Metal'].diffuse_color = (0.8, 0.1, 0.1, 1)
bpy.data.materials['Red Metal'].specular_intensity = 0.5

# create a cube object and set its location to half the focal length
bpy.ops.mesh.primitive_cube_add(location=(0, 0, -focal_length/2))

# assign the material to the object
bpy.context.object.active_material = bpy.data.materials['Red Metal']

# create a camera object and set its location to the origin and rotation to look down the z-axis
bpy.ops.object.camera_add(location=(0, 0, 0), rotation=(-np.pi/2, 0, 0))
bpy.context.object.data.lens = focal_length
bpy.context.scene.camera = bpy.data.objects['Camera']

# create a light object and set its location to the origin and rotation to look down the z-axis
light_data = bpy.data.lights.new(name="light", type='POINT')
light_data.energy = 1000

light_object = bpy.data.objects.new(name="light", object_data=light_data)
bpy.context.collection.objects.link(light_object)
light_object.location = (0, 0, 0)


# view the scene in blender GUI
bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)




# render the scene to an image in the current directory
# bpy.context.scene.render.filepath = '../blender/aluminum_G.png'
# bpy.ops.render.render(write_still=True, use_viewport=True)






# # create a plane offset from the origin
# bpy.ops.mesh.primitive_plane_add(location=(0, 0, 1))
#
# # create a mesh from array of triangle vertices
# verts = [(0, 0, 0), (1, 0, 0), (0, 1, 0)]
# faces = [(0, 1, 2)]
# mesh = bpy.data.meshes.new("mesh")
# mesh.from_pydata(verts, [], faces)
# mesh.update()




