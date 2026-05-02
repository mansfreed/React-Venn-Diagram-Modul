"""Tests for venn_diagram_lab.render.svg."""

from __future__ import annotations

import pytest
from lxml import etree

from venn_diagram_lab.analysis import analyze, list_models
from venn_diagram_lab.errors import UnknownModelError
from venn_diagram_lab.io import Dataset
from venn_diagram_lab.render.svg import (
    SvgImage,
    _find_by_id,
    _is_venn_model,
    _load_template,
    _replace_fill_color,
    _set_text,
    render_venn_svg,
)

_LETTERS = "ABCDEFGHI"


def _bitmask_for_label(label: str) -> int:
    return sum(1 << _LETTERS.index(ch) for ch in label)


class TestSvgImage:
    def test_construction_holds_svg_string(self) -> None:
        img = SvgImage(svg="<svg></svg>")
        assert img.svg == "<svg></svg>"

    def test_repr_svg_returns_raw_string(self) -> None:
        img = SvgImage(svg="<svg></svg>")
        assert img._repr_svg_() == "<svg></svg>"

    def test_str_returns_svg(self) -> None:
        img = SvgImage(svg="<svg></svg>")
        assert str(img) == "<svg></svg>"


class TestIsVennModel:
    def test_accepts_venn_prefix(self) -> None:
        assert _is_venn_model("venn-3-set") is True
        assert _is_venn_model("venn-5a-set-edwards") is True

    def test_rejects_non_venn(self) -> None:
        assert _is_venn_model("names-bar") is False
        assert _is_venn_model("anything-else") is False


class TestLoadTemplate:
    def test_loads_known_model(self) -> None:
        text = _load_template("venn-3-set")
        assert "<svg" in text
        assert 'id="Count_A"' in text

    def test_unknown_model_raises(self) -> None:
        with pytest.raises(UnknownModelError, match="not found"):
            _load_template("venn-not-a-real-model")

    def test_rejects_non_venn_model_name(self) -> None:
        with pytest.raises(UnknownModelError, match="not a venn model"):
            _load_template("names-bar")


_TINY_SVG = """<?xml version="1.0"?>
<svg xmlns="http://www.w3.org/2000/svg">
  <text id="Title">Old Title</text>
  <text id="Count_A">A</text>
  <circle id="ShapeA" style="opacity:0.2;fill:#FFF200;stroke:#000000;stroke-width:3;"/>
</svg>
"""


class TestFindById:
    def test_returns_element(self) -> None:
        root = etree.fromstring(_TINY_SVG.encode())
        el = _find_by_id(root, "Title")
        assert el is not None
        assert el.attrib["id"] == "Title"

    def test_returns_none_when_missing(self) -> None:
        root = etree.fromstring(_TINY_SVG.encode())
        assert _find_by_id(root, "Nonexistent") is None


class TestSetText:
    def test_overwrites_text_content(self) -> None:
        root = etree.fromstring(_TINY_SVG.encode())
        _set_text(root, "Title", "New Title")
        el = _find_by_id(root, "Title")
        assert el is not None
        assert el.text == "New Title"

    def test_silent_when_id_missing(self) -> None:
        root = etree.fromstring(_TINY_SVG.encode())
        _set_text(root, "Nonexistent", "ignored")
        assert _find_by_id(root, "Title").text == "Old Title"

    def test_accepts_empty_string(self) -> None:
        root = etree.fromstring(_TINY_SVG.encode())
        _set_text(root, "Count_A", "")
        assert _find_by_id(root, "Count_A").text == ""


class TestReplaceFillColor:
    def test_replaces_fill_in_inline_style(self) -> None:
        root = etree.fromstring(_TINY_SVG.encode())
        _replace_fill_color(root, "ShapeA", "#ABCDEF")
        el = _find_by_id(root, "ShapeA")
        assert "fill:#ABCDEF" in el.attrib["style"]
        assert "opacity:0.2" in el.attrib["style"]
        assert "stroke:#000000" in el.attrib["style"]

    def test_silent_when_id_missing(self) -> None:
        root = etree.fromstring(_TINY_SVG.encode())
        _replace_fill_color(root, "ShapeNonexistent", "#ABCDEF")

    def test_silent_when_style_has_no_fill(self) -> None:
        svg = '<svg xmlns="http://www.w3.org/2000/svg"><circle id="X" style="opacity:0.5;"/></svg>'
        root = etree.fromstring(svg.encode())
        _replace_fill_color(root, "X", "#ABCDEF")
        assert _find_by_id(root, "X").attrib["style"] == "opacity:0.5;"


