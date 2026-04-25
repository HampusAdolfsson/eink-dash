mod algorithm;
mod types;
pub use types::{Palette, RgbColor};

use color_eyre::eyre::Result;
use std::path::Path;

pub fn dither(input: impl AsRef<Path>, output: impl AsRef<Path>, palette: Palette) -> Result<()> {
    let input_img = image::open(input)?.to_rgb8();
    let result = {
        let width = input_img.width();
        let pixels = input_img
            .pixels()
            .into_iter()
            .map(image_rgb8_to_rgb_color)
            .collect();
        let input_image = types::Image::new(width, pixels)?;
        algorithm::dither(input_image, &palette)
    };
    let output_pixels: Vec<u8> = result.as_raw().iter().flat_map(rgb_color_to_u8s).collect();
    let output_img = image::RgbImage::from_vec(result.width(), result.height(), output_pixels)
        .ok_or_else(|| color_eyre::eyre::eyre!("failed to create output image"))?;
    output_img.save(output)?;
    Ok(())
}

fn rgb_color_to_u8s(color: &RgbColor) -> [u8; 3] {
    [
        (color.0 * 255.0) as u8,
        (color.1 * 255.0) as u8,
        (color.2 * 255.0) as u8,
    ]
}

fn image_rgb8_to_rgb_color(color: &image::Rgb<u8>) -> RgbColor {
    RgbColor(
        color[0] as f32 / 255.0,
        color[1] as f32 / 255.0,
        color[2] as f32 / 255.0,
    )
}
