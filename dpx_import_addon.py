bl_info = {
    "name": "DPX Import to Movie Clip Editor",
    "description": "Import a DPX sequence to set the project’s resolution, frame range, and framerate",
    "author": "Modified by Assistant",
    "version": (1, 1),
    "blender": (2, 80, 0),  # Or higher if needed
    "location": "File > Import > Select DPX Files",
    "category": "Import-Export",
}

import bpy
from bpy_extras.io_utils import ImportHelper
import os
import re
from pathlib import Path

class DPXFileSelector(bpy.types.Operator, ImportHelper):
    """Operator to select DPX files"""
    bl_idname = "import_dpx.dpx_file_selector"
    bl_label = "Select DPX Files"

    # Filter for DPX file types
    filter_glob: bpy.props.StringProperty(
        default="*.dpx",
        options={'HIDDEN'}
    )

    def execute(self, context):
        # Get the file path
        filepath = self.filepath
        directory = os.path.dirname(filepath)
        file_name = os.path.basename(filepath)

        if not os.path.exists(filepath):
            self.report({'ERROR'}, "File not found.")
            return {'CANCELLED'}

        # Extract frame number from file name using regex
        frame_match = re.search(r"(\d+)\.(?:dpx)$", file_name)
        frame_number = int(frame_match.group(1)) if frame_match else 1

        # Sort all DPX files in the directory to determine the first frame
        dpx_files = sorted(
            f for f in os.listdir(directory) if f.lower().endswith('.dpx')
        )

        if not dpx_files:
            self.report({'ERROR'}, "No DPX files found in the directory.")
            return {'CANCELLED'}

        first_frame_match = re.search(r"(\d+)\.(?:dpx)$", dpx_files[0])
        first_frame_number = int(first_frame_match.group(1)) if first_frame_match else 1

        # Load DPX sequence in movie clip editor
        bpy.ops.clip.open(directory=directory, files=[{"name": file_name}])

        # Get the movie clip reference
        movie_clip = bpy.data.movieclips.get(file_name)
        if movie_clip:
            # Set project resolution
            context.scene.render.resolution_x = movie_clip.size[0]
            context.scene.render.resolution_y = movie_clip.size[1]

            # Set the start frame for the movie clip itself
            movie_clip.frame_start = first_frame_number

            # Set the start frame based on the first DPX file's frame number
            context.scene.frame_start = first_frame_number

            # Calculate and set project frame range
            frame_count = len(dpx_files)
            context.scene.frame_end = first_frame_number + frame_count - 1

            # Set FPS to a default (can be adjusted later)
            context.scene.render.fps = 24
            context.scene.render.fps_base = 1.0

        return {'FINISHED'}

# Register the menu option
def menu_func_import(self, context):
    self.layout.operator(DPXFileSelector.bl_idname)

def register():
    bpy.utils.register_class(DPXFileSelector)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)

def unregister():
    bpy.utils.unregister_class(DPXFileSelector)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)

# This ensures the script runs as an addon when registered
if __name__ == "__main__":
    register()
