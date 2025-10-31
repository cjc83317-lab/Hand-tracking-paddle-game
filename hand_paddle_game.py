import cv2
import mediapipe as mp
import pygame
import time
import threading

# 🎮 Pygame setup
pygame.init()
WIDTH, HEIGHT = 640, 480
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hand-Controlled Paddle Game")
clock = pygame.time.Clock()

# 🧱 Game objects
paddle_width, paddle_height = 100, 20
paddle_y = HEIGHT - 40
ball_radius = 10
ball_x, ball_y = WIDTH // 2, HEIGHT // 2
ball_dx, ball_dy = 4, -4

# 🖐️ Hand tracking setup
cap = cv2.VideoCapture(0)
mpHands = mp.solutions.hands
hands = mpHands.Hands(False)
mpDraw = mp.solutions.drawing_utils

finger_x = WIDTH // 2  # Default paddle position

# 🧮 Score and game state
score = 0
font = pygame.font.SysFont("Arial", 36)
lose_font = pygame.font.SysFont("Arial", 48)
game_state = "playing"

def track_hand():
    global finger_x
    while True:
        success, img = cap.read()
        if not success:
            continue

        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(imgRGB)

        if results.multi_hand_landmarks:
            for handLms in results.multi_hand_landmarks:
                h, w, c = img.shape
                index_tip = handLms.landmark[8]  # Index finger tip
                finger_x = int(index_tip.x * WIDTH)

        cv2.imshow("Hand Tracking", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# 🧠 Start hand tracking in a separate thread
threading.Thread(target=track_hand, daemon=True).start()

# 🎮 Game loop
running = True
while running:
    screen.fill((30, 30, 30))

    if game_state == "playing":
        # Paddle position
        paddle_x = max(0, min(WIDTH - paddle_width, finger_x - paddle_width // 2))
        paddle_rect = pygame.Rect(paddle_x, paddle_y, paddle_width, paddle_height)
        pygame.draw.rect(screen, (0, 255, 0), paddle_rect)

        # Ball movement
        ball_x += ball_dx
        ball_y += ball_dy

        # Ball collision with walls
        if ball_x <= 0 or ball_x >= WIDTH:
            ball_dx *= -1
        if ball_y <= 0:
            ball_dy *= -1

        # Ball collision with paddle
        if paddle_rect.collidepoint(ball_x, ball_y + ball_radius):
            ball_dy *= -1
            score += 1

        # Ball out of bounds
        if ball_y > HEIGHT:
            game_state = "lost"

        # Draw ball
        pygame.draw.circle(screen, (255, 0, 0), (ball_x, ball_y), ball_radius)

        # Draw score
        score_text = font.render(f"Score: {score}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))

    elif game_state == "lost":
        lose_text = lose_font.render("You Lose", True, (255, 0, 0))
        retry_text = font.render("Press R to try again or ESC to exit", True, (255, 255, 255))
        screen.blit(lose_text, (WIDTH // 2 - 100, HEIGHT // 2 - 60))
        screen.blit(retry_text, (WIDTH // 2 - 180, HEIGHT // 2))

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and game_state == "lost":
            if event.key == pygame.K_r:
                # Reset game
                ball_x, ball_y = WIDTH // 2, HEIGHT // 2
                ball_dy = -4
                score = 0
                game_state = "playing"
            elif event.key == pygame.K_ESCAPE:
                running = False

    pygame.display.update()
    clock.tick(60)

# 🧹 Cleanup
cap.release()
cv2.destroyAllWindows()
pygame.quit()