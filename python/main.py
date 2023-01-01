import serial
import json
import logging
from fastapi import FastAPI
from model.measurement import Measurement
from threading import Thread

SERIAL_PORT_DEVICE_FILE = "/dev/tty.usbserial-14430"
SERIAL_PORT_BUFFER_SIZE = 50


def initialize_app() -> None:
  global current_measurement
  current_measurement = None
  logging.basicConfig(level=logging.INFO)


def measurement_ready_callback(m: Measurement) -> None:
  global current_measurement
  # logging.info(m)
  current_measurement = m


def _start_scrapping_sensor_data() -> None:
  sdp = SensorDataProcessor(measurement_ready_callback = measurement_ready_callback)

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


class SensorDataProcessor():
  def __init__(self, **kwargs) -> None:
    self.message_buffer = bytearray([])
    self.measurement_ready_callback = kwargs.get("measurement_ready_callback", None)

    self.left_curly_brace_count = 0
    self.right_curly_brace_count = 0


  def process_message(self) -> None:
    message = self.message_buffer.decode("utf8")
    try:
      m = Measurement(message)
      # logging.info(m)
      logging.info(m.to_json())

      if self.measurement_ready_callback is not None:
        logging.debug("Passing measurement message to callback function...")
        self.measurement_ready_callback(m)
    except:
      logging.info(message)



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


@app.get("/api/v1/measurements")
def get_measurements():
  # Translate current_measurement to some API-specific reponse object
  if current_measurement is not None:
    return current_measurement.as_dict()
  else:
    return {}
