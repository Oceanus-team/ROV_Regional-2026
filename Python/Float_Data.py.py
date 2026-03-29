import serial
import time
import matplotlib.pyplot as plt

PORT = "COM8"   #Bluetooth COM port
BAUD = 9600

ser = serial.Serial(PORT, BAUD, timeout=1)
time.sleep(2)

# SEND COMMAND 'S'
ser.write(b'S')
print("Sent S command")


time_data = []
depth_data = []

# WAIT FOR DATA START
while True:
    line = ser.readline().decode(errors='ignore').strip()
    print("WAIT:", line)

    if line == "DATA START":
        print("Receiving data...")
        break

# RECEIVE DATA
while True:
    line = ser.readline().decode(errors='ignore').strip()

    if line == "DATA END":
        print("Done receiving")
        break

    try:
        t, d = line.split(',')

        # convert time (0.1s → seconds)
        time_data.append(int(t) * 0.1)

        # raw depth
        depth_data.append(int(d))

        print("DATA:", t, d)

    except:
        print("BAD:", line)

ser.close()

# DRAW GRAPH
plt.plot(time_data, depth_data)

plt.xlabel("Time (s)")
plt.ylabel("Depth (RAW)")
plt.title("Float Profile")

plt.gca().invert_yaxis()

plt.grid()

plt.show()