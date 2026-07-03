from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from hydro_cli.errors import HydroCliError
from hydro_cli.submit import SubmitService


class FakeResponse:
    headers = {"location": "/record/r1"}
    text = ""


class RecordingClient:
    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    def raw_request(self, method: str, path: str, **kwargs: Any) -> FakeResponse:
        captured_files: dict[str, tuple[object, object, object | None]] = {}
        for name, value in kwargs["files"].items():
            filename = value[0]
            content = value[1]
            content_type = value[2] if len(value) > 2 else None
            if hasattr(content, "read"):
                content = content.read()
            captured_files[name] = (filename, content, content_type)
        self.calls.append(
            {
                "method": method,
                "path": path,
                "files": captured_files,
                "follow_redirects": kwargs.get("follow_redirects"),
            }
        )
        return FakeResponse()


def test_submit_answer_uploads_zip_file_as_hydro_answer(tmp_path: Path) -> None:
    zip_path = tmp_path / "answer.zip"
    zip_path.write_bytes(b"PK\x03\x04answer-data")
    client = RecordingClient()

    rid = SubmitService(client).submit_answer("P1000", zip_path)  # type: ignore[arg-type]

    assert rid == "r1"
    assert client.calls == [
        {
            "method": "POST",
            "path": "/p/P1000/submit",
            "files": {
                "lang": (None, "_", None),
                "code": (None, "", None),
                "file": ("answer.zip", b"PK\x03\x04answer-data", "application/zip"),
            },
            "follow_redirects": False,
        }
    ]


def test_submit_answer_rejects_non_zip_file(tmp_path: Path) -> None:
    answer_path = tmp_path / "answer.txt"
    answer_path.write_text("not a zip\n", encoding="utf-8")
    client = RecordingClient()

    with pytest.raises(HydroCliError, match=r"\.zip"):
        SubmitService(client).submit_answer("P1000", answer_path)  # type: ignore[arg-type]

    assert client.calls == []


def test_source_submit_still_uses_lang_and_code_fields(tmp_path: Path) -> None:
    source_path = tmp_path / "main.cpp"
    source_path.write_text("int main() {}\n", encoding="utf-8")
    client = RecordingClient()

    rid = SubmitService(client).submit("P1000", source_path)  # type: ignore[arg-type]

    assert rid == "r1"
    assert client.calls == [
        {
            "method": "POST",
            "path": "/p/P1000/submit",
            "files": {
                "lang": (None, "cc.cc20o2", None),
                "code": (None, "int main() {}\n", None),
            },
            "follow_redirects": False,
        }
    ]
