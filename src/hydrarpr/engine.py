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
from pathlib import Path

import bpy

import _usdhydra
from usdhydra.engine import HydraRenderEngine


LIBS_DIR = Path(__file__).parent / "libs"


class RPRHydraRenderEngine(HydraRenderEngine):
    bl_idname = 'RPRHydraRenderEngine'
    bl_label = "Hydra: RPR"
    bl_info = "Hydra Radeon ProRender delegate"

    bl_use_preview = True

    delegate_id = "HdRprPlugin"

    @classmethod
    def register(cls):
        super().register()

        _usdhydra.register_plugins([str(LIBS_DIR / "plugin")], [str(LIBS_DIR / "lib")])

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
                'rpr:quality:interactive:rayDepth': quality.max_ray_depth,
                'rpr:quality:interactive:downscale:enable': quality.enable_downscale,
                'rpr:quality:interactive:downscale:resolution': quality.resolution_downscale,
            }
        else:
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

        if settings.render_quality == 'Northstar':
            result['rpr:quality:imageFilterRadius'] = settings.quality.pixel_filter_width

        return result


register, unregister = bpy.utils.register_classes_factory((
    RPRHydraRenderEngine,
))
