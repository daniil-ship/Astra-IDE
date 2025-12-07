import tkinter as tk

class AstraWindow:
    def __init__(self, astra=None):
        self.windows = {}
        self.widgets = {}
        self.astra = astra

    def create_window(self, name, width, height, title):
        if name in self.windows: return f"Окно {name} уже существует"
        win = tk.Toplevel()
        win.title(title)
        win.geometry(f"{width}x{height}")
        self.windows[name] = win
        return f"Окно {name} создано"

    def draw_text(self, win_name, x, y, text, font_size=12, text_color="black", bg_color=None, visible=True):
        win = self.windows.get(win_name)
        if not win: return f"Окно {win_name} не найдено"
        lbl = tk.Label(win, text=text, font=("Arial", font_size), fg=text_color, bg=bg_color)
        if visible:
            lbl.place(x=x, y=y)
        self.widgets[text] = lbl
        return "Текст добавлен"

    def draw_button(self, win_name, x, y, text, func_name, font_size=12, text_color="black", bg_color=None, visible=True):
        win = self.windows.get(win_name)
        if not win: return f"Окно {win_name} не найдено"
        btn = tk.Button(win, text=text, font=("Arial", font_size), fg=text_color, bg=bg_color,
                        command=lambda: self.astra.call_func(func_name) if self.astra else None)
        if visible:
            btn.place(x=x, y=y)
        self.widgets[text] = btn
        return "Кнопка добавлена"

    def draw_square(self, win_name, x, y, size, color, visible=True):
        win = self.windows.get(win_name)
        if not win: return f"Окно {win_name} не найдено"
        canvas = tk.Canvas(win, width=size, height=size)
        if visible:
            canvas.place(x=x, y=y)
        canvas.create_rectangle(0,0,size,size, fill=color)
        self.widgets[f"square_{x}_{y}"] = canvas
        return "Квадрат добавлен"
