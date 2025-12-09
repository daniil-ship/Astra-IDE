import tkinter as tk
from tkinter import ttk, scrolledtext, simpledialog, messagebox, filedialog
import threading, time, os, re
from PIL import Image, ImageTk
from tkhtmlview import HTMLLabel
import json
import subprocess
import webbrowser

# -------------------- Astra Interpreter --------------------
class Astra:
    def __init__(self, debug_output):
        self.variables = {}
        self.functions = {}
        self.libraries = {} 
        self.running = False
        self.debug_output = debug_output
        self.call_stack = []
        
    def split_args(self, args):
        result = []
        buff = ""
        in_string = False

        for ch in args:
            if ch == '"' and not in_string:
                in_string = True
                buff += ch
            elif ch == '"' and in_string:
                in_string = False
                buff += ch
            elif ch == ',' and not in_string:
                result.append(buff.strip().strip('"'))
                buff = ""
            else:
                buff += ch

        if buff:
            result.append(buff.strip().strip('"'))

        return result

    
    def create_window(self, name, width, height, title):
        if name in self.windows: return f"Окно {name} уже существует"
        win = tk.Toplevel()
        win.title(title)
        win.geometry(f"{width}x{height}")
        self.windows[name] = win
        return f"Окно {name} создано"

    def draw_text(self, win_name, x, y, text):
        win = self.windows.get(win_name)
        if not win: return f"Окно {win_name} не найдено"
        lbl = tk.Label(win, text=text)
        lbl.place(x=x, y=y)
        return "Текст добавлен"

    def draw_button(self, win_name, x, y, text, func):
        win = self.windows.get(win_name)
        if not win: return f"Окно {win_name} не найдено"
        btn = tk.Button(win, text=text, command=lambda: func())
        btn.place(x=x, y=y)
        return "Кнопка добавлена"

    def draw_square(self, win_name, x, y, size, color):
        win = self.windows.get(win_name)
        if not win: return f"Окно {win_name} не найдено"
        canvas = tk.Canvas(win, width=size, height=size)
        canvas.place(x=x, y=y)
        canvas.create_rectangle(0,0,size,size, fill=color)
        return "Квадрат добавлен"
        
    def debug(self, msg):
        try:
            self.debug_output.insert(tk.END, str(msg) + "\n")
            self.debug_output.see(tk.END)
        except:
            print(msg)
        
    def parse_args(self, args, expected_count):
        result = []
        current = ""
        inside_quotes = False

        i = 0
        while i < len(args):
            c = args[i]

            if c == '"':
                inside_quotes = not inside_quotes
                current += c
            elif c == ',' and not inside_quotes:
                result.append(current.strip())
                current = ""
            else:
                current += c

            i += 1

        if current:
            result.append(current.strip())

        # Удаляем кавычки
        cleaned = []
        for val in result:
            val = val.strip()
            if val.startswith('"') and val.endswith('"'):
                cleaned.append(val[1:-1])
            else:
                cleaned.append(val)

        if len(cleaned) != expected_count:
            raise ValueError(f"Ожидалось {expected_count} аргументов, получено {len(cleaned)}: {cleaned}")

        return cleaned


    def run_program(self, program):
        self.running = True
        i = 0
        while i < len(program) and self.running:
            line = program[i].strip()
            if not line or line.startswith(";"):
                i += 1
                continue
            try:
                i = self.execute_line(line, program, i)
            except Exception as e:
                self.debug_output.insert(tk.END, f"Ошибка: {e} в строке: {line}\n")
                self.debug_output.see(tk.END)
                i += 1
        self.debug_output.insert(tk.END, "Программа завершена.\n")
        self.debug_output.see(tk.END)
        self.running = False
        
    def call_func(self, name):
        if name in self.functions:
            try:
                self.run_program(self.functions[name])
            except Exception as e:
                self.debug(f"Ошибка в функции {name}: {e}")
        else:
            self.debug(f"Функция '{name}' не найдена")

    def execute_line(self, line, program, index):
        parts = line.strip().split(maxsplit=1)
        if not parts: return index
        cmd = parts[0].upper()
        args = parts[1] if len(parts) > 1 else ""

        # ---------------- Переменные ----------------
        if cmd == "TEXTVAR":
            name, val = [x.strip() for x in args.split(",",1)]
            if val.startswith('"') and val.endswith('"'):
                val = val[1:-1]
            else:
                try:
                    val = int(val)
                except:
                    pass
            self.variables[name] = val

        elif cmd == "UPDATEVAR":
            name, val = [x.strip() for x in args.split(",",1)]
            if val in self.variables:
                self.variables[name] = self.variables[val]
            else:
                try:
                    self.variables[name] = int(val)
                except:
                    self.variables[name] = val

        # ---------------- Арифметика ----------------
        elif cmd == "ADD":
            reg, val = [x.strip() for x in args.split(",",1)]
            self.variables[reg] = self.variables.get(reg,0)+int(self.variables.get(val,val))
        elif cmd == "SUB":
            reg, val = [x.strip() for x in args.split(",",1)]
            self.variables[reg] = self.variables.get(reg,0)-int(self.variables.get(val,val))
        elif cmd == "MOV":
            reg, val = [x.strip() for x in args.split(",",1)]
            if val in self.variables:
                self.variables[reg] = self.variables[val]
            else:
                try:
                    self.variables[reg] = int(val)
                except:
                    self.variables[reg] = val
        elif cmd == "OPEN":
            filename = args.strip().strip('"')
            try:
                with open(filename, "r", encoding="utf-8") as f:
                    content = f.read()
                return content
            except Exception as e:
                raise Exception(f"OPEN error: {e}")

        # ---------------- Вывод ----------------
        elif cmd == "PRINT":
            val = args.strip()
            if val in self.variables:
                val = self.variables[val]
            self.debug_output.insert(tk.END,str(val)+"\n")
            self.debug_output.see(tk.END)           
        elif cmd == "WINDOW":
            name, w, h, title = self.parse_args(args, 4)
            self.debug(self.libraries["AstraWindow"].create_window(
                name, int(w), int(h), title
            ))
        elif cmd == "TEXT":
            if "AstraWindow" in self.libraries:
                args_list = [x.strip() for x in args.split(",")]
                if len(args_list) < 4:
                    self.debug(f"Ошибка: недостаточно аргументов для TEXT: {args_list}")
                else:
                    win, x, y, text = args_list[:4]
                    font_size = int(args_list[4]) if len(args_list) > 4 else 12
                    text_color = args_list[5] if len(args_list) > 5 else "black"
                    bg_color = args_list[6] if len(args_list) > 6 else None
                    visible = args_list[7].lower() == "true" if len(args_list) > 7 else True
                    self.debug(self.libraries["AstraWindow"].draw_text(win, int(x), int(y), text, font_size, text_color, bg_color, visible))
        elif cmd == "BUTTON":
            if "AstraWindow" in self.libraries:
                args_list = [x.strip() for x in args.split(",")]
                if len(args_list) < 5:
                    self.debug(f"Ошибка: недостаточно аргументов для BUTTON: {args_list}")
                else:
                    win, x, y, text, func = args_list[:5]
                    font_size = int(args_list[5]) if len(args_list) > 5 else 12
                    text_color = args_list[6] if len(args_list) > 6 else "black"
                    bg_color = args_list[7] if len(args_list) > 7 else None
                    visible = args_list[8].lower() == "true" if len(args_list) > 8 else True
                    self.debug(self.libraries["AstraWindow"].draw_button(win, int(x), int(y), text, func, font_size, text_color, bg_color, visible))
        elif cmd == "SQUARE":
            if "AstraWindow" in self.libraries:
                args_list = [x.strip() for x in args.split(",")]
                if len(args_list) < 5:
                    self.debug(f"Ошибка: недостаточно аргументов для SQUARE: {args_list}")
                else:
                    win, x, y, size, color = args_list[:5]
                    visible = args_list[5].lower() == "true" if len(args_list) > 5 else True
                    self.debug(self.libraries["AstraWindow"].draw_square(win, int(x), int(y), int(size), color, visible))

        # ---------------- WAIT ----------------
        elif cmd == "WAIT":
            t = float(args.strip())
            for _ in range(int(t*10)):
                if not self.running: break
                time.sleep(0.1)

        # ---------------- Функции ----------------
        elif cmd == "FUNCTION":
            func_name = args.strip()
            self.functions[func_name] = []
            i = index+1
            while i < len(program) and program[i].strip() != "}":
                self.functions[func_name].append(program[i])
                i +=1
            return i

        elif cmd in self.functions:
            self.call_stack.append(index)
            self.run_program(self.functions[cmd])
            self.call_stack.pop()

        # ---------------- Условия ----------------
        elif cmd in ["IF","ELIF"]:
            condition = args.replace("THEN","").strip()
            if "==" in condition:
                var, val = [x.strip() for x in condition.split("==")]
                var_val = self.variables.get(var,0)
                try: val = int(val)
                except: val = self.variables.get(val,0)
                if var_val != val:
                    i = index+1
                    depth=1
                    while i<len(program) and depth>0:
                        l = program[i].strip().upper()
                        if l.startswith(("IF","ELIF")) and depth==1: break
                        elif l=="ELSE" and depth==1: break
                        elif l=="}": depth-=1
                        i+=1
                    return i-1

        elif cmd == "ELSE":
            i=index+1
            depth=1
            while i<len(program) and depth>0:
                l=program[i].strip().upper()
                if l=="ENDIF": depth-=1
                elif l=="}": depth-=1
                i+=1
            return i-1

        # ---------------- Циклы ----------------
        elif cmd == "WHILE":
            var, val = [x.strip() for x in args.split("!=")]
            i = index + 1
            loop_block = []
            depth = 1
            while i < len(program) and depth > 0:
                l = program[i].strip()
                if l.upper().startswith("WHILE"): depth += 1
                elif l == "}": depth -= 1
                if depth > 0: loop_block.append(program[i])
                i += 1

            while self.running and self.variables.get(var, 0) != int(val):
                try:
                    self.run_program(loop_block)
                except StopIteration as e:
                    if str(e) == "break":
                        break
                    elif str(e) == "continue":
                        continue
                time.sleep(0.01)
            return i-1
        elif cmd == "FOR":
            line = args.strip()
            if "=" in line and "TO" in line.upper():
                try:
                    var_part, range_part = line.split("=", 1)
                    var_name = var_part.strip()
                    range_part = range_part.replace("to", "TO").strip()
                    start_str, end_str = range_part.split("TO", 1)
                    try:
                        start = int(start_str.strip())
                    except:
                        start = int(self.variables.get(start_str.strip(), 0))
                    try:
                        end = int(end_str.strip())
                    except:
                        end = int(self.variables.get(end_str.strip(), 0))
                except Exception as e:
                    self.error(f"Ошибка в FOR: {e}")
                    return index
                i2 = index + 1
                block = []
                depth = 1
                while i2 < len(program) and depth > 0:
                    line2 = program[i2].strip()
                    if line2.upper().startswith("FOR"): depth += 1
                    elif line2 == "}": depth -= 1
                    if depth > 0: block.append(program[i2])
                    i2 += 1
                for cur in range(start, end + 1):
                    self.variables[var_name] = cur
                    try:
                        self.run_program(block)
                    except StopIteration as e:
                        if str(e) == "break":
                            break
                        elif str(e) == "continue":
                            continue

                return i2 - 1
            if "IN" in line:
                try:
                    var_name, iterable_raw = line.split("IN", 1)
                    var_name = var_name.strip()
                    iterable_raw = iterable_raw.strip()
                    if iterable_raw in self.variables:
                        iterable_str = self.variables[iterable_raw]
                        iterable = [x.strip() for x in iterable_str.split(",")]
                    else:
                        iterable = [x.strip() for x in iterable_raw.split(",")]
                except Exception as e:
                    self.error(f"Ошибка в FOR IN: {e}")
                    return index
                i2 = index + 1
                block = []
                depth = 1
                while i2 < len(program) and depth > 0:
                    line2 = program[i2].strip()
                    if line2.upper().startswith("FOR"): depth += 1
                    elif line2 == "}": depth -= 1
                    if depth > 0: block.append(program[i2])
                    i2 += 1
                for val in iterable:
                    self.variables[var_name] = val
                    try:
                        self.run_program(block)
                    except StopIteration as e:
                        if str(e) == "break":
                            break
                        elif str(e) == "continue":
                            continue
                return i2 - 1
            self.error("Неверный синтаксис FOR")
            return index

        # ---------------- BREAK/CONTINUE ----------------
        elif cmd=="BREAK":
            raise StopIteration("break")
        elif cmd=="CONTINUE":
            raise StopIteration("continue")

        # ---------------- RETURN ----------------
        elif cmd=="RETURN":
            val = args.strip()
            if val in self.variables:
                self.return_value=self.variables[val]
            else:
                try: self.return_value=int(val)
                except: self.return_value=val
            self.stop_function=True
            return len(program)

        # ---------------- TRY/EXCEPT ----------------
        elif cmd == "USE":
            lib_name = args.strip()
            try:
                module = __import__(f"libs.{lib_name}", fromlist=[lib_name])
                lib_class = getattr(module, lib_name)
                self.libraries[lib_name] = lib_class(self)
                self.debug("Библиотека загружена: " + lib_name)
            except Exception as e:
                self.debug(f"Ошибка подключения {lib_name}: {e}")
        elif cmd == "TRY":
            i = index + 1
            try_block = []
            except_block = []
            depth = 1
            in_except = False
            except_var = None
            while i < len(program) and depth > 0:
                line_raw = program[i]
                line = program[i].strip()

                if line.upper().startswith("TRY"):
                    depth += 1
                elif line.upper().startswith("EXCEPT") and depth == 1:
                    in_except = True

                    parts = line.split()
                    if len(parts) == 3 and parts[1].upper() == "AS":
                        except_var = parts[2]

                    i += 1
                    continue
                    if prev_line.strip().startswith("}") or current_line.strip().startswith("}"):
                        self.depth = max(0, self.depth - 1)
                    if depth == 0:
                        break

                if in_except:
                    except_block.append(line_raw)
                else:
                    try_block.append(line_raw)

                i += 1

            try:
                self.run_program(try_block)
            except Exception as e:
                if except_var:
                    self.variables[except_var] = str(e)
                self.run_program(except_block)

            return i
        elif cmd == "WITH":
            if "=" not in args:
                raise Exception("WITH: нет '='")

            var, val_expr = args.split("=", 1)
            var = var.strip()
            val_expr = val_expr.strip()

            # выполнить правую часть
            parts_val = val_expr.split(maxsplit=1)
            sub_cmd = parts_val[0].upper()

            if sub_cmd == "OPEN":
                val = self.execute_line(val_expr, program, index)
            else:
                if val_expr in self.variables:
                    val = self.variables[val_expr]
                else:
                    try:
                        val = int(val_expr)
                    except:
                        val = val_expr.strip('"')

            old_value = self.variables.get(var)
            self.variables[var] = val

            i = index + 1
            block = []
            depth = 1

            while i < len(program):
                line = program[i].strip()

                if line.upper().startswith("WITH"):
                    depth += 1
                    if prev_line.strip().startswith("}") or current_line.strip().startswith("}"):
                        self.depth = max(0, self.depth - 1)
                    if depth == 0:
                        break

                block.append(program[i])
                i += 1

            self.run_program(block)

            if old_value is None:
                del self.variables[var]
            else:
                self.variables[var] = old_value

            return i
        # ---------------- Закрытие блока ----------------
        elif cmd=="}":
            return index+1

        return index + 1

