use std::path::PathBuf;

use clap::Parser;
use color_eyre::eyre::Result;
use dithers::RgbColor;

/// Convert an image to a limited color palette using dithering.
#[derive(Debug, Parser)]
#[command(version, about)]
struct Args {
    /// Path to the input image.
    input: PathBuf,

    /// Path to write the output image.
    output: PathBuf,

    /// Palette as one or more RGB hex colors (e.g. ff0080 or #ff0080).
    #[arg(required = true)]
    palette: Vec<RgbColor>,
}

fn main() -> Result<()> {
    color_eyre::install()?;

    let args = Args::parse();
    dithers::dither(args.input, args.output, dithers::Palette(args.palette))?;

    Ok(())
}
