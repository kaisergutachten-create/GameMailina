# KinderLernspiel_GUI.py
# Ein einfaches Lernspiel (Zahlen, Buchstaben, Logik) für Kinder (~3 Jahre).
# Plattform: Windows (andere OS funktionieren i.d.R. ebenfalls).
# Abhängigkeiten: NUR Python-Standardbibliothek (tkinter, random, time).
# Start: python KinderLernspiel_GUI.py
#
# Build als EXE (Windows, empfohlen mit Python 3.10+):
#   1) py -m pip install pyinstaller
#   2) py -m PyInstaller --onefile --windowed KinderLernspiel_GUI.py
#      -> dist\KinderLernspiel_GUI.exe
#
# Bedienung: Große Buttons, einfache Aufgaben, positive Rückmeldungen + Sticker-Belohnung.

import tkinter as tk
from tkinter import ttk
import random
import time

APP_TITLE = "Kleines Lernspiel – Zahlen • Buchstaben • Logik"
BG = "#f7fbff"
CARD = "#ffffff"
PRIMARY = "#2563eb"
SUCCESS = "#16a34a"
WARN = "#f59e0b"
ERR = "#b91c1c"
TEXT = "#0f172a"

LARGE_BTN_FONT = ("Segoe UI", 18, "bold")
MID_BTN_FONT = ("Segoe UI", 16, "bold")
BIG_FONT = ("Segoe UI", 32, "bold")
MID_FONT = ("Segoe UI", 20, "bold")
SMALL_FONT = ("Segoe UI", 12)

EMOJIS_FRUITS = ["🍎", "🍌", "🍐", "🍇", "🍓", "🍊"]
EMOJIS_ANIMALS = ["🐶", "🐱", "🐭", "🐰", "🐻", "🦊"]
EMOJIS_MISC = ["⭐", "🚗", "⚽", "🎈", "🧸", "🪁", "🌸"]

