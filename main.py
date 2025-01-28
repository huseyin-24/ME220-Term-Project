from machine import Pin, PWM
import utime

# Define motor control pins
motor1_pin1 = Pin(6, Pin.OUT)  # Motor 1 input 1
motor1_pin2 = Pin(7, Pin.OUT)  # Motor 1 input 2
motor1_enable = Pin(8, Pin.OUT)  # Motor 1 enable pin

motor2_pin1 = Pin(4, Pin.OUT)  # Motor 2 input 1
motor2_pin2 = Pin(3, Pin.OUT)  # Motor 2 input 2
motor2_enable = Pin(2, Pin.OUT)  # Motor 2 enable pin

# Enable both motors
motor1_enable.high()
motor2_enable.high()

# Define ultrasonic sensor pins
trigger_pin = Pin(21, Pin.OUT)  # Trigger pin for ultrasonic sensor
echo_pin = Pin(20, Pin.IN)  # Echo pin for ultrasonic sensor

# Define PWM pins for main motor and trigger motor
main_motor_pwm = PWM(Pin(14))
main_motor_pwm.freq(50)  # Set PWM frequency to 50Hz

trigger_motor_pwm = PWM(Pin(15))
trigger_motor_pwm.freq(50)  # Set PWM frequency to 50Hz

# Global variables to store bottle positions and distances
bottles = []
order_list = []
bottle_positions = []
bottle_distances = []

def translate(value, left_min, left_max, right_min, right_max):
    """
    Translate a value from one range to another.
    For example, convert a value from 1500-7500 to 0-180.
    """
    left_span = left_max - left_min
    right_span = right_max - right_min
    value_scaled = float(value - left_min) / float(left_span)
    return right_min + (value_scaled * right_span)

def motors_on():
    """Turn on both motors."""
    motor1_pin1.high()
    motor1_pin2.low()
    motor2_pin1.high()
    motor2_pin2.low()

def motors_off():
    """Turn off both motors."""
    motor1_pin1.low()
    motor1_pin2.low()
    motor2_pin1.low()
    motor2_pin2.low()

def ultrasonic_distance():
    """
    Measure distance using the ultrasonic sensor.
    Returns the distance in centimeters.
    """
    trigger_pin.low()
    utime.sleep_us(2)
    trigger_pin.high()
    utime.sleep_us(5)
    trigger_pin.low()

    while echo_pin.value() == 0:
        signal_off = utime.ticks_us()
    while echo_pin.value() == 1:
        signal_on = utime.ticks_us()

    time_passed = signal_on - signal_off
    distance = (time_passed * 0.0343) / 2  # Calculate distance in cm
    return distance

def average(lst):
    """Calculate the average of a list of numbers."""
    return sum(lst) / len(lst)

def cluster(data, max_gap):
    """
    Cluster data points into groups based on a maximum gap.
    Returns the average of each cluster.
    """
    data.sort()
    groups = [[data[0]]]
    for x in data[1:]:
        if abs(x - groups[-1][-1]) <= max_gap:
            groups[-1].append(x)
        else:
            groups.append([x])
    return [average(group) for group in groups]

def turn_motor(position):
    """Turn the main motor to a specific position."""
    main_motor_pwm.duty_u16(position)
    utime.sleep(0.1)

def smooth_turn(old_position, new_position):
    """
    Smoothly turn the motor from the old position to the new position.
    Adjusts the position in increments of 50 for smooth movement.
    """
    while ((new_position - old_position) % 50) != 0:
        new_position += 1
    if new_position > old_position:
        for pos in range(old_position, new_position, 50):
            main_motor_pwm.duty_u16(pos)
            utime.sleep(0.05)
    elif new_position < old_position:
        new_position -= 400
        for pos in range(new_position, old_position, 50):
            main_motor_pwm.duty_u16(new_position + old_position - pos)
            utime.sleep(0.05)

