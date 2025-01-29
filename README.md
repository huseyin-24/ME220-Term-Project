## ME220-Term-Project
### Sophomore year project. 
<p float="left">
  <img src="https://github.com/user-attachments/assets/42528b15-ece5-45b5-a60b-71cb3e9504b2" width="300" />
  <img src="https://github.com/user-attachments/assets/986fe32d-6da0-412f-923c-4a15b51cd5f8" width="401" /> 
</p>
<p align="center">The team and robot</p>
This repository documents the term project for ME220: Introduction to Mechatronics, a course offered in Fall 2022 at Middle East Technical University (METU). The project involved designing and building a robot capable of knocking over water bottles arranged randomly in a circular pattern. The robot was required to knock the bottles in a specific order provided by the instructor.
The robot was constructed using scrap materials, with the exception of the Raspberry Pi Pico microcontroller board and basic electronic components.

## How It Works
The Python script running on the Raspberry Pi Pico implements the following logic:
- The robot rotates to scan the area using ultrasonic sensor.
- If a bottle is detected within a specific distance range, its position is recorded.
- After completing the scan, the robot clusters the detected positions.
- The robot moves to each stored position in the specified order and knocks over the bottle using 2 mechanical mechanism:
    - Release one ball using servo motor
    - Throw away the ball using DC motor.

Watch the video below to see how it behaves: 

https://github.com/user-attachments/assets/13ac98d8-1b2a-4084-8208-5e3614e42f30


