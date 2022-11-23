import os
from pathlib import Path

import bpy

import _usdhydra
from usdhydra.engine import HydraRenderEngine


class RPRHydraRenderEngine(HydraRenderEngine):
    bl_idname = 'RPRHydraRenderEngine'
    bl_label = "Hydra: RPR"
    bl_info = "Hydra Radeon ProRender delegate"

    bl_use_preview = True

    delegate_id = "HdRprPlugin"

    @classmethod
    def register(cls):
        super().register(cls)

        # Temporary force enabling of Lighting Compiler until it'll be by default enabled on RPR side
        # Required for some cards
        os.environ['GPU_ENABLE_LC'] = "1"
        _usdhydra.register_plugin(Path(__file__))

    def get_delegate_settings(self, engine_type):
        if engine_type == 'VIEWPORT':
            settings = bpy.context.scene.hydra_rpr.viewport
            quality = settings.interactive_quality
        else:
            settings = bpy.context.scene.hydra_rpr.final
            quality = settings.quality

        denoise = settings.denoise

        result = {
            'rpr:alpha:enable': settings.enable_alpha,
            'rpr:core:renderQuality': settings.render_quality,
            'rpr:core:renderMode': settings.render_mode,
            'rpr:ambientOcclusion:radius': settings.ao_radius,
            'rpr:maxSamples': settings.max_samples,
            'rpr:adaptiveSampling:minSamples': settings.min_adaptive_samples,
            'rpr:adaptiveSampling:noiseTreshold': settings.variance_threshold,

            'rpr:denoising:enable': denoise.enable,
            'rpr:denoising:minIter': denoise.min_iter,
            'rpr:denoising:iterStep': denoise.iter_step,
        }

        if engine_type == 'VIEWPORT':
            result |= {
                'rpr:quality:rayDepth': quality.max_ray_depth,
                'rpr:quality:rayDepthDiffuse': quality.max_ray_depth_diffuse,
                'rpr:quality:rayDepthGlossy': quality.max_ray_depth_glossy,
                'rpr:quality:rayDepthRefraction': quality.max_ray_depth_refraction,
                'rpr:quality:rayDepthGlossyRefraction': quality.max_ray_depth_glossy_refraction,
                'rpr:quality:rayDepthShadow': quality.max_ray_depth_shadow,
                'rpr:quality:raycastEpsilon': quality.raycast_epsilon,
                'rpr:quality:radianceClamping': quality.radiance_clamping,
            }
        else:
            result |= {
                'rpr:quality:interactive:rayDepth': quality.max_ray_depth,
                'rpr:quality:interactive:downscale:enable': quality.enable_downscale,
                'rpr:quality:interactive:downscale:resolution': quality.resolution_downscale,
            }

        if settings.render_quality == 'Northstar':
            result['rpr:quality:imageFilterRadius'] = settings.quality.pixel_filter_width

        return result
