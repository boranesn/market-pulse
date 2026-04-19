from market_pulse.models.market import AnalysisReport


def render_json(report: AnalysisReport) -> str:
    return report.model_dump_json(indent=2)
