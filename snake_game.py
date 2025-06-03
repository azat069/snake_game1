import sys
import random
import mysql.connector
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QLabel,
    QStackedWidget, QComboBox, QLineEdit, QMessageBox, QFormLayout,
    QHBoxLayout, QGridLayout, QListWidget
)
from PyQt5.QtCore import Qt, QTimer, QUrl
from PyQt5.QtGui import QPainter, QColor, QPixmap
from PyQt5.QtMultimedia import QSoundEffect

CELL_SIZE = 40
GRID_WIDTH = 20
GRID_HEIGHT = 20

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="snake_game_db"
    )

button_style = """
    QPushButton {
        font-size: 24px;
        height: 60px;
        min-width: 240px;
        background-color: #2ecc71;
        color: white;
        border-radius: 10px;
    }
    QPushButton:hover {
        background-color: #27ae60;
    }
"""

lineedit_style = """
    QLineEdit {
        font-size: 20px;
        min-height: 40px;
        max-width: 220px;
        padding: 8px;
        border: 2px solid #ccc;
        border-radius: 8px;
    }
"""

fancy_label_style = """
    font-size: 26px;
    font-weight: bold;
    color: #f39c12;
    background-color: #2c3e50;
    padding: 12px;
    border-radius: 12px;
    border: 2px solid #f1c40f;
"""

score_display_style = """
    font-size: 24px;
    color: white;
    background-color: #34495e;
    border-radius: 10px;
    padding: 10px 20px;
"""

class LoginScreen(QWidget):
    def __init__(self, on_login_success):
        super().__init__()
        self.on_login_success = on_login_success
        self.setFixedSize(GRID_WIDTH * CELL_SIZE, GRID_HEIGHT * CELL_SIZE)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        title = QLabel("🔐 Вход в игру")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 32px; font-weight: bold;")
        layout.addWidget(title, alignment=Qt.AlignHCenter)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)
        form.setFormAlignment(Qt.AlignHCenter)

        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.username_input.setStyleSheet(lineedit_style)
        self.password_input.setStyleSheet(lineedit_style)

        form.addRow("Логин:", self.username_input)
        form.addRow("Пароль:", self.password_input)
        layout.addLayout(form)

        self.login_btn = QPushButton("Войти")
        self.register_btn = QPushButton("Регистрация")
        self.login_btn.setStyleSheet(button_style)
        self.register_btn.setStyleSheet(button_style)

        self.login_btn.clicked.connect(self.login)
        self.register_btn.clicked.connect(self.goto_register)
        layout.addWidget(self.login_btn, alignment=Qt.AlignCenter)
        layout.addWidget(self.register_btn, alignment=Qt.AlignCenter)

        self.setLayout(layout)

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username=%s AND password=%s", (username, password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        if user:
            self.on_login_success(user[0], username)
        else:
            QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль!")

    def goto_register(self):
        self.parent().setCurrentIndex(1)
class RegisterScreen(QWidget):
    def __init__(self, back_to_login):
        super().__init__()
        self.back_to_login = back_to_login
        self.setFixedSize(GRID_WIDTH * CELL_SIZE, GRID_HEIGHT * CELL_SIZE)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        title = QLabel("📝 Регистрация")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 32px; font-weight: bold;")
        layout.addWidget(title)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)
        form.setFormAlignment(Qt.AlignHCenter)

        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.confirm_input = QLineEdit()

        self.password_input.setEchoMode(QLineEdit.Password)
        self.confirm_input.setEchoMode(QLineEdit.Password)

        self.username_input.setStyleSheet(lineedit_style)
        self.password_input.setStyleSheet(lineedit_style)
        self.confirm_input.setStyleSheet(lineedit_style)

        form.addRow("Логин:", self.username_input)
        form.addRow("Пароль:", self.password_input)
        form.addRow("Повторите пароль:", self.confirm_input)

        layout.addLayout(form)


        self.register_btn = QPushButton("Создать аккаунт")
        self.register_btn.setStyleSheet(button_style)
        self.register_btn.clicked.connect(self.register)
        layout.addWidget(self.register_btn)


        self.back_btn = QPushButton("← Назад")
        self.back_btn.setStyleSheet(button_style)
        self.back_btn.clicked.connect(self.back_to_login)
        layout.addWidget(self.back_btn)

        self.setLayout(layout)

    def register(self):
        username = self.username_input.text()
        password = self.password_input.text()
        confirm = self.confirm_input.text()
        if password != confirm:
            QMessageBox.warning(self, "Ошибка", "Пароли не совпадают!")
            return
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
            conn.commit()
            cursor.close()
            conn.close()
            QMessageBox.information(self, "Успех", "Регистрация успешна!")
            self.back_to_login()
        except mysql.connector.IntegrityError:
            QMessageBox.warning(self, "Ошибка", "Такой логин уже существует!")



