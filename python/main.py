import serial
import json
import sys

SERIAL_PORT_DEVICE_FILE = "/dev/tty.usbserial-14210"

class Measurement:
  def __init__(self, measurement: object) -> None:
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


  def __str__(self) -> str:
    return f"{self.year}-{self.month:02d}-{self.day:02d} {self.hours:02d}:{self.minutes:02d}:{self.seconds:02d} - temperature: {self.temperature}, humidity: {self.humidity}, AQI: {self.air_quality_index}, PM2.5: {self.pm_2_5}"
  
  def to_json(self) -> str:
    measurement_dictionary = {attribute_name: attribute_value for attribute_name, attribute_value in self.__dict__.items()}
    return json.dumps(measurement_dictionary)


class SensorDataProcessor:
  def __init__(self) -> None:
    self.message_buffer = bytearray([])

    self.left_curly_brace_count = 0
    self.right_curly_brace_count = 0


  def _print_message(self, message: str):
    message = json.loads(message)
    if message["res"] == "4":
      m = Measurement(message)
      # print(m)
      print(m.to_json())
      # self._print_measurement_message(message)


  def process_message(self):
    message = self.message_buffer.decode("utf8")
    self._print_message(message)


  def process_message_portion(self, message_portion: bytes):
    for byte in message_portion:
      self.message_buffer.append(byte)
      if byte == ord('}'):
        self.right_curly_brace_count = self.right_curly_brace_count + 1
        # Check if a message is complete (is proper JSON message)
        if self.left_curly_brace_count == self.right_curly_brace_count:
          self.process_message()
          self.message_buffer.clear()
          self.left_curly_brace_count = 0
          self.right_curly_brace_count = 0
        elif self.right_curly_brace_count > self.left_curly_brace_count:
          # This hasn't happened to me yet, but I assume in really rare cases we might start reading a message from the device from the middle.
          # In such cases the message would miss starting bytes. Just ignore such message and continue reading consecutive ones.
          self.message_buffer.clear()
          self.left_curly_brace_count = 0
          self.right_curly_brace_count = 0
          
      elif byte == ord('{'):
        self.left_curly_brace_count = self.left_curly_brace_count + 1

    # print(f"self.left_curly_brace_count: {self.left_curly_brace_count}")
    # print(f"self.right_curly_brace_count: {self.right_curly_brace_count}")

  # print(msg)


if __name__ == "__main__":
  sdp = SensorDataProcessor()

  with serial.Serial(SERIAL_PORT_DEVICE_FILE, 115200) as serial_port:
    # Stop realtime measurements sending mode
    # serial_port.write(b'{"fun":"05","flag":"0"}')

    # Set time interval for real-time measurements sending mode
    # serial_port.write(b'{"fun":"01","sendtime":"001"}}')

    # Start realtime measurements sending mode
    serial_port.write(b'{"fun":"05","flag":"1"}')
    # serial_port.read(100)

    while True:
      message_portion = serial_port.read(50)
      sdp.process_message_portion(message_portion)