class TestRenderVennSvgBasic:
    def _two_set_result(self):
        ds = Dataset.from_dict({"A": {"X", "Y", "Z"}, "B": {"Y", "Z", "W"}})
        return analyze(ds, model="venn-2-set")

    def test_returns_svg_image(self) -> None:
        img = render_venn_svg(self._two_set_result())
        assert isinstance(img, SvgImage)
        assert img.svg.startswith("<?xml") or img.svg.startswith("<svg")

    def test_count_a_populated(self) -> None:
        img = render_venn_svg(self._two_set_result())
        root = etree.fromstring(img.svg.encode())
        count_a = _find_by_id(root, "Count_A")
        assert count_a is not None
        assert count_a.text == "1"

    def test_count_ab_populated(self) -> None:
        img = render_venn_svg(self._two_set_result())
        root = etree.fromstring(img.svg.encode())
        assert _find_by_id(root, "Count_AB").text == "2"

    def test_missing_region_shows_zero(self) -> None:
        ds = Dataset.from_dict({"A": {"x"}, "B": {"y"}})
        result = analyze(ds, model="venn-2-set")
        img = render_venn_svg(result)
        root = etree.fromstring(img.svg.encode())
        assert _find_by_id(root, "Count_AB").text == "0"


class TestRenderVennSvgNames:
    def _two_set_result_with_names(self):
        ds = Dataset.from_dict({"Human": {"BRCA1", "TP53"}, "Mouse": {"Brca1", "Tp53"}})
        return analyze(ds, model="venn-2-set")

    def test_dataset_names_become_name_a_name_b(self) -> None:
        img = render_venn_svg(self._two_set_result_with_names())
        root = etree.fromstring(img.svg.encode())
        assert _find_by_id(root, "NameA").text == "Human"
        assert _find_by_id(root, "NameB").text == "Mouse"

    def test_custom_set_names_override(self) -> None:
        img = render_venn_svg(
            self._two_set_result_with_names(),
            set_names={"A": "Homo sapiens"},
        )
        root = etree.fromstring(img.svg.encode())
        assert _find_by_id(root, "NameA").text == "Homo sapiens"
        assert _find_by_id(root, "NameB").text == "Mouse"

    def test_show_names_false_blanks_them(self) -> None:
        img = render_venn_svg(self._two_set_result_with_names(), show_names=False)
        root = etree.fromstring(img.svg.encode())
        # lxml represents an empty text node as None after serialisation round-trip.
        assert ((_find_by_id(root, "NameA").text) or "") == ""
        assert ((_find_by_id(root, "NameB").text) or "") == ""


class TestRenderVennSvgTitle:
    def _two_set_result(self):
        ds = Dataset.from_dict({"A": {"x"}, "B": {"x"}})
        return analyze(ds, model="venn-2-set")

    def test_default_title_is_template_default(self) -> None:
        img = render_venn_svg(self._two_set_result())
        root = etree.fromstring(img.svg.encode())
        title = _find_by_id(root, "Title")
        assert title is not None
        assert title.text == "Venn 2-set diagram"

    def test_custom_title_overrides(self) -> None:
        img = render_venn_svg(self._two_set_result(), title="My Comparison")
        root = etree.fromstring(img.svg.encode())
        assert _find_by_id(root, "Title").text == "My Comparison"

    def test_empty_title_blanks_it(self) -> None:
        img = render_venn_svg(self._two_set_result(), title="")
        root = etree.fromstring(img.svg.encode())
        # B2's lxml round-trip behavior: empty text reads back as None
        assert (_find_by_id(root, "Title").text or "") == ""


