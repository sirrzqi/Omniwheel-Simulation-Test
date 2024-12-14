import pygame
import numpy as np

pygame.init()

# Screen setup
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Axebot")

# Colors
GRASS = (86, 125, 70)
BLACK = (0, 0, 0)
ROBOT_COLOR = (100, 150, 255)
TEXT_COLOR = (255, 255, 255)

# Font setup
font = pygame.font.Font(None, 30)

# Robot parameters
L = 85  # Distance from the center of the robot to each wheel in pixels
wheel_angles = np.radians([90, -30, -150])
robot_position = np.array([WIDTH // 2, HEIGHT // 2], dtype=float)  # Initial position
robot_orientation = 0  # Initial orientation of the robot (radians)

# Desired robot velocities (initial)
desired_vx = 0  # m/s (forward speed)
desired_vy = 0  # m/s (sideways speed)
desired_omega = 0  # rad/s (rotational speed)

# Transformation matrix from robot frame to wheel speeds
def get_transformation_matrix():
    return np.array([
        [np.sin(wheel_angles[0]), -np.cos(wheel_angles[0]), -L],
        [np.sin(wheel_angles[1]), -np.cos(wheel_angles[1]), -L],
        [np.sin(wheel_angles[2]), -np.cos(wheel_angles[2]), -L]
    ])

# Inverse kinematics to calculate wheel speeds from desired robot velocity
def calculate_wheel_speeds(vx, vy, omega):
    V = np.array([vx, vy, omega])
    T = get_transformation_matrix()
    wheel_speeds = np.linalg.inv(T) @ V
    return wheel_speeds

# Forward kinematics to calculate robot velocity from wheel speeds
def calculate_robot_velocity(q1, q2, q3):
    T = get_transformation_matrix()
    wheel_speeds = np.array([q1, q2, q3])
    robot_velocity = T @ wheel_speeds
    return robot_velocity

# Simulation parameters
clock = pygame.time.Clock()
FPS = 60
dt = 0.1  # time step (seconds)

# Define base speed and max speed ratio
BASE_SPEED = 0.5
MAX_SPEED_RATIO = 6

running = True
while running:
    screen.fill(GRASS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Key press detection for controlling the robot's desired velocity
    keys = pygame.key.get_pressed()
    forward_speed = 0
    sideways_speed = 0

    if keys[pygame.K_UP]:
        sideways_speed = BASE_SPEED
    elif keys[pygame.K_DOWN]:
        sideways_speed = -BASE_SPEED
    elif keys[pygame.K_9]:  # Maximum speed when "9" is pressed
        sideways_speed = BASE_SPEED * MAX_SPEED_RATIO

    if keys[pygame.K_LEFT]:
        forward_speed = BASE_SPEED
    elif keys[pygame.K_RIGHT]:
        forward_speed = -BASE_SPEED

    if keys[pygame.K_q]:
        desired_omega = -0.5
    elif keys[pygame.K_e]:
        desired_omega = 0.5
    else:
        desired_omega = 0

    # Convert local forward/sideways speeds to global vx, vy based on robot's orientation
    desired_vx = -forward_speed * np.cos(robot_orientation) + sideways_speed * np.sin(robot_orientation)
    desired_vy = -forward_speed * np.sin(robot_orientation) - sideways_speed * np.cos(robot_orientation)

    # Calculate wheel speeds
    q1, q2, q3 = calculate_wheel_speeds(desired_vx, desired_vy, desired_omega)

    # Calculate resulting robot velocity from wheel speeds
    vx, vy, omega = calculate_robot_velocity(q1, q2, q3)

    # Update robot position and orientation
    robot_position += np.array([vx, vy]) * dt * 100  # Scale for visual purposes
    robot_orientation += omega * dt

    # Convert robot orientation to degrees (0-360° range)
    robot_orientation_deg = (np.degrees(robot_orientation) % 360 + 360) % 360
    orientation_text = f"Orientation (degrees): {(360 - robot_orientation_deg) % 360:.2f}"

    # Render wheel speeds and orientation text to the screen
    q_text = [
        f"Wheel q1 Speed: {q1:.2f} m/s",
        f"Wheel q2 Speed: {q2:.2f} m/s",
        f"Wheel q3 Speed: {q3:.2f} m/s",
        f"{orientation_text}"
    ]

    for i, line in enumerate(q_text):
        text_surface = font.render(line, True, TEXT_COLOR)
        screen.blit(text_surface, (10, 10 + i * 30))

    # Draw the robot (circle for simplicity)
    pygame.draw.circle(screen, ROBOT_COLOR, robot_position.astype(int), 20)

    # Draw the wheels as rectangles
    wheel_length = 40
    wheel_width = 10

    for angle in wheel_angles:
        wheel_x = robot_position[0] + L * np.cos(angle + robot_orientation)
        wheel_y = robot_position[1] + L * np.sin(angle + robot_orientation)

        # Create a wheel surface
        wheel_surface = pygame.Surface((wheel_length, wheel_width), pygame.SRCALPHA)
        wheel_surface.fill(BLACK)

        # Rotate the wheel surface
        wheel_angle_degrees = np.degrees(angle + robot_orientation) + 90
        rotated_wheel = pygame.transform.rotate(wheel_surface, -wheel_angle_degrees)

        # Update the rectangle to center the rotated surface
        wheel_rect = rotated_wheel.get_rect(center=(wheel_x, wheel_y))

        # Blit the rotated wheel onto the screen
        screen.blit(rotated_wheel, wheel_rect)

    # Update display and tick the clock
    pygame.display.flip()
    clock.tick(FPS)

# Quit pygame
pygame.quit()