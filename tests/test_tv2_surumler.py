"""Small contracts for the TV-2 metadata collector."""

import importlib.util
from pathlib import Path


SPEC = importlib.util.spec_from_file_location(
    "tv2_surumler", Path(__file__).parents[1] / "scripts" / "tv2_surumler.py"
)
assert SPEC and SPEC.loader
tv2 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(tv2)


def test_extracts_pub_and_page_metadata() -> None:
    page = ('{"script_id_part":"PUB;abc", "symbol":"BINANCE:BTCUSDT", '
            '"interval":"15", "created_at":"2024-01-02T00:00:00Z"}')

    assert tv2._pub(page) == "PUB;abc"
    assert tv2._page_metadata(page, "grafik:60") == ("BINANCE:BTCUSDT", "15")
    assert tv2._json_string(page, "created_at") == "2024-01-02T00:00:00Z"


def test_closed_page_is_reported_with_a_reason(monkeypatch) -> None:
    class Response:
        status_code = 404

        def raise_for_status(self) -> None:
            raise AssertionError("closed page must not be parsed")

    class Session:
        headers: dict[str, str] = {}

        def __enter__(self):
            return self

        def __exit__(self, *_args) -> None:
            return None

        def get(self, *_args, **_kwargs):
            return Response()

    monkeypatch.setattr(tv2.requests, "Session", Session)
    row = {"id": "TV-1", "url": "https://example.invalid/script/x", "tf": "grafik:5"}

    result = tv2.collect(row)

    assert result["id"] == "TV-1"
    assert result["tf"] == "5"
    assert result["kaynak_acik"] == "sayfa kapali (404)"


def test_retry_closed_preserves_old_row_when_page_is_still_closed(monkeypatch, tmp_path) -> None:
    source = tmp_path / "source.csv"
    target = tmp_path / "versions.csv"
    source.write_text(
        "id,url,tf,suzgec_sonucu\nold,https://example.invalid/script/old/,grafik:5,elendi:tf_disi\n",
        encoding="utf-8",
    )
    target.write_text(
        "id,pub,son_surum,son_surum_tarihi,ilk_yayin_tarihi,surum_sayisi,kaynak_acik,yayin_sembolu,tf\n"
        "old,PUB;old,,,,0,script bulunamadi veya kapali,FX:EURUSD,5\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(tv2, "collect", lambda _row: {
        "id": "old", "pub": "", "son_surum": "", "son_surum_tarihi": "",
        "ilk_yayin_tarihi": "", "surum_sayisi": "0", "kaynak_acik": "sayfa kapali (404)",
        "yayin_sembolu": "", "tf": "5",
    })
    monkeypatch.setattr("sys.argv", ["tv2_surumler", "--source", str(source), "--target", str(target), "--retry-closed"])

    assert tv2.main() == 0
    line = target.read_text(encoding="utf-8")
    assert "PUB;old" in line
    assert "yeniden arandi: sayfa kapali (404)" in line
