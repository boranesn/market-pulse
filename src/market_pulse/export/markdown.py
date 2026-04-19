from market_pulse.models.market import AnalysisReport


def render_markdown(report: AnalysisReport) -> str:
    lines = [
        f"# {report.ticker} — {report.depth.capitalize()} Analysis Report",
        f"*Generated: {report.generated_at.strftime('%Y-%m-%d %H:%M UTC')}*",
        "",
        "## Summary",
        report.summary,
        "",
        "## Bull Case",
        *[f"- {line}" for line in report.bull_case.split("\n") if line.strip()],
        "",
        "## Bear Case",
        *[f"- {line}" for line in report.bear_case.split("\n") if line.strip()],
        "",
        "## Key Risks",
        *[f"- ⚠ {risk}" for risk in report.key_risks],
        "",
        "## Signals",
        *[f"- {sig}" for sig in report.signals],
        "",
    ]
    if report.price_target_range:
        lo, hi = report.price_target_range
        lines += [f"## Price Target", f"${lo:.0f} – ${hi:.0f}", ""]
    return "\n".join(lines)
