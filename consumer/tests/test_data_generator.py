# from producer.data_generator import generate_turbine_data


# def test_generator_produces_all_fields():
#     sample = generate_turbine_data()
#     expected_keys = {
#         "turbine_id",
#         "timestamp",
#         "wind_speed",
#         "pitch_angle",
#         "power_output",
#         "temperature",
#         "vibration",
#     }
#     assert expected_keys.issubset(sample.keys())

#     # quick type checks
#     assert isinstance(sample["turbine_id"], str)
#     assert isinstance(sample["wind_speed"], float)
#     assert sample["wind_speed"] >= 0

"""
Unit-tests for the generator – **no real Kafka needed**.
"""
from unittest.mock import patch, MagicMock

from producer.data_generator import generate_turbine_data


@patch("producer.data_generator.get_producer")
def test_generator_produces_all_fields(mock_get_producer: MagicMock) -> None:
    """
    Ensure every generated record contains the expected keys
    and basic sanity on types/ranges.
    """
    # mock Kafka so the import never even tries to connect
    mock_get_producer.return_value = MagicMock()

    sample = generate_turbine_data()

    expected_keys = {
        "turbine_id",
        "timestamp",
        "wind_speed",
        "pitch_angle",
        "power_output",
        "temperature",
        "vibration",
    }
    assert expected_keys.issubset(sample.keys())

    # quick type / value checks
    assert isinstance(sample["turbine_id"], str)
    assert isinstance(sample["wind_speed"], float)
    assert sample["wind_speed"] >= 0