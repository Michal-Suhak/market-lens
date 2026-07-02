import zipfile
from pathlib import Path

from market_lens.collectors.download import download_histdata_m1


def test_download_extracts_csv(tmp_path, monkeypatch):
    def fake_download(*, year, month, pair, time_frame, platform, output_directory, verbose):
        zip_path = Path(output_directory) / "bundle.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("DAT_ASCII_EURUSD_M1_2025.csv", "20250102 000000;1.0;1.0;1.0;1.0;0")
        return "bundle.zip"

    monkeypatch.setattr("market_lens.collectors.download.download_hist_data", fake_download)

    csv_path = download_histdata_m1("eurusd", 2025, dest_dir=tmp_path)

    assert csv_path.exists()
    assert csv_path.name == "DAT_ASCII_EURUSD_M1_2025.csv"
    assert not (tmp_path / "bundle.zip").exists()
