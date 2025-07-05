import pandera.pandas as pa
from pandera import Column, DataFrameSchema
import pandas as pd

turbine_schema = DataFrameSchema({
    "turbine_id": Column(str),
    "timestamp": Column(pa.DateTime),
    "wind_speed": Column(float, checks=pa.Check.in_range(3, 25)),
    "pitch_angle": Column(float, checks=pa.Check.in_range(0, 15)),
    "power_output": Column(float),
    "temperature": Column(float, checks=pa.Check.in_range(30, 90)),
    "vibration": Column(float, checks=pa.Check.in_range(0, 1)),
})
