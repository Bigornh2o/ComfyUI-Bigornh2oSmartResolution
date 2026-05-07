import math

class SmartFluxResolution:
    """
    Smart Flux Resolution Custom Node for ComfyUI.
    Calculates resolution based on requested megapixels and aspect ratio,
    with an automatic smart capping mechanism for the long side.
    """
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "megapixel": ([f"{i/10:.1f}" for i in range(1, 36)], {"default": "3.3"}),
                "aspect_ratio": ([
                    "1:1 (Perfect Square)",
                    "2:3 (Classic Portrait)",
                    "3:4 (Golden Ratio)",
                    "3:5 (Elegant Vertical)",
                    "4:5 (Artistic Frame)",
                    "5:7 (Balanced Portrait)",
                    "5:8 (Tall Portrait)",
                    "7:9 (Modern Portrait)",
                    "9:16 (Slim Vertical)",
                    "9:19 (Tall Slim)",
                    "9:21 (Ultra Tall)",
                    "9:32 (Skyline)",
                    "3:2 (Golden Landscape)",
                    "4:3 (Classic Landscape)",
                    "5:3 (Wide Horizon)",
                    "5:4 (Balanced Frame)",
                    "7:5 (Elegant Landscape)",
                    "8:5 (Cinematic View)",
                    "9:7 (Artful Horizon)",
                    "16:9 (Panorama)",
                    "19:9 (Cinematic Ultrawide)",
                    "21:9 (Epic Ultrawide)",
                    "32:9 (Extreme Ultrawide)"
                ], {"default": "1:1 (Perfect Square)"}),
                "divisible_by": ("INT", {"default": 8, "min": 1, "max": 64, "step": 1}),
                "max_long_side": ("INT", {"default": 2112, "min": 512, "max": 8192, "step": 16}),
                "smart_cap_enable": ("BOOLEAN", {"default": True}),
            }
        }

    RETURN_TYPES = ("INT", "INT", "STRING")
    RETURN_NAMES = ("width", "height", "resolution")
    FUNCTION = "calculate"
    CATEGORY = "Bigornh2o/Resolution"

    def calculate(self, megapixel, aspect_ratio, divisible_by, max_long_side, smart_cap_enable):
        megapixel_float = float(megapixel)
        # 1. Parse ratio
        try:
            ratio_str = aspect_ratio.split(' ')[0]
            w_str, h_str = ratio_str.split(':')
            w_ratio = float(w_str)
            h_ratio = float(h_str)
        except Exception as e:
            raise ValueError(f"Invalid aspect ratio format. Expected 'W:H' (e.g. '16:9'). Received: '{aspect_ratio}'")

        if w_ratio <= 0 or h_ratio <= 0:
            raise ValueError("Aspect ratio components must be strictly positive.")

        # 2. Calculate real ratio
        ratio_long = max(w_ratio, h_ratio) / min(w_ratio, h_ratio)
        is_landscape = w_ratio >= h_ratio

        # 3. Target surface in pixels
        target_surface = megapixel_float * 1_000_000

        # Calculate theoretical dimensions
        if is_landscape:
            th_width = math.sqrt(target_surface * (w_ratio / h_ratio))
            th_height = math.sqrt(target_surface / (w_ratio / h_ratio))
        else:
            th_width = math.sqrt(target_surface / (h_ratio / w_ratio))
            th_height = math.sqrt(target_surface * (h_ratio / w_ratio))
            
        th_long_side = max(th_width, th_height)
        
        was_clamped = False
        effective_mp = megapixel_float

        # 5. Check if we need to clamp
        # mp_cap = (max_long_side^2) / (ratio_long * 1_000_000)
        if smart_cap_enable and th_long_side > max_long_side:
            mp_cap = (max_long_side ** 2) / (ratio_long * 1_000_000)
            effective_mp = min(megapixel_float, mp_cap)
            was_clamped = True

        # 6. Recalculate with effective_mp
        eff_surface = effective_mp * 1_000_000
        if is_landscape:
            raw_width = math.sqrt(eff_surface * (w_ratio / h_ratio))
            raw_height = math.sqrt(eff_surface / (w_ratio / h_ratio))
        else:
            raw_width = math.sqrt(eff_surface / (h_ratio / w_ratio))
            raw_height = math.sqrt(eff_surface * (h_ratio / w_ratio))

        # 8. Apply divisible_by (floor)
        final_width = int(math.floor(raw_width / divisible_by) * divisible_by)
        final_height = int(math.floor(raw_height / divisible_by) * divisible_by)

        # 10. Recalculate effective_megapixel real
        final_mp = (final_width * final_height) / 1_000_000

        resolution_str = f"{final_width} x {final_height}"

        return (final_width, final_height, resolution_str)
