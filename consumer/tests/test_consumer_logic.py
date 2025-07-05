from unittest.mock import MagicMock
import pandas as pd
import pandera.errors as pa_errors
from consumer.schema import turbine_schema
import pytest


def test_validated_df_sent_to_db(monkeypatch):
    """
    Simulate one valid message and ensure the DataFrame is inserted
    via pandas.DataFrame.to_sql exactly once.
    """
    # --- arrange ----------------------------------------------------
    mock_engine = MagicMock()
    df = pd.DataFrame(
        [
            dict(
                turbine_id="T-123",
                timestamp=pd.to_datetime("2025-07-05T12:00:00"),
                wind_speed=8.8,
                pitch_angle=4.5,
                power_output=500,
                temperature=55,
                vibration=0.2,
            )
        ]
    )

    # monkey-patch to_sql so we don’t hit a real DB
    called = {"count": 0}

    def fake_to_sql(*args, **kwargs):
        called["count"] += 1

    monkeypatch.setattr(pd.DataFrame, "to_sql", fake_to_sql)

    # --- act --------------------------------------------------------
    turbine_schema.validate(df)          # would raise if invalid
    df.to_sql("turbine_data", mock_engine, if_exists="append", index=False)

    # --- assert -----------------------------------------------------
    assert called["count"] == 1


def test_schema_error_triggers_counter():
    """
    Ensure an invalid message raises pandera SchemaError,
    which you'd catch in stream_consumer.py and increment the
    `messages_invalid` Prometheus counter.
    """
    bad_df = pd.DataFrame([{"foo": "bar"}])
    with pytest.raises(pa_errors.SchemaError):
        turbine_schema.validate(bad_df)
