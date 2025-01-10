bl_info = {
    "name": "Video Import to Set Project Settings",
    "description": "Import a video to set the project’s resolution, frame range, and framerate",
    "author": "Claudio Rocha",
    "version": (1, 0),
    "blender": (2, 80, 0),  # Or higher if needed
    "location": "File > Import > Select Video File",
    "category": "Import-Export",
}

import bpy
from bpy_extras.io_utils import ImportHelper
import os

class VideoFileSelector(bpy.types.Operator, ImportHelper):
    """Operator to select a video file"""
    bl_idname = "import_video.video_file_selector"
    bl_label = "Select Video File"

    # Filter for video file types
    filter_glob: bpy.props.StringProperty(
        default="*.mp4;*.mov;*.avi;*.mkv;*.flv;*.wmv",
        options={'HIDDEN'}
    )

    def execute(self, context):
        # Get the file path
        filepath = self.filepath
        if not os.path.exists(filepath):
            self.report({'ERROR'}, "File not found.")
            return {'CANCELLED'}
        
        # Load video in movie clip editor
        bpy.ops.clip.open(directory=os.path.dirname(filepath), files=[{"name": os.path.basename(filepath)}])

        # Set project dimensions, frame rate, and number of frames based on video
        movie_clip = bpy.data.movieclips.load(filepath)
        if movie_clip:
            # Set project resolution
            context.scene.render.resolution_x = movie_clip.size[0]
            context.scene.render.resolution_y = movie_clip.size[1]
            
            # Set project frame range
            context.scene.frame_end = movie_clip.frame_duration

            # Get the correct fps from the MovieClip's fps attribute
            fps = movie_clip.fps

            # Match the fps to known standards
            if abs(fps - 23.976) < 0.01:
                context.scene.render.fps = 24
                context.scene.render.fps_base = 1.001
            elif abs(fps - 29.97) < 0.01:
                context.scene.render.fps = 30
                context.scene.render.fps_base = 1.001
            elif abs(fps - 59.94) < 0.01:
                context.scene.render.fps = 60
                context.scene.render.fps_base = 1.001
            else:
                # For other fps values, set fps directly and assume base is 1.0
                context.scene.render.fps = int(round(fps))
                context.scene.render.fps_base = 1.0

        return {'FINISHED'}

# Register the menu option
def menu_func_import(self, context):
    self.layout.operator(VideoFileSelector.bl_idname)

# Register and unregister functions for the addon
def register():
    bpy.utils.register_class(VideoFileSelector)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)

def unregister():
    bpy.utils.unregister_class(VideoFileSelector)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)

# This ensures the script runs as an addon when registered
if __name__ == "__main__":
    register()
