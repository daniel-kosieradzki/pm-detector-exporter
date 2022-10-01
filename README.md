# PM detector measurements exporter
## Introduction
TODO

## Requirements
1. Python 3
2. PySerial module (see Usage section)

## Usage
1. Create virtual environment:
   ```bash
   python3 -m virtualenv venv
   ```
1. Activate newly-created virtual environment, by issuing command like the one below:
   ```bash
   source venv/bin/activate.{your-shell-name}
   ```
   For example for FISH shell use:
   ```bash
   source venv/bin/activate.fish
   ```
1. Install prerequisites:
   ```bash
   pip3 install -r requirements.txt
   ```
1. Run the exporter
   ```bash
   python3 main.py
   ```

## A few useful commands the detector module understands
`{"fun":"05","flag":"1"}` - start realtime stream data

`{"fun":"05","flag":"0"}` - stop realtime stream data

`{"fun":"05","flag":"0"}{"fun":"80"}` - stop and enter config mode; expected response: `{"res":"80","SendInteralTime":"000020","StoreInteralTime":"000000","WritePoint":"000000","ReadPoint":"000000","SendInteralFlag":"000000"}`

`{"fun":"01","sendtime":"020"}{"res":"1"}{"fun":"05","flag":"0"}{"fun":"05","flag":"1"}` - set realtime interval to 20 seconds, start stream data

`{"fun":"03","clock":"20-09-14 18:53:56"}` - set time

`{"fun":"01","sendtime":"005"}`