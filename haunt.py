# Halloween Prop Controller
# Runs on Raspberry Pi with GPIO + PIR sensor + audio playback

import RPi.GPIO as GPIO
import time
import random
import pygame
from pathlib import Path

# ----------------------------
# GPIO Setup
# ----------------------------
GPIO.setmode(GPIO.BCM)

PIR_PIN = 17
ARM_ONE = 23
ARM_TWO = 24

GPIO.setup(PIR_PIN, GPIO.IN)
GPIO.setup(ARM_ONE, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(ARM_TWO, GPIO.OUT, initial=GPIO.LOW)

# ----------------------------
# Config
# ----------------------------
SOUND_FILE = Path("zombie.mp3")
LOG_FILE = Path("halloweenlog.txt")
RANDOM_DELAY_MIN = 0.2
RANDOM_DELAY_MAX = 1.0
ARM_CYCLES = 5

# ----------------------------
# State
# ----------------------------
previous_state = 0
counter = 0

# ----------------------------
# Init pygame for sound
# ----------------------------
pygame.init()
pygame.mixer.init()


# ----------------------------
# Helpers
# ----------------------------
def random_delay():
    return random.uniform(RANDOM_DELAY_MIN, RANDOM_DELAY_MAX)


def make_noise():
    """Play the scary sound."""
    if SOUND_FILE.exists():
        print("  making noise...")
        pygame.mixer.music.load(str(SOUND_FILE))
        pygame.mixer.music.play(0)
    else:
        print(f"  Sound file not found: {SOUND_FILE}")


def move_arms(cycles=ARM_CYCLES):
    """Run randomized arm movement cycles."""
    for _ in range(cycles):
        GPIO.output(ARM_ONE, GPIO.LOW)
        GPIO.output(ARM_TWO, GPIO.LOW)
        time.sleep(1)

        GPIO.output(ARM_ONE, GPIO.HIGH)
        time.sleep(random_delay())

        GPIO.output(ARM_TWO, GPIO.HIGH)
        time.sleep(random_delay())

        GPIO.output(ARM_ONE, GPIO.LOW)
        time.sleep(random_delay())

        GPIO.output(ARM_ONE, GPIO.HIGH)
        GPIO.output(ARM_TWO, GPIO.LOW)
        time.sleep(random_delay())

        GPIO.output(ARM_TWO, GPIO.HIGH)


def log_trigger(message: str):
    """Append a message to the log file with timestamp."""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with LOG_FILE.open("a") as log:
        log.write(f"[{timestamp}] {message}\n")


# ----------------------------
# Main loop
# ----------------------------
print("PIR Module Test (CTRL-C to exit)")
print("Waiting for PIR to settle...")

# Wait until PIR output goes low
while GPIO.input(PIR_PIN) == 1:
    time.sleep(0.1)

print("Ready")

try:
    while True:
        current_state = GPIO.input(PIR_PIN)

        if current_state == 1 and previous_state == 0:
            # PIR triggered
            print("  Motion detected!")
            make_noise()
            counter += 1
            move_arms()
            pygame.mixer.music.stop()

            previous_state = 1
            log_trigger("Motion detected!")

        elif current_state == 0 and previous_state == 1:
            # PIR reset
            print("  Ready")
            GPIO.output(ARM_ONE, GPIO.HIGH)
            GPIO.output(ARM_TWO, GPIO.HIGH)
            previous_state = 0

        time.sleep(0.1)  # reduce CPU load

except KeyboardInterrupt:
    print(f"  You've spooked {counter} people!")
    log_trigger(f"You've spooked {counter} on this run!")
    print("  Quit")

finally:
    GPIO.cleanup()
