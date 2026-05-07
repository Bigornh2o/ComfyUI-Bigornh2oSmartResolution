# Bigornh2o Smart Resolution

A ComfyUI custom node that calculates width and height from a requested aspect ratio and megapixel count, but features an intelligent mathematical clamp to ensure the **long side** never exceeds a user-defined maximum safe value (default 2100 pixels).

This is extremely useful when dealing with very long or ultrawide aspect ratios (e.g., 21:9, 32:9, 9:16) which tend to produce enormous long sides when pushed to higher megapixel targets. Extremely large long-side dimensions can cause VAE encoding errors or artifacts near the end of standard Flux pipelines.

## Features

- **Standard Megapixel Sizing:** Select an aspect ratio and target megapixel. The node handles the exact resolution math while correctly orienting landscape vs portrait.
- **Smart Long Side Clamp:** If the calculated mathematical resolution has a long side exceeding `max_long_side` (e.g. > 2100 px), the node automatically scales the effective megapixels down so that the final image touches but does not exceed the safe long side, keeping the exact aspect ratio intact.
- **Divisible by enforcement:** Results are smoothly floored to the nearest multiple of `divisible_by` (default 8) to satisfy models / VAEs.
- **Extensive UI Feedback:** Provides text previews of what changed, including raw mathematical target resolution vs clamped resolution, clamped status, and final effective megapixels.

## Installation

Since this node is provided via local directory creation:

1. Copy the entire `Bigornh2oSmartResolution` folder to your ComfyUI custom nodes directory:
   `cp -r /path/to/Bigornh2oSmartResolution /workspace/ComfyUI/custom_nodes/`
2. Restart ComfyUI.

## The Math Behind the Smart Clamp

The logic is 100% mathematically consistent for any ratio, as opposed to hard-coding exceptions for specific dropdowns.

When `th_long_side > max_long_side`, we recalculate the allowed "Megapixel Capacity" for that ratio:
`mp_cap = (max_long_side ^ 2) / (ratio_long * 1_000_000)`

Then the node takes:
`effective_mp = min(requested_mp, mp_cap)`

### Examples of clamp at 2100 max long side (approximate):
- **4:5 at 3.3 MP:** No clamp. The calculated long side is safely under 2100.
- **16:9 at 3.3 MP:** Clamped automatically to ~2.48 MP (2100 x 1181)
- **19:9 at 3.3 MP:** Clamped automatically to ~2.08 MP (2100 x 994)
- **21:9 at 3.3 MP:** Clamped automatically to ~1.89 MP (2100 x 900)
- **32:9 at 3.3 MP:** Clamped automatically to ~1.24 MP (2100 x 590)

## Node Inputs

- **megapixel**: Target value from 0.1 to 3.5 (selectable via dropdown).
- **aspect_ratio**: Comprehensive dropdown of standard ratios with semantic names.
- **divisible_by**: Int. Ensure sides divide neatly. Defaults to 8.
- **max_long_side**: The "safe" long side limit. Defaults to 2112.
- **smart_cap_enable**: Toggle the clamping behavior.

## Node Outputs

- **width** (INT)
- **height** (INT)
- **resolution** (STRING): Format `W x H`
