# dithers

`dithers` is a command-line tool for converting images to a limited color palette using dithering.

## Usage

```bash
dithers <input> <output> <palette>...
```

- `<input>` — path to the input image
- `<output>` — path to write the output image
- `<palette>...` — one or more RGB hex colors (e.g. `ff0080` or `#ff0080`)

### Example

Given the input image:

![photo.png](./photo.png)

Run the following command:

```bash
dithers photo.png photo_output.png '000000' 'ffffff'
```

To produce the output image:

![photo_output.png](./photo_output.png)

## Building

```bash
cargo build --release
```