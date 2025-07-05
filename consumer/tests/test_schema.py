import pytest
import pandas as pd
from consumer.schema import turbine_schema


def test_schema_accepts_valid_df():
    df = pd.DataFrame(
        [
            {
                "turbine_id": "T-001",
                "timestamp": "2025-07-05T12:00:00",
                "wind_speed": 12.3,
                "pitch_angle": 5.2,
                "power_output": 1000.0,
                "temperature": 60.0,
                "vibration": 0.3,
            }
        ]
    )
    # Should not raise
    turbine_schema.validate(df)


def test_schema_rejects_missing_column():
    bad_df = pd.DataFrame(
        [
            {
                "turbine_id": "T-002",
                "timestamp": "2025-07-05T12:00:00",
                # wind_speed column is missing!
                "pitch_angle": 5.2,
                "power_output": 1000.0,
                "temperature": 60.0,
                "vibration": 0.3,
            }
        ]
    )
    with pytest.raises(Exception):
        turbine_schema.validate(bad_df)
