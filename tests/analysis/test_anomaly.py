from market_pulse.analysis.anomaly import zscore_anomalies, iqr_anomalies, detect_price_anomalies


def test_zscore_detects_outlier():
    values = [100.0] * 20 + [500.0]
    flags = zscore_anomalies(values)
    assert flags[-1] is True
    assert all(not f for f in flags[:-1])


def test_iqr_detects_outlier():
    values = list(range(1, 21)) + [200]
    flags = iqr_anomalies(values)
    assert flags[-1] is True


def test_no_anomaly_in_uniform():
    values = [50.0] * 30
    assert not any(zscore_anomalies(values))


def test_detect_price_anomalies_returns_string():
    prices = [100.0] * 20 + [500.0]
    result = detect_price_anomalies(prices)
    assert len(result) == 1
    assert "anomaly" in result[0].lower()