class TestRenderVennSvgColors:
    def _two_set_result(self):
        ds = Dataset.from_dict({"A": {"x"}, "B": {"x"}})
        return analyze(ds, model="venn-2-set")

    def test_default_colors_are_template_defaults(self) -> None:
        img = render_venn_svg(self._two_set_result())
        root = etree.fromstring(img.svg.encode())
        shape_a = _find_by_id(root, "ShapeA")
        assert "fill:#FFF200" in shape_a.attrib["style"]

    def test_custom_color_recolors_shape_and_bullet(self) -> None:
        img = render_venn_svg(self._two_set_result(), colors={"A": "#FF0000"})
        root = etree.fromstring(img.svg.encode())
        assert "fill:#FF0000" in _find_by_id(root, "ShapeA").attrib["style"]
        assert "fill:#FF0000" in _find_by_id(root, "BulletA").attrib["style"]
        # Other set untouched.
        shape_b = _find_by_id(root, "ShapeB")
        assert "fill:#FF0000" not in shape_b.attrib["style"]

    def test_color_override_with_partial_set(self) -> None:
        img = render_venn_svg(self._two_set_result(), colors={"A": "#ABCDEF"})
        root = etree.fromstring(img.svg.encode())
        assert "fill:#ABCDEF" in _find_by_id(root, "ShapeA").attrib["style"]
        assert "fill:#2E3192" in _find_by_id(root, "ShapeB").attrib["style"]

    def test_euler_extras_recolored_when_present(self) -> None:
        # venn-4e-set-euler may have ShapeX2 elements (Euler diagrams' second polygon).
        ds = Dataset.from_dict({"A": {"x"}, "B": {"x"}, "C": {"x"}, "D": {"x"}})
        result = analyze(ds, model="venn-4e-set-euler")
        img = render_venn_svg(result, colors={"A": "#ABCDEF"})
        root = etree.fromstring(img.svg.encode())
        shape_a2 = _find_by_id(root, "ShapeA2")
        if shape_a2 is not None:  # only assert if the model actually has it
            assert "fill:#ABCDEF" in shape_a2.attrib["style"]


class TestRenderVennSvgCountSums:
    def test_2_set_model_populates_countsum(self) -> None:
        # All 44 models (including 2-set) have CountSUM_X elements per set.
        ds = Dataset.from_dict({"A": {"x", "y", "z"}, "B": {"x"}})
        img = render_venn_svg(analyze(ds, model="venn-2-set"))
        root = etree.fromstring(img.svg.encode())
        assert _find_by_id(root, "CountSUM_A").text == "3"
        assert _find_by_id(root, "CountSUM_B").text == "1"

    def test_6_set_model_populates_countsum(self) -> None:
        set_sizes = {"A": 10, "B": 20, "C": 30, "D": 40, "E": 50, "F": 60}
        ds = Dataset.from_dict(
            {k: {f"{k}{i}" for i in range(v)} for k, v in set_sizes.items()}
        )
        result = analyze(ds, model="venn-6a-set-edwards")
        img = render_venn_svg(result)
        root = etree.fromstring(img.svg.encode())
        for letter, size in set_sizes.items():
            el = _find_by_id(root, f"CountSUM_{letter}")
            assert el is not None, f"Expected CountSUM_{letter} on 6-set model"
            assert el.text == str(size)

    def test_show_counts_false_blanks_countsum_too(self) -> None:
        set_sizes = {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 6}
        ds = Dataset.from_dict(
            {k: {f"{k}{i}" for i in range(v)} for k, v in set_sizes.items()}
        )
        result = analyze(ds, model="venn-6a-set-edwards")
        img = render_venn_svg(result, show_counts=False)
        root = etree.fromstring(img.svg.encode())
        # B2's lxml round-trip behavior: empty text reads back as None
        assert (_find_by_id(root, "CountSUM_A").text or "") == ""


class TestSvgImageSaveSvg:
    def test_save_to_svg_writes_file(self, tmp_path) -> None:
        img = SvgImage(svg='<svg xmlns="http://www.w3.org/2000/svg"><circle r="1"/></svg>')
        out = tmp_path / "out.svg"
        img.save(out)
        assert out.is_file()
        assert out.read_text(encoding="utf-8") == img.svg

    def test_save_accepts_str_path(self, tmp_path) -> None:
        img = SvgImage(svg='<svg xmlns="http://www.w3.org/2000/svg"/>')
        out = tmp_path / "out.svg"
        img.save(str(out))
        assert out.is_file()

    def test_save_unknown_extension_raises(self, tmp_path) -> None:
        img = SvgImage(svg='<svg xmlns="http://www.w3.org/2000/svg"/>')
        with pytest.raises(ValueError, match="extension"):
            img.save(tmp_path / "out.txt")


_TINY_SVG_CIRCLE = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10">'
    '<circle cx="5" cy="5" r="4"/>'
    '</svg>'
)

_PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


