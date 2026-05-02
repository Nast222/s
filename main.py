import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
from datetime import datetime

FILENAME = "expenses.json"

# --- Работа с JSON ---
def load_expenses():
    if os.path.exists(FILENAME):
        with open(FILENAME, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_expenses(expenses):
    with open(FILENAME, 'w', encoding='utf-8') as f:
        json.dump(expenses, f, ensure_ascii=False, indent=2)

# --- Валидация ---
def is_valid_amount(value):
    try:
        return float(value) > 0
    except ValueError:
        return False

def is_valid_date(value):
    try:
        datetime.strptime(value, "%Y-%m-%d")
        return True
    except ValueError:
        return False

# --- Основная логика ---
class ExpenseTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker")
        self.root.geometry("700x500")

        self.expenses = load_expenses()

        # Виджеты
        self.create_widgets()
        self.update_treeview()

    def create_widgets(self):
        # Поля ввода
        ttk.Label(self.root, text="Сумма:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
        self.amount_entry = ttk.Entry(self.root)
        self.amount_entry.grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(self.root, text="Категория:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.category_entry = ttk.Entry(self.root)
        self.category_entry.grid(row=1, column=1, padx=10, pady=5)

        ttk.Label(self.root, text="Дата (ГГГГ-ММ-ДД):").grid(row=2, column=0, padx=10, pady=5, sticky="e")
        self.date_entry = ttk.Entry(self.root)
        self.date_entry.grid(row=2, column=1, padx=10, pady=5)

        # Кнопки
        ttk.Button(self.root, text="Добавить расход", command=self.add_expense).grid(row=3, column=0, columnspan=2, pady=10)

        # Таблица расходов
        self.columns = ("Сумма", "Категория", "Дата")
        self.tree = ttk.Treeview(self.root, columns=self.columns, show="headings")
        for col in self.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)
        self.tree.grid(row=4, column=0, columnspan=3, padx=10, pady=5, sticky="nsew")

        # Фильтры и сумма
        ttk.Button(self.root, text="Фильтр по категории", command=self.filter_by_category).grid(row=5, column=0, pady=5)
        ttk.Button(self.root, text="Фильтр по дате", command=self.filter_by_date).grid(row=5, column=1, pady=5)
        
        self.sum_label = ttk.Label(self.root, text="Сумма за период: 0.00 ₽")
        self.sum_label.grid(row=6, column=0, columnspan=2, pady=10)
        
        ttk.Button(self.root, text="Подсчитать сумму за период", command=self.calculate_sum).grid(row=6, column=2, pady=10)

    def add_expense(self):
        amount = self.amount_entry.get()
        category = self.category_entry.get()
        date = self.date_entry.get()

        if not all([amount, category, date]):
            messagebox.showerror("Ошибка", "Заполните все поля!")
            return

        if not is_valid_amount(amount):
            messagebox.showerror("Ошибка", "Сумма должна быть положительным числом!")
            return

        if not is_valid_date(date):
            messagebox.showerror("Ошибка", "Дата должна быть в формате ГГГГ-ММ-ДД!")
            return

        self.expenses.append({
            "amount": float(amount),
            "category": category,
            "date": date
        })

        save_expenses(self.expenses)
        self.update_treeview()
        
        # Очистка полей
        self.amount_entry.delete(0, tk.END)
        self.category_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)

    def update_treeview(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        for exp in self.expenses:
            self.tree.insert("", tk.END, values=(exp["amount"], exp["category"], exp["date"]))
        
    def filter_by_category(self):
        category = simpledialog.askstring("Фильтр", "Введите категорию:")
        if category:
            filtered = [e for e in self.expenses if e["category"].lower() == category.lower()]
            self.show_filtered(filtered)
    
    def filter_by_date(self):
        date = simpledialog.askstring("Фильтр", "Введите дату (ГГГГ-ММ-ДД):")
        if date and is_valid_date(date):
            filtered = [e for e in self.expenses if e["date"] == date]
            self.show_filtered(filtered)
    
    def show_filtered(self, filtered_list):
         for i in self.tree.get_children():
             self.tree.delete(i)
         for exp in filtered_list:
             self.tree.insert("", tk.END, values=(exp["amount"], exp["category"], exp["date"]))
    
    def calculate_sum(self):
         start_date = simpledialog.askstring("Период", "Введите начальную дату (ГГГГ-ММ-ДД):")
         end_date   = simpledialog.askstring("Период", "Введите конечную дату (ГГГГ-ММ-ДД):")
         
         if not (start_date and end_date and is_valid_date(start_date) and is_valid_date(end_date)):
             messagebox.showerror("Ошибка", "Некорректный формат даты!")
             return

         start_dt = datetime.strptime(start_date, "%Y-%m-%d")
         end_dt   = datetime.strptime(end_date, "%Y-%m-%d")
         
         total = sum(
             exp["amount"] 
             for exp in self.expenses 
             if start_dt <= datetime.strptime(exp["date"], "%Y-%m-%d") <= end_dt
         )
         
         self.sum_label.config(text=f"Сумма за период: {total:.2f} ₽")

if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTrackerApp(root)
    root.mainloop()
