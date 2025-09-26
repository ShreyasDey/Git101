# main.py
from machine import Pin, PWM # type: ignore
import math

# Our custom module
import web_server  # type: ignore

SSID = "QuadDrive"
PASSWORD = "39250000"

# === Motor Pins ===
ENA = PWM(Pin(8))
ENB = PWM(Pin(9))
IN1 = Pin(10, Pin.OUT)
IN2 = Pin(11, Pin.OUT)
IN3 = Pin(12, Pin.OUT)
IN4 = Pin(13, Pin.OUT)

ENA.freq(1000)
ENB.freq(1000)

# === Global State ===
cmd = 0
spd = 0

# === Thresholds ===
ANGLE_DEADBAND = 10
MAX_TILT = 45

# WRITE YOUR CODE IN THIS FUNCTION
def updateMotorControl(gx, gy, gz):
    global cmd, spd

    # ----------- IMU CONTROL ------------
    angle_x = math.degrees(math.atan2(gx, math.sqrt(gy*gy + gz*gz)))
    angle_y = math.degrees(math.atan2(gy, math.sqrt(gx*gx + gz*gz)))

    cmd = 0
    spd = 0

    if abs(angle_y) > abs(angle_x):
        if angle_y > ANGLE_DEADBAND:
            cmd = 1   # forward
            spd = int((min(angle_y, MAX_TILT) / MAX_TILT) * 65535)
        elif angle_y < -ANGLE_DEADBAND:
            cmd = 2   # backward
            spd = int((min(abs(angle_y), MAX_TILT) / MAX_TILT) * 65535)
    else:
        if angle_x > ANGLE_DEADBAND:
            cmd = 3   # right
            spd = int((min(angle_x, MAX_TILT) / MAX_TILT) * 65535)
        elif angle_x < -ANGLE_DEADBAND:
            cmd = 4   # left
            spd = int((min(abs(angle_x), MAX_TILT) / MAX_TILT) * 65535)

    applyMotorControl()


# WRITE YOUR CODE IN THIS FUNCTION
def applyMotorControl():
    global spd, cmd
    if cmd == 1:  # Forward
        IN1.value(1); IN2.value(0)
        IN3.value(1); IN4.value(0)
    elif cmd == 2:  # Backward
        IN1.value(0); IN2.value(1)
        IN3.value(0); IN4.value(1)
    elif cmd == 3:  # Right
        IN1.value(1); IN2.value(0)
        IN3.value(0); IN4.value(1)
    elif cmd == 4:  # Left
        IN1.value(0); IN2.value(1)
        IN3.value(1); IN4.value(0)
    else:  # Stop
        IN1.value(0); IN2.value(0)
        IN3.value(0); IN4.value(0)
        spd = 0

    ENA.duty_u16(spd)
    ENB.duty_u16(spd)


# === Main Program ===
if __name__ == "__main__":
    web_server.on_data_received = updateMotorControl
    web_server.setup_ap(ssid=SSID, password=PASSWORD)
    web_server.start_server(port=80)
