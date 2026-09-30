"""Matplotlib style for figures in the RevTeX manuscript.

Load it once, at the top of the document::

    import revtexplot as rp
    rp.setup()

``setup()`` reads two flags from ``_quarto.yml``:

``plot-style``
    ``true`` applies the style below; ``false`` leaves matplotlib untouched.
``stix``
    ``true`` sets text and math in STIX Two (from ``_fonts/``), matching the
    manuscript; ``false`` uses Computer Modern, matching the default LaTeX fonts.

The style uses 8 pt text (``\\footnotesize`` in a 10 pt RevTeX document) and
makes one-column figures the default size. Figures are saved at exactly the
requested size, so they appear in the PDF at their natural size and the text
in them matches the manuscript. For a figure spanning both columns, use
``plt.subplots(figsize=rp.WIDE)`` together with the chunk options
``fig-env: "figure*"`` and ``fig-pos: "t"``.
"""

import functools
import logging
from pathlib import Path
import re

import matplotlib as mpl
from matplotlib import font_manager
from matplotlib.figure import Figure

__all__ = [
    "COLUMN_WIDTH", "TEXT_WIDTH", "FOOTNOTESIZE",
    "COLUMN", "WIDE", "figsize", "setup",
]

PROJECT_DIR = Path(__file__).resolve().parent.parent
FONT_DIR = PROJECT_DIR / "_fonts"

# RevTeX 4.2, `aps,reprint`: \columnwidth = 246pt, \textwidth = 510pt.
COLUMN_WIDTH = 246 / 72.27   # inches
TEXT_WIDTH = 510 / 72.27     # inches
FOOTNOTESIZE = 8             # points

GOLDEN = (5 ** 0.5 - 1) / 2


def figsize(width="column", aspect=None):
    """Return a (width, height) tuple in inches.

    `width` is ``"column"``, ``"wide"`` (full text width) or a number of
    inches. `aspect` is height / width; it defaults to the golden ratio for
    column-wide figures and to 1/3 for wide ones.
    """
    if width == "column":
        width, default_aspect = COLUMN_WIDTH, GOLDEN
    elif width == "wide":
        width, default_aspect = TEXT_WIDTH, 1 / 3
    else:
        default_aspect = GOLDEN
    return (width, width * (default_aspect if aspect is None else aspect))


COLUMN = figsize("column")   # one column, 3.40 x 2.10 in
WIDE = figsize("wide")       # both columns, 7.06 x 2.35 in


def _read_flag(name, default):
    """Read a top-level boolean from _quarto.yml."""
    config = PROJECT_DIR / "_quarto.yml"
    if not config.exists():
        return default
    text = config.read_text()
    try:
        import yaml
        value = (yaml.safe_load(text) or {}).get(name, default)
    except ImportError:
        match = re.search(rf"^{re.escape(name)}:\s*(\w+)", text, re.MULTILINE)
        value = match.group(1).lower() == "true" if match else default
    return bool(value)


def _stix_fonts():
    for style in ("Regular", "Italic", "Bold", "BoldItalic"):
        font_manager.fontManager.addfont(str(FONT_DIR / f"STIXTwoText-{style}.ttf"))
    return {
        "font.family": "serif",
        "font.serif": ["STIX Two Text"],
        # mathtext cannot use STIX Two Math, so letters and digits come from
        # STIX Two Text and other symbols from matplotlib's bundled STIX fonts.
        "mathtext.fontset": "custom",
        "mathtext.rm": "STIX Two Text",
        "mathtext.it": "STIX Two Text:italic",
        "mathtext.bf": "STIX Two Text:bold",
        "mathtext.sf": "STIX Two Text",
        "mathtext.fallback": "stix",
    }


def _cm_fonts():
    # fontTools warns about the timestamps in matplotlib's bundled cm fonts
    # each time it embeds them.
    logging.getLogger("fontTools").setLevel(logging.ERROR)
    return {
        "font.family": "serif",
        "font.serif": ["cmr10"],
        "mathtext.fontset": "cm",
        "axes.unicode_minus": False,   # cmr10 has no Unicode minus sign
    }


def _set_inline_bbox(bbox):
    """Set how the notebook's inline backend crops figures when saving.

    Only the `bbox_inches` argument of the figure formatters that Quarto set up
    is changed; reconfiguring the InlineBackend instead would reset the output
    format (e.g. PDF for the PDF output) to PNG.
    """
    try:
        from IPython import get_ipython
    except ImportError:
        return
    ip = get_ipython()
    if ip is None:
        return
    for formatter in ip.display_formatter.formatters.values():
        printer = formatter.type_printers.get(Figure)
        if isinstance(printer, functools.partial) and "bbox_inches" in printer.keywords:
            keywords = {**printer.keywords, "bbox_inches": bbox}
            formatter.for_type(Figure, functools.partial(printer.func, *printer.args, **keywords))


def _reset():
    """Restore matplotlib's defaults, keeping the size and resolution set by
    Quarto. Quarto reuses the Jupyter kernel between renders, so this stops a
    previous render's style from carrying over."""
    keep = {k: mpl.rcParams[k] for k in ("figure.figsize", "figure.dpi", "savefig.dpi")}
    mpl.rcdefaults()
    mpl.rcParams.update(keep)
    _set_inline_bbox("tight")


def setup(enabled=None, stix=None):
    """Apply the manuscript plot style.

    `enabled` and `stix` override the ``plot-style`` and ``stix`` flags in
    _quarto.yml. Returns True if the style was applied.
    """
    if enabled is None:
        enabled = _read_flag("plot-style", True)
    if stix is None:
        stix = _read_flag("stix", False)
    _reset()
    if not enabled:
        return False

    mpl.rcParams.update(_stix_fonts() if stix else _cm_fonts())
    mpl.rcParams.update({
        # Size
        "figure.figsize": COLUMN,
        "figure.constrained_layout.use": True,
        "figure.constrained_layout.h_pad": 0.02,
        "figure.constrained_layout.w_pad": 0.02,
        "savefig.bbox": None,
        # Text: \footnotesize throughout
        "font.size": FOOTNOTESIZE,
        "axes.titlesize": FOOTNOTESIZE,
        "axes.labelsize": FOOTNOTESIZE,
        "xtick.labelsize": FOOTNOTESIZE,
        "ytick.labelsize": FOOTNOTESIZE,
        "legend.fontsize": FOOTNOTESIZE,
        "legend.title_fontsize": FOOTNOTESIZE,
        "figure.titlesize": FOOTNOTESIZE,
        "axes.formatter.use_mathtext": True,
        # Lines and axes
        "lines.linewidth": 1.0,
        "lines.markersize": 3,
        "axes.linewidth": 0.6,
        "grid.linewidth": 0.4,
        "xtick.direction": "in",
        "ytick.direction": "in",
        "xtick.top": True,
        "ytick.right": True,
        "xtick.major.size": 3,
        "ytick.major.size": 3,
        "xtick.minor.size": 1.5,
        "ytick.minor.size": 1.5,
        "xtick.major.width": 0.6,
        "ytick.major.width": 0.6,
        "xtick.minor.width": 0.4,
        "ytick.minor.width": 0.4,
        "legend.frameon": False,
        # Embed fonts as TrueType rather than Type 3
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    })

    # The inline backend crops figures to their content by default, which
    # would change their size; keep the exact figure size instead.
    _set_inline_bbox(None)
    return True
