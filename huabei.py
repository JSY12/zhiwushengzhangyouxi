# -*- coding: UTF-8 -*-
import pygame
import sys
import random
import math
from pygame.locals import *
import json
import os
from datetime import datetime, timedelta

# 初始化pygame
pygame.init()
pygame.mixer.init()

# 确保中文显示正常
pygame.font.init()
font_path = pygame.font.match_font('simsun')  # 尝试匹配中文字体
if not font_path:
    # 如果找不到中文字体，使用默认字体
    default_font = pygame.font.get_default_font()
    font_path = pygame.font.match_font(default_font)

# 游戏常量
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 30

# 颜色定义
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BROWN = (139, 69, 19)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (255, 0, 0)

# 创建屏幕
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("植物成长游戏")
clock = pygame.time.Clock()

# 加载图像资源（这里使用简单图形代替）
class Images:
    seedling = None
    small_tree = None
    sun = None
    water = None
    fruit = None
    
    @classmethod
    def init(cls):
        # 绘制简单的树苗
        cls.seedling = pygame.Surface((50, 100), pygame.SRCALPHA)
        pygame.draw.rect(cls.seedling, BROWN, (22, 70, 6, 30))  # 树干
        pygame.draw.circle(cls.seedling, GREEN, (25, 50), 20)   # 叶子
        
        # 绘制小树
        cls.small_tree = pygame.Surface((80, 150), pygame.SRCALPHA)
        pygame.draw.rect(cls.small_tree, BROWN, (37, 100, 6, 50))  # 树干
        pygame.draw.circle(cls.small_tree, GREEN, (40, 80), 30)    # 叶子
        
        # 绘制太阳
        cls.sun = pygame.Surface((50, 50), pygame.SRCALPHA)
        pygame.draw.circle(cls.sun, YELLOW, (25, 25), 20)
        
        # 绘制水滴
        cls.water = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.ellipse(cls.water, BLUE, (5, 5, 20, 20))
        
        # 绘制果实
        cls.fruit = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(cls.fruit, RED, (10, 10), 10)

# 工具函数
def get_font(size):
    """获取指定大小的字体"""
    return pygame.font.Font(font_path, size)

def draw_text(text, font, color, x, y, center=True):
    """在指定位置绘制文本"""
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    if center:
        text_rect.center = (x, y)
    else:
        text_rect.topleft = (x, y)
    screen.blit(text_surface, text_rect)
    return text_rect

def distance(p1, p2):
    """计算两点之间的距离"""
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])** 2)

