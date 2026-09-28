from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import cv2
import numpy as np
from PIL import Image, ImageTk

BRIGHTNESS_VALUE = 50


class ImageConverter:
    def __init__(self, root):
        self.root = root
        self.style = ttk.Style(root)
        self.style.theme_use("clam")
        self.style.configure(".", background="#171a1f", foreground="#e8edf2")
        self.style.configure("TFrame", background="#171a1f")
        self.style.configure("TLabel", background="#171a1f", foreground="#e8edf2")
        self.style.configure(
            "TLabelframe",
            background="#20252c",
            foreground="#e8edf2",
            bordercolor="#39414b",
        )
        self.style.configure(
            "TLabelframe.Label",
            background="#20252c",
            foreground="#62d6c5",
        )
        self.style.configure(
            "TButton",
            background="#29323c",
            foreground="#f2f5f7",
            bordercolor="#46515d",
            padding=(12, 7),
        )
        self.style.map(
            "TButton",
            background=[("active", "#35434e"), ("disabled", "#22272d")],
            foreground=[("disabled", "#77818b")],
        )
        self.style.configure(
            "TNotebook",
            background="#171a1f",
            bordercolor="#39414b",
        )
        self.style.configure(
            "TNotebook.Tab",
            background="#22272e",
            foreground="#bdc7d0",
            padding=(14, 9),
        )
        self.style.map(
            "TNotebook.Tab",
            background=[("selected", "#303a43"), ("active", "#29323c")],
            foreground=[("selected", "#75e0d0")],
        )
        self.style.configure("TCheckbutton", background="#171a1f", foreground="#e8edf2")
        self.style.map("TCheckbutton", background=[("active", "#171a1f")])
        self.style.configure("TScale", background="#171a1f", troughcolor="#303943")
        root.configure(background="#171a1f")
        self.root.title("Trình xem và chuyển đổi ảnh")
        self.root.geometry("1320x720")
        self.root.minsize(960, 520)

        self.original_bgr = None
        self.original_path = None
        self.geometry_bgr = None
        self.geometry_viewport_size = None
        self.geometry_zoom_level = 1.0
        self.second_bgr = None
        self.second_path = None
        self.and_result = None
        self.photos = {}
        self.views = {}
        self.exercise_buttons = []
        self.result_areas = {}
        self.result_photos = {}

        toolbar = ttk.Frame(root, padding=12)
        toolbar.grid(row=0, column=0, sticky="ew")

        ttk.Button(
            toolbar,
            text="Chọn ảnh",
            command=self.open_image,
        ).pack(side="left", padx=(0, 8))

        self.notebook = ttk.Notebook(root)
        self.notebook.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 8))

        color_page = ttk.Frame(self.notebook, padding=8)
        self.notebook.add(color_page, text="Chuyển màu")
        color_toolbar = ttk.Frame(color_page)
        color_toolbar.grid(row=0, column=0, sticky="ew")
        self.convert_button = ttk.Button(
            color_toolbar,
            text="Chuyển màu",
            command=self.convert_image,
            state="disabled",
        )
        self.convert_button.pack(side="left")

        and_page = ttk.Frame(self.notebook, padding=20)
        self.and_page = and_page
        self.notebook.add(and_page, text="Áp dụng AND")
        ttk.Label(
            and_page,
            text="Áp dụng AND",
            font=("Segoe UI", 14, "bold"),
        ).pack(anchor="w", pady=(0, 12))
        ttk.Label(
            and_page,
            text="Ảnh gốc ở ô 1 sẽ kết hợp với ảnh bạn chọn ở ô 2.",
        ).pack(anchor="w", pady=(0, 12))
        and_controls = ttk.Frame(and_page)
        and_controls.pack(fill="x", pady=(0, 8))
        and_controls.columnconfigure(0, weight=1, uniform="and_controls")
        and_controls.columnconfigure(1, weight=1, uniform="and_controls")

        second_panel = ttk.LabelFrame(and_controls, text="Ảnh thứ hai", padding=12)
        second_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        self.second_image_view = ttk.Label(
            second_panel,
            text="Chưa chọn ảnh thứ hai",
            anchor="center",
        )
        self.second_image_view.pack(anchor="w", pady=(0, 8))
        self.and_select_button = ttk.Button(
            second_panel,
            text="Chọn ảnh thứ hai",
            command=self.choose_second_image,
            state="disabled",
        )
        self.and_select_button.pack(anchor="w")
        self.exercise_buttons.append(self.and_select_button)

        and_action_panel = ttk.LabelFrame(and_controls, text="Thao tác AND", padding=12)
        and_action_panel.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        ttk.Label(
            and_action_panel,
            text="Kết hợp ảnh gốc với ảnh thứ hai theo phép AND.",
            wraplength=360,
        ).pack(anchor="w", pady=(0, 12))
        self.and_apply_button = ttk.Button(
            and_action_panel,
            text="Áp dụng AND",
            command=self.apply_bitwise_and,
            state="disabled",
        )
        self.and_apply_button.pack(anchor="w")
        self.create_result_area("and", and_page)

        save_page = ttk.Frame(self.notebook, padding=20)
        self.notebook.add(save_page, text="Lưu nhiều dạng ảnh")
        ttk.Label(
            save_page,
            text="Lưu dưới nhiều dạng ảnh",
            font=("Segoe UI", 14, "bold"),
        ).pack(anchor="w", pady=(0, 12))
        ttk.Label(save_page, text="Chọn các định dạng cần xuất:").pack(anchor="w")
        self.format_vars = {
            "PNG": tk.BooleanVar(value=True),
            "JPEG": tk.BooleanVar(value=True),
            "BMP": tk.BooleanVar(value=True),
        }
        format_choices = ttk.Frame(save_page)
        format_choices.pack(anchor="w", pady=(6, 12))
        for image_format, variable in self.format_vars.items():
            ttk.Checkbutton(
                format_choices,
                text=image_format,
                variable=variable,
            ).pack(side="left", padx=(0, 12))
        save_button = ttk.Button(
            save_page,
            text="Lưu định dạng đã chọn",
            command=self.save_formats,
            state="disabled",
        )
        save_button.pack(anchor="w")
        self.exercise_buttons.append(save_button)
        self.create_result_area("save", save_page)

        brightness_page = ttk.Frame(self.notebook, padding=20)
        self.brightness_page = brightness_page
        self.notebook.add(brightness_page, text="Tăng cường độ sáng")
        ttk.Label(
            brightness_page,
            text="Tăng cường độ sáng",
            font=("Segoe UI", 14, "bold"),
        ).pack(anchor="w", pady=(0, 12))
        self.brightness_value = tk.IntVar(value=BRIGHTNESS_VALUE)
        self.brightness_label = ttk.Label(
            brightness_page,
            text=f"Mức điều chỉnh: +{BRIGHTNESS_VALUE}",
        )
        self.brightness_label.pack(anchor="w")
        brightness_scale = ttk.Scale(
            brightness_page,
            from_=0,
            to=100,
            orient="horizontal",
            variable=self.brightness_value,
            command=self.update_brightness_label,
        )
        brightness_scale.pack(anchor="w", fill="x", padx=(0, 24), pady=8)
        brightness_button = ttk.Button(
            brightness_page,
            text="Áp dụng độ sáng",
            command=self.increase_brightness,
            state="disabled",
        )
        brightness_button.pack(anchor="w", pady=(4, 0))
        self.exercise_buttons.append(brightness_button)
        self.create_result_area("brightness", brightness_page)

        geometry_page = ttk.Frame(self.notebook, padding=20)
        self.geometry_page = geometry_page
        self.notebook.add(geometry_page, text="Phép biến đổi hình học")
        ttk.Label(
            geometry_page,
            text="Phép biến đổi hình học",
            font=("Segoe UI", 14, "bold"),
        ).pack(fill="x", pady=(0, 12))
        ttk.Label(
            geometry_page,
            text="Mỗi thao tác áp dụng lên ảnh đang chỉnh.",
        ).pack(fill="x", pady=(0, 12))
        geometry_controls = ttk.Frame(geometry_page)
        geometry_controls.pack(fill="x", pady=(0, 8))
        for column in range(8):
            geometry_controls.columnconfigure(
                column,
                weight=1,
                uniform="geometry_button_cells",
            )
        geometry_actions = [
            ("Xoay 90°", self.rotate_geometry),
            ("Dịch trái 50 px", lambda: self.translate_geometry(-50, 0)),
            ("Dịch phải 50 px", lambda: self.translate_geometry(50, 0)),
            ("Dịch lên 50 px", lambda: self.translate_geometry(0, -50)),
            ("Dịch xuống 50 px", lambda: self.translate_geometry(0, 50)),
            ("Phóng to 1.5×", self.zoom_geometry),
            ("Đặt lại ảnh gốc", self.reset_geometry),
        ]
        self.geometry_buttons = []
        for index, (label, command) in enumerate(geometry_actions):
            button = ttk.Button(
                geometry_controls,
                text=label,
                command=command,
                state="disabled",
                width=20,
            )
            row = 0 if index < 4 else 1
            column = index * 2 if index < 4 else 1 + (index - 4) * 2
            button.grid(
                row=row,
                column=column,
                columnspan=2,
                sticky="ew",
                padx=8,
                pady=6,
            )
            self.geometry_buttons.append(button)
            self.exercise_buttons.append(button)
        self.create_result_area("geometry", geometry_page)

        content = ttk.Frame(color_page, padding=(0, 8, 0, 0))
        content.grid(row=1, column=0, sticky="nsew")
        color_page.columnconfigure(0, weight=1)
        color_page.rowconfigure(1, weight=1)

        titles = [
            ("original", "Ảnh nguyên bản"),
            ("gray", "Ảnh grayscale"),
            ("hsv", "Ảnh HSV"),
        ]

        for column, (key, title) in enumerate(titles):
            content.columnconfigure(column, weight=1, uniform="image_panels")
            panel = ttk.LabelFrame(content, text=title, padding=8)
            panel.grid(
                row=0,
                column=column,
                sticky="nsew",
                padx=6,
            )

            view = ttk.Label(panel, anchor="center")
            view.pack(fill="both", expand=True)
            view.configure(text="Chưa có ảnh")
            self.views[key] = view

        content.rowconfigure(0, weight=1)
        root.columnconfigure(0, weight=1)
        root.rowconfigure(1, weight=1)

        self.status = ttk.Label(root, text="Hãy chọn một ảnh.", padding=(12, 4))
        self.status.grid(row=2, column=0, sticky="ew")
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

    @staticmethod
    def read_image_file(path):
        # Pillow hỗ trợ đường dẫn Unicode trên Windows.
        with Image.open(path) as image:
            rgb = np.array(image.convert("RGB"))
        return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)

    def create_result_area(self, key, parent):
        area = ttk.Frame(parent)
        area.pack(fill="both", expand=True, pady=(16, 0))
        ttk.Label(area, text="Kết quả sẽ hiển thị tại đây.").pack(anchor="w")
        self.result_areas[key] = area
        self.result_photos[key] = []

    def open_image(self):
        path = filedialog.askopenfilename(
            title="Chọn ảnh",
            filetypes=[
                (
                    "Tệp ảnh",
                    "*.png *.jpg *.jpeg *.jfif *.bmp *.tif *.tiff *.webp",
                ),
                ("Tất cả tệp", "*.*"),
            ],
        )
        if not path:
            return

        try:
            self.original_bgr = self.read_image_file(path)
            self.original_path = path
            self.geometry_bgr = self.original_bgr.copy()
            self.geometry_viewport_size = self.geometry_bgr.shape[:2]
            self.geometry_zoom_level = 1.0
            self.show_image("original", self.original_bgr)
            self.show_placeholder("gray")
            self.show_placeholder("hsv")
            self.convert_button.configure(state="normal")
            for button in self.exercise_buttons:
                button.configure(state="normal")
            self.and_apply_button.configure(
                state="normal" if self.second_bgr is not None else "disabled"
            )
            self.refresh_and_slots(reset_result=True)
            self.refresh_geometry_preview()
            self.increase_brightness()

            height, width = self.original_bgr.shape[:2]
            self.status.configure(
                text=f"{path}  |  Kích thước: {width} x {height}"
            )
        except Exception as error:
            messagebox.showerror("Không thể mở ảnh", str(error))

    def convert_image(self):
        if self.original_bgr is None:
            return

        gray = cv2.cvtColor(self.original_bgr, cv2.COLOR_BGR2GRAY)

        hsv = cv2.cvtColor(self.original_bgr, cv2.COLOR_BGR2HSV)
        hue, saturation, value = cv2.split(hsv)
        hsv_preview = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

        color_ranges = [
            (0, 10, (0, 0, 255)),
            (170, 179, (0, 0, 255)),
            (11, 20, (0, 128, 255)),
            (21, 34, (0, 255, 255)),
            (35, 84, (0, 255, 0)),
            (85, 99, (255, 255, 0)),
            (100, 124, (255, 0, 0)),
            (125, 145, (128, 0, 128)),
            (146, 169, (203, 192, 255)),
        ]
        chromatic = (saturation >= 45) & (value >= 40)
        for lower_hue, upper_hue, color in color_ranges:
            mask = (
                (hue >= lower_hue)
                & (hue <= upper_hue)
                & chromatic
            )
            hsv_preview[mask] = color

        self.show_image("original", self.original_bgr)
        self.show_image("gray", gray, grayscale=True)
        self.show_image("hsv", hsv_preview)

    def choose_second_image(self):
        if self.original_bgr is None:
            return

        path = filedialog.askopenfilename(
            parent=self.root,
            title="Chọn ảnh thứ hai cho phép AND",
            filetypes=[
                ("Tệp ảnh", "*.png *.jpg *.jpeg *.jfif *.bmp *.tif *.tiff *.webp")
            ],
        )
        if not path:
            return

        try:
            self.second_bgr = self.read_image_file(path)
            self.second_path = path
        except Exception as error:
            messagebox.showerror("Không thể mở ảnh", str(error), parent=self.root)
            return

        self.second_image_view.configure(
            text=Path(path).name,
        )
        self.and_apply_button.configure(state="normal")
        self.refresh_and_slots(reset_result=True)

    def resized_second_image(self):
        if self.original_bgr is None or self.second_bgr is None:
            return None

        height, width = self.original_bgr.shape[:2]
        if self.second_bgr.shape[:2] == (height, width):
            return self.second_bgr.copy()

        # Đưa ảnh thứ hai về cùng kích thước với ảnh gốc trước khi AND.
        interpolation = (
            cv2.INTER_AREA
            if self.second_bgr.shape[0] > height or self.second_bgr.shape[1] > width
            else cv2.INTER_LINEAR
        )
        return cv2.resize(
            self.second_bgr,
            (width, height),
            interpolation=interpolation,
        )

    def refresh_and_slots(self, result=None, reset_result=False):
        if self.original_bgr is None:
            return

        if reset_result:
            self.and_result = None
        elif result is not None:
            self.and_result = result

        self.show_results_in_tab(
            "and",
            [
                ("Ảnh 1 · Ảnh gốc", self.original_bgr),
                ("Ảnh 2", self.resized_second_image()),
                ("Ảnh AND", self.and_result),
            ],
        )

    def on_tab_changed(self, _event=None):
        selected_tab = self.notebook.select()
        if selected_tab == str(self.and_page) and self.original_bgr is not None:
            self.root.after_idle(self.refresh_and_slots)
        elif selected_tab == str(self.brightness_page) and self.original_bgr is not None:
            self.root.after_idle(self.increase_brightness)
        elif selected_tab == str(self.geometry_page) and self.geometry_bgr is not None:
            self.root.after_idle(self.refresh_geometry_preview)

    def apply_bitwise_and(self):
        if self.original_bgr is None or self.second_bgr is None:
            return

        second_image = self.resized_second_image()

        # AND từng bit giữa hai ảnh để tạo ảnh kết quả.
        result = cv2.bitwise_and(self.original_bgr, second_image)
        self.refresh_and_slots(result)

    def save_formats(self):
        if self.original_bgr is None:
            return

        selected_formats = [
            image_format
            for image_format, variable in self.format_vars.items()
            if variable.get()
        ]
        if not selected_formats:
            messagebox.showwarning(
                "Chưa chọn định dạng",
                "Hãy chọn ít nhất một định dạng ảnh.",
                parent=self.root,
            )
            return

        directory = filedialog.askdirectory(
            parent=self.root,
            title="Chọn thư mục lưu ảnh",
        )
        if not directory:
            return

        base_name = Path(self.original_path).stem if self.original_path else "anh"
        all_output_files = {
            "PNG": Path(directory) / f"{base_name}_ket_qua.png",
            "JPEG": Path(directory) / f"{base_name}_ket_qua.jpg",
            "BMP": Path(directory) / f"{base_name}_ket_qua.bmp",
        }
        output_files = {
            image_format: all_output_files[image_format]
            for image_format in selected_formats
        }
        saved_files = []
        failed_files = []
        saved_formats = []
        for image_format, output_path in output_files.items():
            # cv2.imwrite chọn định dạng ảnh theo phần mở rộng của file.
            if cv2.imwrite(str(output_path), self.original_bgr):
                saved_files.append(f"{image_format}: {output_path}")
                saved_formats.append(image_format)
            else:
                failed_files.append(f"{image_format}: {output_path}")

        if failed_files:
            messagebox.showwarning(
                "Lưu ảnh",
                "Không lưu được:\n" + "\n".join(failed_files),
                parent=self.root,
            )
        else:
            messagebox.showinfo(
                "Đã lưu ảnh",
                "Đã lưu các định dạng:\n" + "\n".join(saved_files),
                parent=self.root,
            )

        previews = [
            (f"Ảnh {image_format}", self.original_bgr.copy())
            for image_format in saved_formats
        ]
        if not previews:
            return
        self.show_results_in_tab("save", previews)

    def increase_brightness(self):
        if self.original_bgr is None:
            return

        # cv2.add cộng độ sáng và tự chặn giá trị pixel ở mức 255.
        brightness_level = self.brightness_value.get()
        brightness = np.full_like(self.original_bgr, brightness_level)
        brighter_image = cv2.add(self.original_bgr, brightness)
        self.show_results_in_tab(
            "brightness",
            [
                ("Ảnh gốc", self.original_bgr),
                (f"Tăng sáng +{brightness_level}", brighter_image),
            ],
        )

    def update_brightness_label(self, value):
        brightness_level = round(float(value))
        self.brightness_value.set(brightness_level)
        self.brightness_label.configure(
            text=f"Mức điều chỉnh: +{brightness_level}"
        )

    def rotate_geometry(self):
        if self.geometry_bgr is None:
            return

        # Mỗi lần bấm xoay ảnh hiện tại thêm 90 độ theo chiều kim đồng hồ.
        self.geometry_bgr = cv2.rotate(
            self.geometry_bgr,
            cv2.ROTATE_90_CLOCKWISE,
        )
        viewport_height, viewport_width = self.geometry_viewport_size
        self.geometry_viewport_size = (viewport_width, viewport_height)
        self.refresh_geometry_preview()

    def translate_geometry(self, offset_x, offset_y):
        if self.geometry_bgr is None:
            return

        height, width = self.geometry_bgr.shape[:2]
        translation_matrix = np.float32(
            [[1, 0, offset_x], [0, 1, offset_y]]
        )
        # Dịch ảnh theo hướng đã chọn 50 pixel, giữ nguyên khung ảnh.
        self.geometry_bgr = cv2.warpAffine(
            self.geometry_bgr,
            translation_matrix,
            (width, height),
        )
        self.refresh_geometry_preview()

    def zoom_geometry(self):
        if self.geometry_bgr is None:
            return

        # Phóng ảnh hiện tại lên 1.5 lần theo cả hai chiều.
        self.geometry_bgr = cv2.resize(
            self.geometry_bgr,
            None,
            fx=1.5,
            fy=1.5,
            interpolation=cv2.INTER_LINEAR,
        )
        self.geometry_zoom_level *= 1.5
        self.refresh_geometry_preview()

    def reset_geometry(self):
        if self.original_bgr is None:
            return

        self.geometry_bgr = self.original_bgr.copy()
        self.geometry_viewport_size = self.geometry_bgr.shape[:2]
        self.geometry_zoom_level = 1.0
        self.refresh_geometry_preview()

    def refresh_geometry_preview(self):
        if self.original_bgr is None or self.geometry_bgr is None:
            return

        preview = self.geometry_bgr
        if self.geometry_zoom_level > 1:
            viewport_height, viewport_width = self.geometry_viewport_size
            image_height, image_width = self.geometry_bgr.shape[:2]
            top = max((image_height - viewport_height) // 2, 0)
            left = max((image_width - viewport_width) // 2, 0)
            preview = self.geometry_bgr[
                top : top + viewport_height,
                left : left + viewport_width,
            ]

        self.show_results_in_tab(
            "geometry",
            [
                ("Ảnh gốc", self.original_bgr),
                ("Ảnh đang chỉnh", self.geometry_bgr, preview),
            ],
        )

    def show_results_in_tab(self, key, results):
        area = self.result_areas[key]
        for child in area.winfo_children():
            child.destroy()

        self.root.update_idletasks()
        view_width = max((area.winfo_width() - 24) // max(len(results), 1) - 20, 1)
        view_height = max(area.winfo_height() - 110, 1)
        self.result_photos[key] = []

        for column, result in enumerate(results):
            label, image_array = result[:2]
            preview_array = result[2] if len(result) > 2 else image_array
            area.columnconfigure(column, weight=1, uniform=f"{key}_results")
            panel = ttk.LabelFrame(area, text=label, padding=8)
            panel.grid(row=0, column=column, sticky="nsew", padx=4)

            if image_array is None:
                ttk.Label(panel, text="Chưa có ảnh", anchor="center").pack(
                    fill="both", expand=True
                )
                continue

            if preview_array.ndim == 2:
                image = Image.fromarray(preview_array)
            else:
                rgb = cv2.cvtColor(preview_array, cv2.COLOR_BGR2RGB)
                image = Image.fromarray(rgb)
            image.thumbnail((view_width, view_height), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image, master=self.root)
            self.result_photos[key].append(photo)

            ttk.Label(panel, image=photo, anchor="center").pack(
                fill="both", expand=True
            )
            ttk.Button(
                panel,
                text="Tải ảnh",
                command=lambda name=label, array=image_array: self.download_image(
                    self.root, name, array
                ),
            ).pack(pady=(8, 0))

    def download_image(self, parent, label, image_array):
        base_name = Path(self.original_path).stem if self.original_path else "anh"
        safe_label = "_".join(label.strip().lower().split())
        path = filedialog.asksaveasfilename(
            parent=parent,
            title="Tải ảnh đã xử lý",
            initialfile=f"{base_name}_{safe_label}.png",
            defaultextension=".png",
            filetypes=[
                ("PNG", "*.png"),
                ("JPEG", "*.jpg *.jpeg"),
                ("BMP", "*.bmp"),
            ],
        )
        if not path:
            return

        try:
            if image_array.ndim == 2:
                image = Image.fromarray(image_array)
            else:
                rgb = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)
                image = Image.fromarray(rgb)
            image.save(path)
        except Exception as error:
            messagebox.showerror(
                "Không thể tải ảnh",
                str(error),
                parent=parent,
            )

    def show_placeholder(self, key):
        self.views[key].configure(image="", text="Chưa chuyển đổi")
        self.photos.pop(key, None)

    def show_image(self, key, image_array, grayscale=False):
        if grayscale:
            image = Image.fromarray(image_array)
        else:
            rgb = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(rgb)

        max_width = max(min(view.winfo_width() for view in self.views.values()) - 20, 1)
        max_height = max(min(view.winfo_height() for view in self.views.values()) - 20, 1)
        image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)

        photo = ImageTk.PhotoImage(image)
        self.photos[key] = photo
        self.views[key].configure(image=photo, text="")


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageConverter(root)
    root.mainloop()