class TestSvgImageSavePng:
    def test_save_to_png_writes_png_file(self, tmp_path) -> None:
        img = SvgImage(svg=_TINY_SVG_CIRCLE)
        out = tmp_path / "out.png"
        img.save(out)
        assert out.is_file()
        # PNG magic bytes
        assert out.read_bytes()[:8] == _PNG_MAGIC

    def test_save_to_png_with_dpi_kwarg(self, tmp_path) -> None:
        img = SvgImage(svg=_TINY_SVG_CIRCLE)
        out_low = tmp_path / "low.png"
        out_high = tmp_path / "high.png"
        img.save(out_low, dpi=72)
        img.save(out_high, dpi=300)
        # Higher DPI -> larger file (more pixels). Loose check for sanity.
        assert out_high.stat().st_size > out_low.stat().st_size


_PDF_MAGIC = b"%PDF-"


class TestSvgImageSavePdf:
    def test_save_to_pdf_writes_pdf_file(self, tmp_path) -> None:
        img = SvgImage(svg=_TINY_SVG_CIRCLE)
        out = tmp_path / "out.pdf"
        img.save(out)
        assert out.is_file()
        # PDF magic bytes
        assert out.read_bytes()[: len(_PDF_MAGIC)] == _PDF_MAGIC


class TestRegionResultRenderVenn:
    def test_method_returns_svg_image(self) -> None:
        ds = Dataset.from_dict({"A": {"x"}, "B": {"x"}})
        result = analyze(ds, model="venn-2-set")
        img = result.render_venn()
        assert isinstance(img, SvgImage)

    def test_method_passes_through_kwargs(self) -> None:
        ds = Dataset.from_dict({"A": {"x"}, "B": {"x"}})
        result = analyze(ds, model="venn-2-set")
        img = result.render_venn(title="Custom")
        root = etree.fromstring(img.svg.encode())
        assert _find_by_id(root, "Title").text == "Custom"

    def test_method_uses_result_model_by_default(self) -> None:
        ds = Dataset.from_dict({"A": {"x"}, "B": {"x"}})
        result = analyze(ds, model="venn-2a-set-edwards")  # not the default
        img = result.render_venn()
        # Easiest check: byte-equality against direct render_venn_svg call
        direct = render_venn_svg(result)
        assert img.svg == direct.svg


class TestRoundTrip:
    def test_render_then_parse_counts(self) -> None:
        # Build a 3-set dataset with known per-region counts.
        # A only -> 5, B only -> 3, AB -> 7, ABC -> 2 (others zero/empty)
        a_only = {f"a{i}" for i in range(5)}
        b_only = {f"b{i}" for i in range(3)}
        ab_only = {f"ab{i}" for i in range(7)}
        abc_only = {f"abc{i}" for i in range(2)}
        ds = Dataset.from_dict({
            "A": a_only | ab_only | abc_only,
            "B": b_only | ab_only | abc_only,
            "C": abc_only,
        })
        result = analyze(ds, model="venn-3-set")
        img = result.render_venn()

        root = etree.fromstring(img.svg.encode())
        assert _find_by_id(root, "Count_A").text == "5"
        assert _find_by_id(root, "Count_B").text == "3"
        assert _find_by_id(root, "Count_AB").text == "7"
        assert _find_by_id(root, "Count_ABC").text == "2"
        assert _find_by_id(root, "Count_C").text == "0"
        assert _find_by_id(root, "Count_AC").text == "0"
        assert _find_by_id(root, "Count_BC").text == "0"


EXPECTED_MODEL_COUNT = 44


class TestAll44Models:
    def test_every_venn_model_renders_to_valid_svg(self) -> None:
        rendered = 0
        for m in list_models():
            n = m.set_count
            # Build a simple dataset of n sets, each with one shared item so
            # every region (including the full intersection) has at least one
            # element.
            ds = Dataset.from_dict(
                {chr(ord("A") + i): {"shared", f"item{i}"} for i in range(n)}
            )
            result = analyze(ds, model=m.name)
            img = result.render_venn()

            # Re-parse to confirm the output is well-formed XML.
            root = etree.fromstring(img.svg.encode())

            # Every Count_<letter> for sets A..A+n-1 must exist and hold a
            # digit string.
            for i in range(n):
                el = _find_by_id(root, f"Count_{chr(ord('A') + i)}")
                assert el is not None, f"Model {m.name}: missing Count_{chr(ord('A') + i)}"
                assert el.text is not None
                assert el.text.isdigit(), (
                    f"Model {m.name}: Count_{chr(ord('A') + i)} = {el.text!r}"
                )
            rendered += 1

        # Sanity: the loop actually visited all 44 models.
        assert rendered == EXPECTED_MODEL_COUNT, (
            f"Rendered {rendered} models, expected {EXPECTED_MODEL_COUNT}"
        )
