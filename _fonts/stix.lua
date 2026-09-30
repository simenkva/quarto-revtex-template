-- STIX Two fonts for text and math in HTML and PDF output.
-- Enabled by `stix: true` in _quarto.yml; with `stix: false` this filter does nothing.
--
-- PDF:  adds stix.tex to the preamble (needs pdf-engine: lualatex or xelatex).
-- HTML: attaches the STIX Two web fonts and stix.css for the text, and tells
--       MathJax 4 (html-math-method in _quarto.yml) to use its STIX Two font.

local MATHJAX_CONFIG = [[
<script>
  window.MathJax = {
    output: { font: 'mathjax-stix2' },
    chtml: { matchFontHeight: false }
  };
</script>
]]

function Pandoc(doc)
  if doc.meta.stix ~= true then
    return nil
  end

  if quarto.doc.is_format("latex") then
    quarto.doc.include_file("in-header", quarto.utils.resolve_path("stix.tex"))
  elseif quarto.doc.is_format("html") then
    quarto.doc.include_text("in-header", MATHJAX_CONFIG)
    quarto.doc.add_html_dependency({
      name = "stix-fonts",
      version = "2.13",
      stylesheets = { "stix.css" },
      resources = {
        "STIXTwoText-Regular.woff2",
        "STIXTwoText-Italic.woff2",
        "STIXTwoText-Bold.woff2",
        "STIXTwoText-BoldItalic.woff2",
      },
    })
  end
end
