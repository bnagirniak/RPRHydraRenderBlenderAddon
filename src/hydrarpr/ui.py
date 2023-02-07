# **********************************************************************
# Copyright 2022 Advanced Micro Devices, Inc
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ********************************************************************
import bpy

from .engine import RPRHydraRenderEngine


class Panel(bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'render'
    COMPAT_ENGINES = {RPRHydraRenderEngine.bl_idname}

    @classmethod
    def poll(cls, context):
        return context.engine in cls.COMPAT_ENGINES


class RPR_HYDRA_RENDER_PT_final(Panel):
    bl_idname = 'RPR_HYDRA_RENDER_PT_final'
    bl_label = "RPR Final Settings"

    def draw(self, context):
        settings = context.scene.hydra_rpr.final

        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        col = layout.column()
        col.prop(settings, "render_quality")
        col.prop(settings, "render_mode")


class FinalPanel(bpy.types.Panel):
    bl_parent_id = RPR_HYDRA_RENDER_PT_final.bl_idname
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_options = {'DEFAULT_CLOSED'}

    def settings(self, context):
        return context.scene.hydra_rpr.final


class RPR_HYDRA_RENDER_PT_samples_final(FinalPanel):
    bl_label = "Samples"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        settings = self.settings(context)
        layout.prop(settings, "max_samples")

        col = layout.column(align=True)
        col.prop(settings, "variance_threshold")
        row = col.row()
        row.enabled = settings.variance_threshold > 0.0
        row.prop(settings, "min_adaptive_samples")


class RPR_HYDRA_RENDER_PT_quality_final(FinalPanel):
    bl_label = "Quality"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        quality = self.settings(context).quality

        col = layout.column(align=True)
        col.prop(quality, "max_ray_depth")
        col.prop(quality, "max_ray_depth_diffuse")
        col.prop(quality, "max_ray_depth_glossy")
        col.prop(quality, "max_ray_depth_refraction")
        col.prop(quality, "max_ray_depth_glossy_refraction")

        layout.prop(quality, "raycast_epsilon")
        layout.prop(quality, "radiance_clamping")


class RPR_HYDRA_RENDER_PT_denoise_final(FinalPanel):
    bl_label = ""

    def draw_header(self, context):
        self.layout.prop(self.settings(context).denoise, "enable")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        denoise = self.settings(context).denoise

        layout.enabled = denoise.enable
        layout.prop(denoise, "min_iter")
        layout.prop(denoise, "iter_step")


class RPR_HYDRA_RENDER_PT_film_final(FinalPanel):
    bl_label = "Film"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.prop(self.settings(context), "enable_alpha", text="Transparent Background")


class RPR_HYDRA_RENDER_PT_pixel_filter_final(FinalPanel):
    bl_label = "Pixel Filter"

    @classmethod
    def poll(cls, context):
        return context.scene.hydra_rpr.viewport.render_quality == 'Northstar'

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.prop(self.settings(context).quality, "pixel_filter_width")

#
# VIEWPORT RENDER SETTINGS
#
class RPR_HYDRA_RENDER_PT_viewport(Panel):
    bl_idname = 'RPR_HYDRA_RENDER_PT_viewport'
    bl_label = "RPR Viewport Settings"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        settings = context.scene.hydra_rpr.viewport
        layout.prop(settings, "render_quality")
        layout.prop(settings, "render_mode")


class ViewportPanel(bpy.types.Panel):
    bl_parent_id = RPR_HYDRA_RENDER_PT_viewport.bl_idname
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_options = {'DEFAULT_CLOSED'}

    def settings(self, context):
        return context.scene.hydra_rpr.viewport


class RPR_HYDRA_RENDER_PT_samples_viewport(ViewportPanel):
    bl_label = "Samples"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        settings = self.settings(context)
        layout.prop(settings, "max_samples")

        col = layout.column(align=True)
        col.prop(settings, "variance_threshold")
        row = col.row()
        row.enabled = settings.variance_threshold > 0.0
        row.prop(settings, "min_adaptive_samples")


class RPR_HYDRA_RENDER_PT_quality_viewport(ViewportPanel):
    bl_label = "Quality"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        quality = self.settings(context).interactive_quality
        layout.prop(quality, "max_ray_depth")
        layout.prop(quality, "enable_downscale")
        layout.prop(quality, "resolution_downscale")


class RPR_HYDRA_RENDER_PT_denoise_viewport(ViewportPanel):
    bl_label = ""

    def draw_header(self, context):
        self.layout.prop(self.settings(context).denoise, "enable")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        denoise = self.settings(context).denoise
        layout.enabled = denoise.enable
        layout.prop(denoise, "min_iter")
        layout.prop(denoise, "iter_step")


class RPR_HYDRA_RENDER_PT_pixel_filter_viewport(ViewportPanel):
    bl_label = "Pixel Filter"

    @classmethod
    def poll(cls, context):
        return context.scene.hydra_rpr.viewport.render_quality == 'Northstar'

    def draw(self, context):
        self.layout.use_property_split = True
        self.layout.use_property_decorate = False

        col = self.layout.column()
        col.prop(self.settings(context).quality, "pixel_filter_width")


class RPR_HYDRA_LIGHT_PT_light(Panel):
    """
    Physical light sources
    """
    bl_label = "Light"
    bl_context = 'data'

    @classmethod
    def poll(cls, context):
        return super().poll(context) and context.light

    def draw(self, context):
        layout = self.layout

        light = context.light

        layout.prop(light, "type", expand=True)

        layout.use_property_split = True
        layout.use_property_decorate = False

        main_col = layout.column()

        main_col.prop(light, "color")
        main_col.prop(light, "energy")
        main_col.separator()

        if light.type == 'POINT':
            row = main_col.row(align=True)
            row.prop(light, "shadow_soft_size", text="Radius")

        elif light.type == 'SPOT':
            col = main_col.column(align=True)
            col.prop(light, 'spot_size', slider=True)
            col.prop(light, 'spot_blend', slider=True)

            main_col.prop(light, 'show_cone')

        elif light.type == 'SUN':
            main_col.prop(light, "angle")

        elif light.type == 'AREA':
            main_col.prop(light, "shape", text="Shape")
            sub = main_col.column(align=True)

            if light.shape in {'SQUARE', 'DISK'}:
                sub.prop(light, "size")
            elif light.shape in {'RECTANGLE', 'ELLIPSE'}:
                sub.prop(light, "size", text="Size X")
                sub.prop(light, "size_y", text="Y")

            else:
                main_col.prop(light, 'size')


register_classes, unregister_classes = bpy.utils.register_classes_factory((
    RPR_HYDRA_RENDER_PT_final,
    RPR_HYDRA_RENDER_PT_samples_final,
    RPR_HYDRA_RENDER_PT_quality_final,
    RPR_HYDRA_RENDER_PT_denoise_final,
    RPR_HYDRA_RENDER_PT_film_final,
    RPR_HYDRA_RENDER_PT_pixel_filter_final,

    RPR_HYDRA_RENDER_PT_viewport,
    RPR_HYDRA_RENDER_PT_samples_viewport,
    RPR_HYDRA_RENDER_PT_quality_viewport,
    RPR_HYDRA_RENDER_PT_denoise_viewport,
    RPR_HYDRA_RENDER_PT_pixel_filter_viewport,

    RPR_HYDRA_LIGHT_PT_light,
))


def get_panels():
    # follow the Cycles model of excluding panels we don't want
    exclude_panels = {
        'DATA_PT_area',
        'DATA_PT_falloff_curve',
        'DATA_PT_shadow',
        'DATA_PT_spot',
        'DATA_PT_sunsky',
        'DATA_PT_light',
        'MATERIAL_PT_diffuse',
        'MATERIAL_PT_flare',
        'MATERIAL_PT_halo',
        'MATERIAL_PT_mirror',
        'MATERIAL_PT_options',
        'MATERIAL_PT_pipeline',
        'MATERIAL_PT_shading',
        'MATERIAL_PT_shadow',
        'MATERIAL_PT_specular',
        'MATERIAL_PT_sss',
        'MATERIAL_PT_strand',
        'MATERIAL_PT_transp',
        'MATERIAL_PT_volume_density',
        'MATERIAL_PT_volume_integration',
        'MATERIAL_PT_volume_lighting',
        'MATERIAL_PT_volume_options',
        'MATERIAL_PT_volume_shading',
        'MATERIAL_PT_volume_transp',
        'RENDERLAYER_PT_layer_options',
        'RENDERLAYER_PT_layer_passes',
        'RENDERLAYER_PT_views',
        'RENDER_PT_antialiasing',
        'RENDER_PT_bake',
        'RENDER_PT_motion_blur',
        'RENDER_PT_performance',
        'RENDER_PT_freestyle',
        'RENDER_PT_post_processing',
        'RENDER_PT_shading',
        'RENDER_PT_simplify',
        'RENDER_PT_stamp',
        'SCENE_PT_simplify',
        'SCENE_PT_audio',
        'WORLD_PT_ambient_occlusion',
        'WORLD_PT_environment_lighting',
        'WORLD_PT_gather',
        'WORLD_PT_indirect_lighting',
        'WORLD_PT_mist',
        'WORLD_PT_preview',
        'WORLD_PT_world',
        'NODE_DATA_PT_light',
    }
    include_eevee_panels = {
        'MATERIAL_PT_preview',
        'EEVEE_MATERIAL_PT_context_material',
        'EEVEE_MATERIAL_PT_surface',
        'EEVEE_MATERIAL_PT_volume',
        'EEVEE_MATERIAL_PT_settings',
    }

    for panel_cls in bpy.types.Panel.__subclasses__():
        if hasattr(panel_cls, 'COMPAT_ENGINES') and (
                ('BLENDER_RENDER' in panel_cls.COMPAT_ENGINES and panel_cls.__name__ not in exclude_panels) or
                ('BLENDER_EEVEE' in panel_cls.COMPAT_ENGINES and panel_cls.__name__ in include_eevee_panels)
        ):
            yield panel_cls


def register():
    register_classes()

    for panel_cls in get_panels():
        panel_cls.COMPAT_ENGINES.add(RPRHydraRenderEngine.bl_idname)


def unregister():
    unregister_classes()

    for panel_cls in get_panels():
        if RPRHydraRenderEngine.bl_idname in panel_cls.COMPAT_ENGINES:
            panel_cls.COMPAT_ENGINES.remove(RPRHydraRenderEngine.bl_idname)
