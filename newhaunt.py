# Import required Python libraries
import RPi.GPIO as GPIO
import time
import random
import pygame

# Use BCM GPIO references
# instead of BCM pin numbers
GPIO.setmode(GPIO.BCM)

# Define GPIO to use on Pi
pir = 17
arm_one = 23
arm_two = 24
# counter
counter = 0

print("PIR Module Test (CTRL-C to exit)")

# Set pin as input
GPIO.setup(pir, GPIO.IN)
GPIO.setup(arm_one, GPIO.OUT)
GPIO.setup(arm_two, GPIO.OUT)
GPIO.output(arm_one, False)
GPIO.output(arm_two, False)

current_state = 0
previous_state = 0

pygame.init()


def getRandomNum():
    random_sleep = random.uniform(0, 1)
    return random_sleep


def makeNoise():
    print("  making noise")
    pygame.mixer.music.load("zombie.mp3")
    pygame.mixer.music.play(0)


try:
    print("Waiting for PIR to settle ...")
    # Loop until PIR output is 0
    while GPIO.input(pir) == 1:
        current_state = 0

    print("Ready")

    # Loop until users quits with CTRL-C
    while True:
        # Read PIR state
        current_state = GPIO.input(pir)

        if current_state == 1 and previous_state == 0:
            # PIR is triggered
            print("  Motion detected!")
            makeNoise()
            counter += 1

            for i in range(5):
                GPIO.output(arm_one, False)
                GPIO.output(arm_two, False)
                time.sleep(1)
                GPIO.output(arm_one, True)
                time.sleep(getRandomNum())
                GPIO.output(arm_two, True)
                time.sleep(getRandomNum())
                GPIO.output(arm_one, False)
                time.sleep(getRandomNum())
                GPIO.output(arm_one, True)
                GPIO.output(arm_two, False)
                time.sleep(getRandomNum())
                GPIO.output(arm_two, True)

            pygame.mixer.music.stop()

            # Record previous state
            previous_state = 1

        elif current_state == 0 and previous_state == 1:
            # PIR has returned to ready state
            print("  Ready")
            GPIO.output(arm_one, True)
            GPIO.output(arm_two, True)
            previous_state = 0

        # Wait for 10 milliseconds
        time.sleep(0.01)

except KeyboardInterrupt:
    print("  You've tricked " + str(counter) + " people")
    halloweenlog = open("halloweenlog.txt", "a")
    halloweenlog.write("You've spooked " + str(counter) + " on this run!\n")
    halloweenlog.close()
    print("  Quit")
    # Reset GPIO settings
    GPIO.cleanup()
