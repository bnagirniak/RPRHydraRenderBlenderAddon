import os


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

DEBUG_MODE = bool(int(os.environ.get('HYDRARPR_BLENDER_DEBUG', 0)))
LIBS_DIR = PLUGIN_ROOT_DIR.parent.parent / f'libs-{PYTHON_VERSION}' if DEBUG_MODE else \
                 PLUGIN_ROOT_DIR / f'libs-{PYTHON_VERSION}'


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

