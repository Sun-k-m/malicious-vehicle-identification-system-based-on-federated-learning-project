import tkinter as tk
from ttkbootstrap.widgets import Progressbar
import random
import math
from pathlib import Path

base_path = Path(__file__).parent

class LoadingScreen:
    def __init__(self, root_window):
        """
            初始化加载屏幕。

            Args:
                root_window (tk.Tk or ttkbootstrap.Window): 应用程序的主窗口实例。
        """
        self.root = root_window
        self.loading_win = None
        self.bg_canvas = None
        self.load_progress = None
        self.progress_label = None
        self.stars = []
        self.meteors = []
        self.progress_value = 0
        self.target_progress = 0
        self.neon_border_width = 2
        self.neon_direction = 1

    def create_loading_screen(self):
        """
            创建并显示加载屏幕窗口。
            设置窗口样式，绘制背景、月亮和星星动画，
            创建加载进度条和进度文本，并添加版权信息。
        """
        self.loading_win = tk.Toplevel(self.root)
        self.center_window(self.loading_win, 480, 320)
        self.loading_win.overrideredirect(True)

        self.bg_canvas = tk.Canvas(self.loading_win, width=480, height=320, bg="#191970", highlightthickness=0)
        self.bg_canvas.pack(fill=tk.BOTH, expand=True)
        self.bg_canvas.config(bg="#69A9F2")

        self.draw_moon()
        self.create_stars()
        self.animate_stars()

        loading_label = tk.Label(
            self.bg_canvas,
            text="系统初始化中...",
            font=("微软雅黑", 16, "bold"),
            fg="#ECF0F1",
            bg="#191970"
        )
        self.bg_canvas.create_window(240, 60, window=loading_label)

        self.load_progress = Progressbar(
            self.bg_canvas,
            orient='horizontal',
            mode='determinate',
            length=250,
            style="Neon.Horizontal.TProgressbar"
        )
        self.bg_canvas.create_window(240, 160, window=self.load_progress)

        self.animate_neon_border()

        self.progress_label = tk.Label(
            self.bg_canvas,
            text="0%",
            font=("微软雅黑", 10),
            fg="#ECF0F1",
            bg="#191970"
        )
        self.bg_canvas.create_window(240, 210, window=self.progress_label)

        copyright_label = tk.Label(
            self.bg_canvas,
            text="恶意车辆识别系统 | Copyright © 2025 ",
            font=("微软雅黑", 9),
            fg="#7B68EE",
            bg="#191970"
        )
        self.bg_canvas.create_window(240, 280, window=copyright_label)

        self.animate_progress()
        self.loading_win.update()

    def create_stars(self):
        """
            在背景画布上创建随机分布的星星。
            星星的数量、位置、大小和亮度均随机生成。
        """
        num_stars = 150
        for _ in range(num_stars):
            x = random.randint(0, 479)
            y = random.randint(0, 319)
            size = random.randint(1, 2)
            brightness = random.randint(200, 255)
            color = f'#%02x%02x%02x' % (brightness, brightness, brightness)
            star = self.bg_canvas.create_oval(x - size, y - size, x + size, y + size, fill=color, outline="")
            self.stars.append(star)

    def create_meteor(self):
        """
            创建一个流星动画对象。
            流星的起始位置、角度、速度和长度随机生成。

            返回:
                dict: 包含流星身体ID、位置、角度和速度的字典。
        """
        start_x = random.randint(0, 150)
        start_y = random.randint(-50, 0)
        angle_min = math.radians(40)
        angle_max = math.radians(50)
        angle = random.uniform(angle_min, angle_max)
        speed = random.uniform(2, 2.5)
        length = random.randint(70, 75)
        fixed_width = 2
        meteor_body = [{"id": self.bg_canvas.create_line(
            start_x, start_y, start_x + length * math.cos(angle),
            start_y + length * math.sin(angle), fill='#ffffff', width=fixed_width),
            "length": length}]
        return {"body": meteor_body, "x": float(start_x), "y": float(start_y),
                "angle": angle, "speed": speed}

    def draw_moon(self):
        """
            在背景画布上绘制月亮图案。
            月亮由两个重叠的圆形组成，模拟月相效果。
        """
        moon_x, moon_y = 420, 50
        radius = 32
        outer_circle = (moon_x - radius, moon_y - radius, moon_x + radius, moon_y + radius)
        inner_circle_offset = -14
        inner_circle = (moon_x - radius + inner_circle_offset, moon_y - radius,
                        moon_x + radius + inner_circle_offset, moon_y + radius)
        self.bg_canvas.create_oval(*outer_circle, fill="#FFFAF0", outline="")
        self.bg_canvas.create_oval(*inner_circle, fill="#69A9F2", outline="")

    def animate_stars(self):
        """
            更新流星动画。
            计算流星的新位置，更新画布上的流星线条，并移除超出屏幕的流星。
            根据最大流星数量创建新的流星。
        """
        dt = 0.8
        new_meteors = []
        max_meteors = 1
        if not tk.Toplevel.winfo_exists(self.loading_win):
            return

        for meteor in self.meteors:
            if not meteor["body"]:
                continue
            meteor["x"] += meteor["speed"] * math.cos(meteor["angle"]) * dt
            meteor["y"] += meteor["speed"] * math.sin(meteor["angle"]) * dt
            for segment in meteor["body"]:
                try:
                    self.bg_canvas.coords(segment["id"], meteor["x"], meteor["y"],
                                          meteor["x"] + segment["length"] * math.cos(meteor["angle"]),
                                          meteor["y"] + segment["length"] * math.sin(meteor["angle"]))
                except tk.TclError:
                    pass
            if meteor["y"] <= 350 and meteor["body"]:
                new_meteors.append(meteor)
            else:
                for segment in meteor["body"]:
                    try:
                        self.bg_canvas.delete(segment["id"])
                    except tk.TclError:
                        pass
        self.meteors = new_meteors
        while len(self.meteors) < max_meteors and tk.Toplevel.winfo_exists(self.loading_win):
            self.meteors.append(self.create_meteor())
        self.root.after(30, self.animate_stars)

    def animate_neon_border(self):
        """
            实现进度条的霓虹边框动画效果。
            周期性地改变边框的宽度，模拟霓虹灯的呼吸效果。
        """
        if self.loading_win and tk.Toplevel.winfo_exists(self.loading_win):
            self.neon_border_width += 0.2 * self.neon_direction
            if self.neon_border_width > 3 or self.neon_border_width < 1:
                self.neon_direction *= -1

            self.bg_canvas.delete("neon_border")
            offset = int(self.neon_border_width)
            self.bg_canvas.create_rectangle(
                240 - 125 - offset, 160 - 10 - offset,
                240 + 125 + offset, 160 + 10 + offset,
                outline="#FFE0E5", width=self.neon_border_width, tags="neon_border", fill=""
            )
            self.root.after(30, self.animate_neon_border)


    def animate_progress(self):
        """
            平滑地更新进度条的显示值。
            使进度条从当前值逐渐趋近目标值，并更新进度百分比文本。
        """
        if self.loading_win and tk.Toplevel.winfo_exists(self.loading_win):
            if self.progress_value < self.target_progress:
                self.progress_value += (self.target_progress - self.progress_value) * 0.15
                self.load_progress['value'] = self.progress_value
                self.progress_label.config(text=f"{int(self.progress_value)}%")
            self.root.after(30, self.animate_progress)

    def update_progress(self, value, description):
        """
            更新加载进度条的显示值和描述文本。

            Args:
                value (int): 目标进度百分比。
                description (str): 当前加载步骤的描述文本。
        """
        self.root.after(0, lambda: [
            setattr(self, 'target_progress', value),
            self.progress_label.config(text=f"{int(value)}% - {description}")
        ])

    def destroy_loading_screen(self):
        """
            销毁加载屏幕窗口。
        """
        if self.loading_win:
            self.loading_win.destroy()

    def center_window(self, win, width, height):
        """
            将指定窗口居中显示在屏幕上。

            变量:
                win (tk.Toplevel or tk.Tk): 需要居中的窗口实例。
                width (int): 窗口的宽度。
                height (int): 窗口的高度。
        """
        screen_width = win.winfo_screenwidth()
        screen_height = win.winfo_screenheight()
        x = int((screen_width - width) / 2)
        y = int((screen_height - height) / 2)
        win.geometry(f"{width}x{height}+{x}+{y}")