# 游戏数据管理
class GameData:
    def __init__(self):
        self.users = {}
        self.current_user = None
        self.load_data()
        
    def load_data(self):
        """从文件加载游戏数据"""
        if os.path.exists("game_data.json"):
            try:
                with open("game_data.json", "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.users = data.get("users", {})
            except:
                print("加载数据失败，使用新数据")
    
    def save_data(self):
        """保存游戏数据到文件"""
        data = {
            "users": self.users
        }
        with open("game_data.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    
    def register_user(self, username, password):
        """注册新用户"""
        if username in self.users:
            return False, "用户名已存在"
        
        # 初始化新用户数据
        self.users[username] = {
            "password": password,
            "points": 100,  # 初始积分
            "plants": [],
            "unlocked_areas": ["garden"]  # 初始解锁区域
        }
        self.save_data()
        return True, "注册成功"
    
    def login_user(self, username, password):
        """用户登录"""
        if username not in self.users:
            return False, "用户名不存在"
        
        if self.users[username]["password"] != password:
            return False, "密码错误"
        
        self.current_user = username
        return True, "登录成功"
    
    def add_plant(self, plant_type, area="garden"):
        """添加新植物"""
        if not self.current_user:
            return False, "请先登录"
            
        user_data = self.users[self.current_user]
        
        # 检查是否有足够的积分
        if user_data["points"] < 50:  # 假设购买种子需要50积分
            return False, "积分不足，无法购买种子"
            
        # 检查区域是否已解锁
        if area not in user_data["unlocked_areas"]:
            return False, "该区域未解锁"
        
        # 扣除积分
        user_data["points"] -= 50
        
        # 添加新植物
        plant_id = len(user_data["plants"])
        now = datetime.now().isoformat()
        user_data["plants"].append({
            "id": plant_id,
            "type": plant_type,
            "area": area,
            "stage": 1,  # 初始为树苗阶段
            "water_level": 50,
            "sun_level": 50,
            "last_watered": now,
            "last_sunned": now,
            "fruits": 0,
            "position": (random.randint(100, SCREEN_WIDTH-100), 
                         random.randint(200, SCREEN_HEIGHT-200))
        })
        
        self.save_data()
        return True, "植物已种植"
    
    def get_user_plants(self):
        """获取当前用户的所有植物"""
        if not self.current_user:
            return []
        return self.users[self.current_user]["plants"]
    
    def get_user_points(self):
        """获取当前用户的积分"""
        if not self.current_user:
            return 0
        return self.users[self.current_user]["points"]
    
    def update_plant_status(self):
        """更新所有植物的状态（水分和阳光会随时间减少）"""
        if not self.current_user:
            return
            
        user_data = self.users[self.current_user]
        now = datetime.now()
        
        for plant in user_data["plants"]:
            # 计算上次浇水到现在的时间
            last_watered = datetime.fromisoformat(plant["last_watered"])
            water_time_diff = (now - last_watered).total_seconds() / 60  # 分钟
            
            # 计算上次晒太阳到现在的时间
            last_sunned = datetime.fromisoformat(plant["last_sunned"])
            sun_time_diff = (now - last_sunned).total_seconds() / 60  # 分钟
            
            # 水分和阳光随时间减少，第一阶段减少更快
            if plant["stage"] == 1:  # 树苗阶段
                plant["water_level"] = max(0, plant["water_level"] - water_time_diff * 0.5)
                plant["sun_level"] = max(0, plant["sun_level"] - sun_time_diff * 0.5)
            else:  # 小树阶段
                plant["water_level"] = max(0, plant["water_level"] - water_time_diff * 0.2)
                plant["sun_level"] = max(0, plant["sun_level"] - sun_time_diff * 0.2)
            
            # 检查是否可以成长到下一阶段
            if plant["stage"] == 1 and plant["water_level"] > 70 and plant["sun_level"] > 70:
                plant["stage"] = 2
                # 成长奖励积分
                user_data["points"] += 100
                self.save_data()
            
            # 检查是否结果
            if plant["stage"] == 2 and random.random() < 0.001:  # 小概率结果
                plant["fruits"] = min(5, plant["fruits"] + 1)
        
        self.save_data()
    
    def water_plant(self, plant_id):
        """给植物浇水"""
        if not self.current_user:
            return False, "请先登录"
            
        user_data = self.users[self.current_user]
        
        for plant in user_data["plants"]:
            if plant["id"] == plant_id:
                plant["water_level"] = min(100, plant["water_level"] + 30)
                plant["last_watered"] = datetime.now().isoformat()
                self.save_data()
                return True, "浇水成功"
        
        return False, "植物不存在"
    
    def sun_plant(self, plant_id):
        """给植物晒太阳"""
        if not self.current_user:
            return False, "请先登录"
            
        user_data = self.users[self.current_user]
        
        for plant in user_data["plants"]:
            if plant["id"] == plant_id:
                plant["sun_level"] = min(100, plant["sun_level"] + 30)
                plant["last_sunned"] = datetime.now().isoformat()
                self.save_data()
                return True, "晒太阳成功"
        
        return False, "植物不存在"
    
    def harvest_fruits(self, plant_id):
        """收获果实（通过摇晃动作触发）"""
        if not self.current_user:
            return False, "请先登录"
            
        user_data = self.users[self.current_user]
        
        for plant in user_data["plants"]:
            if plant["id"] == plant_id and plant["fruits"] > 0:
                fruits_harvested = plant["fruits"]
                plant["fruits"] = 0
                # 果实可以兑换积分
                user_data["points"] += fruits_harvested * 10
                self.save_data()
                return True, f"收获了{fruits_harvested}个果实，获得{fruits_harvested * 10}积分"
        
        return False, "该植物没有可收获的果实"

# 重力感应模拟器（实际设备上可使用传感器数据）
class GravitySensor:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0
        self.shake_threshold = 2.0  # 摇晃阈值
        self.pour_threshold = 1.5   # 倾倒阈值
        self.last_update = pygame.time.get_ticks()
        self.shake_detected = False
        self.pour_detected = False
        
    def update(self):
        """更新传感器状态（使用键盘模拟）"""
        keys = pygame.key.get_pressed()
        
        # 重置状态
        self.shake_detected = False
        self.pour_detected = False
        
        # 使用方向键模拟重力感应
        if keys[K_LEFT]:
            self.x = -1.0
        elif keys[K_RIGHT]:
            self.x = 1.0
        else:
            self.x = 0.0
            
        if keys[K_UP]:
            self.y = -1.0
        elif keys[K_DOWN]:
            self.y = 1.0
        else:
            self.y = 0.0
        
        # 计算加速度大小
        acceleration = math.sqrt(self.x**2 + self.y**2 + self.z**2)
        
        # 检测摇晃动作（快速移动）
        current_time = pygame.time.get_ticks()
        if current_time - self.last_update < 100:  # 100ms内的变化
            if acceleration > self.shake_threshold:
                self.shake_detected = True
        
        # 检测倾倒动作（较大角度）
        if abs(self.x) > self.pour_threshold or abs(self.y) > self.pour_threshold:
            self.pour_detected = True
            
        self.last_update = current_time

# 按钮类
class Button:
    def __init__(self, x, y, width, height, text, action=None, color=GRAY, 
                 hover_color=WHITE, text_color=BLACK):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.active = True
        
    def draw(self):
        """绘制按钮"""
        # 检查鼠标是否悬停在按钮上
        color = self.hover_color if self.is_hovered() and self.active else self.color
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)  # 边框
        draw_text(self.text, get_font(20), self.text_color, 
                 self.rect.centerx, self.rect.centery)
    
    def is_hovered(self):
        """检查鼠标是否悬停在按钮上"""
        return self.rect.collidepoint(pygame.mouse.get_pos())
    
    def is_clicked(self, event):
        """检查按钮是否被点击"""
        if self.active and event.type == MOUSEBUTTONDOWN and event.button == 1:
            return self.is_hovered()
        return False

# 输入框类
class InputBox:
    def __init__(self, x, y, width, height, label, password=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.label = label
        self.text = ""
        self.color = GRAY
        self.active = False
        self.password = password
        
    def draw(self):
        """绘制输入框"""
        # 绘制标签
        draw_text(self.label, get_font(18), BLACK, 
                 self.rect.x, self.rect.y - 25, center=False)
        
        # 绘制输入框
        color = WHITE if self.active else self.color
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)  # 边框
        
        # 绘制输入的文本（密码显示为*）
        display_text = "*" * len(self.text) if self.password else self.text
        if display_text:
            draw_text(display_text, get_font(18), BLACK, 
                     self.rect.centerx, self.rect.centery)
        else:
            draw_text("点击输入...", get_font(16), GRAY, 
                     self.rect.centerx, self.rect.centery)
    
    def handle_event(self, event):
        """处理输入事件"""
        if event.type == MOUSEBUTTONDOWN:
            # 如果点击了输入框，激活它
            self.active = self.rect.collidepoint(event.pos)
            self.color = WHITE if self.active else GRAY
        elif event.type == KEYDOWN and self.active:
            if event.key == K_RETURN:
                self.active = False
                self.color = GRAY
            elif event.key == K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                self.text += event.unicode

# 游戏状态管理
class GameState:
    def __init__(self):
        self.state = "login"  # 初始状态为登录
        self.message = ""
        self.message_timer = 0
        
    def set_state(self, state):
        """设置游戏状态"""
        self.state = state
        self.clear_message()
        
    def show_message(self, text, duration=3000):
        """显示提示消息"""
        self.message = text
        self.message_timer = pygame.time.get_ticks() + duration
        
    def clear_message(self):
        """清除提示消息"""
        self.message = ""
        self.message_timer = 0
        
    def draw_message(self):
        """绘制提示消息"""
        if self.message and pygame.time.get_ticks() < self.message_timer:
            text_surface = get_font(20).render(self.message, True, RED)
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH//2, 50))
            pygame.draw.rect(screen, WHITE, (text_rect.x-10, text_rect.y-10, 
                                           text_rect.width+20, text_rect.height+20))
            pygame.draw.rect(screen, BLACK, (text_rect.x-10, text_rect.y-10, 
                                           text_rect.width+20, text_rect.height+20), 2)
            screen.blit(text_surface, text_rect)

# 植物类
class Plant:
    def __init__(self, plant_data):
        self.id = plant_data["id"]
        self.type = plant_data["type"]
        self.stage = plant_data["stage"]
        self.water_level = plant_data["water_level"]
        self.sun_level = plant_data["sun_level"]
        self.fruits = plant_data["fruits"]
        self.position = plant_data["position"]
        
    def draw(self):
        """绘制植物"""
        x, y = self.position
        
        # 根据生长阶段绘制不同的植物
        if self.stage == 1:  # 树苗阶段
            screen.blit(Images.seedling, (x - 25, y - 50))
        else:  # 小树阶段
            screen.blit(Images.small_tree, (x - 40, y - 75))
        
        # 绘制果实
        for i in range(self.fruits):
            fruit_x = x + 20 + i * 15
            fruit_y = y - 30 + i * 5
            screen.blit(Images.fruit, (fruit_x, fruit_y))
        
        # 绘制水分和阳光指示条
        self.draw_status_bar(x, y + 50, "水分", self.water_level, BLUE)
        self.draw_status_bar(x, y + 70, "阳光", self.sun_level, YELLOW)
    
    def draw_status_bar(self, x, y, label, value, color):
        """绘制状态条"""
        # 绘制标签
        draw_text(label, get_font(14), BLACK, x - 40, y, center=False)
        
        # 绘制状态条背景
        pygame.draw.rect(screen, WHITE, (x, y - 10, 100, 20))
        pygame.draw.rect(screen, BLACK, (x, y - 10, 100, 20), 1)
        
        # 绘制状态条
        fill_width = int(value)
        pygame.draw.rect(screen, color, (x, y - 10, fill_width, 20))
        
        # 绘制数值
        draw_text(f"{int(value)}%", get_font(14), BLACK, x + 110, y, center=False)
    
    def is_clicked(self, pos):
        """检查植物是否被点击"""
        x, y = self.position
        # 根据植物大小定义点击区域
        width = 50 if self.stage == 1 else 80
        height = 100 if self.stage == 1 else 150
        plant_rect = pygame.Rect(x - width//2, y - height//2, width, height)
        return plant_rect.collidepoint(pos)

# 游戏主类
class PlantGame:
    def __init__(self):
        self.data = GameData()
        self.state_manager = GameState()
        self.gravity_sensor = GravitySensor()
        self.selected_plant_id = None
        
        # 初始化图像
        Images.init()
        
        # 创建UI元素
        self.create_ui_elements()
        
    def create_ui_elements(self):
        """创建UI元素"""
        # 登录/注册界面按钮
        button_width = 150
        button_height = 40
        button_y = SCREEN_HEIGHT - 100
        
        self.login_button = Button(
            SCREEN_WIDTH//2 - button_width - 20, button_y,
            button_width, button_height, "登录", action="login"
        )
        
        self.register_button = Button(
            SCREEN_WIDTH//2 + 20, button_y,
            button_width, button_height, "注册", action="register"
        )
        
        # 输入框
        input_width = 300
        input_height = 40
        input_x = SCREEN_WIDTH//2 - input_width//2
        
        self.username_input = InputBox(
            input_x, SCREEN_HEIGHT//2 - 50,
            input_width, input_height, "用户名"
        )
        
        self.password_input = InputBox(
            input_x, SCREEN_HEIGHT//2 + 50,
            input_width, input_height, "密码", password=True
        )
        
        # 游戏界面按钮
        self.plant_tree_button = Button(
            50, 50, 120, 40, "种植植物", action="plant_tree"
        )
        
        self.water_button = Button(
            50, 110, 120, 40, "浇水", action="water_plant"
        )
        
        self.sun_button = Button(
            50, 170, 120, 40, "晒太阳", action="sun_plant"
        )
        
        self.harvest_button = Button(
            50, 230, 120, 40, "收获果实", action="harvest_fruits"
        )
        
        self.logout_button = Button(
            SCREEN_WIDTH - 150, 50, 100, 40, "退出登录", action="logout"
        )
    
    def handle_events(self):
        """处理游戏事件"""
        for event in pygame.event.get():
            if event.type == QUIT:
                self.data.save_data()
                pygame.quit()
                sys.exit()
            
            # 处理输入框事件
            if self.state_manager.state in ["login", "register"]:
                self.username_input.handle_event(event)
                self.password_input.handle_event(event)
            
            # 处理按钮点击
            self.handle_button_click(event)
            
            # 处理植物点击
            if self.state_manager.state == "game" and event.type == MOUSEBUTTONDOWN:
                self.handle_plant_click(event.pos)
        
        # 更新重力传感器
        self.gravity_sensor.update()
        
        # 处理重力感应事件
        self.handle_gravity_events()
    
    def handle_button_click(self, event):
        """处理按钮点击事件"""
        if self.state_manager.state in ["login", "register"]:
            if self.login_button.is_clicked(event):
                self.process_login()
            elif self.register_button.is_clicked(event):
                self.process_register()
        
        elif self.state_manager.state == "game":
            if self.plant_tree_button.is_clicked(event):
                success, msg = self.data.add_plant("普通树")
                self.state_manager.show_message(msg)
            elif self.water_button.is_clicked(event) and self.selected_plant_id is not None:
                success, msg = self.data.water_plant(self.selected_plant_id)
                self.state_manager.show_message(msg)
            elif self.sun_button.is_clicked(event) and self.selected_plant_id is not None:
                success, msg = self.data.sun_plant(self.selected_plant_id)
                self.state_manager.show_message(msg)
            elif self.harvest_button.is_clicked(event) and self.selected_plant_id is not None:
                success, msg = self.data.harvest_fruits(self.selected_plant_id)
                self.state_manager.show_message(msg)
            elif self.logout_button.is_clicked(event):
                self.data.current_user = None
                self.state_manager.set_state("login")
                self.selected_plant_id = None
                self.state_manager.show_message("已退出登录")
    
    def handle_plant_click(self, pos):
        """处理植物点击事件"""
        plants = self.data.get_user_plants()
        for plant_data in plants:
            plant = Plant(plant_data)
            if plant.is_clicked(pos):
                self.selected_plant_id = plant.id
                self.state_manager.show_message(f"已选择植物 #{plant.id}")
                return
        
        # 如果点击了空白处，取消选择
        self.selected_plant_id = None
        self.state_manager.show_message("已取消选择")
    
    def handle_gravity_events(self):
        """处理重力感应事件"""
        if self.state_manager.state == "game" and self.selected_plant_id is not None:
            # 摇晃动作 - 收获果实
            if self.gravity_sensor.shake_detected:
                success, msg = self.data.harvest_fruits(self.selected_plant_id)
                self.state_manager.show_message(msg)
            
            # 倾倒动作 - 浇水
            if self.gravity_sensor.pour_detected:
                success, msg = self.data.water_plant(self.selected_plant_id)
                self.state_manager.show_message(msg)
    
    def process_login(self):
        """处理登录逻辑"""
        username = self.username_input.text.strip()
        password = self.password_input.text.strip()
        
        if not username or not password:
            self.state_manager.show_message("请输入用户名和密码")
            return
        
        success, msg = self.data.login_user(username, password)
        self.state_manager.show_message(msg)
        
        if success:
            self.state_manager.set_state("game")
            # 清空输入框
            self.username_input.text = ""
            self.password_input.text = ""
    
    def process_register(self):
        """处理注册逻辑"""
        username = self.username_input.text.strip()
        password = self.password_input.text.strip()
        
        if not username or not password:
            self.state_manager.show_message("请输入用户名和密码")
            return
        
        success, msg = self.data.register_user(username, password)
        self.state_manager.show_message(msg)
        
        if success:
            # 注册成功后自动登录
            self.data.login_user(username, password)
            self.state_manager.set_state("game")
            # 清空输入框
            self.username_input.text = ""
            self.password_input.text = ""
    
    def update(self):
        """更新游戏状态"""
        if self.state_manager.state == "game":
            self.data.update_plant_status()
    
    def draw_login_screen(self):
        """绘制登录/注册界面"""
        screen.fill(WHITE)
        
        # 绘制标题
        draw_text("植物成长游戏", get_font(40), BLACK, SCREEN_WIDTH//2, 100)
        draw_text("请登录或注册", get_font(24), BLACK, SCREEN_WIDTH//2, 160)
        
        # 绘制输入框
        self.username_input.draw()
        self.password_input.draw()
        
        # 绘制按钮
        self.login_button.draw()
        self.register_button.draw()
        
        # 根据当前状态更改按钮文本
        if self.state_manager.state == "login":
            self.login_button.text = "登录"
            self.register_button.text = "前往注册"
        else:
            self.login_button.text = "前往登录"
            self.register_button.text = "注册"
    
    def draw_game_screen(self):
        """绘制游戏界面"""
        screen.fill((240, 240, 240))  # 浅灰色背景
        
        # 绘制用户信息
        draw_text(f"用户: {self.data.current_user}", get_font(20), BLACK, 100, 20, center=False)
        draw_text(f"积分: {self.data.get_user_points()}", get_font(20), BLACK, SCREEN_WIDTH - 100, 20)
        
        # 绘制按钮
        self.plant_tree_button.draw()
        self.water_button.draw()
        self.sun_button.draw()
        self.harvest_button.draw()
        self.logout_button.draw()
        
        # 绘制植物
        plants = self.data.get_user_plants()
        if not plants:
            draw_text("还没有植物，点击'种植植物'开始吧！", get_font(20), GRAY, 
                     SCREEN_WIDTH//2, SCREEN_HEIGHT//2)
        else:
            for plant_data in plants:
                plant = Plant(plant_data)
                plant.draw()
                
                # 如果是选中的植物，绘制选中框
                if plant.id == self.selected_plant_id:
                    x, y = plant.position
                    width = 50 if plant.stage == 1 else 80
                    height = 100 if plant.stage == 1 else 150
                    pygame.draw.rect(screen, RED, 
                                    (x - width//2, y - height//2, width, height), 3)
        
        # 绘制操作提示
        draw_text("操作提示:", get_font(16), BLACK, SCREEN_WIDTH - 200, 100, center=False)
        draw_text("- 点击植物进行选择", get_font(14), BLACK, SCREEN_WIDTH - 200, 130, center=False)
        draw_text("- 方向键模拟重力感应", get_font(14), BLACK, SCREEN_WIDTH - 200, 155, center=False)
        draw_text("- 左右快速移动模拟摇晃（收获）", get_font(14), BLACK, SCREEN_WIDTH - 200, 180, center=False)
        draw_text("- 上下倾斜模拟浇水", get_font(14), BLACK, SCREEN_WIDTH - 200, 205, center=False)
    
    def draw(self):
        """绘制游戏画面"""
        if self.state_manager.state in ["login", "register"]:
            self.draw_login_screen()
        elif self.state_manager.state == "game":
            self.draw_game_screen()
        
        # 绘制提示消息
        self.state_manager.draw_message()
        
        pygame.display.flip()
    
    def run(self):
        """运行游戏主循环"""
        while True:
            self.handle_events()
            self.update()
            self.draw()
            clock.tick(FPS)

# 启动游戏
if __name__ == "__main__":
    game = PlantGame()
    game.run()

