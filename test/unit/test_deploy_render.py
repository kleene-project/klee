"""Unit tests for the deployment-diff rendering (pure function, fast tier)."""
import pytest

from klee.deploy import render_diff

pytestmark = pytest.mark.unit


def test_render_empty_diff():
    assert render_diff({"containers": {}, "images": {}, "networks": {}, "volumes": {}}) == []


def test_render_missing_on_host():
    diff = {
        "containers": {"db": [{"type": "missing_on_host"}]},
        "images": {},
        "networks": {},
        "volumes": {},
    }
    lines = render_diff(diff)
    assert lines == ["container 'db' is missing on the host"]


def test_render_not_equal():
    diff = {
        "containers": {
            "db": [
                {
                    "type": "not_equal",
                    "property": "user",
                    "value_host": "root",
                    "value_spec": "ntpd",
                }
            ]
        },
        "images": {},
        "networks": {},
        "volumes": {},
    }
    assert render_diff(diff) == [
        "container 'db': property 'user' differs: host='root' spec='ntpd'"
    ]


def test_render_unknown_entry_keeps_repr():
    diff = {
        "images": {"FreeBSD:latest": [{"type": "base_image_wrong_dataset_origin"}]},
        "containers": {},
        "networks": {},
        "volumes": {},
    }
    lines = render_diff(diff)
    assert len(lines) == 1
    assert "image 'FreeBSD:latest'" in lines[0]
    assert "base_image_wrong_dataset_origin" in lines[0]
