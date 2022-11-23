from .engine import USDHydraHdRprEngine
from usdhydra.ui import USDHydra_Panel


class USDHYDRA_RENDER_PT_final(USDHydra_Panel):
    bl_label = "RPR Settings"
    bl_parent_id = 'USDHYDRA_RENDER_PT_render_settings_final'
    COMPAT_ENGINES = {USDHydraHdRprEngine.bl_idname}

    def draw(self, context):
        render_settings = context.scene.hdrpr.final

        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        col = layout.column()
        # col.prop(render_settings, "device")
        col.prop(render_settings, "render_quality")
        col.prop(render_settings, "render_mode")


class USDHYDRA_RENDER_PT_samples_final(USDHydra_Panel):
    bl_label = "Samples"
    bl_parent_id = 'USDHYDRA_RENDER_PT_render_settings_final'
    bl_options = {'DEFAULT_CLOSED'}
    COMPAT_ENGINES = {USDHydraHdRprEngine.bl_idname}

    def draw(self, context):
        render_settings = context.scene.hdrpr.final

        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.prop(render_settings, "max_samples")

        col = layout.column(align=True)
        col.prop(render_settings, "variance_threshold")
        row = col.row()
        row.enabled = render_settings.variance_threshold > 0.0
        row.prop(render_settings, "min_adaptive_samples")


class USDHYDRA_RENDER_PT_quality_final(USDHydra_Panel):
    bl_label = "Quality"
    bl_parent_id = 'USDHYDRA_RENDER_PT_render_settings_final'
    bl_space_type = 'PROPERTIES'
    bl_options = {'DEFAULT_CLOSED'}
    COMPAT_ENGINES = {USDHydraHdRprEngine.bl_idname}

    def draw(self, context):
        render_settings = context.scene.hdrpr.final
        quality = render_settings.quality

        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        col = layout.column(align=True)
        col.prop(quality, "max_ray_depth")
        col.prop(quality, "max_ray_depth_diffuse")
        col.prop(quality, "max_ray_depth_glossy")
        col.prop(quality, "max_ray_depth_refraction")
        col.prop(quality, "max_ray_depth_glossy_refraction")

        layout.prop(quality, "raycast_epsilon")
        layout.prop(quality, "radiance_clamping")


class USDHYDRA_RENDER_PT_denoise_final(USDHydra_Panel):
    bl_label = ""
    bl_parent_id = 'USDHYDRA_RENDER_PT_render_settings_final'
    bl_options = {'DEFAULT_CLOSED'}
    COMPAT_ENGINES = {USDHydraHdRprEngine.bl_idname}

    def draw_header(self, context):
        denoise = context.scene.hdrpr.final.denoise
        self.layout.prop(denoise, "enable")

    def draw(self, context):
        denoise = context.scene.hdrpr.final.denoise

        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.enabled = denoise.enable
        layout.prop(denoise, "min_iter")
        layout.prop(denoise, "iter_step")


class USDHYDRA_RENDER_PT_film_final(USDHydra_Panel):
    bl_label = "Film"
    bl_parent_id = 'USDHYDRA_RENDER_PT_render_settings_final'
    bl_options = {'DEFAULT_CLOSED'}
    COMPAT_ENGINES = {USDHydraHdRprEngine.bl_idname}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        render_settings = context.scene.hdrpr.final

        layout.prop(render_settings, "enable_alpha", text="Transparent Background")


class USDHYDRA_RENDER_PT_pixel_filter_final(USDHydra_Panel):
    bl_label = "Pixel Filter"
    bl_parent_id = 'USDHYDRA_RENDER_PT_render_settings_final'
    bl_space_type = 'PROPERTIES'
    bl_options = {'DEFAULT_CLOSED'}
    COMPAT_ENGINES = {USDHydraHdRprEngine.bl_idname}

    def draw(self, context):
        render_settings = context.scene.hdrpr.final
        quality = render_settings.quality

        self.layout.use_property_split = True
        self.layout.use_property_decorate = False

        col = self.layout.column()
        col.prop(quality, "pixel_filter_width")

#
# VIEWPORT RENDER SETTINGS
#
class USDHYDRA_RENDER_PT_viewport(USDHydra_Panel):
    bl_label = "RPR Settings"
    bl_parent_id = 'USDHYDRA_RENDER_PT_render_settings_viewport'
    COMPAT_ENGINES = {USDHydraHdRprEngine.bl_idname}

    def draw(self, context):
        render_settings = context.scene.hdrpr.viewport

        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        layout = layout.column()
        # layout.prop(render_settings, "device")
        layout.prop(render_settings, "render_quality")
        layout.prop(render_settings, "render_mode")


class USDHYDRA_RENDER_PT_samples_viewport(USDHydra_Panel):
    bl_label = "Samples"
    bl_parent_id = 'USDHYDRA_RENDER_PT_render_settings_viewport'
    bl_options = {'DEFAULT_CLOSED'}
    COMPAT_ENGINES = {USDHydraHdRprEngine.bl_idname}

    def draw(self, context):
        render_settings = context.scene.hdrpr.viewport

        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.prop(render_settings, "max_samples")

        col = layout.column(align=True)
        col.prop(render_settings, "variance_threshold")
        row = col.row()
        row.enabled = render_settings.variance_threshold > 0.0
        row.prop(render_settings, "min_adaptive_samples")


class USDHYDRA_RENDER_PT_quality_viewport(USDHydra_Panel):
    bl_label = "Quality"
    bl_parent_id = 'USDHYDRA_RENDER_PT_render_settings_viewport'
    bl_space_type = 'PROPERTIES'
    bl_options = {'DEFAULT_CLOSED'}
    COMPAT_ENGINES = {USDHydraHdRprEngine.bl_idname}

    def draw(self, context):
        render_settings = context.scene.hdrpr.viewport
        quality = render_settings.interactive_quality

        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.prop(quality, "max_ray_depth")
        # layout.prop(quality, "enable_downscale")
        # layout.prop(quality, "resolution_downscale")


class USDHYDRA_RENDER_PT_denoise_viewport(USDHydra_Panel):
    bl_label = ""
    bl_parent_id = 'USDHYDRA_RENDER_PT_render_settings_viewport'
    bl_options = {'DEFAULT_CLOSED'}
    COMPAT_ENGINES = {USDHydraHdRprEngine.bl_idname}

    def draw_header(self, context):
        denoise = context.scene.hdrpr.viewport.denoise
        self.layout.prop(denoise, "enable")

    def draw(self, context):
        denoise = context.scene.hdrpr.viewport.denoise

        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.enabled = denoise.enable
        layout.prop(denoise, "min_iter")
        layout.prop(denoise, "iter_step")


class USDHYDRA_RENDER_PT_pixel_filter_viewport(USDHydra_Panel):
    bl_label = "Pixel Filter"
    bl_parent_id = 'USDHYDRA_RENDER_PT_render_settings_viewport'
    bl_space_type = 'PROPERTIES'
    bl_options = {'DEFAULT_CLOSED'}
    COMPAT_ENGINES = {USDHydraHdRprEngine.bl_idname}

    @classmethod
    def poll(cls, context):
        return super().poll(context) and context.scene.hdrpr.viewport.render_quality == 'Northstar'

    def draw(self, context):
        render_settings = context.scene.hdrpr.viewport
        quality = render_settings.quality

        self.layout.use_property_split = True
        self.layout.use_property_decorate = False

        col = self.layout.column()
        col.prop(quality, "pixel_filter_width")
