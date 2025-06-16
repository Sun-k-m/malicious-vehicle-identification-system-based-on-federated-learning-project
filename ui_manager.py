import tkinter as tk
from ttkbootstrap.widgets import Frame, LabelFrame, Entry, Label, Progressbar
from tkinter import filedialog, messagebox
from collections import defaultdict
from typing import Dict
from pathlib import Path
import json
import random
import tkinter.font
from utils import create_color_transition, scaled_font, scaled_dimension

base_path = Path(__file__).parent


class UIManager:
    def __init__(self, root, app_instance, pygame_module=None, scale_factor=1.0):
        """
            初始化用户界面管理器

            root: Tkinter根窗口实例
            app_instance: 应用程序主实例
            pygame_module: Pygame模块，用于音效播放
            scale_factor: 界面元素的缩放因子
        """
        self.root = root
        self.app = app_instance
        self.style = root.style
        self.pygame = pygame_module
        self.scale_factor = scale_factor  # 存储缩放因子

        # 定义字体大小的基准值
        self.base_font_size = 12
        self.header_font_size = 14
        self.button_font_size = 11
        self.label_font_size_small = 12  # 用于输入字段标签的字体大小

        # 统一管理占位符的颜色样式
        self.placeholder_styles = {
            "normal": {"foreground": "black"},  # 用户输入文本的颜色
            "placeholder": {"foreground": "grey"}  # 占位符文本的颜色
        }

        self.label_colors = {
            "normal_bg": "#6DD5A7",
            "normal_fg": "#FFFFFF",
            "hover_bg": "#E8F5E9",
            "hover_fg": "#3F3F3F"
        }
        self.button_colors = {
            "normal_bg": "#378DFC",
            "normal_fg": "#FFFFFF",
            "hover_bg": "#C3E3FF",
            "hover_fg": "#3F3F3F"
        }
        self.save_button_colors = {
            "normal_bg": "#28A745",
            "normal_fg": "#FFFFFF",
            "hover_bg": "#C8E6C9",
            "hover_fg": "#3F3F3F"
        }
        self.transition_steps = 15
        self.transition_delay = 5
        self.bg_color = self.root.style.colors.bg

        self.main_frame = None
        self.progress = None
        self.result_text = None
        self.file_path = tk.StringVar()
        self.input_vars = {}
        self.entries = {}
        self.results = []
        self.vehicle_attack_counts = defaultdict(int)
        self.last_saved_record = None
        self.last_analysis_result = None
        self.string_vars = {}
        self.manual_input_entries = self.entries.copy()
        self.manual_input_vars: Dict[str, tk.StringVar] = {}

        # 修正 input_fields_config 的默认值类型，使其与 type 匹配
        self.input_fields_config = {
            "rcvTime": {"label": "接收时间", "default": 0.0, "type": float},
            "sendTime": {"label": "发送时间", "default": 0.0, "type": float},
            "sender": {"label": "发送者ID", "default": 0, "type": int},
            "vehicleId": {"label": "车辆ID", "default": 0, "type": int},
            "EventID": {"label": "事件ID", "default": 0, "type": int},
            "pos": {"label": "位置 (x,y,z)", "default": [0.0, 0.0, 0.0], "type": list},
            "spd": {"label": "速度", "default": [0.0, 0.0, 0.0], "type": list},
            "acl": {"label": "加速度", "default": [0.0, 0.0, 0.0], "type": list},
            "hed": {"label": "航向", "default": [0.0, 0.0, 0.0], "type": list},
            "pos_noise": {"label": "位置噪声", "default": [0.0, 0.0, 0.0], "type": list},
            "spd_noise": {"label": "速度噪声", "default": [0.0, 0.0, 0.0], "type": list},
            "acl_noise": {"label": "加速度噪声", "default": [0.0, 0.0, 0.0], "type": list},
            "hed_noise": {"label": "航向噪声", "default": [0.0, 0.0, 0.0], "type": list},
            "sender_GPS": {"label": "北斗(GPS)位置", "default": [0.0, 0.0, 0.0], "type": list},
            "currentDirection": {"label": "当前方向", "default": [0.0, 0.0, 0.0], "type": list},
            "laneIndex": {"label": "车道索引", "default": 0, "type": int},
            "lanePosition": {"label": "车道位置", "default": 0, "type": int},
            "maxSpeed": {"label": "最大速度(km/h)", "default": 0, "type": int},
            "maxDeceleration": {"label": "最大减速度(m/s²)", "default": 0, "type": int},
            "hazardOccurrencePercentage": {"label": "危险概率(%)", "default": 0, "type": int},
        }

        self._animation_canvas = None
        self._car_animation_canvas = None
        self._particles = []

    def animate_color(self, widget, bg_colors, fg_colors, step=0):
        """
            执行控件背景和前景色的渐变动画

            widget: 需要动画的Tkinter控件
            bg_colors: 背景颜色渐变列表
            fg_colors: 前景颜色渐变列表
            step: 动画当前步骤
        """
        if step < len(bg_colors):
            widget.config(bg=bg_colors[step], fg=fg_colors[step])
            self.root.after(self.transition_delay, self.animate_color, widget, bg_colors, fg_colors, step + 1)

    def create_hover_effect(self, widget, color_config):
        """
            为控件创建鼠标悬停效果，包括颜色渐变

            widget: 需要添加悬停效果的Tkinter控件
            color_config: 包含正常和悬停状态颜色配置的字典
        """
        def get_current_color():
            return widget.cget("bg"), widget.cget("fg")

        def generate_transition(start_bg, start_fg, end_bg, end_fg):
            bg_colors = create_color_transition(start_bg, end_bg, self.transition_steps)
            fg_colors = create_color_transition(start_fg, end_fg, self.transition_steps)
            return bg_colors, fg_colors

        def on_enter(e):
            current_bg, current_fg = get_current_color()
            enter_bg, enter_fg = generate_transition(current_bg, current_fg,
                                                     color_config["hover_bg"], color_config["hover_fg"])
            self.animate_color(widget, enter_bg, enter_fg)

        def on_leave(e):
            current_bg, current_fg = get_current_color()
            leave_bg, leave_fg = generate_transition(current_bg, current_fg,
                                                     color_config["normal_bg"], color_config["normal_fg"])
            self.animate_color(widget, leave_bg, leave_fg)

        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
        widget.config(cursor="hand2")

    def create_widgets(self):
        """
        创建应用程序的主界面控件
        这包括设置整体布局、创建各个功能区域（如文件分析区、实时数据输入区、分析结果显示区），
        并初始化相关的UI元素（如按钮、输入框、文本框、进度条和画布）
        """
        # 初始化一个Tkinter画布，用于显示动画效果
        # 设置画布高度，根据缩放因子调整，背景色使用当前主题背景色，无高亮边框
        self._animation_canvas = tk.Canvas(
            self.root,
            height=scaled_dimension(100, self.scale_factor),
            bg=self.bg_color,
            highlightthickness=0
        )
        # 将动画画布打包到主窗口顶部，填充水平方向，无垂直填充
        self._animation_canvas.pack(fill=tk.X, pady=0)
        # 为画布绑定鼠标左键点击事件，触发播放云朵点击音效
        self._animation_canvas.bind("<Button-1>", self.play_cloud_click_sound)

        # 创建主框架，作为所有主要UI区域的容器
        self.main_frame = Frame(self.root)
        # 将主框架打包到主窗口中，填充所有可用空间，并设置内外边距
        self.main_frame.pack(fill=tk.BOTH, expand=True,
                             padx=scaled_dimension(50, self.scale_factor),
                             pady=(0, scaled_dimension(1, self.scale_factor)))

        # 创建一个LabelFrame，用于包含文件选择相关的控件
        # 设置其样式为"info"，并自定义标签文本、字体、前景色、背景色和内边距
        file_frame = LabelFrame(
            self.main_frame, bootstyle="info",
            labelwidget=Label(text="文件选择", font=scaled_font(self.header_font_size, self.scale_factor) + ("bold",),
                              foreground="#1874CD", background=self.style.colors.bg,
                              padding=scaled_dimension(5, self.scale_factor))
        )
        # 将文件选择框架打包到主框架中，填充水平方向，并设置垂直内边距
        file_frame.pack(fill=tk.X, pady=scaled_dimension(2, self.scale_factor),
                        ipady=scaled_dimension(10, self.scale_factor))

        # 创建一个Entry控件，用于显示用户选择的文件路径
        # 绑定一个StringVar来动态更新文本，设置宽度并应用样式
        Entry(file_frame, textvariable=self.file_path, width=scaled_dimension(80, self.scale_factor),
              bootstyle="primary").pack(side=tk.LEFT, padx=scaled_dimension(15, self.scale_factor),
                                        fill=tk.X, expand=True)

        # 创建一个“选择文件”按钮
        # 设置文本、点击命令、背景色、前景色、字体、边框样式和活动状态颜色
        browse_btn = tk.Button(
            file_frame, text="选择文件", command=self.app.browse_file,
            bg=self.button_colors["normal_bg"], fg=self.button_colors["normal_fg"],
            font=scaled_font(self.button_font_size, self.scale_factor),
            relief="flat", borderwidth=0,
            activebackground=self.button_colors["hover_bg"], activeforeground=self.button_colors["hover_fg"]
        )
        # 将“选择文件”按钮打包到文件选择框架中，靠左对齐，并设置水平外边距
        browse_btn.pack(side=tk.LEFT, padx=scaled_dimension(15, self.scale_factor))
        # 为“选择文件”按钮创建鼠标悬停时的颜色渐变效果
        self.create_hover_effect(browse_btn, self.button_colors)

        # 创建一个“开始分析”按钮
        # 设置文本、点击命令、背景色、前景色、字体、边框样式和活动状态颜色
        analyze_file_btn = tk.Button(
            file_frame, text="开始分析", command=self.app.analyze_file,
            bg=self.button_colors["normal_bg"], fg=self.button_colors["normal_fg"],
            font=scaled_font(self.button_font_size, self.scale_factor),
            relief="flat", borderwidth=0,
            activebackground=self.button_colors["hover_bg"], activeforeground=self.button_colors["hover_fg"]
        )
        # 将“开始分析”按钮打包到文件选择框架中，靠左对齐，并设置水平外边距
        analyze_file_btn.pack(side=tk.LEFT, padx=scaled_dimension(15, self.scale_factor))
        # 为“开始分析”按钮创建鼠标悬停时的颜色渐变效果
        self.create_hover_effect(analyze_file_btn, self.button_colors)

        # 创建一个LabelFrame，用于包含实时数据输入相关的控件
        # 设置其样式为"info"，并自定义标签文本、字体、前景色、背景色和内边距
        input_frame = LabelFrame(
            self.main_frame, bootstyle="info",
            labelwidget=Label(text="实时数据输入",
                              font=scaled_font(self.header_font_size, self.scale_factor) + ("bold",),
                              foreground="#7B68EE", background=self.style.colors.bg,
                              padding=scaled_dimension(5, self.scale_factor))
        )
        # 将实时数据输入框架打包到主框架中，填充水平方向，并设置垂直内边距
        input_frame.pack(fill=tk.X, pady=scaled_dimension(5, self.scale_factor),
                         ipady=scaled_dimension(15, self.scale_factor))
        # 调用方法在input_frame内部创建具体的输入字段
        self.create_input_fields(input_frame)

        # 创建一个LabelFrame，用于显示分析结果
        # 设置其样式为"info"，固定高度，并自定义标签文本、字体、前景色、背景色和内边距
        result_frame = LabelFrame(
            self.main_frame, bootstyle="info", height=scaled_dimension(150, self.scale_factor),
            labelwidget=Label(text="分析结果", font=scaled_font(self.header_font_size, self.scale_factor) + ("bold",),
                              foreground="#7B68EE", background=self.style.colors.bg,
                              padding=scaled_dimension(5, self.scale_factor))
        )
        # 将分析结果框架打包到主框架中，填充所有可用空间，并设置垂直外边距
        result_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 0))

        # 创建一个进度条，用于显示文件分析进度
        # 设置方向为水平，模式为确定性，样式为"success-striped"，最大值为100
        self.progress = Progressbar(
            result_frame, orient='horizontal', mode='determinate',
            bootstyle="success-striped", maximum=100
        )
        # 初始状态下隐藏进度条
        self.progress.pack_forget()

        # 创建一个Text控件，用于显示详细的分析结果文本
        # 设置高度，根据内容自动换行，背景色、前景色使用当前主题颜色，并应用缩放后的字体
        self.result_text = tk.Text(
            result_frame, height=scaled_dimension(8, self.scale_factor),
            wrap=tk.WORD,
            bg=self.style.colors.inputbg, fg=self.style.colors.inputfg,
            font=scaled_font(self.base_font_size, self.scale_factor)
        )
        # 将结果文本区域打包到分析结果框架中，填充所有可用空间，并设置内外边距
        self.result_text.pack(fill=tk.BOTH, expand=True,
                              padx=scaled_dimension(20, self.scale_factor),
                              pady=scaled_dimension(10, self.scale_factor))

    def play_cloud_click_sound(self, event):
        if not self.pygame:
            return

        try:
            sound_path = base_path / "sounds" / "click.mp3"
            if sound_path.exists():
                self.pygame.mixer.Sound(str(sound_path)).play()
            else:
                messagebox.showerror("错误", f"音效文件 {sound_path} 不存在")
        except Exception as e:
            messagebox.showerror("错误", f"音效播放失败: {str(e)}")

    def clear_previous_results(self):
        """清除结果和输入框"""
        self.clear_results_only()
        for field, entry in self.entries.items():
            placeholder = self.get_field_placeholder(field)
            entry.delete(0, tk.END)
            # Re-add placeholder using the dedicated method
            self._add_placeholder(entry, placeholder)

    def show_progress(self):
        self.result_text.pack_forget()
        self.progress.pack(fill=tk.X, padx=scaled_dimension(20, self.scale_factor),
                           pady=scaled_dimension(20, self.scale_factor))
        self.root.update_idletasks()

    def hide_progress(self):
        self.progress.pack_forget()
        self.result_text.pack(fill=tk.BOTH, expand=True)
        self.root.update_idletasks()

    def handle_analysis_error(self, message="❌ 分析过程中发生错误"):
        self.hide_progress()
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, message, "line_spacing")
        self.result_text.config(state=tk.DISABLED)

    def _add_placeholder(self, entry, placeholder_text):
        """为输入框添加占位符功能"""
        # Store the placeholder text directly on the entry widget
        entry.placeholder_text = placeholder_text
        entry.insert(0, placeholder_text)
        entry.config(foreground=self.placeholder_styles["placeholder"]["foreground"])  # 初始为灰色占位符样式

        # 绑定焦点事件
        entry.bind('<FocusIn>', self._on_entry_focusin)
        entry.bind('<FocusOut>', self._on_entry_focusout)

    def _on_entry_focusin(self, event):
        """处理输入框获得焦点事件"""
        entry = event.widget
        # 只要当前文本是占位符文本，就清除它
        if entry.get() == entry.placeholder_text:
            entry.delete(0, tk.END)
            entry.config(foreground=self.placeholder_styles["normal"]["foreground"])

    def _on_entry_focusout(self, event):
        """处理输入框失去焦点事件"""
        entry = event.widget
        if not entry.get().strip():  # 如果输入框为空
            entry.insert(0, entry.placeholder_text)
            entry.config(foreground=self.placeholder_styles["placeholder"]["foreground"])

    def get_field_placeholder(self, field):
        """
            获取指定字段的占位符文本

            field: 字段名称
            返回: 字段的占位符字符串
        """
        config = self.input_fields_config.get(field)
        if config:
            default_value = config.get("default")
            if isinstance(default_value, list):
                # 将列表转换为逗号分隔的字符串，例如 [0.0, 0.0, 0.0] -> "0.0,0.0,0.0"
                return ','.join(map(str, default_value))
            return str(default_value)  # 确保所有默认值都转换为字符串
        return '0'

    def create_input_fields(self, parent):
        """
        在指定的父控件中创建实时数据输入字段

        parent: 包含输入字段的Tkinter控件
        """
        fields = []
        # 遍历配置字典，收集每个输入字段的键、显示标签和占位符文本
        for key, config in self.input_fields_config.items():
            placeholder_str = self.get_field_placeholder(key)
            fields.append((key, config["label"], placeholder_str))

        # 初始化字典，用于存储每个输入字段的StringVar实例和Entry控件实例
        self.input_vars = {}
        self.entries = {}

        # 创建一个Frame作为输入字段的网格布局容器
        input_grid = Frame(parent)
        # 将网格容器打包到父控件中，填充所有可用空间，并设置内外边距
        input_grid.pack(fill=tk.BOTH, expand=True,
                        padx=scaled_dimension(20, self.scale_factor),
                        pady=scaled_dimension(5, self.scale_factor))

        # 获取用于标签的字体对象，以便精确测量文本宽度，确保布局对齐
        label_font_obj = tkinter.font.Font(family=scaled_font(self.label_font_size_small, self.scale_factor)[0],
                                           size=scaled_font(self.label_font_size_small, self.scale_factor)[1])

        max_label_pixel_width = 0
        # 计算所有标签文本的最大像素宽度，以便后续统一设置标签列宽
        for _, label_text, _ in fields:
            text_pixel_width = label_font_obj.measure(label_text)
            if text_pixel_width > max_label_pixel_width:
                max_label_pixel_width = text_pixel_width

        # 根据计算出的最大标签宽度，加上额外填充，确定统一的标签列像素宽度
        # 确保有一个合理的最小宽度，以适应不同缩放因子
        unified_label_pixel_width = max(scaled_dimension(20, self.scale_factor),
                                        max_label_pixel_width + scaled_dimension(20, self.scale_factor))

        # 确定输入框列的统一像素宽度，基于标签宽度的比例
        unified_entry_pixel_width = max(scaled_dimension(20, self.scale_factor),
                                        int(unified_label_pixel_width * (5 / 6)))
        # 设置外部 input_grid 的网格列权重，使其在窗口拉伸时能够均匀扩展
        for col_idx in range(4):
            input_grid.columnconfigure(col_idx, weight=1, uniform="col_group")

        # 遍历所有字段配置，创建并布局对应的标签和输入框
        for idx, (field, label_text, placeholder) in enumerate(fields):
            # 计算当前字段在4列网格中的行和列索引
            row = idx // 4
            col = idx % 4

            # 为每个标签和输入框对创建一个独立的Frame，以便更好地控制布局
            frame = Frame(input_grid)
            # 将该Frame放置到网格的指定位置，并使其填充单元格，设置内外部间距
            frame.grid(row=row, column=col, sticky=tk.NSEW,
                       padx=scaled_dimension(5, self.scale_factor),
                       pady=scaled_dimension(10, self.scale_factor))

            # 配置frame内部的列：标签列固定宽度，输入框列允许拉伸
            frame.columnconfigure(0, weight=0, minsize=unified_label_pixel_width)  # 标签列固定宽度
            frame.columnconfigure(1, weight=1)  # 输入框列允许拉伸
            # 确保行也能响应拉伸，使得frame内的内容垂直居中或按需排列
            frame.rowconfigure(0, weight=1)

            # 创建标签控件
            label_widget = tk.Label(
                frame, text=label_text,
                anchor="center",  # 文本居中对齐
                font=scaled_font(self.label_font_size_small, self.scale_factor),  # 应用缩放后的字体
                relief="flat", borderwidth=0, highlightthickness=0  # 无边框样式
            )
            # 将标签放置在内部Frame的第一列，并使其水平填充，设置右侧内边距和垂直内填充
            label_widget.grid(row=0, column=0, sticky='ew',
                              padx=(0, scaled_dimension(8, self.scale_factor)),
                              ipady=scaled_dimension(5, self.scale_factor))
            # 设置标签的背景色和前景色为正常状态颜色
            label_widget.config(
                background=self.label_colors["normal_bg"],
                foreground=self.label_colors["normal_fg"]
            )
            # 为标签添加鼠标悬停效果
            self.create_hover_effect(label_widget, self.label_colors)

            # 创建输入框控件
            var = tk.StringVar()  # 为每个Entry创建一个StringVar来管理其文本内容
            entry = Entry(frame, textvariable=var, bootstyle="info")  # 设置输入框的textvariable并应用样式
            # 将输入框放置在内部Frame的第二列，并使其水平填充
            entry.grid(row=0, column=1, sticky='ew')

            # 调用辅助方法为输入框添加占位符功能
            self._add_placeholder(entry, placeholder)

            # 将StringVar和Entry控件实例存储到字典中，以便后续通过字段名访问
            self.input_vars[field] = var
            self.entries[field] = entry

        # 创建一个Frame作为按钮的容器
        button_frame = Frame(parent)
        # 将按钮容器打包到父控件底部，并设置垂直外边距
        button_frame.pack(pady=scaled_dimension(10, self.scale_factor))

        # 创建一个“保存并分析”按钮
        # 设置文本、点击命令、背景色、前景色、字体、边框样式、活动状态颜色和尺寸
        analyze_btn = tk.Button(
            button_frame, text="保存并分析", command=self.save_and_analyze,
            bg=self.button_colors["normal_bg"], fg=self.button_colors["normal_fg"],
            font=scaled_font(13, self.scale_factor),
            relief="flat", borderwidth=0,
            activebackground=self.button_colors["hover_bg"], activeforeground=self.button_colors["hover_fg"],
            width=scaled_dimension(20, self.scale_factor),
            height=scaled_dimension(1, self.scale_factor)
        )
        # 将“保存并分析”按钮打包到按钮容器中，靠左对齐，并设置水平外边距
        analyze_btn.pack(side=tk.LEFT, padx=scaled_dimension(10, self.scale_factor))
        # 为“保存并分析”按钮创建鼠标悬停时的颜色渐变效果
        self.create_hover_effect(analyze_btn, self.button_colors)

    def save_record(self):
        try:
            input_data = self.get_manual_input_data()
            record = self.app.data_persistence_manager.generate_complete_record(input_data)
            self.app.data_persistence_manager.save_record(record)
            self.last_saved_record = record
            messagebox.showinfo("成功", "记录已成功保存到 saved_records.json")
        except ValueError as e:
            messagebox.showerror("错误", str(e))
        except Exception as e:
            messagebox.showerror("错误", f"保存记录失败: {str(e)}")

    def generate_sender_pseudo(self, sender):
        random.seed(sender)
        return random.randint(10000, 99999)

    def update_last_saved_record_attack_status(self, is_attack):
        """
            更新最近保存记录的攻击状态

            is_attack: 布尔值，指示是否为攻击行为
        """
        if self.last_saved_record is None:
            return

        file_path = base_path / "saved_records.json"
        if not file_path.exists():
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            for record in reversed(data):
                if (record.get('savedTimestamp') == self.last_saved_record.get('savedTimestamp') and
                        record.get('vehicleId') == self.last_saved_record.get('vehicleId')):
                    record['hazardAttack'] = 1 if is_attack else 0
                    break

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

        except Exception as e:
            messagebox.showerror("错误", f"更新攻击状态失败: {str(e)}")

    def browse_file_dialog(self):
        """
            打开文件浏览对话框，允许用户选择JSON文件

            返回: 所选文件的路径字符串，如果用户取消则返回空字符串
        """
        filepath = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        return filepath

    def set_file_path(self, path):
        """
            设置文件路径

            path: 文件路径字符串
        """
        self.file_path.set(path)

    def get_file_path(self):
        return self.file_path.get()

    def get_manual_input_data(self) -> Dict:
        """
            从手动输入字段获取数据并进行类型转换

            返回: 包含输入数据的字典
        """
        input_data = {}
        for field, config in self.input_fields_config.items():
            entry = self.entries[field]
            raw_value = entry.get().strip()
            field_type = config.get("type", str)
            default_value = config.get("default")

            # 如果当前值是占位符，就将其视为空字符串处理
            if raw_value == entry.placeholder_text:
                raw_value = ""

            try:
                if field_type == list:
                    if raw_value.startswith('[') and raw_value.endswith(']'):
                        input_data[field] = json.loads(raw_value)
                    elif raw_value: # 只有当raw_value不为空时才尝试分割
                        values = [float(x.strip()) for x in raw_value.split(',')]
                        if len(values) == 3:
                            input_data[field] = values
                        else:
                            input_data[field] = default_value if isinstance(default_value, list) else [0.0, 0.0, 0.0]
                    else: # 如果raw_value为空，使用列表默认值
                        input_data[field] = default_value if isinstance(default_value, list) else [0.0, 0.0, 0.0]
                elif field_type == float:
                    input_data[field] = float(raw_value) if raw_value else default_value
                elif field_type == int:
                    input_data[field] = int(raw_value) if raw_value else default_value
                else:
                    input_data[field] = raw_value if raw_value else default_value
            except (ValueError, json.JSONDecodeError):
                input_data[field] = default_value

        return input_data

    def show_analysis_result(self, results, vehicle_attack_counts, filepath):
        """
            在界面上显示文件分析结果

            results: 分析结果列表
            vehicle_attack_counts: 车辆攻击次数统计字典
            filepath: 被分析文件的路径
        """
        self.results = results
        self.vehicle_attack_counts = vehicle_attack_counts

        total = len(self.results)
        attack_count = sum(1 for r in self.results if r["prediction"] == 1)
        attack_ratio = attack_count / total if total > 0 else 0

        vehicle_id = "未知车辆"
        if self.vehicle_attack_counts:
            # Get the first vehicle ID, assuming a single vehicle ID for file analysis context
            vehicle_id = next(iter(self.vehicle_attack_counts.keys()))
        elif self.results:
            # Fallback to try to get vehicleId from the first record if available
            try:
                with open(filepath, 'r', encoding='utf-8') as f: # Added encoding
                    first_record = json.load(f)[0]
                    vehicle_id = first_record.get("vehicleId", "未知车辆")
            except Exception:
                pass  # If file cannot be read or is empty, vehicle_id remains "未知车辆"

        result_text = ''
        result_text += f"总数据量：{total} 条\n"
        result_text += f"攻击次数：{attack_count} 次\n"
        result_text += f"攻击比例：{attack_ratio * 100:.1f}%\n"

        if attack_ratio >= 0.1:
            result_text += "❌ 车辆安全评级：恶意车辆"
            style = "danger"
        elif attack_ratio >= 0.05:
            result_text += "⚠️ 车辆安全评级：嫌疑车辆"
            style = "warning"
        else:
            result_text += "✅ 车辆安全评级：正常车辆"
            style = "success"

        result_text += "\n 诊断说明："
        if attack_count == 0:
            result_text += "未检测到恶意攻击行为，车辆行为完全符合安全规范"
        else:
            result_text += f"该车辆共计检测到异常行为{attack_count}次，占比{attack_ratio * 100:.1f}%，属于"
            if attack_ratio >= 0.1:
                result_text += "持续性的恶意活动特征，建议立即采取处理措施"
            elif attack_ratio >= 0.05:
                result_text += "间歇性异常行为，建议加强监控并记录日志"
            else:
                result_text += "偶发性异常数据，建议进行人工复核"

        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, result_text, "line_spacing")
        self.result_text.tag_configure("header", font=scaled_font(self.header_font_size, self.scale_factor) + ("bold",))
        self.result_text.tag_add("header", "1.0", "1.end")
        self.result_text.tag_add("result", "1.0", "end")
        self.result_text.tag_config("result", foreground=self.style.colors.get(style))
        self.result_text.tag_configure("line_spacing",
                                       spacing1=scaled_dimension(8, self.scale_factor),  # 段落上方间距
                                       spacing2=scaled_dimension(4, self.scale_factor),  # 行内间距
                                       spacing3=scaled_dimension(8, self.scale_factor))  # 段落下方间距
        self.result_text.config(state=tk.DISABLED)
        self.play_result_sound(style)

    def show_single_result(self, result):
        """
            在界面上显示单条实时数据的分析结果

            result: 单条数据分析结果字典
        """
        self.last_analysis_result = result

        result_text = "实时分析结果：\n\n"
        result_text += f"攻击概率: {result['attack_prob'] * 100:.1f}%\n\n"

        if result['prediction'] == 1:
            result_text += "❌ 当前状态：检测到攻击行为"
            style = "danger"
            is_attack = True
        else:
            result_text += "✅当前状态：正常行驶"
            style = "success"
            is_attack = False

        if self.last_saved_record:
            self.update_last_saved_record_attack_status(is_attack)

        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, result_text, "line_spacing")
        self.result_text.tag_add("result", "1.0", "end")
        self.result_text.tag_config("result", foreground=self.style.colors.get(style))
        self.result_text.config(state=tk.DISABLED)
        self.play_result_sound(style)

    def play_result_sound(self, result_style):
        if not self.pygame:
            return

        try:
            sound_map = {
                "danger": "error.mp3",
                "warning": "suspicious.wav",
                "success": "safe.mp3"
            }
            if result_style in sound_map:
                sound_path = base_path / "sounds" / sound_map[result_style]
                if sound_path.exists():
                    self.pygame.mixer.Sound(str(sound_path)).play()
                else:
                    messagebox.showerror("错误", f"音效文件 {sound_path} 不存在")
        except Exception as e:
            messagebox.showerror("错误", f"音效播放失败: {str(e)}")

    def set_progress_maximum(self, value):
        self.progress['maximum'] = value

    def update_progress_value(self, value):
        self.progress['value'] = value
        self.root.update_idletasks()

    def get_canvas(self):
        return self._animation_canvas

    def clear_results_only(self):
        self.results.clear()
        self.vehicle_attack_counts.clear()
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        self.result_text.config(state=tk.DISABLED)
        self.hide_progress()

    def save_and_analyze(self):
        try:
            input_data = self.get_manual_input_data()
            record = self.app.data_persistence_manager.generate_complete_record(input_data)
            self.app.data_persistence_manager.save_record(record)
            last_record = self.app.data_persistence_manager.get_last_record()
            self.app.analyze_manual(last_record)
            messagebox.showinfo("成功", "记录已保存并分析完成")
        except ValueError as e:
            messagebox.showerror("错误", str(e))
        except Exception as e:
            messagebox.showerror("错误", f"保存或分析失败: {str(e)}")