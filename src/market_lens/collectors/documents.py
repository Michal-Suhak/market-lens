from __future__ import annotations

from collections.abc import Iterable
from datetime import date, datetime

import requests
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

from market_lens.collectors.fomc import fomc_announcement_utc
from market_lens.storage import Document

FED_STATEMENT_URL = "https://www.federalreserve.gov/newsevents/pressreleases/monetary{date}a.htm"


def extract_statement_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    article = soup.select_one("#article") or soup.select_one("div.col-xs-12.col-sm-8.col-md-8")
    if article is None:
        raise ValueError("FOMC statement article not found in page")
    paragraphs = (p.get_text(strip=True) for p in article.find_all("p"))
    return "\n\n".join(p for p in paragraphs if p)


def build_fed_statement(text: str, published_ts_utc: datetime) -> Document:
    return Document(
        institution="FED", doc_type="FOMC", published_ts_utc=published_ts_utc, text=text
    )


def fetch_fed_statement(meeting_date: date) -> Document:
    url = FED_STATEMENT_URL.format(date=meeting_date.strftime("%Y%m%d"))
    resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
    resp.raise_for_status()
    return build_fed_statement(
        extract_statement_text(resp.text), fomc_announcement_utc(meeting_date)
    )


def load_fed_statements(session: Session, meeting_dates: Iterable[date]) -> int:
    docs = [fetch_fed_statement(d) for d in meeting_dates]
    session.add_all(docs)
    session.commit()
    return len(docs)
