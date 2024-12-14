import pygame
import numpy as np

pygame.init()

WIDTH, HEIGHT = 800, 600
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
L = 50  # Distance from the center of the robot to each wheel in pixels
wheel_angles = np.radians([90, -150, -30])  
robot_position = np.array([WIDTH // 2, HEIGHT // 2], dtype=float)  # Initial position
robot_orientation = 0  # Initial orientation of the robot (radians)

# Desired robot velocities (initial)
desired_vx = 0  # m/s (forward speed)
desired_vy = 0  # m/s (sideways speed)
desired_omega = 0  # rad/s (rotational speed)

# Transformation matrix from robot frame to wheel speeds
def get_transformation_matrix():
    return np.array([
        [np.sin(wheel_angles[0] + np.pi/2), -np.cos(wheel_angles[0] + np.pi/2), -L],
        [np.sin(wheel_angles[1] + np.pi/2), -np.cos(wheel_angles[1] + np.pi/2), -L],
        [np.sin(wheel_angles[2] + np.pi/2), -np.cos(wheel_angles[2] + np.pi/2), -L]
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

running = True
while running:
    screen.fill(GRASS)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Key press detection for controlling the robot's desired velocity
    keys = pygame.key.get_pressed()
    forward_speed = 0
    sideways_speed = 0

    # Adjust the speed based on key input, relative to the robot's orientation
    if keys[pygame.K_UP]:
        sideways_speed = 0.5  # Move forward relative to robot
    elif keys[pygame.K_DOWN]:
        sideways_speed = -0.5  # Move backward relative to robot

    if keys[pygame.K_LEFT]:
        forward_speed = 0.5  # Move left relative to robot
    elif keys[pygame.K_RIGHT]:
        forward_speed = -0.5   # Move right relative to robot

    if keys[pygame.K_q]:   # Rotate counterclockwise
        desired_omega = -0.5
    elif keys[pygame.K_e]: # Rotate clockwise
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
    robot_orientation_deg = (np.degrees(robot_orientation) % 360 + 360) % 360  # Ensures 0-360 range
    orientation_text = f"Orientation (degrees): {(360 - robot_orientation_deg) % 360:.2f}"
    
    # Render wheel speeds and orientation text to the screen
    q_text = [
        f"Wheel q1 Speed: {q1:.2f} m/s",
        f"Wheel q2 Speed: {q2:.2f} m/s",
        f"Wheel q3 Speed: {q3:.2f} m/s",
        f"{orientation_text}"
    ]
    
    # Draw each line of text on the screen
    for i, line in enumerate(q_text):
        text_surface = font.render(line, True, TEXT_COLOR)
        screen.blit(text_surface, (10, 10 + i * 30))  # Adjust y-position for each line

    # Draw the robot (circle for simplicity)
    pygame.draw.circle(screen, ROBOT_COLOR, robot_position.astype(int), 20)

    # Draw the wheels as small circles around the robot
    for angle in wheel_angles:
        wheel_x = robot_position[0] + L * np.cos(angle + robot_orientation)
        wheel_y = robot_position[1] + L * np.sin(angle + robot_orientation)
        pygame.draw.circle(screen, BLACK, (int(wheel_x), int(wheel_y)), 5)

    # Update display and tick the clock
    pygame.display.flip()
    clock.tick(FPS)

# Quit pygame
pygame.quit()
