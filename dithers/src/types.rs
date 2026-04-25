//! Types used by the dithering algorithms.

use std::ops::{Add, Mul, Sub};

use color_eyre::eyre::Result;

/// An RGB color.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct RgbColor(pub f32, pub f32, pub f32);

impl std::str::FromStr for RgbColor {
    type Err = color_eyre::eyre::Error;

    fn from_str(s: &str) -> Result<Self> {
        let s = s.trim_start_matches('#');
        if s.len() != 6 {
            return Err(color_eyre::eyre::eyre!(
                "expected a 6-digit hex color, got {:?}",
                s
            ));
        }
        let r = u8::from_str_radix(&s[0..2], 16)?;
        let g = u8::from_str_radix(&s[2..4], 16)?;
        let b = u8::from_str_radix(&s[4..6], 16)?;
        Ok(RgbColor(
            r as f32 / 255.0,
            g as f32 / 255.0,
            b as f32 / 255.0,
        ))
    }
}

impl Add for RgbColor {
    type Output = Self;

    fn add(self, rhs: Self) -> Self::Output {
        RgbColor(self.0 + rhs.0, self.1 + rhs.1, self.2 + rhs.2)
    }
}

impl Sub for RgbColor {
    type Output = Self;

    fn sub(self, rhs: Self) -> Self::Output {
        RgbColor(self.0 - rhs.0, self.1 - rhs.1, self.2 - rhs.2)
    }
}

impl Mul<f32> for RgbColor {
    type Output = Self;

    fn mul(self, rhs: f32) -> Self::Output {
        RgbColor(self.0 * rhs, self.1 * rhs, self.2 * rhs)
    }
}

/// A color palette, used as the target colors for dithering.
pub struct Palette(pub Vec<RgbColor>);

pub struct Image {
    width: u32,
    data: Vec<RgbColor>,
}

impl Image {
    pub fn new(width: u32, data: Vec<RgbColor>) -> Result<Self> {
        if (data.len() as u32) % width != 0 {
            return Err(color_eyre::eyre::eyre!(
                "data length must be a multiple of width"
            ));
        }
        Ok(Self { width, data })
    }

    pub fn filled(width: u32, height: u32, color: RgbColor) -> Self {
        Self {
            width,
            data: vec![color; (width * height) as usize],
        }
    }

    pub fn width(&self) -> u32 {
        self.width
    }

    pub fn height(&self) -> u32 {
        (self.data.len() as u32) / self.width
    }

    pub fn pixel(&self, x: u32, y: u32) -> Option<&RgbColor> {
        let idx = (y * self.width + x) as usize;
        self.data.get(idx)
    }

    pub fn pixel_mut(&mut self, x: u32, y: u32) -> Option<&mut RgbColor> {
        let idx = (y * self.width + x) as usize;
        self.data.get_mut(idx)
    }

    pub fn as_raw(&self) -> &Vec<RgbColor> {
        &self.data
    }
}
