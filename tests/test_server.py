import os
import sys
from pathlib import Path

import pytest

os.environ.setdefault("LIBRARY_API_KEY", "test-key")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from server import _normalize_arguments, _remote_tools  # noqa: E402


def test_remote_catalog_is_read_only_and_disables_file_writes():
    [tool] = _remote_tools()

    assert tool.annotations is not None
    assert tool.annotations.read_only_hint is True
    properties = tool.input_schema["properties"]
    assert "save_file" not in properties
    assert "output_dir" not in properties
    assert properties["target_apis"]["maxItems"] == 6


def test_normalize_arguments_forces_no_file_write():
    arguments = _normalize_arguments(
        {"lat": 36.6953, "lon": 137.2113, "target_apis": [3, 5], "distance": 100}
    )

    assert arguments["save_file"] is False


@pytest.mark.parametrize(
    "arguments,message",
    [
        ({"lat": 91, "lon": 137, "target_apis": [3]}, "lat"),
        ({"lat": 36, "lon": 181, "target_apis": [3]}, "lon"),
        ({"lat": 36, "lon": 137, "target_apis": []}, "target_apis"),
        ({"lat": 36, "lon": 137, "target_apis": [31]}, "target_apis"),
        ({"lat": 36, "lon": 137, "target_apis": [3, 3]}, "重複"),
        ({"lat": 36, "lon": 137, "target_apis": [3], "distance": 426}, "distance"),
        ({"lat": 36, "lon": 137, "target_apis": [3], "save_file": True}, "ファイル保存"),
    ],
)
def test_normalize_arguments_rejects_unsafe_inputs(arguments, message):
    with pytest.raises(ValueError, match=message):
        _normalize_arguments(arguments)
