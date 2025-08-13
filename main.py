import pygame
import random
import os
import time

pygame.init()

screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("떨어지는 정답 찾기")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

font = pygame.font.Font("fonts/Pinkfong Baby Shark Font_ Bold.ttf", 36)


score = 0
goal = 100

correct_path = "images/correct"
wrong_path = "images/wrong"

image_scale = 0.6
falling_speed = 0.5

def load_and_scale_image(path, scale):
    try:
        img = pygame.image.load(path).convert_alpha()
        size = round(img.get_width() * scale), round(img.get_height() * scale)
        return pygame.transform.scale(img, size)
    except pygame.error as e:
        return None

def load_images(correct_dir, wrong_dir, scale):
    correct_images = [load_and_scale_image(os.path.join(correct_dir, f), scale) for f in os.listdir(correct_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')) and os.path.isfile(os.path.join(correct_dir, f))]
    wrong_images = [load_and_scale_image(os.path.join(wrong_dir, f), scale) for f in os.listdir(wrong_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')) and os.path.isfile(os.path.join(wrong_dir, f))]
    return [img for img in correct_images if img is not None], [img for img in wrong_images if img is not None]

correct_loaded_images, wrong_loaded_images = load_images(correct_path, wrong_path, image_scale)

game_state = "playing"
falling_items = []
falling_items_data = {}
next_id = 0

def create_falling_items():
    global falling_items, falling_items_data, next_id
    falling_items = []
    falling_items_data = {}
    next_id = 0
    
    if not correct_loaded_images or not wrong_loaded_images:
        return False
    
    correct_img = random.choice(correct_loaded_images)
    correct_x = random.randint(50, screen_width - 50 - correct_img.get_width())
    rect = correct_img.get_rect(topleft=(correct_x, -correct_img.get_height()))
    falling_items.append({"id": next_id, "label": "correct", "img": correct_img, "rect": rect})
    falling_items_data[next_id] = float(rect.y)
    next_id += 1

    num_wrong = 3
    wrong_selections = random.sample(wrong_loaded_images, min(num_wrong, len(wrong_loaded_images)))
    for img in wrong_selections:
        wrong_x = random.randint(50, screen_width - 50 - img.get_width())
        rect = img.get_rect(topleft=(wrong_x, random.randint(-500, -50 - img.get_height())))
        falling_items.append({"id": next_id, "label": "wrong", "img": img, "rect": rect})
        falling_items_data[next_id] = float(rect.y)
        next_id += 1
    
    return True

if not create_falling_items():
    running = False

running = True
st = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN and game_state == "playing":
            if event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                for item in falling_items:
                    if item["rect"].collidepoint(mouse_pos):
                        if item["label"] == "correct":
                            score += 20
                        else:
                            score -= 5
                        create_falling_items()
                        break

    if game_state == "playing":
        if st :
            start = time.time()
            st = False
        should_create_new_items = False
        for item in falling_items:
            item_id = item["id"]
            if item_id in falling_items_data:
                falling_items_data[item_id] += falling_speed
                item["rect"].y = int(falling_items_data[item_id])

            if item["rect"].top > screen_height:
                should_create_new_items = True
                break

        if should_create_new_items:
            create_falling_items()
        end = time.time()
        if end-start > 60 :
            game_state = "game_over"
            game_result_text = "게임 오버... 1분 시간제한이 끝났습니다."

    if score >= goal and game_state == "playing":
        game_state = "game_over"
        game_result_text = f"게임 승리!    지난 시간: {(end-start):.2f}초"
    elif score < -10 and game_state == "playing":
        game_state = "game_over"
        game_result_text = "게임 오버... 점수가 -10점 미만입니다."

    if game_state == "game_over" and event.type == pygame.KEYDOWN:
        if event.key == pygame.K_r:
            score = 0
            game_state = "playing"
            create_falling_items()
            st = True

    screen.fill(WHITE)

    if game_state == "playing":
        for item in falling_items:
            screen.blit(item["img"], item["rect"])

        score_text = font.render(f"점수: {score}     지난 시간: {(end-start):.2f}초", True, BLACK)
        screen.blit(score_text, (10, 10))
    elif game_state == "game_over":
        result_text = font.render(game_result_text, True, BLACK)
        text_rect = result_text.get_rect(center=(screen_width // 2, screen_height // 2 - 20))
        screen.blit(result_text, text_rect)

    pygame.display.flip()

pygame.quit()