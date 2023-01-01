import json


class Measurement:
  def __init__(self, measurement_string: str) -> None:
    measurement = json.loads(measurement_string)
    # Check if the message object in fact contains a measurement
    if measurement["res"] == "4":
      self.year = int(measurement['y'])
      self.month = int(measurement['m'])
      self.day = int(measurement['d'])
      self.hours = int(measurement['h'])
      self.minutes = int(measurement['min'])
      self.seconds = int(measurement['sec'])

      self.temperature = float(measurement['t'])
      self.humidity = float(measurement['r'])

      self.pm_2_5 = int(measurement['cpm2.5'])
      self.pm_1_0 = int(measurement['cpm1.0'])
      self.pm_10 = int(measurement['cpm10'])

      self.air_quality_index = int(measurement['aqi'])
    else:
      raise Exception("Class object initialization failed!!!")

  def __str__(self) -> str:
    return f"{self.year}-{self.month:02d}-{self.day:02d} {self.hours:02d}:{self.minutes:02d}:{self.seconds:02d} - temperature: {self.temperature}, humidity: {self.humidity}, AQI: {self.air_quality_index}, PM2.5: {self.pm_2_5}"
  
  def to_json(self) -> str:
    measurement_dictionary = {attribute_name: attribute_value for attribute_name, attribute_value in self.__dict__.items()}
    return json.dumps(measurement_dictionary)
  
  def as_dict(self) -> dict:
    return self.__dict__