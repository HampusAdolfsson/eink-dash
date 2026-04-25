use super::types::{Image, Palette, RgbColor};

// Diffusion kernels, as (x offset, y offset, weight)

/// Floyd-Steinberg dithering kernel.
const FLOYD_STEINBERG: [(i32, i32, f32); 4] = [
    (1, 0, 7.0 / 16.0),
    (-1, 1, 3.0 / 16.0),
    (0, 1, 5.0 / 16.0),
    (1, 1, 1.0 / 16.0),
];

/// Jarvis, Judice, and Ninke dithering kernel.
const JJN: [(i32, i32, f32); 12] = [
    (1, 0, 7.0 / 48.0),
    (2, 0, 5.0 / 48.0),
    (-2, 1, 3.0 / 48.0),
    (-1, 1, 5.0 / 48.0),
    (0, 1, 7.0 / 48.0),
    (1, 1, 5.0 / 48.0),
    (2, 1, 3.0 / 48.0),
    (-2, 2, 1.0 / 48.0),
    (-1, 2, 3.0 / 48.0),
    (0, 2, 5.0 / 48.0),
    (1, 2, 3.0 / 48.0),
    (2, 2, 1.0 / 48.0),
];

pub fn dither(mut input: Image, palette: &Palette) -> Image {
    let mut output = Image::filled(input.width(), input.height(), RgbColor(0.0, 0.0, 0.0));
    for y in 0..input.height() {
        for x in 0..input.width() {
            let original = input.pixel(x, y).unwrap();
            let quantized = quantize_color(original, palette);
            *output.pixel_mut(x, y).unwrap() = quantized;
            let error = *original - quantized;
            for (dx, dy, weight) in FLOYD_STEINBERG.iter() {
                let x2 = x as i32 + dx;
                let y2 = y as i32 + dy;
                if (x2 < 0) || y2 < 0 {
                    continue;
                }
                if let Some(pixel) = input.pixel_mut(x2 as u32, y2 as u32) {
                    *pixel = *pixel + error * *weight;
                }
            }
        }
    }
    output
}

/// Quantize a color to the nearest color in the palette.
fn quantize_color(color: &RgbColor, palette: &Palette) -> RgbColor {
    assert!(!palette.0.is_empty(), "palette must not be empty");
    let diffs = palette.0.iter().map(|c| {
        let diff = *color - *c;
        diff.0 * diff.0 + diff.1 * diff.1 + diff.2 * diff.2
    });
    diffs
        .enumerate()
        .min_by(|(_, a), (_, b)| a.partial_cmp(b).unwrap())
        .map(|(idx, _)| palette.0[idx])
        .unwrap()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_quantize_color() {
        let palette = Palette(vec![RgbColor(0.0, 0.0, 0.0), RgbColor(1.0, 1.0, 1.0)]);
        {
            let quantized = quantize_color(&RgbColor(0.1, 0.1, 0.1), &palette);
            assert_eq!(quantized, RgbColor(0.0, 0.0, 0.0));
        }
        {
            let quantized = quantize_color(&RgbColor(0.9, 0.9, 0.9), &palette);
            assert_eq!(quantized, RgbColor(1.0, 1.0, 1.0));
        }
    }
}
