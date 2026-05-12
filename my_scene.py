"""
File: my_scene.py
Group Members:
1. Parkamol Su-uthai (6810742186)
2. Siriyakorn Chatkaew (6810742251)
3. Suchansini Hirunprateeb (6810742269)
"""

import time
from graphics import Canvas
import random

# ----- Constants ------
# 1.canvas setting
CANVAS_WIDTH = 800
CANVAS_HEIGHT = 600
CANVAS_TITLE = "My Creative Scene"
FRAME_DELAY = 1 / 30 

# 2.Catship setting
CATSHIP_W = 162
CATSHIP_H = 124

# 3.Bullet setting
BULLET_W = 2
BULLET_H = 40
BULLET_SPEED = 80

# 4.Asteroid setting
ASTEROID_COUNT = random.randint(6, 9)
ASTEROID_SPEED = 5

# 5.Cat setting
CAT_BACK_SPEED = 7   # ความเร็วแมวตัวหลัง
CAT_FRONT_SPEED = 10  # ความเร็วแมวตัวหน้า (ให้เร็วกว่า)

# 6.Menu setting
BTN_X = (CANVAS_WIDTH / 2) - 100
BTN_Y = 440
BTN_W = 200
BTN_H = 100
ENDING_FONT = "Arial 48 bold"
LOSE_NUM = 1


# ----- other Variables  ------
# 1.Stroage variables
stars = []
asteroids = [] #list เก็บอุกาบาต
cats = [] #list เก็บแมว
bullets = [] #list เก็บกระสุน

# 2.Menu variables
game_started = False


def main():
    """Creates a canvas, draws the scene, and runs the animation loop.""" 
    global canvas 
    canvas = Canvas(CANVAS_WIDTH, CANVAS_HEIGHT, CANVAS_TITLE) 
    canvas.on_mouse_pressed = on_mouse_pressed
    
    draw_startpage(canvas)

    #state ของ ยานแมว
    ship = None
    
    while True:
        if game_started:
            # Update positions / states of animated
            ship = cat_ship(canvas,ship)
            shooting(canvas, bullets)  
            move_asteroids(canvas, asteroids)
            move_cats(canvas, cats)          
            stars_blink(canvas, stars)

            #เช็คการชนกันของสิ่งต่างๆ
            bullet_hit_asteroid(canvas)
            bullet_hit_cat(canvas)

            #เช็เงื่อนไขการจบเกม
            check_end_game(canvas)

            #เช็คเงื่อนไขการปิดเกม
            if (len(cats) == LOSE_NUM or len(cats) == 0) and len(asteroids) == 0:
                break

        canvas.update()
        time.sleep(FRAME_DELAY)  

# ---- Mouse handler ----
def on_mouse_pressed(x, y):
    global game_started, menu_bg, start_btn, stars, asteroids, cats

    if not game_started:
        # หาพิกัดของปุ่ม start จากตำแหน่งจริงบน canvas
        left = canvas.get_left_x(start_btn) # ขอบซ้ายของปุ่ม
        top = canvas.get_top_y(start_btn) # ขอบบนของปุ่ม
        right = left + canvas.get_obj_width(start_btn) # ขอบขวา (ซ้าย + ความกว้าง)
        bottom = top + canvas.get_obj_height(start_btn) # ขอบล่าง (บน + ความสูง)

        # ตรวจสอบว่าเมาส์ที่คลิก (x, y) อยู่ภายในพื้นที่ของปุ่มหรือไม่
        if left <= x <= right and top <= y <= bottom:
            game_started = True
            canvas.delete(menu_bg)
            canvas.delete(start_btn)

            draw_background(canvas)
            stars = create_stars(canvas, 40)
            
            # --- สร้างแมวด้วยความเร็วที่ต่างกัน ---
            # 1. แมวตัวหลัง: พิกัด Y=20, ความเร็ว CAT_BACK_SPEED (7)
            cats.append(create_cat(canvas, "img/IMG_4091.PNG", 20, CAT_BACK_SPEED))
            
            # 2. วาดอุกกาบาต (อยู่เลเยอร์กลาง)
            asteroids = setup_asteroids(canvas)
            
            # 3. แมวตัวหน้า: พิกัด Y=250, ความเร็ว CAT_FRONT_SPEED (10)
            cats.append(create_cat(canvas, "img/IMG_4090.PNG", 250, CAT_FRONT_SPEED))
    else:
        #ในกรณีที่เกมเริ่มแล้วให้การกดคลิ๊กเมาส์เป็นการเรียกใช้ฟังก์ชั่นสร้างลูกกระสุนเพื่อยิงออกมา
        create_bullet(canvas, x)



