import time
import threading
from ttkbootstrap import Window
from pathlib import Path
from tkinter import messagebox
from loading_screen import LoadingScreen
from ui_manager import UIManager
from data_processor import DataProcessor
from model_handler import ModelHandler
from animation_manager import AnimationManager
from data_persistence_manager import DataPersistenceManager
from utils import center_window

try:
    import pygame
    pygame.mixer.init()
except ImportError:
    messagebox.showwarning("警告", "Pygame 未安装。音效将禁用。")
    pygame = None
except Exception as e:
    messagebox.showwarning("警告", f"Pygame 混音器初始化失败: {e}。音效将禁用。")
    pygame = None

base_path = Path(__file__).parent

# 定义设计基准：在 2560x1440 屏幕上期望的主窗口大小为 1800x1200
DESIGN_SCREEN_WIDTH = 2560
DESIGN_SCREEN_HEIGHT = 1440
DESIGN_WINDOW_WIDTH_ON_SCREEN = 1800
DESIGN_WINDOW_HEIGHT_ON_SCREEN = 1200

# 计算窗口相对于设计屏幕的比例
RELATIVE_WINDOW_WIDTH_RATIO = DESIGN_WINDOW_WIDTH_ON_SCREEN / DESIGN_SCREEN_WIDTH
RELATIVE_WINDOW_HEIGHT_RATIO = DESIGN_WINDOW_HEIGHT_ON_SCREEN / DESIGN_SCREEN_HEIGHT

class VehicleSecurityApp:
    def __init__(self):
        """
            初始化车辆安全应用程序。
            设置主窗口，计算并调整窗口大小以适应不同屏幕分辨率，
            初始化加载屏幕并启动后台加载线程。
        """
        self.root = Window(title="恶意车辆识别系统 | Copyright © 2025", themename="morph")
        center_window(self.root, 1800, 1200)
        # 获取当前屏幕的逻辑像素尺寸
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        # 根据设计比例和当前屏幕尺寸计算实际窗口大小
        actual_window_width = int(screen_width * RELATIVE_WINDOW_WIDTH_RATIO)
        actual_window_height = int(screen_height * RELATIVE_WINDOW_HEIGHT_RATIO)
        # 设置最小窗口尺寸，防止在极低分辨率屏幕上窗口过小
        MIN_WINDOW_WIDTH = 1000
        MIN_WINDOW_HEIGHT = 700
        self.final_window_width = max(actual_window_width, MIN_WINDOW_WIDTH)
        self.final_window_height = max(actual_window_height, MIN_WINDOW_HEIGHT)
        # 居中显示主窗口
        center_window(self.root, self.final_window_width, self.final_window_height)
        # 启动时隐藏主窗口
        self.root.withdraw()
        # 强制更新窗口，确保 winfo_width() 和 winfo_height() 返回的是最终的尺寸
        self.root.update_idletasks()
        # 计算全局缩放因子，用于调整内部控件和字体大小
        # 以设计窗口的宽度作为基准来计算缩放因子
        self.global_scale_factor = self.root.winfo_width() / DESIGN_WINDOW_WIDTH_ON_SCREEN
        self.loading_complete = False
        self.loading_error = None
        # 传递缩放因子给加载屏幕
        self.loading_screen = LoadingScreen(self.root)
        self.loading_screen.create_loading_screen()
        threading.Thread(target=self.background_loading, daemon=True).start()
        self.monitor_loading()
        self.model = None
        self.metadata = None
        self.ui_manager = None
        self.data_processor = None
        self.data_persistence_manager = DataPersistenceManager()
        self.animation_manager = None

    def background_loading(self):
        """
            在后台线程中执行资源加载任务。
            包括模拟UI初始化、模型加载、数据处理器准备、动画系统配置。
            更新加载屏幕的进度，并在加载过程中处理可能发生的错误。
        """
        try:
            steps = [
                ("初始化UI...", 20),
                ("加载模型...", 45),
                ("准备数据处理器...", 75),
                ("配置动画系统...", 90),
                ("完成...", 100)
            ]
            for desc, progress in steps:
                time.sleep(0.7)
                self.loading_screen.update_progress(progress, desc)
            self.model, self.metadata = ModelHandler.load_model(base_path)
            self.data_processor = DataProcessor(self.model, self.metadata)
            self.loading_complete = True
        except Exception as e:
            self.loading_error = e
            self.loading_complete = True

    def monitor_loading(self):
        """
            监控后台加载线程的完成状态。
            如果加载完成，则销毁加载屏幕并显示主窗口；
            如果加载过程中发生错误，则显示错误信息并关闭应用程序；
            否则，继续每隔100毫秒检查加载状态。
        """
        if self.loading_complete:
            if self.loading_error:
                messagebox.showerror("错误", f"初始化失败: {str(self.loading_error)}")
                self.root.destroy()
            else:
                self.loading_screen.destroy_loading_screen()
                self.root.deiconify()
                self.initialize_ui()
        else:
            self.root.after(100, self.monitor_loading)

    def initialize_ui(self):
        """
            初始化用户界面组件。
            创建UIManager实例以构建主界面，并创建AnimationManager实例以管理动画效果。
        """
        self.ui_manager = UIManager(self.root, self, pygame,self.global_scale_factor)
        self.ui_manager.create_widgets()
        self.animation_manager = AnimationManager(self.root, self.ui_manager.get_canvas(),self.global_scale_factor)
        self.animation_manager.create_car_animation()
        self.animation_manager.create_animation_area()

    def browse_file(self):
        """
            打开文件浏览对话框，允许用户选择JSON文件。
            如果用户选择了文件，则更新UI管理器中的文件路径。
        """
        filepath = self.ui_manager.browse_file_dialog()
        if filepath:
            self.ui_manager.set_file_path(filepath)

    def analyze_file(self):
        """
            分析选定的JSON文件中的车辆数据。
            首先检查文件路径是否已选择，然后显示进度条。
            加载JSON数据，对每条记录进行分析，并更新进度。
            分析完成后，显示分析结果，或在发生错误时显示错误信息。
        """
        filepath = self.ui_manager.get_file_path()
        if not filepath:
            messagebox.showwarning("警告", "请先选择要分析的JSON文件")
            return
        self.ui_manager.clear_previous_results()
        self.ui_manager.show_progress()
        try:
            records = self.data_persistence_manager.load_json_data(filepath) # 新代码
            total = len(records)
            self.ui_manager.set_progress_maximum(total)
            results, attack_counts = self.data_processor.analyze_file_data(
                records,
                lambda idx: self.ui_manager.update_progress_value(idx)
            )
            self.ui_manager.hide_progress()
            self.ui_manager.show_analysis_result(results, attack_counts, filepath)
        except Exception as e:
            self.ui_manager.handle_analysis_error(f"文件分析失败: {str(e)}")

    def analyze_manual(self, record):
        """
            分析手动输入的单条车辆数据记录。
            调用数据处理器进行分析，并显示分析结果。
            处理在分析过程中可能发生的ValueError或其他异常。
        """
        try:
            result = self.data_processor.analyze_manual_data(record)
            self.ui_manager.show_single_result(result)
        except ValueError as e:
            messagebox.showerror("错误", f"手动分析失败: {e}")
        except Exception as e:
            messagebox.showerror("错误", f"手动分析时发生未知错误: {e}")

if __name__ == "__main__":
    app = VehicleSecurityApp()
    app.root.mainloop()