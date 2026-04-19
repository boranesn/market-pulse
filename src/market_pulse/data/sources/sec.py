from __future__ import annotations

import aiohttp

_EDGAR_BASE = "https://data.sec.gov"
_HEADERS = {"User-Agent": "market-pulse/1.0 ozboranesen@gmail.com"}


async def fetch_latest_filing(ticker: str, form_type: str = "10-K") -> dict[str, object]:
    """Fetch the latest 10-K or 10-Q filing metadata for a ticker."""
    cik = await _get_cik(ticker)
    url = f"{_EDGAR_BASE}/submissions/CIK{cik:010d}.json"
    async with aiohttp.ClientSession(headers=_HEADERS) as session:
        async with session.get(url) as resp:
            resp.raise_for_status()
            data: dict[str, object] = await resp.json(content_type=None)
    filings: dict[str, object] = data.get("filings", {})  # type: ignore[assignment]
    recent: dict[str, list[object]] = filings.get("recent", {})  # type: ignore[assignment]
    forms: list[str] = recent.get("form", [])  # type: ignore[assignment]
    dates: list[str] = recent.get("filingDate", [])  # type: ignore[assignment]
    accessions: list[str] = recent.get("accessionNumber", [])  # type: ignore[assignment]
    for form, date, acc in zip(forms, dates, accessions):
        if form == form_type:
            return {"ticker": ticker, "form": form, "date": date, "accession": acc, "cik": cik}
    return {"ticker": ticker, "form": None, "date": None, "accession": None, "cik": cik}


async def _get_cik(ticker: str) -> int:
    url = f"{_EDGAR_BASE}/files/company_tickers.json"
    async with aiohttp.ClientSession(headers=_HEADERS) as session:
        async with session.get(url) as resp:
            resp.raise_for_status()
            data: dict[str, dict[str, object]] = await resp.json(content_type=None)
    for entry in data.values():
        if str(entry.get("ticker", "")).upper() == ticker.upper():
            return int(entry["cik_str"])  # type: ignore[arg-type]
    raise ValueError(f"CIK not found for ticker: {ticker}")
