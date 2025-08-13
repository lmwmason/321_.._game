import pygame
import random
import os
import time

pygame.init()
sound = pygame.mixer.Sound("sounds/spy.wav")
sound.play(-1)
cor_sound = pygame.mixer.Sound("sounds/cor.wav")
wro_sound = pygame.mixer.Sound("sounds/wro.wav")

info = pygame.display.Info()
screen_width = info.current_w
screen_height = info.current_h
screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
pygame.display.set_caption("떨어지는 정답 찾기")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
BLUE = (65, 105, 225)
RED = (255, 69, 0)
GREEN = (0, 255, 0)

try:
    font_path = "fonts/Pinkfong Baby Shark Font_ Bold.ttf"
    if not os.path.exists(font_path):
        font = pygame.font.Font(None, 60)
    else:
        font = pygame.font.Font(font_path, 60)
    
    title_font_path = "fonts/Pinkfong Baby Shark Font_ Bold.ttf"
    if not os.path.exists(title_font_path):
        title_font = pygame.font.Font(None, 120)
    else:
        title_font = pygame.font.Font(title_font_path, 120)

except pygame.error as e:
    font = pygame.font.Font(None, 60)
    title_font = pygame.font.Font(None, 120)

score = 0
goal = 100

correct_path = "images/correct"
wrong_path = "images/wrong"

image_scale = 0.6
falling_speed = 1

def load_and_scale_image(path, scale):
    try:
        img = pygame.image.load(path).convert_alpha()
        size = round(img.get_width() * scale), round(img.get_height() * scale)
        return pygame.transform.scale(img, size)
    except pygame.error as e:
        return None