class StartScreen(QWidget):
    def __init__(self, start_callback, logout_callback):
        super().__init__()
        self.setFixedSize(GRID_WIDTH * CELL_SIZE, GRID_HEIGHT * CELL_SIZE)

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        self.layout.setSpacing(15)

        self.high_score_label = QLabel("🏆 Рекорд: 0")
        self.high_score_label.setAlignment(Qt.AlignCenter)
        self.high_score_label.setStyleSheet(fancy_label_style)
        self.layout.addWidget(self.high_score_label)

        title = QLabel("🐍 Змейка")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 48px; font-weight: bold; color: #27ae60;")
        self.layout.addWidget(title)

        self.layout.addStretch(1)

        self.start_button = QPushButton("🚀 Начать игру")
        self.start_button.setStyleSheet(button_style)
        self.start_button.clicked.connect(lambda: start_callback(self.selected_skin()))
        self.layout.addWidget(self.start_button, alignment=Qt.AlignCenter)

        self.layout.addStretch(1)

        self.layout.addStretch()

        # нижняя панель
        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(30, 10, 30, 20)

        # селектор скинов
        skin_layout = QVBoxLayout()
        skin_label = QLabel("🎨 Скин змейки")
        skin_label.setStyleSheet("font-size: 18px;")
        skin_label.setAlignment(Qt.AlignLeft)
        self.skin_selector = QComboBox()
        self.skin_selector.addItem("Классика", "classic")
        self.skin_selector.addItem("Красный", "red")
        self.skin_selector.addItem("Радужный", "rainbow")
        self.skin_selector.setFixedHeight(40)
        self.skin_selector.setFixedWidth(220)
        self.skin_selector.setStyleSheet("font-size: 18px; padding: 4px;")

        skin_layout.addWidget(skin_label)
        skin_layout.addWidget(self.skin_selector)
        skin_layout.addStretch()

        bottom_layout.addLayout(skin_layout)

        # топ игроков
        top_layout = QVBoxLayout()
        top_label = QLabel("🏅 Топ игроки")
        top_label.setAlignment(Qt.AlignRight)
        top_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.top_players_list = QListWidget()
        self.top_players_list.setFixedWidth(250)
        self.top_players_list.setStyleSheet("font-size: 16px; background-color: #ecf0f1; border-radius: 8px; padding: 5px;")
        top_layout.addWidget(top_label)
        top_layout.addWidget(self.top_players_list)
        top_layout.addStretch()

        bottom_layout.addStretch()
        bottom_layout.addLayout(top_layout)

        self.layout.addLayout(bottom_layout)

        # Кнопка выхода
        self.logout_button = QPushButton("🚪 Выйти из аккаунта")
        self.logout_button.setStyleSheet(button_style)
        self.layout.addWidget(self.logout_button, alignment=Qt.AlignCenter)
        self.logout_button.clicked.connect(logout_callback)

        self.setLayout(self.layout)

    def selected_skin(self):
        return self.skin_selector.currentData()

    def update_top_players(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.username, MAX(h.score) 
            FROM high_scores h 
            JOIN users u ON u.id = h.user_id 
            GROUP BY h.user_id 
            ORDER BY MAX(h.score) DESC 
            LIMIT 5
        """)
        results = cursor.fetchall()
        cursor.close()
        conn.close()

        self.top_players_list.clear()
        for name, score in results:
            self.top_players_list.addItem(f"{name} — {score}")


class GameOverScreen(QWidget):
    def __init__(self, restart_callback, menu_callback):
        super().__init__()
        self.setFixedSize(GRID_WIDTH * CELL_SIZE, GRID_HEIGHT * CELL_SIZE)
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        label = QLabel("💀 Вы проиграли!")
        label.setStyleSheet("font-size: 42px; font-weight: bold; color: #e74c3c;")
        layout.addWidget(label)

        self.record_label = QLabel("")
        self.record_label.setStyleSheet("font-size: 26px; color: #f1c40f; font-weight: bold;")
        layout.addWidget(self.record_label)

        self.final_score_label = QLabel("")
        self.final_score_label.setStyleSheet("font-size: 24px; color: white; background-color: #2c3e50; padding: 10px; border-radius: 10px;")
        layout.addWidget(self.final_score_label)

        self.restart_button = QPushButton("🔁 Заново")
        self.menu_button = QPushButton("🏠 В меню")
        self.restart_button.setStyleSheet(button_style)
        self.menu_button.setStyleSheet(button_style)
        self.restart_button.clicked.connect(restart_callback)
        self.menu_button.clicked.connect(menu_callback)
        layout.addWidget(self.restart_button)
        layout.addWidget(self.menu_button)

        self.setLayout(layout)

    def set_record_broken(self, is_broken):
        self.record_label.setText("🎉 Новый рекорд! 🎉" if is_broken else "")

    def set_final_score_info(self, username, score, high_score):
        self.final_score_label.setText(f"Игрок: {username} | Очки: {score} | Рекорд: {high_score}")
class PauseScreen(QWidget):
    def __init__(self, resume_callback, stop_callback):
        super().__init__()
        self.setFixedSize(GRID_WIDTH * CELL_SIZE, GRID_HEIGHT * CELL_SIZE)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        label = QLabel("⏸ Игра на паузе")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size: 36px; font-weight: bold; color: #f39c12;")
        layout.addWidget(label)

        self.resume_button = QPushButton("▶ Продолжить")
        self.resume_button.setStyleSheet(button_style)
        self.resume_button.clicked.connect(resume_callback)
        layout.addWidget(self.resume_button)

        self.quit_button = QPushButton("🛑 Остановить игру")
        self.quit_button.setStyleSheet(button_style)
        self.quit_button.clicked.connect(stop_callback)
        layout.addWidget(self.quit_button)

        self.setLayout(layout)
class SnakeGame(QWidget):
    def __init__(self, game_over_callback, skin, update_score_callback, pause_callback, parent=None):
        super().__init__(parent)
        self.setFixedSize(GRID_WIDTH * CELL_SIZE, GRID_HEIGHT * CELL_SIZE)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_game)
        self.snake = [(5, 5), (4, 5), (3, 5)]
        self.direction = (1, 0)
        self.food = self.place_food()
        self.golden_apple = None
        self.game_over_callback = game_over_callback
        self.update_score_callback = update_score_callback
        self.pause_callback = pause_callback
        self.score = 0
        self.skin = skin
        self.update_score_callback(0)
        self.timer.start(100)
        self.setFocusPolicy(Qt.StrongFocus)
        self.game_over = False

        self.eat_sound = QSoundEffect()
        self.eat_sound.setSource(QUrl.fromLocalFile("sounds/eat.wav"))
        self.eat_sound.setVolume(0.9)

        self.game_over_sound = QSoundEffect()
        self.game_over_sound.setSource(QUrl.fromLocalFile("sounds/game_over.wav"))
        self.game_over_sound.setVolume(0.9)

        self.food_img = QPixmap("images/food.png")
        self.head_img = QPixmap("images/head.png")
        self.golden_img = QPixmap("images/golden_apple.png")

    def place_food(self):
        while True:
            pos = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
            if pos not in self.snake:
                return pos

    def maybe_spawn_golden_apple(self):
        if self.golden_apple is None and random.random() < 0.1:
            while True:
                pos = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
                if pos not in self.snake and pos != self.food:
                    self.golden_apple = pos
                    break

    def keyPressEvent(self, event):
        if self.game_over:
            return

        key = event.key()
        if key == Qt.Key_Escape:
            self.timer.stop()
            self.pause_callback()
            return

        if key == Qt.Key_Up and self.direction != (0, 1):
            self.direction = (0, -1)
        elif key == Qt.Key_Down and self.direction != (0, -1):
            self.direction = (0, 1)
        elif key == Qt.Key_Left and self.direction != (1, 0):
            self.direction = (-1, 0)
        elif key == Qt.Key_Right and self.direction != (-1, 0):
            self.direction = (1, 0)

    def update_game(self):
        if self.game_over:
            return

        head = self.snake[0]
        new_head = ((head[0] + self.direction[0]) % GRID_WIDTH, (head[1] + self.direction[1]) % GRID_HEIGHT)
        if new_head in self.snake:
            self.timer.stop()
            self.game_over = True
            self.game_over_sound.play()
            self.game_over_callback(self.score)
            return

        self.snake.insert(0, new_head)
        if new_head == self.food:
            self.food = self.place_food()
            self.maybe_spawn_golden_apple()
            self.score += 1
            self.update_score_callback(self.score)
            self.eat_sound.play()
        elif self.golden_apple and new_head == self.golden_apple:
            self.golden_apple = None
            self.score += 2
            self.update_score_callback(self.score)
            self.eat_sound.play()
        else:
            self.snake.pop()
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)

        # Шахматный фон
        light_green = QColor("#a8d5a2")
        dark_green = QColor("#91c788")
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                color = light_green if (x + y) % 2 == 0 else dark_green
                painter.fillRect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE, color)

        if self.food:
            painter.drawPixmap(self.food[0]*CELL_SIZE, self.food[1]*CELL_SIZE, CELL_SIZE, CELL_SIZE, self.food_img)

        if self.golden_apple:
            painter.drawPixmap(self.golden_apple[0]*CELL_SIZE, self.golden_apple[1]*CELL_SIZE, CELL_SIZE, CELL_SIZE, self.golden_img)

        for i, (x, y) in enumerate(self.snake):
            if i == 0:
                painter.drawPixmap(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE, self.head_img)
            else:
                if self.skin == "red":
                    painter.setBrush(QColor("#e74c3c"))
                elif self.skin == "rainbow":
                    painter.setBrush(QColor(random.randint(0,255), random.randint(0,255), random.randint(0,255)))
                else:
                    painter.setBrush(QColor("#006400"))
                painter.drawRect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Змейка")
        self.user_id = None
        self.username = None
        self.stack = QStackedWidget()

        self.login_screen = LoginScreen(self.login_success)
        self.register_screen = RegisterScreen(lambda: self.stack.setCurrentIndex(0))
        self.start_screen = StartScreen(self.start_game, self.logout)
        self.game_over_screen = GameOverScreen(self.restart_game, self.back_to_menu)
        self.pause_screen = PauseScreen(self.resume_game, self.force_game_over)

        self.stack.addWidget(self.login_screen)      # 0
        self.stack.addWidget(self.register_screen)   # 1
        self.stack.addWidget(self.start_screen)      # 2
        self.stack.addWidget(QWidget())              # 3 — SnakeGame
        self.stack.addWidget(self.game_over_screen)  # 4
        self.stack.addWidget(self.pause_screen)      # 5

        self.score_label = QLabel("")
        self.score_label.setAlignment(Qt.AlignCenter)
        self.score_label.setStyleSheet("font-size: 28px;")

        layout = QVBoxLayout()
        layout.addWidget(self.score_label)
        layout.addWidget(self.stack)
        self.setLayout(layout)
        self.show_score(False)
        self.stack.setCurrentIndex(0)

    def show_score(self, visible):
        self.score_label.setVisible(visible)

    def update_score(self, score):
        high = self.get_user_high_score()
        self.score_label.setText(
            f"<span style='font-size:24px; color:white;'>👤 <b>{self.username}</b> | "
            f"🎯 Очки: <b>{score}</b> | 🏆 Рекорд: <b>{high}</b></span>"
        )
        self.score_label.setStyleSheet("background-color: #34495e; padding: 10px; border-radius: 10px;")

    def get_user_high_score(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(score) FROM high_scores WHERE user_id=%s", (self.user_id,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result[0] if result and result[0] else 0

    def update_user_score(self, score):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO high_scores (user_id, score) VALUES (%s, %s)", (self.user_id, score))
        conn.commit()
        cursor.close()
        conn.close()

    def login_success(self, user_id, username):
        self.user_id = user_id
        self.username = username
        self.stack.setCurrentIndex(2)
        self.start_screen.high_score_label.setText(f"🏆 Рекорд: {self.get_user_high_score()}")
        self.start_screen.update_top_players()

    def start_game(self, skin):
        self.skin = skin
        old_game = self.stack.widget(3)
        if old_game:
            old_game.deleteLater()

        self.game = SnakeGame(
            game_over_callback=self.show_game_over,
            skin=skin,
            update_score_callback=self.update_score,
            pause_callback=self.pause_game,
            parent=self
        )
        self.stack.removeWidget(old_game)
        self.stack.insertWidget(3, self.game)
        self.stack.setCurrentIndex(3)
        self.show_score(True)

    def restart_game(self):
        self.start_game(self.skin)

    def back_to_menu(self):
        self.stack.setCurrentIndex(2)
        self.show_score(False)
        self.start_screen.update_top_players()

    def logout(self):
        self.user_id = None
        self.username = None
        self.show_score(False)
        self.stack.setCurrentIndex(0)

    def show_game_over(self, score):
        is_new_record = score > self.get_user_high_score()
        if is_new_record:
            self.update_user_score(score)
        self.update_score(score)
        self.game_over_screen.set_record_broken(is_new_record)
        self.game_over_screen.set_final_score_info(self.username, score, self.get_user_high_score())
        self.stack.setCurrentIndex(4)
        self.show_score(True)

    def pause_game(self):
        self.stack.setCurrentIndex(5)
        self.show_score(False)

    def resume_game(self):
        self.stack.setCurrentIndex(3)
        self.game.timer.start()
        self.show_score(True)

    def force_game_over(self):
        self.show_game_over(self.game.score)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
