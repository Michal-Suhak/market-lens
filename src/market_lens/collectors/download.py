from __future__ import annotations

import zipfile
from pathlib import Path

from histdata import download_hist_data
from histdata.api import Platform, TimeFrame


def download_histdata_m1(
    pair: str,
    year: int | str,
    *,
    month: int | str | None = None,
    dest_dir: str | Path = "data/prices",
) -> Path:
    """Download a HistData M1 zip for a pair and extract its CSV into dest_dir; return the CSV path."""
    dest = Path(dest_dir)
    dest.mkdir(parents=True, exist_ok=True)
    zip_name = download_hist_data(
        year=str(year),
        month=str(month) if month is not None else None,
        pair=pair,
        time_frame=TimeFrame.ONE_MINUTE,
        platform=Platform.GENERIC_ASCII,
        output_directory=str(dest),
        verbose=False,
    )
    zip_path = dest / Path(zip_name).name
    with zipfile.ZipFile(zip_path) as zf:
        csv_name = next(name for name in zf.namelist() if name.lower().endswith(".csv"))
        zf.extract(csv_name, dest)
    zip_path.unlink()
    return dest / csv_name
