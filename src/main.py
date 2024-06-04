#!/usr/bin/env python3

import time
import sys

import bme280
import numpy as np
import smbus2
import sounddevice as sd

# Dataset options
CSV_PATH = "climate_data.csv"
RESOLUTION = 0.1	# Refresh time in seconds

# I2C Options
ADDRESS = 0x76
BUS = smbus2.SMBus(1)
CALIBRATION_PARAMS = bme280.load_calibration_params(BUS, ADDRESS)

# Audio options
SAMPLE_RATE = 44100
CHANNELS = 1
BUFFER_SIZE = int(SAMPLE_RATE * RESOLUTION)    # Number of frames per buffer. Hz = 1/seg -> 1/seg * seg = Eskalarra -> Zenbat sample erresoluzio denboran.

def get_sound_level(stream: sd.Stream):
	indata, _ = stream.read(BUFFER_SIZE)	# Blocking!! This will wait until the buffer is full
	rms_val = np.sqrt(np.mean(indata ** 2))
	db_val = 20 * np.log10(rms_val) if rms_val > 0 else -np.inf
	return db_val


def main() -> int:
	print("\033c")
	with sd.Stream(samplerate=SAMPLE_RATE, channels=CHANNELS, dtype="float32") as stream:
		with open(CSV_PATH, "a+") as file:
			file.write("Time,Temperature,Humidity,Pressure,SoundLvL\n")
			while True:
				try:
					data = bme280.sample(BUS, ADDRESS, CALIBRATION_PARAMS)
					unix_timestamp = time.time_ns()
					temperature_celsius = data.temperature
					pressure = data.pressure
					humidity = data.humidity
					sound_lvl = get_sound_level(stream)
					if sound_lvl == -np.inf:
						print("The microphone disconnected! Execution stopped.")
						input("Press key to exit.")
						sys.exit(1)
					file.write(f"{unix_timestamp},{temperature_celsius:.2f},{pressure:.2f},{humidity:.2f},{sound_lvl:.2f}\n")
					print("Time: {}".format(unix_timestamp))
					print("Temp: {:.2f} ºC".format(temperature_celsius))
					print("Pressure: {:.2f} hPa".format(pressure))
					print("Humidity: {:.2f} %".format(humidity))
					print("Sound Level: {:.2f} dB".format(sound_lvl))
					print("\033[H\033[j")
				except KeyboardInterrupt:
					print("Program stopped")
					print("\033c")
					break
				except Exception as e:
					print("Unexpected exception: ", str(e))
					break

	return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
