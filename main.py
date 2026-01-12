import tkinter as tk
from tkinter import ttk, messagebox
import itertools

# Константы для цветов
COLORS = {
    'bg': '#2b2b2b',
    'sidebar': '#3c3f41',
    'canvas': '#ffffff',
    'gate': '#4a9eff',
    'gate_active': '#6ab0ff',
    'input': '#6bbf59',
    'output': '#ff6b6b',
    'not': '#ffa154',
    'wire': '#555',
    'wire_active': '#ffcc00',
    'text': '#ffffff',
    'text_dark': '#333333',
    'button': '#4a9eff',
    'button_hover': '#6ab0ff'
}


class Gate:
    def __init__(self, typ, x, y):
        self.type = typ
        self.x = x
        self.y = y
        self.value = False
        self.inputs = []
        self.width = 80
        self.height = 50
        self.selected = False
        self.radius = 8

        # Определяем цвета в зависимости от типа
        if typ == 'IN':
            self.color = COLORS['input']
        elif typ == 'OUT':
            self.color = COLORS['output']
        elif typ == 'NOT':
            self.color = COLORS['not']
        else:
            self.color = COLORS['gate']

    def compute(self):
        if self.type == 'IN':
            return self.value
        elif self.type == 'OUT':
            return self.inputs[0] if self.inputs else False
        elif self.type == 'NOT':
            return not self.inputs[0]
        elif self.type == 'AND':
            return all(self.inputs)
        elif self.type == 'OR':
            return any(self.inputs)
        elif self.type == 'XOR':
            return sum(self.inputs) % 2 == 1
        elif self.type == 'NAND':
            return not all(self.inputs)
        elif self.type == 'NOR':
            return not any(self.inputs)
        return False

    def contains_point(self, x, y):
        """Проверяет, находится ли точка внутри гейта"""
        return (self.x <= x <= self.x + self.width and
                self.y <= y <= self.y + self.height)

    def get_input_port(self):
        """Возвращает координаты входного порта"""
        return (self.x, self.y + self.height // 2)

    def get_output_port(self):
        """Возвращает координаты выходного порта"""
        return (self.x + self.width, self.y + self.height // 2)


class Connection:
    def __init__(self, src, dst):
        self.src = src
        self.dst = dst


class ModernApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🔌 Logic Circuit Simulator")
        self.root.geometry("1300x750")
        self.root.configure(bg=COLORS['bg'])

        # Устанавливаем стиль для ttk
        self.setup_styles()

        # Данные схемы
        self.gates = []
        self.connections = []
        self.drag_gate = None
        self.drag_offset = (0, 0)
        self.connect_mode = False
        self.connect_start = None

        # Создаем интерфейс
        self.create_interface()

        # Пример схемы для демонстрации
        self.create_demo_circuit()

        # Привязываем горячие клавиши
        self.bind_hotkeys()

    def setup_styles(self):
        """Настройка стилей для ttk виджетов"""
        style = ttk.Style()
        style.theme_use('clam')

        # Настройка кнопок
        style.configure('Modern.TButton',
                        background=COLORS['button'],
                        foreground=COLORS['text'],
                        borderwidth=1,
                        focusthickness=3,
                        focuscolor='none',
                        font=('Segoe UI', 10),
                        padding=8
                        )
        style.map('Modern.TButton',
                  background=[('active', COLORS['button_hover']),
                              ('pressed', COLORS['gate_active'])],
                  foreground=[('pressed', COLORS['text'])]
                  )

        # Настройка меток
        style.configure('Title.TLabel',
                        background=COLORS['sidebar'],
                        foreground=COLORS['text'],
                        font=('Segoe UI', 12, 'bold')
                        )

    def create_interface(self):
        """Создание интерфейса"""
        # Главный контейнер
        main_container = tk.Frame(self.root, bg=COLORS['bg'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Левая панель (sidebar)
        self.create_sidebar(main_container)

        # Разделитель
        separator = ttk.Separator(main_container, orient='vertical')
        separator.pack(side=tk.LEFT, fill=tk.Y, padx=5)

        # Правая панель (рабочая область)
        self.create_workspace(main_container)

    def create_sidebar(self, parent):
        """Создание боковой панели с элементами"""
        sidebar = tk.Frame(parent, bg=COLORS['sidebar'], width=220)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)

        # Заголовок
        title_frame = tk.Frame(sidebar, bg=COLORS['sidebar'])
        title_frame.pack(fill=tk.X, pady=(0, 10))
        tk.Label(title_frame, text="ЛОГИЧЕСКИЕ ЭЛЕМЕНТЫ",
                 bg=COLORS['sidebar'], fg=COLORS['text'],
                 font=('Segoe UI', 11, 'bold')).pack(pady=15)

        # Элементы схемы
        elements_frame = tk.Frame(sidebar, bg=COLORS['sidebar'])
        elements_frame.pack(fill=tk.X, padx=10, pady=5)

        elements = [
            ('🔘 Вход (IN)', 'IN'),
            ('💡 Выход (OUT)', 'OUT'),
            ('∧ И (AND)', 'AND'),
            ('∨ ИЛИ (OR)', 'OR'),
            ('¬ НЕ (NOT)', 'NOT'),
            ('⊕ Искл. ИЛИ (XOR)', 'XOR'),
            ('⊼ И-НЕ (NAND)', 'NAND'),
            ('⊽ ИЛИ-НЕ (NOR)', 'NOR')
        ]

        for text, typ in elements:
            btn = ttk.Button(elements_frame, text=text, style='Modern.TButton',
                             command=lambda t=typ: self.add_gate(t))
            btn.pack(fill=tk.X, pady=3)

        # Разделитель
        ttk.Separator(sidebar, orient='horizontal').pack(fill=tk.X, pady=15)

        # Панель управления
        control_frame = tk.Frame(sidebar, bg=COLORS['sidebar'])
        control_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(control_frame, text="УПРАВЛЕНИЕ",
                 bg=COLORS['sidebar'], fg=COLORS['text'],
                 font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 8))

        controls = [
            ('▶ Запустить симуляцию', self.calc),
            ('📊 Таблица истинности', self.show_table),
            ('🔗 Соединить элементы', self.toggle_conn),
            ('🗑 Очистить схему', self.clear),
            ('💾 Сохранить схему', self.save_circuit),
            ('📂 Загрузить схему', self.load_circuit)
        ]

        for text, command in controls:
            btn = ttk.Button(control_frame, text=text, style='Modern.TButton',
                             command=command)
            btn.pack(fill=tk.X, pady=2)

        # Статус бар
        status_frame = tk.Frame(sidebar, bg=COLORS['sidebar'])
        status_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

        self.status = tk.Label(status_frame, text="✓ Готов к работе",
                               bg=COLORS['sidebar'], fg='#6bbf59',
                               font=('Segoe UI', 9))
        self.status.pack(fill=tk.X)

    def create_workspace(self, parent):
        """Создание рабочей области"""
        workspace = tk.Frame(parent, bg=COLORS['bg'])
        workspace.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Панель инструментов холста
        toolbar = tk.Frame(workspace, bg=COLORS['sidebar'], height=40)
        toolbar.pack(fill=tk.X)
        toolbar.pack_propagate(False)

        tk.Label(toolbar, text="Рабочая область",
                 bg=COLORS['sidebar'], fg=COLORS['text'],
                 font=('Segoe UI', 10)).pack(side=tk.LEFT, padx=10)

        # Информация о режиме
        self.mode_label = tk.Label(toolbar, text="Режим: Выбор",
                                   bg=COLORS['sidebar'], fg='#ffcc00',
                                   font=('Segoe UI', 9))
        self.mode_label.pack(side=tk.RIGHT, padx=10)

        # Холст для рисования
        canvas_frame = tk.Frame(workspace, bg=COLORS['bg'])
        canvas_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

        # Полосы прокрутки
        v_scroll = ttk.Scrollbar(canvas_frame, orient='vertical')
        h_scroll = ttk.Scrollbar(canvas_frame, orient='horizontal')

        self.canvas = tk.Canvas(canvas_frame, bg=COLORS['canvas'],
                                yscrollcommand=v_scroll.set,
                                xscrollcommand=h_scroll.set,
                                scrollregion=(0, 0, 2000, 2000))

        v_scroll.config(command=self.canvas.yview)
        h_scroll.config(command=self.canvas.xview)

        self.canvas.grid(row=0, column=0, sticky='nsew')
        v_scroll.grid(row=0, column=1, sticky='ns')
        h_scroll.grid(row=1, column=0, sticky='ew')

        canvas_frame.grid_rowconfigure(0, weight=1)
        canvas_frame.grid_columnconfigure(0, weight=1)

        # Привязка событий
        self.canvas.bind("<Button-1>", self.click)
        self.canvas.bind("<B1-Motion>", self.drag)
        self.canvas.bind("<ButtonRelease-1>", self.release)
        self.canvas.bind("<Double-Button-1>", self.dblclick)
        self.canvas.bind("<MouseWheel>", self.zoom)
        self.canvas.bind("<Control-MouseWheel>", self.horizontal_scroll)

    def create_demo_circuit(self):
        """Создание демонстрационной схемы"""
        # Добавляем элементы
        gates_data = [
            ('IN', 150, 150),
            ('IN', 150, 250),
            ('AND', 350, 200),
            ('OUT', 550, 200)
        ]

        for typ, x, y in gates_data:
            self.add_gate(typ, x, y)

        # Создаем соединения
        if len(self.gates) >= 4:
            self.connections = [
                Connection(self.gates[0], self.gates[2]),
                Connection(self.gates[1], self.gates[2]),
                Connection(self.gates[2], self.gates[3])
            ]
            self.redraw()

    def bind_hotkeys(self):
        """Привязка горячих клавиш"""
        self.root.bind('<c>', lambda e: self.toggle_conn())
        self.root.bind('<Delete>', lambda e: self.delete_selected())
        self.root.bind('<Escape>', lambda e: self.cancel_connection())
        self.root.bind('<Control-s>', lambda e: self.save_circuit())
        self.root.bind('<Control-l>', lambda e: self.load_circuit())
        self.root.bind('<F5>', lambda e: self.calc())

    def add_gate(self, typ, x=None, y=None):
        """Добавление нового элемента"""
        if x is None or y is None:
            x, y = 400, 300

        gate = Gate(typ, x, y)
        self.gates.append(gate)
        self.redraw()
        self.status.config(text=f"✓ Добавлен элемент {typ}", fg='#6bbf59')

    def redraw(self):
        """Перерисовка всего холста"""
        self.canvas.delete("all")

        # Сетка для фона
        self.draw_grid()

        # Рисуем все соединения
        for conn in self.connections:
            src_x, src_y = conn.src.get_output_port()
            dst_x, dst_y = conn.dst.get_input_port()

            # Цвет провода в зависимости от значения
            wire_color = COLORS['wire_active'] if conn.src.value else COLORS['wire']
            self.canvas.create_line(src_x, src_y, dst_x, dst_y,
                                    fill=wire_color, width=3,
                                    arrow=tk.LAST, arrowshape=(8, 10, 5))

        # Рисуем все элементы
        for gate in self.gates:
            self.draw_gate(gate)

    def draw_grid(self):
        """Рисует сетку на холсте"""
        grid_size = 20
        width = 2000
        height = 2000

        # Вертикальные линии
        for x in range(0, width, grid_size):
            self.canvas.create_line(x, 0, x, height,
                                    fill='#f0f0f0', tags='grid')

        # Горизонтальные линии
        for y in range(0, height, grid_size):
            self.canvas.create_line(0, y, width, y,
                                    fill='#f0f0f0', tags='grid')

    def draw_gate(self, gate):
        """Рисует один элемент"""
        x, y = gate.x, gate.y
        width, height = gate.width, gate.height
        radius = gate.radius

        # Выбираем цвет фона
        if gate.selected:
            fill_color = COLORS['gate_active']
            outline_color = '#ffcc00'
            outline_width = 3
        else:
            fill_color = gate.color
            outline_color = '#333'
            outline_width = 2

        # Рисуем скругленный прямоугольник
        self.canvas.create_rectangle(
            x + radius, y, x + width - radius, y + height,
            fill=fill_color, outline=outline_color, width=outline_width
        )
        self.canvas.create_rectangle(
            x, y + radius, x + width, y + height - radius,
            fill=fill_color, outline=outline_color, width=outline_width
        )
        self.canvas.create_oval(
            x, y, x + 2 * radius, y + 2 * radius,
            fill=fill_color, outline=outline_color, width=outline_width
        )
        self.canvas.create_oval(
            x + width - 2 * radius, y, x + width, y + 2 * radius,
            fill=fill_color, outline=outline_color, width=outline_width
        )
        self.canvas.create_oval(
            x, y + height - 2 * radius, x + 2 * radius, y + height,
            fill=fill_color, outline=outline_color, width=outline_width
        )
        self.canvas.create_oval(
            x + width - 2 * radius, y + height - 2 * radius,
            x + width, y + height,
            fill=fill_color, outline=outline_color, width=outline_width
        )

        # Текст элемента
        self.canvas.create_text(
            x + width // 2, y + height // 2,
            text=gate.type, font=('Segoe UI', 10, 'bold'),
            fill=COLORS['text']
        )

        # Отображаем значение для входов и выходов
        if gate.type in ('IN', 'OUT'):
            value_text = "1" if gate.value else "0"
            value_color = "#2ecc71" if gate.value else "#e74c3c"
            self.canvas.create_text(
                x + width - 15, y + 15,
                text=value_text, font=('Segoe UI', 12, 'bold'),
                fill=value_color
            )

        # Рисуем порты подключения
        if gate.type != 'IN':  # Входной порт
            ix, iy = gate.get_input_port()
            self.canvas.create_oval(
                ix - 6, iy - 6, ix + 6, iy + 6,
                fill='#e74c3c', outline='#c0392b', width=2
            )

        if gate.type != 'OUT':  # Выходной порт
            ox, oy = gate.get_output_port()
            self.canvas.create_oval(
                ox - 6, oy - 6, ox + 6, oy + 6,
                fill='#2ecc71', outline='#27ae60', width=2
            )

    def find_gate(self, x, y):
        """Поиск элемента по координатам"""
        for gate in self.gates:
            if gate.contains_point(x, y):
                return gate
        return None

    def find_gate_at_port(self, x, y):
        """Поиск элемента и порта по координатам"""
        for gate in self.gates:
            if gate.type != 'IN':
                ix, iy = gate.get_input_port()
                if abs(x - ix) < 10 and abs(y - iy) < 10:
                    return gate, 'input'

            if gate.type != 'OUT':
                ox, oy = gate.get_output_port()
                if abs(x - ox) < 10 and abs(y - oy) < 10:
                    return gate, 'output'

        return None, None

    def click(self, event):
        """Обработка клика мыши"""
        x, y = event.x, event.y

        if self.connect_mode:
            gate, port_type = self.find_gate_at_port(x, y)
            if gate:
                if self.connect_start is None:
                    if port_type == 'output':
                        self.connect_start = (gate, port_type)
                        self.status.config(text="Выберите входной порт...", fg='#ffcc00')
                else:
                    start_gate, start_type = self.connect_start
                    if port_type == 'input' and gate != start_gate:
                        self.connections.append(Connection(start_gate, gate))
                        self.connect_start = None
                        self.connect_mode = False
                        self.redraw()
                        self.mode_label.config(text="Режим: Выбор")
                        self.status.config(text="✓ Соединение создано", fg='#6bbf59')
                    else:
                        self.cancel_connection()
            return

        # Проверяем клик на порт для начала соединения
        gate, port_type = self.find_gate_at_port(x, y)
        if gate and port_type == 'output':
            self.connect_start = (gate, port_type)
            self.connect_mode = True
            self.mode_label.config(text="Режим: Соединение")
            self.status.config(text="Выберите входной порт...", fg='#ffcc00')
            return

        # Снимаем выделение со всех элементов
        for g in self.gates:
            g.selected = False

        # Ищем элемент под курсором
        clicked_gate = self.find_gate(x, y)
        if clicked_gate:
            clicked_gate.selected = True
            self.drag_gate = clicked_gate
            self.drag_offset = (x - clicked_gate.x, y - clicked_gate.y)
            self.redraw()
            self.status.config(text=f"Выбран: {clicked_gate.type}", fg='#3498db')
        else:
            self.redraw()

    def drag(self, event):
        """Обработка перетаскивания мыши"""
        if self.drag_gate:
            self.drag_gate.x = event.x - self.drag_offset[0]
            self.drag_gate.y = event.y - self.drag_offset[1]
            self.redraw()

    def release(self, event):
        """Обработка отпускания кнопки мыши"""
        self.drag_gate = None

    def dblclick(self, event):
        """Обработка двойного клика"""
        gate = self.find_gate(event.x, event.y)
        if gate:
            if gate.type == 'IN':
                gate.value = not gate.value
                self.redraw()
                self.status.config(text=f"Вход изменен: {'1' if gate.value else '0'}",
                                   fg='#9b59b6')
            elif gate.type == 'OUT':
                self.status.config(text=f"Выход: {'1' if gate.value else '0'}",
                                   fg='#e74c3c')
            else:
                self.status.config(text=f"Элемент {gate.type}", fg='#3498db')

    def zoom(self, event):
        """Обработка зума колесиком мыши"""
        scale = 1.1 if event.delta > 0 else 0.9
        self.canvas.scale("all", event.x, event.y, scale, scale)

    def horizontal_scroll(self, event):
        """Горизонтальная прокрутка с Ctrl"""
        self.canvas.xview_scroll(-1 if event.delta > 0 else 1, "units")

    def calc(self):
        """Запуск симуляции схемы"""
        # Очищаем входы всех элементов (кроме IN)
        for gate in self.gates:
            if gate.type != 'IN':
                gate.inputs = []

        # Передаем значения по соединениям
        for conn in self.connections:
            value = conn.src.compute()
            conn.dst.inputs.append(value)

        # Вычисляем значения выходов
        for gate in self.gates:
            if gate.type == 'OUT':
                gate.value = gate.compute()

        self.redraw()
        self.status.config(text="✅ Симуляция завершена", fg='#2ecc71')

    def show_table(self):
        """Показ таблицы истинности"""
        ins = [g for g in self.gates if g.type == 'IN']
        outs = [g for g in self.gates if g.type == 'OUT']

        if not ins:
            messagebox.showinfo("Информация", "Добавьте входные элементы (IN)")
            return

        if len(ins) > 8:
            messagebox.showwarning("Предупреждение",
                                   "Рекомендуется не более 8 входов для лучшей читаемости")

        # Создаем окно таблицы
        table_win = tk.Toplevel(self.root)
        table_win.title("📊 Таблица истинности")
        table_win.geometry("800x500")
        table_win.configure(bg=COLORS['bg'])

        # Создаем Treeview с полосами прокрутки
        frame = tk.Frame(table_win, bg=COLORS['bg'])
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Заголовки
        headers = [f"IN{i + 1}" for i in range(len(ins))] + [f"OUT{i + 1}" for i in range(len(outs))]

        tree = ttk.Treeview(frame, columns=headers, show='headings', height=20)

        # Настраиваем заголовки
        for header in headers:
            tree.heading(header, text=header)
            tree.column(header, width=80, anchor='center')

        # Добавляем полосы прокрутки
        v_scroll = ttk.Scrollbar(frame, orient='vertical', command=tree.yview)
        h_scroll = ttk.Scrollbar(frame, orient='horizontal', command=tree.xview)
        tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        tree.grid(row=0, column=0, sticky='nsew')
        v_scroll.grid(row=0, column=1, sticky='ns')
        h_scroll.grid(row=1, column=0, sticky='ew')

        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        # Генерируем все комбинации
        total_rows = 2 ** len(ins)
        progress_step = max(1, total_rows // 20)  # Обновляем прогресс каждые 5%

        for i, bits in enumerate(itertools.product([False, True], repeat=len(ins))):
            # Устанавливаем значения входов
            for gate, val in zip(ins, bits):
                gate.value = val

            # Запускаем симуляцию
            self.calc()

            # Формируем строку
            row_values = [str(int(v)) for v in bits] + \
                         [str(int(g.value)) for g in outs]

            # Добавляем строку в таблицу
            tree.insert('', 'end', values=row_values)

            # Обновляем прогресс для больших таблиц
            if total_rows > 100 and i % progress_step == 0:
                table_win.update()

        # Информация о таблице
        info_label = tk.Label(table_win,
                              text=f"Всего строк: {total_rows} | Входов: {len(ins)} | Выходов: {len(outs)}",
                              bg=COLORS['bg'], fg=COLORS['text'])
        info_label.pack(pady=(0, 10))

    def clear(self):
        """Очистка всей схемы"""
        if messagebox.askyesno("Подтверждение", "Удалить все элементы и соединения?"):
            self.gates = []
            self.connections = []
            self.connect_mode = False
            self.connect_start = None
            self.redraw()
            self.mode_label.config(text="Режим: Выбор")
            self.status.config(text="✓ Схема очищена", fg='#6bbf59')

    def toggle_conn(self):
        """Переключение режима соединения"""
        self.connect_mode = not self.connect_mode
        if self.connect_mode:
            self.mode_label.config(text="Режим: Соединение")
            self.status.config(text="🔗 Режим соединения активен", fg='#ffcc00')
        else:
            self.cancel_connection()

    def cancel_connection(self):
        """Отмена соединения"""
        self.connect_mode = False
        self.connect_start = None
        self.mode_label.config(text="Режим: Выбор")
        self.status.config(text="Режим соединения отменен", fg='#e74c3c')

    def delete_selected(self):
        """Удаление выбранного элемента"""
        for gate in self.gates[:]:  # Используем копию списка для безопасного удаления
            if gate.selected:
                # Удаляем все соединения с этим элементом
                self.connections = [c for c in self.connections
                                    if c.src != gate and c.dst != gate]
                self.gates.remove(gate)
                self.status.config(text=f"✓ Удален элемент {gate.type}", fg='#e74c3c')
                break
        self.redraw()

    def save_circuit(self):
        """Сохранение схемы (заглушка)"""
        self.status.config(text="💾 Функция сохранения в разработке", fg='#9b59b6')

    def load_circuit(self):
        """Загрузка схемы (заглушка)"""
        self.status.config(text="📂 Функция загрузки в разработке", fg='#9b59b6')


if __name__ == "__main__":
    root = tk.Tk()
    app = ModernApp(root)
    root.mainloop()