# Quarto RevTeX starter template

This repository contains a minimal [quarto](https://www.quarto,org) manuscript project that is set up to use RevTex 4.2 as LaTeX documentclass when rendering PDF.

## Fonts

By default the HTML and PDF output use the [STIX Two](https://github.com/stipub/stixfonts) fonts for text and math. The font files are in `_fonts/`, so nothing needs to be installed. The fonts are switched on by one line in `_quarto.yml`:

```yaml
stix: true   # false: default fonts
```

With `stix: true`, the filter `_fonts/stix.lua` does the following:

- PDF: adds `_fonts/stix.tex` (`fontspec` + `unicode-math`) to the preamble. The PDF is built with `lualatex` either way.
- HTML: adds `_fonts/stix.css` and the STIX Two Text web fonts, and sets MathJax to its built-in `mathjax-stix2` font. MathJax 4 is loaded from jsdelivr (`html-math-method` in `_quarto.yml`), and it also fetches the math font from there.

With `stix: false` you get the default fonts: Latin Modern in the PDF, and in HTML the Bootstrap font with MathJax 4's default New Computer Modern math font.

The STIX Two fonts are licensed under the SIL Open Font License; see `_fonts/OFL.txt`.

## Plots

The local Python package `revtexplot/` styles matplotlib figures to match the PDF: one-column default size, 8 pt text (`\footnotesize`) in STIX Two or Computer Modern (following `stix`), and fonts embedded as TrueType. It is loaded by the first chunk in `index.qmd` and switched on by

```yaml
plot-style: true   # false: matplotlib defaults
```

Use `figsize=rp.WIDE` for figures spanning both columns, and `rp.figsize(width, aspect)` for other sizes.

# License

This project is licensed under the [MIT License](LICENSE).

