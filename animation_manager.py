import random
import numpy as np
import tkinter as tk
from pathlib import Path
from PIL import Image, ImageTk
from tkinter import messagebox
from utils import scaled_dimension
from utils import hex_to_rgb, rgb_to_hex

base_path = Path(__file__).parent

class AnimationManager:
    def __init__(self, root, canvas, scale_factor=1.0):
        """
            初始化动画管理器。

            root: Tkinter根窗口实例。
            canvas: 用于绘制动画的Tkinter画布。
            scale_factor: 界面元素的缩放因子。
        """
        self.root = root
        # self.canvas 接收 UIManager 提供的画布，用于云朵和粒子效果
        self.canvas = canvas
        self.bg_color = self.root.style.colors.bg
        self.scale_factor = scale_factor  # 存储缩放因子

        # 车辆动画相关属性
        self.car_image = None
        self.car_pos = 0
        self.car_speed = scaled_dimension(4,self.scale_factor)  # 使用缩放后的速度
        self.trail_segments = []
        self.trail_length = 50
        self.max_trail_lines = 150
        self.line_spacing = scaled_dimension(4,self.scale_factor)  # 使用缩放后的间距
        self.rainbow_colors = [
            '#FF0000', '#FF7F00', '#FFFF00', '#00FF00',
            '#0000FF', '#4B0082', '#8F00FF'
        ]

        # 云朵动画相关属性
        self.clouds_data = []
        self.current_cloud_index = 0
        # self.positions 初始值，会在 create_animation_area 中根据 root 宽度更新
        self.positions = [(0, 400), (400, 800), (800, 1200)]
        self.active_cloud = None

        # 小车动画专用的 Canvas，初始化为 None，将在 create_car_animation 中创建并打包到 root 底部
        self.car_canvas = None

        # 粒子效果相关属性
        self.particles = []
        self.particle_colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEEAD']
        self.particle_animating = False

        # 绑定粒子效果事件到 UIManager 提供的 Canvas
        if self.canvas:
            self.canvas.bind("<Motion>", self.spawn_particles_on_move)

    def create_animation_area(self):
        """
        创建并初始化云朵动画。
        云朵将在由 UIManager 提供的 self.canvas 上显示。
        """
        try:
            # 加载并调整云朵图片大小，使其适应顶部较小的 canvas 区域
            cloud_base_height = 100  # 假设顶部 canvas 高度约60px，
            scaled_cloud_height = scaled_dimension(cloud_base_height,self.scale_factor)
            self.clouds_data = [
                {"img": ImageTk.PhotoImage(
                    Image.open(base_path / "images" / "云朵1.png").resize(
                        (int(scaled_cloud_height * 1.2), scaled_cloud_height))),
                    "y_pos": 0, "speed": scaled_dimension(2,self.scale_factor)},
                {"img": ImageTk.PhotoImage(
                    Image.open(base_path / "images" / "云朵2.png").resize(
                        (int(scaled_cloud_height * 1.2), scaled_cloud_height))),
                    "y_pos": 0, "speed": scaled_dimension(2,self.scale_factor)},
                {"img": ImageTk.PhotoImage(
                    Image.open(base_path / "images" / "云朵3.png").resize(
                        (int(scaled_cloud_height * 1.2), scaled_cloud_height))),
                    "y_pos": 0, "speed": scaled_dimension(2,self.scale_factor)}
            ]
        except Exception as e:
            messagebox.showerror("图片错误", f"无法加载云朵图片: {str(e)}")
            return

        # 强制更新 root 窗口以获取正确的宽度，用于计算云朵的起始和目标位置
        self.root.update_idletasks()
        root_width = self.root.winfo_width()

        # 云朵在 root 窗口宽度内随机出现和移动
        self.positions = [
            (0, root_width // 3),
            (root_width // 3, 2 * root_width // 3),
            (2 * root_width // 3, root_width)
        ]

        self.create_next_cloud()

    def create_next_cloud(self):
        """
        创建下一片云朵并开始其动画。
        确保操作在 self.canvas 之上。
        """
        if not self.canvas or not self.canvas.winfo_exists():
            return

        # 删除上一片活动的云朵
        if self.active_cloud:
            self.canvas.delete(self.active_cloud["id"])

        cloud_config = self.clouds_data[self.current_cloud_index]

        # 强制更新 root 窗口以获取正确宽度，用于云朵起始位置
        self.root.update_idletasks()
        start_x = self.root.winfo_width() + scaled_dimension(50,self.scale_factor)  # 从主窗口右侧外部开始

        # 目标X位置基于 root 窗口的宽度和预设的区域
        region = self.positions[self.current_cloud_index]
        target_x = random.randint(region[0], region[1] - cloud_config["img"].width())

        cloud_id = self.canvas.create_image(
            start_x, cloud_config["y_pos"], image=cloud_config["img"], anchor=tk.NW
        )
        self.active_cloud = {
            "id": cloud_id, "speed": cloud_config["speed"],
            "target_x": target_x, "width": cloud_config["img"].width(),
            "phase": "entering"  # "entering" 表示从右侧进入到目标位置，"leaving" 表示从目标位置向左侧离开
        }
        self.current_cloud_index = (self.current_cloud_index + 1) % len(self.clouds_data)
        self.move_clouds()

    def move_clouds(self):
        """
        动画云朵的移动。
        确保操作在 self.canvas 上。
        """
        if not self.active_cloud or not self.canvas or not self.canvas.winfo_exists():
            return

        x, y = self.canvas.coords(self.active_cloud["id"])
        speed = self.active_cloud["speed"]

        if self.active_cloud["phase"] == "entering":
            new_x = x - speed * 2  # 进入阶段速度快一点
            if new_x <= self.active_cloud["target_x"]:
                self.active_cloud["phase"] = "leaving"
                new_x = self.active_cloud["target_x"]  # 确保停在目标位置
        else:  # phase == "leaving"
            new_x = x - speed

        self.canvas.coords(self.active_cloud["id"], new_x, y)

        # 如果云朵完全离开左侧，则创建下一片云朵
        if new_x < -self.active_cloud["width"]:
            self.create_next_cloud()
        else:
            self.root.after(40, self.move_clouds)

    def spawn_particles_on_move(self, event):
        """
        在鼠标移动时生成少量粒子效果。
        粒子将在 self.canvas 上显示。
        """
        x, y = event.x, event.y
        for _ in range(4):  # 鼠标移动时生成少量粒子
            angle = np.random.uniform(0, 2 * np.pi)
            # 粒子速度缩放
            speed = np.random.uniform(1, 2) * self.scale_factor
            vx = speed * np.cos(angle)
            vy = speed * np.sin(angle) * 0.7 - 2 * self.scale_factor
            # 粒子大小缩放
            size = np.random.uniform(3, 6) * self.scale_factor
            shape = np.random.choice(["circle", "square"], p=[0.7, 0.3])
            if shape == "circle":
                particle = self.canvas.create_oval(
                    x - size, y - size, x + size, y + size,
                    fill=np.random.choice(self.particle_colors), outline=''
                )
            else:
                particle = self.canvas.create_rectangle(
                    x - size, y - size, x + size, y + size,
                    fill=np.random.choice(self.particle_colors), outline=''
                )
            self.particles.append({
                "id": particle, "x": x, "y": y, "vx": vx, "vy": vy, "life": 1.0,
                "size": size, "color": np.random.choice(self.particle_colors), "fade_color": "#FFA500"
            })
        if not self.particle_animating:
            self.particle_animating = True
            self.animate_particles()

    def animate_particles(self):
        """
        动画化粒子的移动和生命周期。
        确保操作在 self.canvas 上。
        """
        to_remove = []
        if not self.canvas or not self.canvas.winfo_exists():
            self.particle_animating = False
            return

        for p in self.particles:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            # 重力缩放
            p["vy"] += 0.2 * self.scale_factor
            # 模拟空气阻力
            p["vx"] *= 0.98
            p["vy"] *= 0.98
            p["life"] -= 0.02  # 减少生命值
            current_size = max(1, p["size"] * p["life"])  # 尺寸随存活时间减少

            # 粒子颜色渐变效果
            if p["life"] > 0.5:
                # 前半段生命周期从原始颜色到白色
                blend_ratio = (p["life"] - 0.5) * 2
                color = self.color_interpolate(p["color"], "#FFFFFF", blend_ratio)
            else:
                # 后半段生命周期从白色到褪色
                blend_ratio = (0.5 - p["life"]) * 2
                color = self.color_interpolate("#FFFFFF", p["fade_color"], blend_ratio)

            self.canvas.itemconfig(p["id"], fill=color)  # 在 self.canvas 上更新颜色
            self.canvas.coords(p["id"], p["x"] - current_size, p["y"] - current_size,
                               p["x"] + current_size, p["y"] + current_size)  # 在 self.canvas 上更新位置和大小

            # 如果粒子超出画布或生命值耗尽，则标记为移除
            if (p["x"] < -20 or p["x"] > self.canvas.winfo_width() + 20 or
                    p["y"] < -20 or p["y"] > self.canvas.winfo_height() + 20 or
                    p["life"] <= 0):
                to_remove.append(p)

        # 移除标记的粒子
        for p in to_remove:
            self.canvas.delete(p["id"])  # 在 self.canvas 上删除
            self.particles.remove(p)

        # 如果还有粒子，继续动画
        if self.particles:
            self.particle_animating = True
            self.root.after(40, self.animate_particles)
        else:
            self.particle_animating = False  # 所有粒子都已消失，停止动画循环

    def color_interpolate(self, color1, color2, ratio):
        """在两种十六进制颜色之间进行插值"""
        rgb1 = hex_to_rgb(color1)
        rgb2 = hex_to_rgb(color2)

        # 对每个RBG分量进行插值
        interpolated_rgb = (
            max(0, min(255, int(rgb1[0] + (rgb2[0] - rgb1[0]) * ratio))),
            max(0, min(255, int(rgb1[1] + (rgb2[1] - rgb1[1]) * ratio))),
            max(0, min(255, int(rgb1[2] + (rgb2[2] - rgb1[2]) * ratio)))
        )
        return rgb_to_hex(interpolated_rgb)

    def create_car_animation(self):
        # 加载小车图片
        if not hasattr(self, 'car_image') or self.car_image is None:
            try:
                car_original_width = 100
                car_original_height = 70
                self.scaled_car_width = scaled_dimension(car_original_width,self.scale_factor)
                self.scaled_car_height = scaled_dimension(car_original_height,self.scale_factor)
                car_img = Image.open(base_path / "images" / "汽车.png").resize(
                    (self.scaled_car_width, self.scaled_car_height)
                )
                self.car_image = ImageTk.PhotoImage(car_img)
            except Exception as e:
                messagebox.showerror("图片错误", f"无法加载小车图片: {str(e)}")
                return

        # 确保car_canvas已创建
        if not hasattr(self, 'car_canvas') or self.car_canvas is None or not self.car_canvas.winfo_exists():
            # 修改画布的默认尺寸设置，确保在小屏幕上也有合适的尺寸
            default_width = max(scaled_dimension(800,self.scale_factor), 600)  # 最小600像素宽度
            default_height = max(scaled_dimension(100,self.scale_factor), 80)  # 最小80像素高度

            self.car_canvas = tk.Canvas(
                self.root,
                width=default_width,
                height=default_height,
                bg=self.bg_color,
                highlightthickness=0
            )
            self.car_canvas.pack(fill=tk.BOTH, expand=True, side=tk.BOTTOM, pady=0)

        # 强制更新UI确保获取正确尺寸
        self.root.update_idletasks()
        self.car_canvas.update_idletasks()

        # 获取正确的画布宽度
        canvas_width = self.car_canvas.winfo_width()

        # 如果获取到的宽度异常小，使用窗口宽度作为参考
        if canvas_width < 100:
            try:
                canvas_width = self.root.winfo_width()
                if canvas_width < 100:
                    canvas_width = 800  # 最后的默认值
            except:
                canvas_width = 800

        # 设置初始位置
        self.car_pos = canvas_width + scaled_dimension(50,self.scale_factor)

        # 创建小车图像
        self.car = self.car_canvas.create_image(
            self.car_pos, scaled_dimension(10,self.scale_factor), image=self.car_image, anchor=tk.NW
        )

        # 初始化固定数量的拖尾线段，而不是每次都创建新的
        self.trail_lines = []
        for _ in range(self.max_trail_lines * len(self.rainbow_colors)):  # 预创建最大数量的线段
            line = self.car_canvas.create_line(0, 0, 0, 0, fill="", width=0, tags="trail", state=tk.HIDDEN)
            self.trail_lines.append(line)
        self.current_trail_line_index = 0

        self.animate_car()

    def animate_car(self):
        """
        动画化小车的移动和拖尾效果。
        确保所有操作都在 self.car_canvas 上进行。
        """
        # 确保 car_canvas 存在且已准备好
        if not self.car_canvas or not self.car_canvas.winfo_exists():
            return

        # 小车向左移动
        self.car_pos -= self.car_speed
        self.car_canvas.coords(self.car, self.car_pos, scaled_dimension(10,self.scale_factor))

        # 修改拖尾创建的频率控制 - 让拖尾更密集
        # 调整频率，可能不再是直接创建，而是更新现有线条
        # 控制拖尾的密度，每次移动时都尝试更新一些拖尾线条
        self.create_trail()  # 现在 create_trail 会复用线条而不是创建新线条

        # 获取当前画布宽度
        canvas_width = self.car_canvas.winfo_width()
        if canvas_width < 100:  # 防止异常值
            canvas_width = 800

        # 如果小车完全离开左侧，则重置其位置到 car_canvas 的右侧外部
        if self.car_pos < -scaled_dimension(100,self.scale_factor):
            self.car_pos = canvas_width + scaled_dimension(50,self.scale_factor)
            # 清除所有拖尾，或将其重置为隐藏，以避免旧拖尾突然出现
            for line_id in self.trail_lines:
                self.car_canvas.itemconfig(line_id, state=tk.HIDDEN)

        # 固定的动画延迟，旨在更流畅的帧率
        delay = 30  # 目标约 33ms/frame = 30 FPS，兼顾流畅性和性能
        self.root.after(delay, self.animate_car)

    def create_trail(self):
        """
        在小车后面创建彩虹拖尾线段。
        现在复用预创建的线段，并通过更新其坐标来模拟拖尾效果。
        确保操作在 self.car_canvas 上进行。
        """
        if not self.car_canvas or not self.car_canvas.winfo_exists():
            return

        car_y = scaled_dimension(10,self.scale_factor)  # 小车顶部位置
        car_center_y = car_y + self.scaled_car_height / 2  # 小车中心Y坐标

        canvas_width = self.car_canvas.winfo_width()
        canvas_height = self.car_canvas.winfo_height()

        if canvas_width < 100:
            canvas_width = scaled_dimension(800,self.scale_factor)

        min_trail_length = max(scaled_dimension(80,self.scale_factor), int(canvas_width * 0.1))
        max_trail_length = max(scaled_dimension(200,self.scale_factor), int(canvas_width * 0.1))
        base_trail_length = min(max_trail_length, max(min_trail_length, int(canvas_width * 0.15)))

        # 为每种彩虹颜色创建一条平行线段
        for i, color in enumerate(self.rainbow_colors):
            offset = (i - 3) * self.line_spacing
            y = car_center_y + offset

            y = max(self.line_spacing, min(canvas_height - self.line_spacing, y))

            trail_start_x = self.car_pos + self.scaled_car_width  # 从小车中心附近开始
            trail_end_x = self.car_pos + self.scaled_car_width  + base_trail_length  # 向右延伸，模拟拖尾

            # 每次动画循环时，为每种颜色使用一个循环的线段索引
            # 这样可以复用有限的线段对象
            line_idx_offset = i * (self.max_trail_lines // len(self.rainbow_colors))
            line_id = self.trail_lines[(self.current_trail_line_index + line_idx_offset) % self.max_trail_lines]

            # 如果线段完全超出画布，则隐藏它，而不是更新其坐标
            if trail_end_x < 0 or trail_start_x > canvas_width:
                self.car_canvas.itemconfig(line_id, state=tk.HIDDEN)
                continue

            # 裁剪拖尾线段到画布范围内
            clipped_start_x = max(0, trail_start_x)
            clipped_end_x = min(canvas_width, trail_end_x)

            if clipped_end_x - clipped_start_x < 5:  # 如果裁剪后线段太短，则隐藏
                self.car_canvas.itemconfig(line_id, state=tk.HIDDEN)
                continue

            # 更新现有线段的坐标和颜色，使其可见
            self.car_canvas.coords(line_id, clipped_start_x, y, clipped_end_x, y)
            self.car_canvas.itemconfig(line_id, fill=color, width=max(1, scaled_dimension(3,self.scale_factor)), state=tk.NORMAL)

        # 每次创建拖尾时，递增当前线段索引，实现循环使用
        self.current_trail_line_index = (self.current_trail_line_index + 1) % (
                    self.max_trail_lines // len(self.rainbow_colors))