# ---- Helper functions ----

# 1.start background function
def draw_background(canvas):
    """Draw the main game background."""
    canvas.create_image(0, 0, "img/IMG_4092.PNG")

def draw_startpage(canvas):
    """Draw the start menu screen."""
    global menu_bg, start_btn
    menu_bg = canvas.create_image(0, 0, "img/IMG_4095.PNG")
    start_btn = canvas.create_image(BTN_X, BTN_Y, "img/IMG_4096.PNG")

def create_stars(canvas, count):
    """สร้างดวงดาวหลายๆดวง"""
    stars_list = []
    for _ in range(count):
        x = random.randint(0, CANVAS_WIDTH)
        y = random.randint(0, CANVAS_HEIGHT)
        size = random.randint(2, 4)
        star = canvas.create_oval(x, y, x + size, y + size, fill="white")

        stars_list.append({
            "id": star,
            "min": 1,
            "max": size + 2,
            "grow": True
        })
    return stars_list

def stars_blink(canvas, stars_list):
    """ทำให้ดาวกะพริบ โดยการปรับขนาดดาวแต่ละดวง"""
    for star in stars_list:
        coords = canvas.coords(star["id"])
        if len(coords) != 4:
            continue

        x1, y1, x2, y2 = coords
        size = x2 - x1

        if star["grow"]:
            size += 0.3
            if size >= star["max"]:
                star["grow"] = False
        else:
            size -= 0.3
            if size <= star["min"]:
                star["grow"] = True

        cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
        canvas.coords(star["id"], cx - size/2, cy - size/2, cx + size/2, cy + size/2)


# 2.Cat Functions
def create_cat(canvas, path, y_pos, speed):
    """สร้างแมวโดยรับค่าตำแหน่ง Y และความเร็วที่ต้องการ"""
    size_w, size_h = 100, 80 
    x = random.randint(0, CANVAS_WIDTH - size_w)
    cat_obj = canvas.create_image(x, y_pos, path, width=size_w, height=size_h)
    
    # สุ่มทิศทาง (ซ้าย/ขวา) แล้วคูณด้วยความเร็วที่ส่งมา
    direction = random.choice([-1, 1]) * speed
    return [cat_obj, direction]

def move_cats(canvas, cat_list):
    """จัดการการเคลื่อนที่ของแมวซ้ายขวา"""
    for item in cat_list:
        obj, dx = item[0], item[1]
        canvas.move(obj, dx, 0)
        curr_x = canvas.get_left_x(obj)
        if curr_x <= 0 or curr_x + canvas.get_obj_width(obj) >= CANVAS_WIDTH:
            item[1] = -dx


# 3.Asteroid Functions
def create_asteroid(canvas): 
    """สร้างอุกกาบาตและจำกัดให้อยู่ในช่วง Y 100-220"""
    size = random.randint(40, 80) #สุ่มขนาดอุกกาบาด
    #สุ่มตำแหน่ง x,y
    x = random.randint(0, CANVAS_WIDTH - size)
    y = random.randint(100, 220) 
    asteroid_obj = canvas.create_image(x, y,"img/astriod.png", width=size, height=size) #resizeภาพอุกกาบาด
    direction = random.choice([-1, 1]) * ASTEROID_SPEED #สุ่มทิศทางที่เริ่มเด้งไป
    return [asteroid_obj, direction]

def setup_asteroids(canvas):
    """กำหนดจุดเกิดของอุกาบาต"""
    asteroids_list = []
    for _ in range(ASTEROID_COUNT):
        asteroids_list.append(create_asteroid(canvas)) #เพิ่มอุกกาบาดเข้าไปในcanvasตามจำนวนที่randomมา
    return asteroids_list

def move_asteroids(canvas, asteroids_list):
    """จัดการการเคลื่อนที่ซ้ายขวาของอุกาบาต"""
    for item in asteroids_list:
        obj, dx = item[0], item[1]
        canvas.move(obj, dx, 0)

        #เช็คตำแหน่งปัจจุบันดูว่าชนขอบจอรึยัง
        curr_x = canvas.get_left_x(obj)
        obj_width = canvas.get_obj_width(obj)
        if curr_x <= 0 or curr_x + obj_width >= CANVAS_WIDTH:
            item[1] = -dx      #เด้งกลับหลังชน


