import pygame
import time
import serial


import serial
import serial.tools.list_ports

BAUD = 115200
tilt_factor = 200

#Auto detect TTL ports
def detect_ft232_ports():
    ports = list(serial.tools.list_ports.comports())
    ttl_ports = []

    for p in ports:
        print(f"Found: {p.device} | {p.description} | VID:{p.vid} PID:{p.pid}")

        # FT232RL common identifiers
        if (
            "FT232" in p.description
            or "FTDI" in p.description
            or (p.vid == 0x0403 and p.pid == 0x6001)
        ):
            ttl_ports.append(p.device)

    return ttl_ports


# Detect ports
ttl_ports = detect_ft232_ports()

if len(ttl_ports) < 2:
    print("❌ Could not detect two FT232 TTL ports.")
    exit()

print("✅ Using ports:", ttl_ports)

ser1 = serial.Serial(ttl_ports[0], BAUD)
ser2 = serial.Serial(ttl_ports[1], BAUD)
pygame.init()
pygame.joystick.init()

if pygame.joystick.get_count() == 0:
    print("No controller detected")
    quit()

js = pygame.joystick.Joystick(0)
js.init()

deadzone = 0.8

def map_1000_2000(value):
    # value = -value
    return int(1500 + value * 500)

def normalize_trigger(value):
    return (value + 1) / 2

# MAIN LOOP 
while True:

    first_line = ser1.readline().decode("utf-8", errors="ignore").strip()
    second_line = ser2.readline().decode("utf-8", errors="ignore").strip()

    print(f"Voltage = {second_line}")

    if "Yaw" in first_line:
        try:
            data = line.split(":")[-1].split(",")

            if len(data) < 5:
                continue

            yaw  = float(data[0])
            pitch = float(data[1])
            roll = float(data[2])
            temp = float(data[3])
            volt = float(data[4])
            leak = float(data[5])

            output = ("Yaw:", yaw,
                  "Pitch:", pitch,
                  "Roll:", roll,
                  "Temp:", temp,
                  "Voltage:", volt,
                  "Leak:", leak)
          

            print(output, end='\r', flush=True)

        except Exception as e:
            print("Bad packet:", line)
    pygame.event.pump()

    # RL motors (stick X axes) 
    left_x = js.get_axis(2)
    right_x = js.get_axis(0)

    if left_x > deadzone:
        RL1 = 1
    elif left_x < -deadzone:
        RL1 = -1
    else:
        RL1 = 0

    if right_x > deadzone:
        RL2 = 1
    elif right_x < -deadzone:
        RL2 = -1
    else:
        RL2 = 0

    #ESCFB motors (stick Y axes) 
    left_y = js.get_axis(3)
    right_y = js.get_axis(1)

    ESCFB1 = map_1000_2000(left_y)
    ESCFB2 = map_1000_2000(right_y)

    # ----- ESCUP (rear triggers) -----
    left_trigger = normalize_trigger(js.get_axis(4))
    right_trigger = normalize_trigger(js.get_axis(5))
    if left_trigger > 0.01 and right_trigger < 0.01:
        ESCUP1 = int(1500 - left_trigger * 500)
        ESCUP2 = int(1500 + left_trigger * 500)
    elif right_trigger > 0.01 and left_trigger < 0.01:
        ESCUP1 = int(1500 + right_trigger * 500)
        ESCUP2 = int(1500 - right_trigger * 500)
    else:
        ESCUP1 = ESCUP2 = 1500

    #Tilt scaling via buttons 
    if(ESCUP1 != 1500 and ESCUP2 != 1500):
        if js.get_button(0):  # X button → tilt forward
            ESCUP1 = int((1500 + (ESCUP1 - 1500)) + tilt_factor)
            ESCUP2 = int((1500 + (ESCUP2 - 1500)) + tilt_factor)
        if js.get_button(1):  # O button → tilt backward
            ESCUP1 = int((1500 + (ESCUP1 - 1500)) - tilt_factor)
            ESCUP2 = int((1500 + (ESCUP2 - 1500)) - tilt_factor)

    # constrain ESC values
    ESCUP1 = max(1000, min(2000, ESCUP1))
    ESCUP2 = max(1000, min(2000, ESCUP2))

    # ARM (L1/R1)
    ARM = 0
    if js.get_button(4):  # L1
        ARM = 1
    if js.get_button(5):  # R1
        ARM = -1

    print(f"ARM value = {ARM}")
    # FORK (DPAD X) 
    hat_x, hat_y = js.get_hat(0)  # D-pad
    FORK = hat_x  # -1 = left, 0 = neutral, 1 = right

    # ----- Build packets -----
    packet1 = f"{ARM} {RL1} 0 {ESCUP1} {ESCFB1} # {FORK} {RL2} 0 {ESCUP2} {ESCFB2}\n"

    # Send packets over UART
    ser1.write(packet1.encode())
    ser2.write(packet1.encode())

    # ----- Print for debugging -----
    # print(packet1)

    time.sleep(0.15)
