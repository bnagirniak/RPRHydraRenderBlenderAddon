bl_info = {
    "name": "USD Hydra: RPR",
    "author": "AMD",
    "version": (1, 0, 0),
    "blender": (3, 5, 0),
    "location": "Info header > Render engine menu",
    "description": "USD Hydra RPR renderer",
    "tracker_url": "",
    "doc_url": "",
    "community": "",
    "downloads": "",
    "main_web": "",
    "support": 'TESTING',
    "category": "Render"
}

from bpy.utils import register_class, unregister_class, register_classes_factory
import addon_utils

from . import (
    engine,
    properties,
    ui,
)

register_ui, unregister_ui = register_classes_factory(
    [
        ui.USDHYDRA_RENDER_PT_final,
        ui.USDHYDRA_RENDER_PT_viewport,
        ui.USDHYDRA_RENDER_PT_denoise_final,
        ui.USDHYDRA_RENDER_PT_denoise_viewport,
        ui.USDHYDRA_RENDER_PT_film_final,
        ui.USDHYDRA_RENDER_PT_pixel_filter_final,
        ui.USDHYDRA_RENDER_PT_pixel_filter_viewport,
        ui.USDHYDRA_RENDER_PT_quality_final,
        ui.USDHYDRA_RENDER_PT_quality_viewport,
        ui.USDHYDRA_RENDER_PT_samples_final,
        ui.USDHYDRA_RENDER_PT_samples_viewport,
    ]
)

register_properties, unregister_properties = register_classes_factory(
    [
        properties.ContourSettings,
        properties.DenoiseSettings,
        properties.InteractiveQualitySettings,
        properties.QualitySettings,
        properties.RenderSettings,
        # properties.ViewportRenderSettings,
        # properties.FinalRenderSettings,
        properties.SceneProperties,
    ]
)


def register():
    enabled, loaded = addon_utils.check('usdhydra')
    if enabled and loaded:
        register_class(engine.USDHydraHdRprEngine)
        register_properties()
        register_ui()
        engine.register()

    else:
        addon_utils.disable(engine.USDHydraHdRprEngine.bl_idname)


def unregister():
    try:
        unregister_class(engine.USDHydraHdRprEngine)
        unregister_ui()
        unregister_properties()
        engine.unregister()
    except Exception as err:
        from usdhydra.utils import logging
        log = logging.Log("HdRprBlenderDelegate")
        log.warn("Delegate  Unregistering", err)

