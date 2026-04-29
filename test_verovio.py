import verovio
from pathlib import Path

tk = verovio.toolkit()
tk.loadFile(str(Path(__file__).parent / "idea-n10-gibran-alcocer-8bars.mxl"))
tk.setOptions({
    "pageWidth": 2100,
    "pageHeight": 2970,
    "scale": 40,
    "adjustPageHeight": True,
})
svg = tk.renderToSVG(1)
Path("score_test.svg").write_text(svg)
print(f"Pages: {tk.getPageCount()}, SVG size: {len(svg)} chars")