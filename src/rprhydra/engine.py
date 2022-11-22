from pathlib import Path

import bpy

from usdhydra.engine import USDHydraEngine
from usdhydra.utils import register_delegate, unregister_delegate


def register():
    register_delegate(Path(__file__).parent, USDHydraHdRprEngine.bl_idname)


def unregister():
    unregister_delegate(USDHydraHdRprEngine.bl_idname)


class USDHydraHdRprEngine(USDHydraEngine):
    bl_idname = 'HdRprBlenderDelegate'
    bl_label = "USD Hydra: Rpr"
    bl_info = "USD Hydra HdRpr rendering plugin"

    bl_use_preview = True
    bl_use_shading_nodes = True
    bl_use_shading_nodes_custom = False
    bl_use_gpu_context = True

    session = None

    delegate_name = "HdRprPlugin"

    def sync_final_delegate_settings(self):
        hdrpr = bpy.context.scene.hdrpr.final
        quality = hdrpr.quality
        denoise = hdrpr.denoise

        # settings = {
        #     'rpr:alpha:enable': hdrpr.enable_alpha,
        #     'rpr:core:renderQuality': hdrpr.render_quality,
        #     'rpr:core:renderMode': hdrpr.render_mode,
        #     'rpr:ambientOcclusion:radius': hdrpr.ao_radius,
        #     'rpr:maxSamples': hdrpr.max_samples,
        #     'rpr:adaptiveSampling:minSamples': hdrpr.min_adaptive_samples,
        #     'rpr:adaptiveSampling:noiseTreshold': hdrpr.variance_threshold,
        #     'rpr:quality:rayDepth': quality.max_ray_depth,
        #     'rpr:quality:rayDepthDiffuse': quality.max_ray_depth_diffuse,
        #     'rpr:quality:rayDepthGlossy': quality.max_ray_depth_glossy,
        #     'rpr:quality:rayDepthRefraction': quality.max_ray_depth_refraction,
        #     'rpr:quality:rayDepthGlossyRefraction': quality.max_ray_depth_glossy_refraction,
        #     'rpr:quality:rayDepthShadow': quality.max_ray_depth_shadow,
        #     'rpr:quality:raycastEpsilon': quality.raycast_epsilon,
        #     'rpr:quality:radianceClamping': quality.radiance_clamping,
        #     'rpr:denoising:enable': denoise.enable,
        #     'rpr:denoising:minIter': denoise.min_iter,
        #     'rpr:denoising:iterStep': denoise.iter_step,
        # }
        #
        # if hdrpr.render_quality == 'Northstar':
        #     settings['rpr:quality:imageFilterRadius'] = hdrpr.quality.pixel_filter_width

        settings = (
            ('rpr:alpha:enable', hdrpr.enable_alpha),
            ('rpr:core:renderQuality', hdrpr.render_quality),
            ('rpr:core:renderMode', hdrpr.render_mode),
            ('rpr:ambientOcclusion:radius', hdrpr.ao_radius),
            ('rpr:maxSamples', hdrpr.max_samples),
            ('rpr:adaptiveSampling:minSamples', hdrpr.min_adaptive_samples),
            ('rpr:adaptiveSampling:noiseTreshold', hdrpr.variance_threshold),
            ('rpr:quality:rayDepth', quality.max_ray_depth),
            ('rpr:quality:rayDepthDiffuse', quality.max_ray_depth_diffuse),
            ('rpr:quality:rayDepthGlossy', quality.max_ray_depth_glossy),
            ('rpr:quality:rayDepthRefraction', quality.max_ray_depth_refraction),
            ('rpr:quality:rayDepthGlossyRefraction', quality.max_ray_depth_glossy_refraction),
            ('rpr:quality:rayDepthShadow', quality.max_ray_depth_shadow),
            ('rpr:quality:raycastEpsilon', quality.raycast_epsilon),
            ('rpr:quality:radianceClamping', quality.radiance_clamping),
            ('rpr:denoising:enable', denoise.enable),
            ('rpr:denoising:minIter', denoise.min_iter),
            ('rpr:denoising:iterStep', denoise.iter_step),
        )

        if hdrpr.render_quality == 'Northstar':
            settings += (('rpr:quality:imageFilterRadius', hdrpr.quality.pixel_filter_width),)

        return settings

    def sync_viewport_delegate_settings(self):
        hdrpr = bpy.context.scene.hdrpr.viewport
        quality = hdrpr.interactive_quality
        denoise = hdrpr.denoise

        # settings = {
        #     'rpr:alpha:enable': False,
        #     'rpr:core:renderQuality': hdrpr.render_quality,
        #     'rpr:core:renderMode': hdrpr.render_mode,
        #     'rpr:ambientOcclusion:radius': hdrpr.ao_radius,
        #     'rpr:maxSamples': hdrpr.max_samples,
        #     'rpr:adaptiveSampling:minSamples': hdrpr.min_adaptive_samples,
        #     'rpr:adaptiveSampling:noiseTreshold': hdrpr.variance_threshold,
        #     'rpr:quality:interactive:rayDepth': quality.max_ray_depth,
        #     'rpr:quality:interactive:downscale:enable': quality.enable_downscale,
        #     'rpr:quality:interactive:downscale:resolution': quality.resolution_downscale,
        #     'rpr:denoising:enable': denoise.enable,
        #     'rpr:denoising:minIter': denoise.min_iter,
        #     'rpr:denoising:iterStep': denoise.iter_step,
        # }
        #
        # if hdrpr.render_quality == 'Northstar':
        #     settings['rpr:quality:imageFilterRadius'] = hdrpr.quality.pixel_filter_width

        settings = (
            ('rpr:alpha:enable', False),
            ('rpr:core:renderQuality', hdrpr.render_quality),
            ('rpr:core:renderMode', hdrpr.render_mode),
            ('rpr:ambientOcclusion:radius', hdrpr.ao_radius),
            ('rpr:maxSamples', hdrpr.max_samples),
            ('rpr:adaptiveSampling:minSamples', hdrpr.min_adaptive_samples),
            ('rpr:adaptiveSampling:noiseTreshold', hdrpr.variance_threshold),
            ('rpr:quality:interactive:rayDepth', quality.max_ray_depth),
            ('rpr:quality:interactive:downscale:enable', quality.enable_downscale),
            ('rpr:quality:interactive:downscale:resolution', quality.resolution_downscale),
            ('rpr:denoising:enable', denoise.enable),
            ('rpr:denoising:minIter', denoise.min_iter),
            ('rpr:denoising:iterStep', denoise.iter_step),
        )

        if hdrpr.render_quality == 'Northstar':
            settings += (('rpr:quality:imageFilterRadius', hdrpr.quality.pixel_filter_width),)

        return settings
