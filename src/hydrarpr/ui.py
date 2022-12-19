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


class HYDRA_RPR_RENDER_PT_final(Panel):
    bl_label = "RPR Final Settings"


    def draw(self, context):
        settings = context.scene.usdhydra_rpr.final

        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        col = layout.column()
        col.prop(settings, "render_quality")
        col.prop(settings, "render_mode")


class FinalPanel(bpy.types.Panel):
    # bl_parent_id = HYDRA_RPR_RENDER_PT_final.bl_idname
    bl_options = {'DEFAULT_CLOSED'}
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'render'

    def settings(self, context):
        return context.scene.usdhydra_rpr.final


class HYDRA_RPR_RENDER_PT_samples_final(FinalPanel):
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


class HYDRA_RPR_RENDER_PT_quality_final(FinalPanel):
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


class HYDRA_RPR_RENDER_PT_denoise_final(FinalPanel):
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


class HYDRA_RPR_RENDER_PT_film_final(FinalPanel):
    bl_label = "Film"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.prop(self.settings(context), "enable_alpha", text="Transparent Background")


class HYDRA_RPR_RENDER_PT_pixel_filter_final(FinalPanel):
    bl_label = "Pixel Filter"

    @classmethod
    def poll(cls, context):
        return context.scene.usdhydra_rpr.viewport.render_quality == 'Northstar'

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.prop(self.settings(context).quality, "pixel_filter_width")

#
# VIEWPORT RENDER SETTINGS
#
class HYDRA_RPR_RENDER_PT_viewport(Panel):
    bl_label = "RPR Viewport Settings"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        settings = context.scene.usdhydra_rpr.viewport
        layout.prop(settings, "render_quality")
        layout.prop(settings, "render_mode")


class ViewportPanel(bpy.types.Panel):
    # bl_parent_id = HYDRA_RPR_RENDER_PT_viewport.bl_idname
    bl_options = {'DEFAULT_CLOSED'}
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'render'

    def settings(self, context):
        return context.scene.usdhydra_rpr.viewport


class HYDRA_RPR_RENDER_PT_samples_viewport(ViewportPanel):
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


class HYDRA_RPR_RENDER_PT_quality_viewport(ViewportPanel):
    bl_label = "Quality"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        quality = self.settings(context).interactive_quality
        layout.prop(quality, "max_ray_depth")
        layout.prop(quality, "enable_downscale")
        layout.prop(quality, "resolution_downscale")


class HYDRA_RPR_RENDER_PT_denoise_viewport(ViewportPanel):
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


class HYDRA_RPR_RENDER_PT_pixel_filter_viewport(ViewportPanel):
    bl_label = "Pixel Filter"

    @classmethod
    def poll(cls, context):
        return context.scene.usdhydra_rpr.viewport.render_quality == 'Northstar'

    def draw(self, context):
        self.layout.use_property_split = True
        self.layout.use_property_decorate = False

        col = self.layout.column()
        col.prop(self.settings(context).quality, "pixel_filter_width")


register, unregister = bpy.utils.register_classes_factory((
    HYDRA_RPR_RENDER_PT_final,
    HYDRA_RPR_RENDER_PT_viewport,
    HYDRA_RPR_RENDER_PT_denoise_final,
    HYDRA_RPR_RENDER_PT_denoise_viewport,
    HYDRA_RPR_RENDER_PT_film_final,
    HYDRA_RPR_RENDER_PT_pixel_filter_final,
    HYDRA_RPR_RENDER_PT_pixel_filter_viewport,
    HYDRA_RPR_RENDER_PT_quality_final,
    HYDRA_RPR_RENDER_PT_quality_viewport,
    HYDRA_RPR_RENDER_PT_samples_final,
    HYDRA_RPR_RENDER_PT_samples_viewport,
))