# -------------------- Astra IDE --------------------
class AstraIDE:
    KEYWORDS = ["TEXTVAR","UPDATEVAR","PRINT","ADD","SUB","MOV","WAIT",
                "FUNCTION","IF","ELSE","WHILE","THEN","CATCH","TRY",
                "RETURN","IN","FOR","ELIF","BREAK","CONTINUE","USE","EXCEPT","WITH"]
    HINTS = {
        "TEXTVAR": "TEXTVAR имя,значение — Создание переменной",
        "RETURN": "RETURN имя — Возвратить",
        "FOR": "FOR имя IN значение — Для имя значение (закрывается })",
        "IN": "FOR имя IN значение — Для имя значение (закрывается })",
        "THEN": "THEN — Тогда",
        "TRY": "TRY - Попробовать",
        "CATCH": "CATCH — Поймать",
        "UPDATEVAR": "UPDATEVAR имя,значение — Обновление переменной",
        "PRINT": "PRINT выражение — Вывод значения",
        "ADD": "ADD имя,значение — Прибавить число к переменной",
        "SUB": "SUB имя,значение — Вычесть число из переменной",
        "MOV": "MOV имя,значение — Присвоить значение переменной",
        "WAIT": "WAIT секунды — Пауза выполнения",
        "IF": "IF var==значение — Условие",
        "ELSE": "ELSE — Иначе",
        "WHILE": "WHILE var!=значение — Цикл",
        "FUNCTION": "FUNCTION имя — Определение функции",
        "}": "} - Закончить",
        "ELIF": "ELIF - Дополнительное условие",
        "BREAK": "BREAK - Досрочно завершить цикл",
        "CONTINUE": "CONTINUE - Пропускает оставшуюся часть текущей итерации",
        "USE": "USE - Использовать библиотеку например: USE AstraWindow (встроеная  библиотека).",
        "EXCEPT": "EXCEPT - Кроме",
        "AS": "AS - Как",
        "WITH": "WITH - С"
    }
    
    def open_build_settings(self):
        settings = self.build_settings

        win = tk.Toplevel(self.root)
        win.title("Настройки сборки")
        win.geometry("450x350")

        ttk.Label(win, text="Имя проекта:").pack(anchor="w", padx=10)
        name_var = tk.StringVar(value=settings.get("name", "AstraProject"))
        ttk.Entry(win, textvariable=name_var).pack(fill=tk.X, padx=10)

        ttk.Label(win, text="Версия:").pack(anchor="w", padx=10)
        version_var = tk.StringVar(value=settings.get("version", "1.0"))
        ttk.Entry(win, textvariable=version_var).pack(fill=tk.X, padx=10)

        ttk.Label(win, text="Файлы/папки (через ;)").pack(anchor="w", padx=10)
        include_var = tk.StringVar(value=";".join(settings.get("include_files", [])))
        ttk.Entry(win, textvariable=include_var).pack(fill=tk.X, padx=10)

        ttk.Label(win, text="Пакеты (через ;)").pack(anchor="w", padx=10)
        packages_var = tk.StringVar(value=";".join(settings.get("packages", [])))
        ttk.Entry(win, textvariable=packages_var).pack(fill=tk.X, padx=10)

        def save():
            self.build_settings = {
                "name": name_var.get(),
                "version": version_var.get(),
                "include_files": include_var.get().split(";"),
                "packages": packages_var.get().split(";")
            }
            self.save_build_settings_file()
            messagebox.showinfo("Готово", "Настройки сохранены")
            win.destroy()

        ttk.Button(win, text="Сохранить", command=save).pack(pady=20)
    
    def load_build_settings(self):
        try:
            if os.path.exists("build_settings.json"):
                with open("build_settings.json", "r", encoding="utf-8") as f:
                    self.build_settings = json.load(f)
            else:
                self.build_settings = {
                    "name": "AstraProject",
                    "version": "1.0",
                    "include_files": ["icons"],
                    "packages": ["tkinter", "PIL", "tkhtmlview"]
                }
        except:
            self.build_settings = {}
            
    def save_build_settings_file(self):
        try:
            with open("build_settings.json", "w", encoding="utf-8") as f:
                json.dump(self.build_settings, f, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror("Ошибка сохранения", str(e))

    def build_exe(self):
        if not hasattr(self, "build_settings"):
            messagebox.showerror("Ошибка", "Нет настроек сборки!")
            return

        settings = self.build_settings
        include_args = []

        for item in settings["include_files"]:
            if os.path.exists(item):
                include_args.extend(["--add-data", f"{item}{os.pathsep}{item}"])

        cmd = [
            "pyinstaller",
            "--onefile",
            "--windowed",
            f"--name={settings['name']}",
        ] + include_args + [
            self.current_file if self.current_file else "main.py"
        ]

        threading.Thread(target=lambda: subprocess.run(cmd), daemon=True).start()
        messagebox.showinfo("Сборка", "Сборка .exe запущена")
        
    def build_msi(self):
        if not hasattr(self, "build_settings"):
            messagebox.showerror("Ошибка", "Нет настроек сборки!")
            return

        settings = self.build_settings
        app_name = settings["name"]
        app_version = settings["version"]

        # 1 — создаём exe через PyInstaller
        exe_cmd = [
            "pyinstaller",
            "--windowed",
            "--onedir",
            f"--name={app_name}",
            self.current_file if self.current_file else "main.py"
        ]
        subprocess.run(exe_cmd)
        
        cfg = f"""
[Application]
name={app_name}
version={app_version}
entry_point=main:main
icon=icons\\icon.ico

[Python]
version=3.11.0
bitness=64

[Include]
files=dist/{app_name}
"""

        with open("installer.cfg", "w", encoding="utf-8") as f:
            f.write(cfg)
        msi_cmd = ["pynsist", "installer.cfg"]
        subprocess.run(msi_cmd)

        messagebox.showinfo("Готово", f"MSI установщик создан: build/{app_name}-{app_version}.msi")

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Astra IDE")
        self.root.geometry("1000x600")

        # ---------------- Проект ----------------
        project_frame = ttk.Frame(self.root, width=300)
        project_frame.pack(side=tk.LEFT, fill=tk.Y)
        ttk.Label(project_frame, text="Проект").pack(pady=5)

        self.tree = ttk.Treeview(project_frame)
        self.tree.pack(expand=True, fill=tk.BOTH, padx=5)
        self.tree.bind("<Double-1>", self.open_file_from_tree)

        btn_frame = ttk.Frame(project_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        ttk.Button(btn_frame, text="Создать файл", command=self.create_file).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Обновить", command=self.load_project_files).pack(side=tk.LEFT, padx=2)
        self.load_project_files()

        # ---------------- Редактор ----------------
        editor_frame = ttk.Frame(self.root)
        editor_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        self.editor = scrolledtext.ScrolledText(editor_frame, wrap=tk.NONE, undo=True)
        self.editor.pack(expand=True, fill=tk.BOTH)
        self.editor.tag_config("error", background="#FFCCCC")      # красная
        self.editor.tag_config("warning", background="#FFF4CC")    # жёлтая
        self.error_count = 0
        self.warning_count = 0

        def highlight_issues(self, errors=None, warnings=None):
            """
            errors = list of line numbers with errors
            warnings = list of line numbers with warnings
            """
            self.editor.tag_remove("error", "1.0", tk.END)
            self.editor.tag_remove("warning", "1.0", tk.END)
            if errors:
                for line in errors:
                    start = f"{line}.0"
                    end = f"{line}.0 lineend"
                    self.editor.tag_add("error", start, end)
            if warnings:
                for line in warnings:
                    start = f"{line}.0"
                    end = f"{line}.0 lineend"
                    self.editor.tag_add("warning", start, end)
            total_lines = int(self.editor.index('end-1c').split('.')[0])
            self.status_label.config(
                text=f"Строк: {total_lines} | Ошибки: {len(errors) if errors else 0} | Предупреждения: {len(warnings) if warnings else 0}"
            )
        def run_program_with_highlighting(self):
            code_lines = self.editor.get("1.0", tk.END).splitlines()
            errors = []
            warnings = []

            for i, line in enumerate(code_lines, start=1):
                try:
                    if "PRINT" in line and "UNKNOWN" in line:
                        warnings.append(i)
                    if "ERROR" in line:
                        raise Exception("Test error")
                except Exception as e:
                    errors.append(i)
            self.highlight_issues(errors, warnings)
        self.status_label = ttk.Label(self.root, text="Строк: 0 | Ошибки: 0 | Предупреждения: 0(в разработке)", anchor="w")# не работает пока что
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)
        self.editor.bind("<KeyRelease>", self.highlight_syntax)
        self.editor.bind("<ButtonRelease>", self.on_cursor_move)

        # ---------------- Подсветка ----------------
        self.editor.tag_config("keyword", foreground="blue")
        self.editor.tag_config("string", foreground="green")
        self.editor.tag_config("comment", foreground="gray")
        self.editor.tag_config("number", foreground="orange")
        self.editor.tag_config("variable", foreground="purple")

        # ---------------- Кнопки с локальными иконками ----------------
        button_frame = ttk.Frame(editor_frame)
        button_frame.pack(fill=tk.X)

        self.icons = {}
        def load_local_icon(path,size=(25,25)):
            try:
                img = Image.open(path).convert("RGBA")
                img = img.resize(size, Image.Resampling.LANCZOS)
                return ImageTk.PhotoImage(img)
            except Exception as e:
                print(f"Ошибка загрузки {path}: {e}")
                return None

        self.icons["run"] = load_local_icon("icons/run.png")
        self.icons["stop"] = load_local_icon("icons/stop.png")
        self.icons["save"] = load_local_icon("icons/save.png")
        self.icons["guide"] = load_local_icon("icons/guide.png")
        self.icons["buildexe"] = load_local_icon("icons/buildexe.png")
        self.icons["buildmsi"] = load_local_icon("icons/buildmsi.png")
        self.icons["settings"] = load_local_icon("icons/settings.png")

        ttk.Button(button_frame, text="Собрать ", image=self.icons["run"], command=self.start_program).pack(side=tk.LEFT, padx=4)
        ttk.Button(button_frame, text="Собрать ", image=self.icons["stop"], command=self.stop_program).pack(side=tk.LEFT, padx=4)
        ttk.Button(button_frame, text="Собрать ", image=self.icons["save"], command=self.save_file).pack(side=tk.LEFT, padx=4)
        ttk.Button(button_frame, text="Собрать ", image=self.icons["guide"], command=self.create_guide_window).pack(side=tk.LEFT, padx=4)
        ttk.Button(button_frame, text="Собрать ", image=self.icons["settings"], command=self.open_build_settings).pack(side=tk.LEFT, padx=4)
        ttk.Button(button_frame, text="Собрать ", image=self.icons["buildexe"], command=self.build_exe).pack(side=tk.LEFT, padx=4)
        ttk.Button(button_frame, text="Собрать ", image=self.icons["buildmsi"], command=self.build_msi).pack(side=tk.LEFT, padx=4)


        # ---------------- Debug Output ----------------
        debug_frame = ttk.Frame(self.root, height=150)
        debug_frame.pack(side=tk.BOTTOM, fill=tk.X)
        ttk.Label(debug_frame, text="Debug Output").pack()
        self.debug_output = scrolledtext.ScrolledText(debug_frame, height=10)
        self.debug_output.pack(expand=True, fill=tk.X)

        # ---------------- Подсказка ----------------
        hint_frame = ttk.Frame(self.root, height=25)
        hint_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.hint_label = ttk.Label(hint_frame, text="Подсказка по командам Astra...", anchor="w")
        self.hint_label.pack(fill=tk.X)

        self.astra = Astra(self.debug_output)
        self.current_file = None
        self.load_build_settings()

    # ---------------- Подсветка ----------------
    def highlight_syntax(self, event=None):
        code = self.editor.get("1.0", tk.END)
        for tag in ["keyword","string","comment","number","variable"]:
            self.editor.tag_remove(tag, "1.0", tk.END)

        comment_spans = []
        for match in re.finditer(r';.*', code):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.editor.tag_add("comment", start, end)
            comment_spans.append((match.start(), match.end()))

        for match in re.finditer(r'"[^"]*"', code):
            if not any(s <= match.start() < e for s,e in comment_spans):
                start = f"1.0+{match.start()}c"
                end = f"1.0+{match.end()}c"
                self.editor.tag_add("string", start, end)

        for kw in self.KEYWORDS:
            for match in re.finditer(r'\b'+kw+r'\b', code):
                if not any(s <= match.start() < e for s,e in comment_spans):
                    start = f"1.0+{match.start()}c"
                    end = f"1.0+{match.end()}c"
                    self.editor.tag_add("keyword", start, end)

        for match in re.finditer(r'\b\d+\b', code):
            if not any(s <= match.start() < e for s,e in comment_spans):
                start = f"1.0+{match.start()}c"
                end = f"1.0+{match.end()}c"
                self.editor.tag_add("number", start, end)

        for match in re.finditer(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', code):
            word = match.group()
            if word not in self.KEYWORDS and not any(s <= match.start() < e for s,e in comment_spans):
                start = f"1.0+{match.start()}c"
                end = f"1.0+{match.end()}c"
                self.editor.tag_add("variable", start, end)

        self.on_cursor_move()
        
    def call_func(self, name):
        if name not in self.functions:
            self.debug(f"Функция '{name}' не найдена")
            return
        self.run_program(self.functions[name])

    # ---------------- Панель подсказки ----------------
    def on_cursor_move(self, event=None):
        try:
            idx = self.editor.index(tk.INSERT)
            line_start = f"{idx.split('.')[0]}.0"
            line_text = self.editor.get(line_start, f"{line_start} lineend").strip()
            first_word = line_text.split()[0] if line_text else ""
            hint = self.HINTS.get(first_word.upper(), "Astra IDE: используйте команды TEXTVAR, UPDATEVAR, PRINT, IF, WHILE, FUNCTION...")
            self.hint_label.config(text=hint)
        except:
            self.hint_label.config(text="")

    # ---------------- Работа с проектом ----------------
    def load_project_files(self):
        self.tree.delete(*self.tree.get_children())
        self.insert_files(os.getcwd(), "")

    def insert_files(self, path, parent):
        try:
            for item in os.listdir(path):
                abs_path = os.path.join(path, item)
                if os.path.isdir(abs_path):
                    node = self.tree.insert(parent, "end", text=item, open=False)
                    self.insert_files(abs_path, node)
                else:
                    self.tree.insert(parent, "end", text=item, values=(abs_path,))
        except Exception as e:
            print(f"Ошибка при загрузке файлов: {e}")
            
    def run_program_with_highlighting(self):
        code_lines = self.editor.get("1.0", tk.END).splitlines()
        errors = []
        warnings = []

        for i, line in enumerate(code_lines, start=1):
            try:
                # Тестовое выполнение, можно интегрировать с Astra
                if "PRINT" in line and "UNKNOWN" in line:
                    warnings.append(i)
                if "ERROR" in line:
                    raise Exception("Test error")
            except Exception as e:
                errors.append(i)
        
        self.highlight_issues(errors, warnings)

    def create_file(self):
        filename = simpledialog.askstring("Создать файл", "Введите имя файла:")
        if filename:
            if not os.path.splitext(filename)[1]:
                filename += ".ast"
            if os.path.exists(filename):
                messagebox.showerror("Ошибка","Файл уже существует!")
                return
            with open(filename, "w", encoding="utf-8") as f:
                f.write("; Новый файл Astra\n")
            self.load_project_files()
            messagebox.showinfo("Готово", f"Файл {filename} создан")

    def open_file_from_tree(self, event):
        selected = self.tree.selection()
        if selected:
            node = selected[0]
            try:
                text = self.tree.item(node, "text")
                abs_path = os.path.join(os.getcwd(), text)
                if os.path.isfile(abs_path):
                    with open(abs_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    self.editor.delete("1.0", tk.END)
                    self.editor.insert(tk.END, content)
                    self.highlight_syntax()
                    self.current_file = abs_path
                    self.debug_output.insert(tk.END,f"Открыт файл {abs_path}\n")
                    self.debug_output.see(tk.END)
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

    def save_file(self):
        if self.current_file:
            try:
                with open(self.current_file, "w", encoding="utf-8") as f:
                    f.write(self.editor.get("1.0", tk.END))
                self.debug_output.insert(tk.END,f"Файл {self.current_file} сохранён\n")
                self.debug_output.see(tk.END)
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))
        else:
            filename = filedialog.asksaveasfilename(defaultextension=".ast", filetypes=[("All files","*.*")])
            if filename:
                try:
                    with open(filename, "w", encoding="utf-8") as f:
                        f.write(self.editor.get("1.0", tk.END))
                    self.current_file = filename
                    self.load_project_files()
                    self.debug_output.insert(tk.END,f"Файл {filename} сохранён\n")
                    self.debug_output.see(tk.END)
                except Exception as e:
                    messagebox.showerror("Ошибка", str(e))

    # ---------------- Программы ----------------
    def start_program(self):
        code = [line for line in self.editor.get("1.0", tk.END).splitlines() if line.strip() != ""]
        if not code:
            self.debug_output.insert(tk.END, "Нет кода для выполнения!\n")
            self.debug_output.see(tk.END)
            return
        threading.Thread(target=self.astra.run_program, args=(code,), daemon=True).start()

    def stop_program(self):
        self.astra.running = False
        self.debug_output.insert(tk.END, "Программа остановлена пользователем.\n")
        self.debug_output.see(tk.END)

    def create_guide_window(self):
        script_dir = os.path.dirname(__file__)
        file_path = os.path.join(script_dir, 'index.html')
        url = 'file:///' + os.path.abspath(file_path)
        webbrowser.open(url)
    def run(self):
        self.root.mainloop()

# -------------------- Запуск IDE --------------------
if __name__=="__main__":
    ide = AstraIDE()
    ide.run()

