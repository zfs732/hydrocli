from __future__ import annotations

from hydro_cli.cli import _build_case_rows


def test_final_case_rows_collapse_passed_and_hide_cancelled() -> None:
    rows = _build_case_rows(
        [
            {"case": "#1", "status": "Accepted", "score": "12", "time": "", "memory": "", "message": ""},
            {"case": "#1-1", "status": "Accepted", "score": "", "time": "1ms", "memory": "1 MiB", "message": ""},
            {"case": "#2", "status": "Time Exceeded", "score": "0", "time": "", "memory": "", "message": ""},
            {"case": "#2-1", "status": "Accepted", "score": "", "time": "1ms", "memory": "1 MiB", "message": ""},
            {"case": "#2-2", "status": "Cancelled", "score": "", "time": "0ms", "memory": "0 Bytes", "message": ""},
            {"case": "#2-3", "status": "Time Exceeded", "score": "", "time": ">=2s", "memory": "64 MiB", "message": ""},
        ],
        final=True,
    )

    assert [row["case"] for row in rows] == ["#1", "#2", "  #2-1", "  #2-3"]
    assert rows[0]["subtask"] == "#1"
    assert rows[1]["subtask"] == "#2"


def test_strict_case_rows_hide_judge_messages() -> None:
    rows = _build_case_rows(
        [
            {
                "case": "#1",
                "status": "Wrong Answer Correct assignment. Maximum trouble level : 1000000.00 .",
                "score": "0",
                "time": "1ms",
                "memory": "1 MiB",
                "message": "Correct assignment. Maximum trouble level : 1000000.00 .",
            },
            {
                "case": "#1-1",
                "status": "Accepted",
                "score": "",
                "time": "1ms",
                "memory": "1 MiB",
                "message": "Score : 10.00 points.",
            },
            {
                "case": "#2",
                "status": "OLE output is too long",
                "score": "0",
                "time": "1ms",
                "memory": "1 MiB",
                "message": "output is too long",
            },
            {
                "case": "#3",
                "status": "ILE input stream exceeded limit",
                "score": "0",
                "time": "1ms",
                "memory": "1 MiB",
                "message": "input stream exceeded limit",
            },
        ],
        final=False,
        strict=True,
    )

    assert rows[0]["status"] == "Wrong Answer"
    assert rows[0]["message"] == ""
    assert rows[1]["status"] == "Accepted"
    assert rows[1]["message"] == ""
    assert rows[2]["status"] == "OLE"
    assert rows[2]["message"] == ""
    assert rows[3]["status"] == "ILE"
    assert rows[3]["message"] == ""
