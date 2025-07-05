from producer.data_generator import generate_turbine_data


def test_generator_produces_all_fields():
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

    # quick type checks
    assert isinstance(sample["turbine_id"], str)
    assert isinstance(sample["wind_speed"], float)
    assert sample["wind_speed"] >= 0
