"""Shared beat, measure and rendered-page model for the bundled excerpt."""
from dataclasses import dataclass
from pathlib import Path
import xml.etree.ElementTree as ET
from music21 import converter
import verovio

SCORE_FILE = Path(__file__).parent / 'idea-n10-gibran-alcocer-8bars.mxl'


def build_lookup(score_path):
    measures = converter.parse(str(score_path)).parts[0].getElementsByClass('Measure')
    lookup = [(float(m.offset), float(m.offset + m.duration.quarterLength), m.number)
              for m in measures]
    if not lookup:
        raise ValueError('Score has no measures')
    pickup = next((start for start, _, n in lookup if n == 1), 0.0)
    return lookup, pickup


def beat_to_measure(beat, lookup, pickup_offset):
    shifted = beat + pickup_offset
    for start, end, number in lookup:
        if start <= shifted < end:
            return number
    return lookup[-1][2] if shifted >= lookup[-1][1] else None


@dataclass
class ScoreModel:
    pages: list[str]
    measures: list[dict]
    boundaries: list[float]
    pickup: float


def render_score(score_path=SCORE_FILE):
    """Encode a two-page rehearsal layout, then discover its actual SVG IDs."""
    lookup, pickup = build_lookup(score_path)
    tk = verovio.toolkit()
    if not tk.loadFile(str(score_path)):
        raise ValueError('Cannot load score')
    ET.register_namespace('', 'http://www.music-encoding.org/ns/mei')
    root = ET.fromstring(tk.getMEI())
    ns = {'m': 'http://www.music-encoding.org/ns/mei'}
    tag = '{' + ns['m'] + '}'
    xml_id = '{http://www.w3.org/XML/1998/namespace}id'
    mei_measures = root.findall('.//m:measure', ns)
    if len(mei_measures) != len(lookup):
        raise ValueError('Rendered score and timing map disagree')
    # Four measures per page; two per system. Keep IDs assigned by Verovio.
    for parent in root.iter():
        for child in list(parent):
            if child.tag in (tag + 'pb', tag + 'sb'):
                parent.remove(child)
    for index, measure in enumerate(mei_measures):
        if index and index % 2 == 0:
            parent = next(p for p in root.iter() if measure in list(p))
            parent.insert(list(parent).index(measure), ET.Element(tag + ('pb' if index % 4 == 0 else 'sb')))
    tk.setOptions({'breaks': 'encoded', 'pageWidth': 2100, 'pageHeight': 2970,
                   'scale': 40, 'adjustPageHeight': True, 'svgViewBox': True})
    if not tk.loadData(ET.tostring(root, encoding='unicode')):
        raise ValueError('Cannot render rehearsal layout')
    pages = [tk.renderToSVG(i) for i in range(1, tk.getPageCount() + 1)]
    models = []
    for (start, end, number), measure in zip(lookup, mei_measures):
        mid = measure.get(xml_id)
        page = next((i for i, svg in enumerate(pages) if f'id="{mid}"' in svg), None)
        if page is None:
            raise ValueError(f'Measure {number} missing from rendered pages')
        models.append(dict(number=number, start=start-pickup, end=end-pickup, id=mid, page=page))
    boundaries = [max(m['end'] for m in models if m['page'] == i)
                  for i in range(len(pages)-1)]
    return ScoreModel(pages, models, boundaries, pickup)