# 4.cat spaceship functionn
def cat_ship(canvas,ship):
    """สร้างยานแมวกาศและการขยับยาน"""
    mouse_x = canvas.get_mouse_x()

    x_1 = mouse_x - CATSHIP_W/2
    y_1 = CANVAS_HEIGHT - CATSHIP_H

    #เช็คว่าเกินขอบจอมั้ย
    if x_1 <= 0:
        x_1 = 0
    elif x_1 + CATSHIP_W >= CANVAS_WIDTH:
        x_1 = CANVAS_WIDTH - CATSHIP_W
    
    #เช็ค state ว่าเป็นรอบแรกหรือรอบถัดไป
    if ship is None:
        ship = canvas.create_image(x_1, y_1, "img/cat_ship.png")
    else:
        old_x = canvas.get_left_x(ship)
        old_y = canvas.get_top_y(ship)
        canvas.move(ship, x_1 - old_x, y_1 - old_y)
    
    return ship


# 5.bullet function
def create_bullet(canvas,mouse_x):
    """สร้างลูกกระสุน"""

    # random สี
    color_set = ["#54FF2D","#FF2DC3"]
    bullet_color = random.choice(color_set)

    x_1 = mouse_x - BULLET_W / 2
    y_1 = CANVAS_HEIGHT - CATSHIP_H
    x_2 = x_1 + BULLET_W
    y_2 = y_1 - BULLET_H

    #สร้างกระสุน
    bullet = canvas.create_rectangle(x_1,y_1,x_2,y_2,bullet_color)

    #เก็บกระสุนไว้ใน list
    bullets.append(bullet)

def shooting(canvas, bullets):
    """การเคลื่อนที่ของลูกกระสุน"""
    for bullet in bullets[:]:
        # move ลูกกระสุน
        canvas.move(bullet, 0, - BULLET_SPEED)
        #เช็คว่าเกินขอบจอมั้ย
        if canvas.get_top_y(bullet) <= 0:
            canvas.delete(bullet)
            bullets.remove(bullet)


# 6.overlapping function
def check_collisions(canvas,obj1,obj2):
    """ตรวจสอบการทับกันของ2วัตถุ"""
    x1 = canvas.get_left_x(obj1)
    y1 = canvas.get_top_y(obj1)
    x2 = x1 + canvas.get_obj_width(obj1)
    y2 = y1 + canvas.get_obj_height(obj1)

    overlapping_items = canvas.find_overlapping(x1, y1, x2, y2)
    
    if obj2 in overlapping_items:
        return True
    else:
        return False
    
def bullet_hit_asteroid(canvas):
    """เช็ตว่ามีลูกกระสุนยิงโดนอุกาบาตมั้ย"""
    for bullet in bullets[:]:
    
        for asteroid in asteroids[:]:
            if check_collisions(canvas,bullet, asteroid[0]):
                canvas.delete(asteroid[0])
                canvas.delete(bullet)

                asteroids.remove(asteroid)
                bullets.remove(bullet)

                break

def bullet_hit_cat(canvas):
    """เช็ตว่ามีลูกกระสุนยิงโดนแมวมั้ย"""
    for bullet in bullets[:]:
        for cat in cats[:]:
            if check_collisions(canvas,bullet,cat[0]):
                canvas.delete(cat[0])
                canvas.delete(bullet)
                cats.remove(cat)
                bullets.remove(bullet)
                break
    
# 7.end game condition function
def check_end_game(canvas):
    """เงื่อนไขการจบเกม"""
    #หากยิงโดนแมว
    if len(cats) == LOSE_NUM:
        canvas.create_text(CANVAS_WIDTH/2, CANVAS_HEIGHT/2, "YOU LOSE", 
            font= ENDING_FONT, color="red", anchor="center")
    
    #หากอุกาบาตหมดก่อน
    if len(asteroids) == 0:
        canvas.create_text(CANVAS_WIDTH/2, CANVAS_HEIGHT/2, "YOU WIN!", 
            font=ENDING_FONT, color="yellow", anchor="center")


if __name__ == "__main__":
    main()