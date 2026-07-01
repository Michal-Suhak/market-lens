"""Smoke test: ensure the market_lens package is importable and installed correctly."""

import market_lens


def test_package_is_importable():
    assert market_lens is not None


def test_package_has_version():
    assert isinstance(market_lens.__version__, str)
    assert market_lens.__version__ != ""
