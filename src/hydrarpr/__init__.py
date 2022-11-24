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


from . import engine, properties, ui


def register():
    engine.register()
    properties.register()
    ui.register()


def unregister():
    ui.unregister()
    properties.unregister()
    engine.unregister()