def shoot():
    """Trigger the shooting mechanism."""
    trigger_motor_pwm.duty_u16(1500)
    utime.sleep(0.105)
    trigger_motor_pwm.duty_u16(4500)

def initialize():
    """Initialize the system by centering the motor and turning off motors."""
    turn_motor(1500)
    utime.sleep(1)
    motors_off()
    trigger_motor_pwm.duty_u16(4500)

def scan_for_bottles():
    """Scan for bottles by rotating the motor and measuring distances."""
    bottles = []
    for pos in range(1500, 7500, 50):
        turn_motor(pos)
        angle = int(translate(pos, 1500, 7500, 0, 180))
        distance = ultrasonic_distance()
        bottles.append((pos, angle, distance))
        utime.sleep(0.01)
    return bottles

def find_bottle_locations(scan_data):
    """Find the positions of bottles from the scan data."""
    for data_point in scan_data:
        if 8 < data_point[2] < 16:  # Filter distances between 8cm and 16cm
            bottle_positions.append(data_point[0])
            bottle_distances.append(data_point[2])
    return cluster(bottle_positions, 500)

def test_sequence_1(order):
    """Test sequence 1: Move to predefined angles and shoot."""
    initialize()
    angles = [45, 92, 140]
    for num in order:
        order_list.append(int(num))
    
    old_position = 1500
    for order in order_list:
        angle = angles[order - 1]
        new_position = int(translate(angle, 0, 180, 1500, 7500))
        new_position = (new_position // 50) * 50  # Round to nearest 50
        smooth_turn(old_position, new_position)
        old_position = new_position
        utime.sleep(0.5)
        motors_on()
        utime.sleep(0.5)
        shoot()
        utime.sleep(1)
        motors_off()

def test_sequence_2():
    """Test sequence 2: Scan for bottles and print their locations."""
    initialize()
    bottles = scan_for_bottles()
    bottle_locations = find_bottle_locations(bottles)
    print("Bottle locations:", bottle_locations)
    print("Number of bottles found:", len(bottle_locations))

def test_sequence_3(order):
    """Test sequence 3: Move to detected bottle locations and shoot."""
    initialize()
    bottles = scan_for_bottles()
    bottle_locations = find_bottle_locations(bottles)
    
    for num in order:
        order_list.append(int(num))
    
    smooth_turn(7500, 1500)  # Reset motor position
    old_position = 1500
    for order in order_list:
        target_position = bottle_locations[order - 1]
        target_position = (target_position // 50) * 50  # Round to nearest 50
        smooth_turn(old_position, target_position - 100)
        old_position = target_position - 100
        utime.sleep(0.5)
        motors_on()
        utime.sleep(0.5)
        shoot()
        utime.sleep(1)
        motors_off()

def test_sequence_4(order):
    """Test sequence 4: Similar to sequence 3 but with a smaller cluster gap."""
    initialize()
    bottles = scan_for_bottles()
    bottle_locations = find_bottle_locations(bottles)
    
    for num in order:
        order_list.append(int(num))
    
    smooth_turn(7500, 1500)  # Reset motor position
    old_position = 1500
    for order in order_list:
        target_position = bottle_locations[order - 1]
        target_position = (target_position // 50) * 50  # Round to nearest 50
        smooth_turn(old_position, target_position - 100)
        old_position = target_position - 100
        utime.sleep(0.5)
        motors_on()
        utime.sleep(0.5)
        shoot()
        utime.sleep(1)
        motors_off()

# Main execution
initialize()
shoot_order_1 = input("Please enter the order for Test 1: ")
test_sequence_1(shoot_order_1)

initialize()
input("WAITING...")  # Pause for user input

test_sequence_2()

initialize()
shoot_order_3 = input("Please enter the order for Test 3: ")
test_sequence_3(shoot_order_3)

initialize()
input("WAITING...")  # Pause for user input

initialize()
shoot_order_4 = input("Please enter the order for Test 4: ")
test_sequence_4(shoot_order_4)