class StickerBar(ttk.Frame):
    """Zeigt gesammelte Sticker an. Nach X richtigen Antworten gibt es 1 Sticker."""
    def __init__(self, master, goal=5):
        super().__init__(master, padding=(8,6))
        self.goal = goal
        self.counter = 0
        self.stickers = 0
        self.configure(style="Card.TFrame")

        self.info = ttk.Label(self, text="Sticker:", style="Info.TLabel")
        self.info.grid(row=0, column=0, sticky="w")

        self.sticker_lbl = ttk.Label(self, text="🌟" * self.stickers, style="Big.TLabel")
        self.sticker_lbl.grid(row=0, column=1, sticky="w", padx=(8,0))

        self.progress = ttk.Progressbar(self, length=160, maximum=self.goal)
        self.progress.grid(row=0, column=2, padx=(12,0))

    def add_point(self):
        self.counter += 1
        self.progress["value"] = self.counter
        if self.counter >= self.goal:
            self.counter = 0
            self.stickers += 1
            self.progress["value"] = 0
            self.sticker_lbl.configure(text="🌟" * self.stickers)
            return True  # new sticker achieved
        return False

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.configure(bg=BG)
        self.geometry("960x620")
        self.minsize(800, 560)
        self._style()
        self.correct_total = 0
        self.incorrect_total = 0

        # Header
        header = ttk.Frame(self, padding=12, style="Flat.TFrame")
        header.pack(fill="x")
        ttk.Label(header, text="🎮 Kleines Lernspiel", style="Title.TLabel").pack(side="left")

        self.sticker_bar = StickerBar(header, goal=5)
        self.sticker_bar.pack(side="right")

        # Navigation
        nav = ttk.Frame(self, padding=(12,6), style="Flat.TFrame")
        nav.pack(fill="x")
        ttk.Button(nav, text="Zahlen", style="Primary.TButton", command=self.show_numbers).pack(side="left", padx=(0,8))
        ttk.Button(nav, text="Buchstaben", style="Primary.TButton", command=self.show_letters).pack(side="left", padx=8)
        ttk.Button(nav, text="Logik", style="Primary.TButton", command=self.show_logic).pack(side="left", padx=8)
        ttk.Button(nav, text="🔀 Mix", command=self.random_game).pack(side="left", padx=(16,0))

        self.status = ttk.Label(self, text="Viel Spaß beim Lernen! 😊", style="Info.TLabel", anchor="center")
        self.status.pack(fill="x", padx=12)

        # Content Area (switching frames)
        self.container = ttk.Frame(self, padding=12, style="Flat.TFrame")
        self.container.pack(expand=True, fill="both")

        self.frames = {}
        for F in (NumbersPage, LettersPage, LogicPage):
            frame = F(self.container, self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.show_numbers()

        # Footer (score)
        footer = ttk.Frame(self, padding=12, style="Flat.TFrame")
        footer.pack(fill="x")
        self.score_lbl = ttk.Label(footer, text=self._score_text(), style="Info.TLabel")
        self.score_lbl.pack(side="left")

        ttk.Button(footer, text="Neues Spiel", command=self.reset).pack(side="right")

    def _style(self):
        style = ttk.Style(self)
        # Themed styles
        style.configure("Flat.TFrame", background=BG)
        style.configure("Card.TFrame", background=CARD, relief="flat")
        style.configure("Title.TLabel", background=BG, foreground=TEXT, font=("Segoe UI", 20, "bold"))
        style.configure("Big.TLabel", background=BG, foreground=TEXT, font=BIG_FONT)
        style.configure("Huge.TLabel", background=CARD, foreground=TEXT, font=("Segoe UI", 56, "bold"))
        style.configure("Info.TLabel", background=BG, foreground=TEXT, font=MID_FONT)
        style.configure("CardTitle.TLabel", background=CARD, foreground=TEXT, font=MID_FONT)
        style.configure("Result.TLabel", background=CARD, foreground=TEXT, font=("Segoe UI", 24, "bold"))
        style.configure("TLabel", background=CARD, foreground=TEXT, font=MID_FONT)
        style.configure("Primary.TButton", font=MID_BTN_FONT)
        style.configure("TButton", font=MID_BTN_FONT)
        style.map("Primary.TButton", background=[("active", PRIMARY)])

    def show_frame(self, name):
        frame = self.frames[name]
        frame.tkraise()
        frame.new_round()

    def show_numbers(self):
        self.show_frame("NumbersPage")
        self.status.configure(text="🔢 Zahlen: Zähle und wähle!")

    def show_letters(self):
        self.show_frame("LettersPage")
        self.status.configure(text="🔤 Buchstaben: Finde den richtigen Buchstaben!")

    def show_logic(self):
        self.show_frame("LogicPage")
        self.status.configure(text="🧠 Logik: Was passt?")

    def random_game(self):
        choice = random.choice(["NumbersPage", "LettersPage", "LogicPage"])
        self.show_frame(choice)
        if choice == "NumbersPage":
            self.status.configure(text="🔀 Mix → Zahlenrunde!")
        elif choice == "LettersPage":
            self.status.configure(text="🔀 Mix → Buchstabenrunde!")
        else:
            self.status.configure(text="🔀 Mix → Logikrunde!")

    def handle_result(self, is_correct, frame):
        if is_correct:
            self.correct_total += 1
            frame.flash(True)
            got_sticker = self.sticker_bar.add_point()
            if got_sticker:
                self.status.configure(text="🎉 Super! Du hast einen Sticker verdient! 🌟")
            else:
                self.status.configure(text=random.choice([
                    "Toll gemacht! 👍", "Super! 😊", "Prima! 💫", "Klasse! 👏"
                ]))
        else:
            self.incorrect_total += 1
            frame.flash(False)
            self.status.configure(text=random.choice([
                "Fast! Versuch's nochmal. 🙂", "Kein Problem – nochmal! 💪"
            ]))
        self.score_lbl.configure(text=self._score_text())

    def _score_text(self):
        return f"Richtig: {self.correct_total}   |   Versuche: {self.correct_total + self.incorrect_total}"

    def reset(self):
        self.correct_total = 0
        self.incorrect_total = 0
        self.sticker_bar.counter = 0
        self.sticker_bar.stickers = 0
        self.sticker_bar.progress['value'] = 0
        self.sticker_bar.sticker_lbl.configure(text="")
        self.score_lbl.configure(text=self._score_text())
        self.status.configure(text="Neues Spiel – viel Spaß! 😄")
        for frame in self.frames.values():
            frame.new_round()


class BasePage(ttk.Frame):
    def __init__(self, master, app: App):
        super().__init__(master, padding=16, style="Card.TFrame")
        self.app = app
        self.configure(borderwidth=0)
        self.card = ttk.Frame(self, padding=16, style="Card.TFrame")
        self.card.pack(expand=True, fill="both")

        self.title_lbl = ttk.Label(self.card, text="", style="CardTitle.TLabel")
        self.title_lbl.pack()

        self.canvas = tk.Canvas(self.card, bg="white", height=240, highlightthickness=0)
        self.canvas.pack(pady=8, fill="x")

        self.buttons_frame = ttk.Frame(self.card, padding=(0,8), style="Card.TFrame")
        self.buttons_frame.pack()

        self.feedback = ttk.Label(self.card, text="", style="Result.TLabel")
        self.feedback.pack(pady=4)

    def clear_buttons(self):
        for w in self.buttons_frame.winfo_children():
            w.destroy()

    def flash(self, good=True):
        """Kurzer Farbblick im Canvas zur Rückmeldung."""
        color = "#d1fae5" if good else "#fee2e2"
        orig = self.canvas["bg"]
        self.canvas.configure(bg=color)
        self.canvas.update_idletasks()
        self.after(180, lambda: self.canvas.configure(bg=orig))


class NumbersPage(BasePage):
    """Zeige 1–5 Emojis, Kind soll die Anzahl wählen."""
    def __init__(self, master, app: App):
        super().__init__(master, app)

    def new_round(self):
        self.title_lbl.configure(text="Zähle die Dinge und wähle die richtige Zahl!")
        self.feedback.configure(text="")
        self.clear_buttons()
        self.canvas.delete("all")

        count = random.randint(1, 5)
        emojis = random.sample(EMOJIS_FRUITS + EMOJIS_ANIMALS + EMOJIS_MISC, k=count)

        # Zeichne Emojis in einer Zeile
        x = 60
        for e in emojis:
            self.canvas.create_text(x, 120, text=e, font=("Segoe UI Emoji", 48))
            x += 120

        options = {count}
        while len(options) < 4:
            options.add(random.randint(1, 5))
        options = list(options)
        random.shuffle(options)

        for n in options:
            btn = ttk.Button(self.buttons_frame, text=str(n), command=lambda n=n: self.check(n), style="Primary.TButton")
            btn.pack(side="left", padx=8, pady=6)

        self.correct = count

    def check(self, val):
        if val == self.correct:
            self.feedback.configure(text="Richtig! 🎉", foreground=SUCCESS)
            self.app.handle_result(True, self)
            self.after(700, self.new_round)
        else:
            self.feedback.configure(text="Oh, versuch's nochmal! 🙂", foreground=WARN)
            self.app.handle_result(False, self)


class LettersPage(BasePage):
    """Zeige Zielbuchstabe, wähle aus 4 großen Buchstaben."""
    def __init__(self, master, app: App):
        super().__init__(master, app)
        self.alphabet = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

    def new_round(self):
        self.title_lbl.configure(text="Finde den richtigen Buchstaben!")
        self.feedback.configure(text="")
        self.clear_buttons()
        self.canvas.delete("all")

        target = random.choice(self.alphabet)
        self.canvas.create_text(480, 120, text=target, font=("Segoe UI", 120, "bold"), fill=PRIMARY)

        options = {target}
        while len(options) < 4:
            options.add(random.choice(self.alphabet))
        options = list(options)
        random.shuffle(options)

        for ch in options:
            btn = ttk.Button(self.buttons_frame, text=ch, command=lambda ch=ch: self.check(ch), style="Primary.TButton")
            btn.pack(side="left", padx=8, pady=6)

        self.correct = target

    def check(self, ch):
        if ch == self.correct:
            self.feedback.configure(text="Super! 🎈", foreground=SUCCESS)
            self.app.handle_result(True, self)
            self.after(700, self.new_round)
        else:
            self.feedback.configure(text="Nicht ganz, nochmal! 😊", foreground=WARN)
            self.app.handle_result(False, self)


class LogicPage(BasePage):
    """Zwei Logik-Modi: (A) Was passt nicht? (B) Form/ Farbe zuordnen."""
    def __init__(self, master, app: App):
        super().__init__(master, app)

    def new_round(self):
        self.feedback.configure(text="")
        self.clear_buttons()
        self.canvas.delete("all")

        mode = random.choice(["odd_one_out", "shape_match"])
        if mode == "odd_one_out":
            self.title_lbl.configure(text="Was passt nicht?")
            self.odd_one_out_round()
        else:
            self.title_lbl.configure(text="Welche Form passt?")
            self.shape_match_round()

    def odd_one_out_round(self):
        # 3 gleiche aus einer Gruppe + 1 Fremdes
        group = random.choice([EMOJIS_FRUITS, EMOJIS_ANIMALS, EMOJIS_MISC])
        other_groups = [g for g in [EMOJIS_FRUITS, EMOJIS_ANIMALS, EMOJIS_MISC] if g is not group]
        same = random.choice(group)
        odd = random.choice(random.choice(other_groups))

        items = [same, same, same, odd]
        random.shuffle(items)
        for i, e in enumerate(items):
            x = 240 * i + 120
            self.canvas.create_text(x, 120, text=e, font=("Segoe UI Emoji", 64))

        for i, e in enumerate(items):
            btn = ttk.Button(self.buttons_frame, text=f"{i+1}", command=lambda i=i, e=e: self.check_odd(e, same), style="Primary.TButton")
            btn.pack(side="left", padx=8, pady=6)

    def check_odd(self, chosen, expected_same):
        if chosen != expected_same:
            self.feedback.configure(text="Richtig! Das ist anders. 🎉", foreground=SUCCESS)
            self.app.handle_result(True, self)
            self.after(700, self.new_round)
        else:
            self.feedback.configure(text="Nicht ganz – such das andere Symbol! 🙂", foreground=WARN)
            self.app.handle_result(False, self)

    def shape_match_round(self):
        # Ziel-Form zeichnen (Kreis, Quadrat, Dreieck) und Buttons mit Namen
        self.canvas.delete("all")
        shape = random.choice(["Kreis", "Quadrat", "Dreieck"])
        # random color (pastel-ish)
        color = random.choice(["#60a5fa", "#f472b6", "#34d399", "#fbbf24", "#a78bfa"])

        # Draw reference shape centered
        if shape == "Kreis":
            self.canvas.create_oval(360, 60, 600, 300, fill=color, width=0)
        elif shape == "Quadrat":
            self.canvas.create_rectangle(360, 60, 600, 300, fill=color, width=0)
        else:  # Dreieck
            self.canvas.create_polygon(480, 60, 360, 300, 600, 300, fill=color, width=0)

        opts = ["Kreis", "Quadrat", "Dreieck"]
        random.shuffle(opts)
        for name in opts:
            btn = ttk.Button(self.buttons_frame, text=name, command=lambda name=name, shape=shape: self.check_shape(name, shape), style="Primary.TButton")
            btn.pack(side="left", padx=8, pady=6)

        self.correct = shape

    def check_shape(self, name, shape):
        if name == shape:
            self.feedback.configure(text="Genau richtig! 💡", foreground=SUCCESS)
            self.app.handle_result(True, self)
            self.after(700, self.new_round)
        else:
            self.feedback.configure(text="Schau genau hin – nochmal! 👀", foreground=WARN)
            self.app.handle_result(False, self)


if __name__ == "__main__":
    app = App()
    app.mainloop()
