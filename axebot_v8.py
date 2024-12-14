import pygame
import numpy as np

class Robot:
    def __init__(self, position, orientation, L, wheel_angles, color):
        self.position = np.array(position, dtype=float)
        self.orientation = orientation  # radians
        self.L = L  # Distance from center to each wheel
        self.wheel_angles = np.radians(wheel_angles)
        self.color = color
        self.font = pygame.font.Font(None, 30)

    def get_transformation_matrix(self):
        return np.array([
            [np.sin(self.wheel_angles[0]), -np.cos(self.wheel_angles[0]), -self.L],
            [np.sin(self.wheel_angles[1]), -np.cos(self.wheel_angles[1]), -self.L],
            [np.sin(self.wheel_angles[2]), -np.cos(self.wheel_angles[2]), -self.L]
        ])

    def calculate_wheel_speeds(self, vx, vy, omega):
        V = np.array([vx, vy, omega])
        T = self.get_transformation_matrix()
        return np.linalg.inv(T) @ V

    def calculate_robot_velocity(self, q1, q2, q3):
        T = self.get_transformation_matrix()
        wheel_speeds = np.array([q1, q2, q3])
        return T @ wheel_speeds

    def update(self, vx, vy, omega, dt):
        self.position += np.array([vx, vy]) * dt * 100  # Scale for visual purposes
        self.orientation += omega * dt

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, self.position.astype(int), 20)

        for angle in self.wheel_angles:
            wheel_x = self.position[0] + self.L * np.cos(angle + self.orientation)
            wheel_y = self.position[1] + self.L * np.sin(angle + self.orientation)

            # Create a wheel surface
            wheel_surface = pygame.Surface((40, 10), pygame.SRCALPHA)
            wheel_surface.fill((0, 0, 0))

            # Rotate the wheel surface
            wheel_angle_degrees = np.degrees(angle + self.orientation) + 90
            rotated_wheel = pygame.transform.rotate(wheel_surface, -wheel_angle_degrees)

            # Update the rectangle to center the rotated surface
            wheel_rect = rotated_wheel.get_rect(center=(wheel_x, wheel_y))

            # Blit the rotated wheel onto the screen
            screen.blit(rotated_wheel, wheel_rect)

    def render_status(self, screen, q1, q2, q3):
        orientation_deg = (np.degrees(self.orientation) % 360 + 360) % 360
        text_lines = [
            f"Wheel q1 Speed: {q1:.2f} m/s",
            f"Wheel q2 Speed: {q2:.2f} m/s",
            f"Wheel q3 Speed: {q3:.2f} m/s",
            f"Orientation (degrees): {(360 - orientation_deg) % 360:.2f}"
        ]

        for i, line in enumerate(text_lines):
            text_surface = self.font.render(line, True, (255, 255, 255))
            screen.blit(text_surface, (10, 10 + i * 30))


class Simulation:
    def __init__(self, width, height):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Axebot Simulation")
        self.clock = pygame.time.Clock()
        self.running = True
        self.FPS = 60
        self.dt = 0.1  # Time step in seconds
        self.robot = Robot(
            position=[width // 2, height // 2],
            orientation=0,
            L=85,
            wheel_angles=[90, -30, -150],
            color=(100, 150, 255)
        )
        self.BASE_SPEED = 0.5
        self.MAX_SPEED_RATIO = 6

    def handle_input(self):
        keys = pygame.key.get_pressed()
        forward_speed = 0
        sideways_speed = 0
        desired_omega = 0

        if keys[pygame.K_UP]:
            sideways_speed = self.BASE_SPEED
        elif keys[pygame.K_DOWN]:
            sideways_speed = -self.BASE_SPEED
        elif keys[pygame.K_9]:
            sideways_speed = self.BASE_SPEED * self.MAX_SPEED_RATIO

        if keys[pygame.K_LEFT]:
            forward_speed = self.BASE_SPEED
        elif keys[pygame.K_RIGHT]:
            forward_speed = -self.BASE_SPEED

        if keys[pygame.K_q]:
            desired_omega = -0.5
        elif keys[pygame.K_e]:
            desired_omega = 0.5

        desired_vx = -forward_speed * np.cos(self.robot.orientation) + sideways_speed * np.sin(self.robot.orientation)
        desired_vy = -forward_speed * np.sin(self.robot.orientation) - sideways_speed * np.cos(self.robot.orientation)

        return desired_vx, desired_vy, desired_omega

    def run(self):
        while self.running:
            self.screen.fill((86, 125, 70))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            # Handle input and compute desired velocities
            desired_vx, desired_vy, desired_omega = self.handle_input()

            # Calculate wheel speeds
            q1, q2, q3 = self.robot.calculate_wheel_speeds(desired_vx, desired_vy, desired_omega)

            # Calculate resulting robot velocity from wheel speeds
            vx, vy, omega = self.robot.calculate_robot_velocity(q1, q2, q3)

            # Update robot state
            self.robot.update(vx, vy, omega, self.dt)

            # Draw the robot and render its status
            self.robot.draw(self.screen)
            self.robot.render_status(self.screen, q1, q2, q3)

            pygame.display.flip()
            self.clock.tick(self.FPS)

        pygame.quit()


if __name__ == "__main__":
    sim = Simulation(1280, 720)
    sim.run()