def load_images(correct_dir, wrong_dir, scale):
    if not os.path.isdir(correct_dir) or not os.path.isdir(wrong_dir):
        return [], []
    
    correct_images = [load_and_scale_image(os.path.join(correct_dir, f), scale) for f in os.listdir(correct_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')) and os.path.isfile(os.path.join(correct_dir, f))]
    wrong_images = [load_and_scale_image(os.path.join(wrong_dir, f), scale) for f in os.listdir(wrong_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')) and os.path.isfile(os.path.join(wrong_dir, f))]
    return [img for img in correct_images if img is not None], [img for img in wrong_images if img is not None]

correct_loaded_images, wrong_loaded_images = load_images(correct_path, wrong_path, image_scale)

game_state = "title"
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
    
    all_images = [{"img": random.choice(correct_loaded_images), "label": "correct"}]
    num_wrong = min(3, len(wrong_loaded_images))
    wrong_selections = random.sample(wrong_loaded_images, num_wrong)
    
    for img in wrong_selections:
        all_images.append({"img": img, "label": "wrong"})

    random.shuffle(all_images)
    
    occupied_x = []
    y_offset = 0 
    
    for item in all_images:
        img = item["img"]
        label = item["label"]
        
        while True:
            x = random.randint(50, screen_width - 50 - img.get_width())
            is_overlap = any(abs(x - ox) < 150 for ox in occupied_x)
            if not is_overlap:
                occupied_x.append(x)
                break
        
        rect = img.get_rect(topleft=(x, -img.get_height() - y_offset))
        falling_items.append({"id": next_id, "label": label, "img": img, "rect": rect})
        falling_items_data[next_id] = float(rect.y)
        next_id += 1
        y_offset += random.randint(150, 300) 
    
    return True

running = True
start_time = 0
end_time = 0

speed_options = [1, 2, 3]
selected_speed_index = 0

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if game_state == "title":
                button_x = screen_width // 2 - 300
                button_y = screen_height // 2 + 50
                button_width = 200
                button_height = 70
                for i in range(len(speed_options)):
                    rect = pygame.Rect(button_x + i * 220, button_y, button_width, button_height)
                    if rect.collidepoint(mouse_pos):
                        selected_speed_index = i
                        break
                
                start_button_rect = pygame.Rect(screen_width // 2 - 150, screen_height // 2 + 200, 300, 80)
                if start_button_rect.collidepoint(mouse_pos):
                    falling_speed = speed_options[selected_speed_index]
                    if create_falling_items():
                        game_state = "playing"
                        score = 0
                        start_time = time.time()
                    else:
                        game_state = "error"
                        
            elif game_state == "playing":
                if event.button == 1:
                    for item in falling_items:
                        if item["rect"].collidepoint(mouse_pos):
                            if item["label"] == "correct":
                                cor_sound.play()
                                score += 10
                                
                            else:
                                wro_sound.play()
                                score -= 5
                                
                            create_falling_items()
                            break
                exit_button_rect = pygame.Rect(screen_width - 150, 10, 140, 60)
                if exit_button_rect.collidepoint(mouse_pos):
                    running = False
            
            elif game_state == "game_over":
                restart_button_rect = pygame.Rect(screen_width // 2 - 250, screen_height // 2 + 100, 200, 70)
                if restart_button_rect.collidepoint(mouse_pos):
                    score = 0
                    game_state = "title"
                    
                exit_button_rect = pygame.Rect(screen_width // 2 + 50, screen_height // 2 + 100, 200, 70)
                if exit_button_rect.collidepoint(mouse_pos):
                    running = False

    screen.fill(WHITE)

    if game_state == "title":
        title_text = title_font.render("떨어지는 정답 찾기", True, BLUE)
        title_rect = title_text.get_rect(center=(screen_width // 2, screen_height // 2 - 250))
        screen.blit(title_text, title_rect)
        
        goal_text = font.render(f"목표 점수: {goal}", True, BLACK)
        goal_rect = goal_text.get_rect(center=(screen_width // 2, screen_height // 2 - 100))
        screen.blit(goal_text, goal_rect)
        
        speed_text = font.render("속도 선택:", True, BLACK)
        speed_rect = speed_text.get_rect(center=(screen_width // 2, screen_height // 2))
        screen.blit(speed_text, speed_rect)
        
        button_x = screen_width // 2 - 300
        button_y = screen_height // 2 + 50
        button_width = 200
        button_height = 70
        
        for i, speed in enumerate(["느림", "보통", "빠름"]):
            rect = pygame.Rect(button_x + i * 220, button_y, button_width, button_height)
            color = BLUE if i == selected_speed_index else GRAY
            pygame.draw.rect(screen, color, rect, border_radius=10)
            
            button_text = font.render(speed, True, WHITE if i == selected_speed_index else BLACK)
            text_rect = button_text.get_rect(center=rect.center)
            screen.blit(button_text, text_rect)
            
        start_button_rect = pygame.Rect(screen_width // 2 - 150, screen_height // 2 + 200, 300, 80)
        pygame.draw.rect(screen, GREEN, start_button_rect, border_radius=10)
        start_button_text = font.render("게임 시작", True, WHITE)
        start_text_rect = start_button_text.get_rect(center=start_button_rect.center)
        screen.blit(start_button_text, start_text_rect)
        
    elif game_state == "playing":
        end_time = time.time()
        elapsed_time = end_time - start_time
        
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

        if score >= goal:
            game_state = "game_over"
            game_result_text = f"게임 승리! 시간: {elapsed_time:.2f}초"
            game_result_color = BLUE
        elif score <= -10:
            game_state = "game_over"
            game_result_text = "게임 오버! 점수가 -10점 미만이에요."
            game_result_color = RED
        elif elapsed_time > 60:
            game_state = "game_over"
            game_result_text = "게임 오버! 1분 시간 제한이 끝났어요."
            game_result_color = RED

        for item in falling_items:
            screen.blit(item["img"], item["rect"])
            
        pygame.draw.rect(screen, GRAY, (0, 0, screen_width, 80))
        
        score_text = font.render(f"점수: {score} / {goal}", True, BLACK)
        score_rect = score_text.get_rect(topleft=(20, 10))
        screen.blit(score_text, score_rect)
        
        timer_text = font.render(f"남은 시간: {max(0, 60 - elapsed_time):.2f}초", True, BLACK)
        timer_rect = timer_text.get_rect(topright=(screen_width - 20, 10))
        screen.blit(timer_text, timer_rect)
        
        exit_button_rect = pygame.Rect(screen_width // 2 - 70, 10, 140, 60)
        pygame.draw.rect(screen, RED, exit_button_rect, border_radius=10)
        exit_button_text = font.render("종료", True, WHITE)
        exit_text_rect = exit_button_text.get_rect(center=exit_button_rect.center)
        screen.blit(exit_button_text, exit_text_rect)

    elif game_state == "game_over":
        result_text = title_font.render(game_result_text, True, game_result_color)
        result_rect = result_text.get_rect(center=(screen_width // 2, screen_height // 2 - 100))
        screen.blit(result_text, result_rect)
        
        final_score_text = font.render(f"최종 점수: {score}", True, BLACK)
        final_score_rect = final_score_text.get_rect(center=(screen_width // 2, screen_height // 2))
        screen.blit(final_score_text, final_score_rect)
        
        restart_button_rect = pygame.Rect(screen_width // 2 - 250, screen_height // 2 + 100, 200, 70)
        pygame.draw.rect(screen, BLUE, restart_button_rect, border_radius=10)
        restart_button_text = font.render("다시 시작", True, WHITE)
        restart_text_rect = restart_button_text.get_rect(center=restart_button_rect.center)
        screen.blit(restart_button_text, restart_text_rect)
        
        exit_button_rect = pygame.Rect(screen_width // 2 + 50, screen_height // 2 + 100, 200, 70)
        pygame.draw.rect(screen, RED, exit_button_rect, border_radius=10)
        exit_button_text = font.render("종료", True, WHITE)
        exit_text_rect = exit_button_text.get_rect(center=exit_button_rect.center)
        screen.blit(exit_button_text, exit_text_rect)

    elif game_state == "error":
        error_text = font.render("게임 시작에 필요한 이미지가 없어요. 게임을 종료합니다.", True, RED)
        error_rect = error_text.get_rect(center=(screen_width // 2, screen_height // 2))
        screen.blit(error_text, error_rect)
        
    pygame.display.flip()

pygame.quit()