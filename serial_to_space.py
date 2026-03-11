"""
Listen on a serial port and press the space key when the string "hello" arrives.
Dependencies: pip install pyserial keyboard
"""

import time

import keyboard  # type: ignore
import serial


PORT = "COM7"  # Serial port number 0 on Windows maps to COM1; change if needed.
BAUD = 115200
# Mind+ button A is configured to print "hello". Include "a" as a secondary trigger
# in case the device sends just the letter instead of the full word.
TRIGGERS = (b"hello", b"a")
DEBUG = True  # Set False to silence logs.
# Debounce to avoid rapid repeat on noisy serial streams.
DEBOUNCE_SEC = 0.2


def main() -> None:
    try:
        with serial.Serial(PORT, BAUD, timeout=0.1) as ser:
            ser.reset_input_buffer()  # Drop any stale bytes to avoid false triggers.
            buffer = b""
            last_fire = 0.0
            while True:
                data = ser.read(ser.in_waiting or 1)
                if data:
                    buffer += data
                    if DEBUG:
                        # Show raw incoming bytes for troubleshooting.
                        try:
                            print(f"RX: {data.decode(errors='replace').rstrip()!r}")
                        except Exception:
                            print(f"RX bytes: {data!r}")
                    # Avoid unbounded growth if a lot of data streams in.
                    if len(buffer) > 2048:
                        buffer = buffer[-2048:]

                    # Case-insensitive search for any trigger in buffer.
                    lower_buf = buffer.lower()
                    if any(t in lower_buf for t in TRIGGERS):
                        now = time.time()
                        if now - last_fire >= DEBOUNCE_SEC:
                            if DEBUG:
                                print(f"Trigger received in buffer={buffer!r}; sending space")
                            keyboard.send("space")
                            last_fire = now
                        buffer = b""
                else:
                    time.sleep(0.01)
    except KeyboardInterrupt:
        # Graceful exit on Ctrl+C.
        return
    except serial.SerialException as exc:
        print(f"Serial error opening/using {PORT}: {exc}")


if __name__ == "__main__":
    main()
