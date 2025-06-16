def center_window(win, width, height):
    """
       将指定窗口居中显示在屏幕上。

       win: 需要居中的窗口实例。
       width: 窗口的宽度。
       height: 窗口的高度。
    """
    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()
    x = int((screen_width - width) / 2)
    y = int((screen_height - height) / 2)
    win.geometry(f"{width}x{height}+{x}+{y}")

def hex_to_rgb(color):
    """
       将十六进制颜色字符串转换为RGB元组。

       color: 十六进制颜色字符串（例如"#RRGGBB"或"RRGGBB"）。
       返回: RGB颜色元组。
    """
    color = color.lstrip('#')
    if len(color) == 3:
        color = ''.join([c * 2 for c in color])
    return tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb):
    """
        将RGB颜色元组转换为十六进制字符串。

        rgb: RGB颜色元组。
        返回: 十六进制颜色字符串。
    """
    return '#%02x%02x%02x' % rgb

def create_color_transition(start_color, end_color, steps):
    start = hex_to_rgb(start_color)
    end = hex_to_rgb(end_color)
    return [
        rgb_to_hex((
            max(0, min(255, int(start[0] + (end[0] - start[0]) * i / steps))),
            max(0, min(255, int(start[1] + (end[1] - start[1]) * i / steps))),
            max(0, min(255, int(start[2] + (end[2] - start[2]) * i / steps)))
        )) for i in range(steps + 1)
    ]

def scaled_font(base_size,scale_factor):
    """
        根据缩放因子计算调整后的字体大小。

        base_size: 字体的基础大小。
        scale_factor: 缩放因子。
        返回: 包含字体名称和调整后大小的元组。
    """
    return ("微软雅黑", max(8, int(base_size * scale_factor)))

def scaled_dimension(base_dim,scale_factor):
    """
        根据缩放因子计算调整后的尺寸。

        base_dim: 基础尺寸。
        scale_factor: 缩放因子。
        返回: 调整后的尺寸整数。
    """
    return max(1, int(base_dim * scale_factor))

