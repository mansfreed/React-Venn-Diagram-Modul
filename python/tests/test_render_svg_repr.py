"""Tests for SvgImage Jupyter inline-render hooks."""

from __future__ import annotations

from venn_diagram_lab.render.svg import SvgImage

_TINY_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10">'
    '<rect width="10" height="10" fill="#fff"/></svg>'
)


def test_repr_svg_returns_the_svg_string():
    img = SvgImage(svg=_TINY_SVG)
    assert img._repr_svg_() == _TINY_SVG


def test_repr_mimebundle_returns_svg_and_text_keys():
    img = SvgImage(svg=_TINY_SVG)
    bundle = img._repr_mimebundle_()
    assert "image/svg+xml" in bundle
    assert "text/plain" in bundle
    assert bundle["image/svg+xml"] == _TINY_SVG
    assert "SvgImage" in bundle["text/plain"]


def test_repr_mimebundle_respects_include_filter():
    img = SvgImage(svg=_TINY_SVG)
    bundle = img._repr_mimebundle_(include={"image/svg+xml"})
    assert "image/svg+xml" in bundle
    assert "text/plain" not in bundle


def test_repr_mimebundle_respects_exclude_filter():
    img = SvgImage(svg=_TINY_SVG)
    bundle = img._repr_mimebundle_(exclude={"text/plain"})
    assert "image/svg+xml" in bundle
    assert "text/plain" not in bundle
