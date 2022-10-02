import serial
import json
import logging
from fastapi import FastAPI
from model.measurement import Measurement
from threading import Thread

SERIAL_PORT_DEVICE_FILE = "/dev/tty.usbserial-14210"
SERIAL_PORT_BUFFER_SIZE = 50


def initialize_app() -> None:
  logging.basicConfig(level=logging.INFO)

def _start_scrapping_sensor_data() -> None:
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
      message_portion = serial_port.read(SERIAL_PORT_BUFFER_SIZE)
      sdp.process_message_portion(message_portion)


def start_scrapping_sensor_data() -> None:
  Thread(
    target=_start_scrapping_sensor_data,
    daemon=True
  ).start()


def start_api() -> None:
  global app
  app = FastAPI()


class SensorDataProcessor:
  def __init__(self) -> None:
    self.message_buffer = bytearray([])

    self.left_curly_brace_count = 0
    self.right_curly_brace_count = 0


  def _print_message(self, message: str) -> None:
    message_object = json.loads(message)
    if message_object["res"] == "4":
      m = Measurement(message_object)
      logging.info(m.to_json())
    else:
      logging.info(message)


  def process_message(self) -> None:
    message = self.message_buffer.decode("utf8")
    self._print_message(message)


  def process_message_portion(self, message_portion: bytes) -> None:
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


initialize_app()
start_scrapping_sensor_data()
start_api()

@app.get("/health")
def check_health():
  #TODO: Implement some real checks like checking whether serial port has been opened successfully
  return {"status_code": 0, "message": "OK"}

# @app.get("api/v1/measurements")
