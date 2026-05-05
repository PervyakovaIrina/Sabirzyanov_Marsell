import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

# Имя файла для хранения данных
DATA_FILE = "movies.json"

class MovieLibrary:
    def __init__(self, root):
        self.root = root
        self.root.title("Movie Library (GosPrompt AI)")
        self.root.geometry("800x600")

        self.movies = []
        self.load_data()

        # --- Интерфейс: Форма ввода ---
        input_frame = tk.LabelFrame(root, text="Добавить фильм", padx=10, pady=10)
        input_frame.pack(fill="x", padx=10, pady=5)

        # Название
        tk.Label(input_frame, text="Название:").grid(row=0, column=0, sticky="w")
        self.entry_title = tk.Entry(input_frame, width=30)
        self.entry_title.grid(row=0, column=1, padx=5)

        # Жанр
        tk.Label(input_frame, text="Жанр:").grid(row=0, column=2, sticky="w")
        self.entry_genre = ttk.Combobox(input_frame, values=["Драма", "Комедия", "Боевик", "Фантастика", "Ужасы", "Детектив", "Другое"], state="readonly", width=20)
        self.entry_genre.grid(row=0, column=3, padx=5)
        self.entry_genre.current(0)

        # Год
        tk.Label(input_frame, text="Год:").grid(row=0, column=4, sticky="w")
        self.entry_year = tk.Entry(input_frame, width=10)
        self.entry_year.grid(row=0, column=5, padx=5)

        # Рейтинг
        tk.Label(input_frame, text="Рейтинг (0-10):").grid(row=0, column=6, sticky="w")
        self.entry_rating = tk.Entry(input_frame, width=10)
        self.entry_rating.grid(row=0, column=7, padx=5)

        btn_add = tk.Button(input_frame, text="Добавить фильм", command=self.add_movie, bg="#4CAF50", fg="white")
        btn_add.grid(row=0, column=8, padx=10)

        # --- Интерфейс: Фильтры ---
        filter_frame = tk.LabelFrame(root, text="Фильтр", padx=10, pady=10)
        filter_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(filter_frame, text="Жанр:").grid(row=0, column=0, sticky="w")
        self.filter_genre = ttk.Combobox(filter_frame, values=["Все"] + ["Драма", "Комедия", "Боевик", "Фантастика", "Ужасы", "Детектив", "Другое"], state="readonly", width=15)
        self.filter_genre.grid(row=0, column=1, padx=5)
        self.filter_genre.set("Все")

        tk.Label(filter_frame, text="Год от:").grid(row=0, column=2, sticky="w")
        self.filter_year_start = tk.Entry(filter_frame, width=10)
        self.filter_year_start.grid(row=0, column=3, padx=5)

        tk.Label(filter_frame, text="Год до:").grid(row=0, column=4, sticky="w")
        self.filter_year_end = tk.Entry(filter_frame, width=10)
        self.filter_year_end.grid(row=0, column=5, padx=5)

        btn_filter = tk.Button(filter_frame, text="Применить", command=self.apply_filter)
        btn_filter.grid(row=0, column=6, padx=10)

        btn_reset = tk.Button(filter_frame, text="Сбросить", command=self.reset_filter)
        btn_reset.grid(row=0, column=7, padx=10)

        # --- Интерфейс: Таблица ---
        columns = ("title", "genre", "year", "rating")
        self.tree = ttk.Treeview(root, columns=columns, show="headings")

        self.tree.heading("title", text="Название")
        self.tree.heading("genre", text="Жанр")
        self.tree.heading("year", text="Год")
        self.tree.heading("rating", text="Рейтинг")

        self.tree.column("title", width=250)
        self.tree.column("genre", width=100)
        self.tree.column("year", width=80)
        self.tree.column("rating", width=80)

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Скроллбар
        scrollbar = ttk.Scrollbar(root, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Загрузка данных при старте
        self.refresh_table()

    def validate_input(self):
        title = self.entry_title.get().strip()
        genre = self.entry_genre.get()
        year_str = self.entry_year.get().strip()
        rating_str = self.entry_rating.get().strip()

        if not title:
            messagebox.showerror("Ошибка", "Введите название фильма!")
            return None

        if not year_str:
            messagebox.showerror("Ошибка", "Введите год выпуска!")
            return None
        
        try:
            year = int(year_str)
            if year < 1888 or year > 2026: # Примерная валидация
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Год должен быть целым числом (например, 2023)!")
            return None

        if not rating_str:
            messagebox.showerror("Ошибка", "Введите рейтинг!")
            return None

        try:
            rating = float(rating_str)
            if rating < 0 or rating > 10:
                messagebox.showerror("Ошибка", "Рейтинг должен быть от 0 до 10!")
                return None
        except ValueError:
            messagebox.showerror("Ошибка", "Рейтинг должен быть числом!")
            return None

        return {"title": title, "genre": genre, "year": year, "rating": rating}

    def add_movie(self):
        data = self.validate_input()
        if data:
            self.movies.append(data)
            self.save_data()
            self.refresh_table()
            # Очистка полей
            self.entry_title.delete(0, tk.END)
            self.entry_year.delete(0, tk.END)
            self.entry_rating.delete(0, tk.END)
            self.entry_title.focus()

    def apply_filter(self):
        self.refresh_table()

    def reset_filter(self):
        self.filter_genre.set("Все")
        self.filter_year_start.delete(0, tk.END)
        self.filter_year_end.delete(0, tk.END)
        self.refresh_table()

    def refresh_table(self):
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Получение фильтров
        genre_filter = self.filter_genre.get()
        start_str = self.filter_year_start.get().strip()
        end_str = self.filter_year_end.get().strip()

        try:
            start_year = int(start_str) if start_str else None
            end_year = int(end_str) if end_str else None
        except ValueError:
            messagebox.showwarning("Внимание", "Годы должны быть числами!")
            return

        for movie in self.movies:
            # Фильтр по жанру
            if genre_filter != "Все" and movie["genre"] != genre_filter:
                continue

            # Фильтр по году
            if start_year and movie["year"] < start_year:
                continue
            if end_year and movie["year"] > end_year:
                continue

            # Добавление в таблицу
            self.tree.insert("", tk.END, values=(
                movie["title"], 
                movie["genre"], 
                movie["year"], 
                f"{movie['rating']:.1f}"
            ))

    def save_data(self):
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.movies, f, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror("Ошибка сохранения", str(e))

    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    self.movies = json.load(f)
            except json.JSONDecodeError:
                self.movies = []
                messagebox.showwarning("Предупреждение", "Файл данных поврежден, создан новый.")

if __name__ == "__main__":
    root = tk.Tk()
    app = MovieLibrary(root)
    root.mainloop()
