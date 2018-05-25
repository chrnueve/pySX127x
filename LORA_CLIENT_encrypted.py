#!/usr/bin/env python3

""" This program sends a response whenever it receives the "INF" """

# Copyright 2018 Rui Silva.
#
# This file is part of rpsreal/pySX127x, fork of mayeranalytics/pySX127x.
#
# pySX127x is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public
# License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# pySX127x is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more
# details.
#
# You can be released from the requirements of the license by obtaining a commercial license. Such a license is
# mandatory as soon as you develop commercial activities involving pySX127x without disclosing the source code of your
# own applications, or shipping pySX127x with a closed source product.
#
# You should have received a copy of the GNU General Public License along with pySX127.  If not, see
# <http://www.gnu.org/licenses/>.

import time, base64
from SX127x.LoRa import *
from SX127x.LoRaArgumentParser import LoRaArgumentParser
from SX127x.board_config import BOARD
from Crypto.Cipher import AES

BOARD.setup()
BOARD.reset()
parser = LoRaArgumentParser("Lora tester")


class mylora(LoRa):
    def __init__(self, verbose=False):
        super(mylora, self).__init__(verbose)
        self.set_mode(MODE.SLEEP)
        self.set_dio_mapping([0] * 6)
        self.key = '1234567890123456'

    def on_rx_done(self):
        BOARD.led_on()
        #print("\nRxDone")
        self.clear_irq_flags(RxDone=1)
        payload = self.read_payload(nocheck=True )
        
        mens=payload[4:-1] #to discard \xff\xff\x00\x00 and \x00 at the end
        mens=bytes(mens).decode("utf-8",'ignore')
        cipher = AES.new(self.key)
        decoded = cipher.decrypt(base64.b64decode(mens))
        decoded = bytes(decoded).decode("utf-8",'ignore')
        print ("== RECEIVE: ", mens, "  |  Decoded: ",decoded )
        
        
        BOARD.led_off()
        if mens=="INF             ":
            print("Received data request INF - going to send mens:DATA RASPBERRY PI")
            time.sleep(2)

            msg_text = 'DATA RASPI      ' # 16 char
            cipher = AES.new(self.key)
            encoded = base64.b64encode(cipher.encrypt(msg_text))
            lista=list(encoded)
            lista.insert(0,0)
            lista.insert(0,0)
            lista.insert(0,255)
            lista.insert(0,255)
            lista.append(0)
            self.write_payload(lista)
            #self.write_payload([255, 255, 0, 0, 68, 65, 84, 65, 32, 82, 65, 83, 80, 66, 69, 82, 82, 89, 32, 80, 73, 0]) # Send DATA RASPBERRY PI
            self.set_mode(MODE.TX)
            print ("== SEND: DATA RASPI        |  Encoded: ", encoded)
        time.sleep(.5)
        self.reset_ptr_rx()
        self.set_mode(MODE.RXCONT)

    def on_tx_done(self):
        print("\nTxDone")
        print(self.get_irq_flags())

    def on_cad_done(self):
        print("\non_CadDone")
        print(self.get_irq_flags())

    def on_rx_timeout(self):
        print("\non_RxTimeout")
        print(self.get_irq_flags())

    def on_valid_header(self):
        print("\non_ValidHeader")
        print(self.get_irq_flags())

    def on_payload_crc_error(self):
        print("\non_PayloadCrcError")
        print(self.get_irq_flags())

    def on_fhss_change_channel(self):
        print("\non_FhssChangeChannel")
        print(self.get_irq_flags())

    def start(self):          
        while True:
            self.reset_ptr_rx()
            self.set_mode(MODE.RXCONT) # Receiver mode
            while True:
                pass;
            

lora = mylora(verbose=False)
args = parser.parse_args(lora) # configs in LoRaArgumentParser.py

#lora.set_mode(MODE.STDBY)
lora.set_pa_config(pa_select=1)


assert(lora.get_agc_auto_on() == 1)

try:
    print("START")
    lora.start()
except KeyboardInterrupt:
    sys.stdout.flush()
    print("Exit")
    sys.stderr.write("KeyboardInterrupt\n")
finally:
    sys.stdout.flush()
    print("Exit")
    lora.set_mode(MODE.SLEEP)
BOARD.teardown()
