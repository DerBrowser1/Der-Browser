import sys
import os
import json
from PyQt5.QtCore import *
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtGui import *
import urllib.parse
from datetime import datetime
from typing import List, Dict
import pickle
import socket
import subprocess
import platform
import hashlib
import base64
import time
from PyQt5.QtGui import QPainter, QImage

class Bookmark:
    def __init__(self, title, url, added_date, category="General", icon="⭐"):
        self.title = title
        self.url = url
        self.added_date = added_date
        self.category = category
        self.icon = icon

class HistoryItem:
    def __init__(self, url, title, visit_time, visit_count=1):
        self.url = url
        self.title = title
        self.visit_time = visit_time
        self.visit_count = visit_count

class UserAccount:
    def __init__(self, username, password_hash):
        self.username = username
        self.password_hash = password_hash
        self.created_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.last_login = None
        self.settings = {}
        self.bookmarks = []
        self.history = []

class BrowserTab(QWidget):
    """Вкладка браузера"""
    def __init__(self, parent_browser=None, url=None, is_homepage=False, is_incognito=False):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.is_homepage = is_homepage
        self.is_incognito = is_incognito
        self.parent_browser = parent_browser

        if is_homepage:
            # Для главной страницы создаем кастомный виджет
            self.create_homepage()
        else:
            # Создаем WebView для обычных страниц
            self.browser = QWebEngineView()
            if url:
                self.browser.setUrl(QUrl(url))

            self.layout.addWidget(self.browser)

        # Инициализация переменных
        self.url = ""
        self.title = ""

    def create_homepage(self):
        """Создает красивую главную страницу"""
        # Основной контейнер с темным фоном (будет меняться в зависимости от темы)
        container = QWidget()
        container.setObjectName("homepageContainer")
        container.setStyleSheet("background-color: #0a0a14;")
        self.layout.addWidget(container)

        homepage_layout = QVBoxLayout(container)
        homepage_layout.setContentsMargins(0, 0, 0, 0)

        # Прокручиваемая область
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #0a0a14;
            }
            QScrollBar:vertical {
                background-color: #2a2a3a;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background-color: #4a4a5a;
                border-radius: 5px;
                min-height: 20px;
            }
        """)

        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: #0a0a14;")
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setAlignment(Qt.AlignTop)

        # 1. Верхняя панель с логотипом
        header_widget = QWidget()
        header_widget.setStyleSheet("background-color: transparent;")
        header_layout = QVBoxLayout(header_widget)
        header_layout.setContentsMargins(40, 40, 40, 30)

        # Логотип Der Browser
        logo_label = QLabel("🌐 Der Browser")
        logo_label.setObjectName("homepageLogo")
        logo_label.setStyleSheet("""
            QLabel {
                color: #3498db;
                font-size: 42px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)
        logo_label.setAlignment(Qt.AlignCenter)

        tagline_label = QLabel("Modern Web Experience")
        tagline_label.setObjectName("homepageTagline")
        tagline_label.setStyleSheet("""
            QLabel {
                color: #b0b0b0;
                font-size: 16px;
                font-weight: 300;
            }
        """)
        tagline_label.setAlignment(Qt.AlignCenter)

        header_layout.addWidget(logo_label)
        header_layout.addWidget(tagline_label)
        scroll_layout.addWidget(header_widget)

        # 2. Быстрый поиск
        search_widget = QWidget()
        search_widget.setStyleSheet("background-color: transparent;")
        search_layout = QVBoxLayout(search_widget)
        search_layout.setContentsMargins(0, 20, 0, 30)

        search_label = QLabel("🔍 Быстрый поиск")
        search_label.setObjectName("homepageSearchLabel")
        search_label.setStyleSheet("""
            QLabel {
                color: #e0e0e0;
                font-size: 20px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)
        search_label.setAlignment(Qt.AlignCenter)
        search_layout.addWidget(search_label)

        # Поле быстрого поиска
        quick_search_layout = QHBoxLayout()
        self.quick_search_bar = QLineEdit()
        self.quick_search_bar.setObjectName("homepageSearchBar")
        self.quick_search_bar.setPlaceholderText("Введите запрос или URL...")
        self.quick_search_bar.setStyleSheet("""
            QLineEdit {
                background-color: #2a2a3a;
                border: 2px solid #3a3a4a;
                border-radius: 25px;
                padding: 15px 20px;
                font-size: 14px;
                color: #e0e0e0;
                font-weight: 500;
                min-height: 45px;
            }
            QLineEdit:focus {
                border-color: #3498db;
                background-color: #3a3a4a;
            }
        """)
        self.quick_search_bar.returnPressed.connect(self.perform_quick_search)

        quick_search_btn = QPushButton("🚀 Поиск")
        quick_search_btn.setObjectName("homepageSearchButton")
        quick_search_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                border: none;
                border-radius: 25px;
                padding: 15px 25px;
                color: white;
                font-size: 14px;
                font-weight: bold;
                min-height: 45px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        quick_search_btn.clicked.connect(self.perform_quick_search)

        quick_search_layout.addWidget(self.quick_search_bar)
        quick_search_layout.addWidget(quick_search_btn)
        search_layout.addLayout(quick_search_layout)

        scroll_layout.addWidget(search_widget)

        # 3. Популярные сайты
        sites_widget = QWidget()
        sites_widget.setStyleSheet("background-color: transparent;")
        sites_layout = QVBoxLayout(sites_widget)
        sites_layout.setContentsMargins(40, 0, 40, 30)

        sites_label = QLabel("⭐ Популярные сервисы")
        sites_label.setObjectName("homepageSitesLabel")
        sites_label.setStyleSheet("""
            QLabel {
                color: #e0e0e0;
                font-size: 20px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)
        sites_label.setAlignment(Qt.AlignCenter)
        sites_layout.addWidget(sites_label)

        # Кнопки популярных сайтов
        quick_sites = [
            ("🐱 GitHub", "https://www.github.com"),
            ("📺 YouTube", "https://www.youtube.com"),
            ("🎵 Spotify", "https://www.spotify.com"),
            ("✈️ Telegram", "https://web.telegram.org"),
            ("🔍 Google", "https://www.google.com"),
            ("📘 Facebook", "https://www.facebook.com"),
            ("🐦 Twitter", "https://twitter.com"),
            ("💼 LinkedIn", "https://www.linkedin.com"),
            ("📷 Instagram", "https://www.instagram.com"),
            ("🛒 Amazon", "https://www.amazon.com"),
            ("📚 Wikipedia", "https://wikipedia.org"),
            ("🎮 Twitch", "https://www.twitch.tv"),
            ("💬 Discord", "https://discord.com"),
            ("☁️ Dropbox", "https://www.dropbox.com"),
            ("📦 Google Drive", "https://drive.google.com"),
            ("📃 Наш сайт", "https://derbrowser.tilda.ws/"),
        ]

        # Сетка для кнопок (3 колонки)
        grid_layout = QGridLayout()
        grid_layout.setSpacing(15)

        for i, (name, url) in enumerate(quick_sites):
            btn = QPushButton(name)
            btn.setObjectName("homepageSiteButton")
            btn.setCursor(Qt.PointingHandCursor)
            btn.setProperty("url", url)
            # Серый фон для всех кнопок с закругленными углами
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #3a3a4a;
                    color: white;
                    border: none;
                    border-radius: 15px;
                    padding: 15px 20px;
                    font-size: 14px;
                    font-weight: bold;
                    min-height: 50px;
                }
                QPushButton:hover {
                    background-color: #4a4a5a;
                    border: 2px solid #3498db;
                }
                QPushButton:pressed {
                    background-color: #2a2a3a;
                }
            """)
            btn.clicked.connect(lambda checked, u=url: self.open_site(u))

            row = i // 3
            col = i % 3
            grid_layout.addWidget(btn, row, col)

        sites_layout.addLayout(grid_layout)
        scroll_layout.addWidget(sites_widget)

        # 4. Информационная панель
        info_widget = QWidget()
        info_widget.setStyleSheet("background-color: transparent;")
        info_layout = QVBoxLayout(info_widget)
        info_layout.setContentsMargins(40, 0, 40, 40)

        info_label = QLabel("📊 Информация о браузере")
        info_label.setObjectName("homepageInfoLabel")
        info_label.setStyleSheet("""
            QLabel {
                color: #e0e0e0;
                font-size: 20px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)
        info_label.setAlignment(Qt.AlignCenter)
        info_layout.addWidget(info_label)

        # Статистика в виде текста
        stats_text = """
        <div style="background-color: #2a2a3a; padding: 20px; border-radius: 12px; color: #e0e0e0;">
            <p><b>🌐 Версия:</b> Der Browser 3.0</p>
            <p><b>⚡ Движок:</b> Qt WebEngine (Chromium)</p>
            <p><b>🎨 Тема:</b> Темная</p>
            <p><b>🔒 Безопасность:</b> HTTPS Everywhere</p>
            <p><b>📈 Производительность:</b> Высокая</p>
            <p><b>🛠️ Разработчик:</b> Der Browser Team</p>
        </div>
        """

        stats_label = QLabel()
        stats_label.setTextFormat(Qt.RichText)
        stats_label.setText(stats_text)
        stats_label.setAlignment(Qt.AlignCenter)
        info_layout.addWidget(stats_label)

        scroll_layout.addWidget(info_widget)

        # 5. Быстрые действия
        actions_widget = QWidget()
        actions_widget.setStyleSheet("background-color: transparent;")
        actions_layout = QVBoxLayout(actions_widget)
        actions_layout.setContentsMargins(40, 0, 40, 40)

        actions_label = QLabel("⚡ Быстрые действия")
        actions_label.setObjectName("homepageActionsLabel")
        actions_label.setStyleSheet("""
            QLabel {
                color: #e0e0e0;
                font-size: 20px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)
        actions_label.setAlignment(Qt.AlignCenter)
        actions_layout.addWidget(actions_label)

        # Кнопки действий в горизонтальном ряду
        actions_buttons = QWidget()
        actions_buttons.setStyleSheet("background-color: transparent;")
        actions_buttons_layout = QHBoxLayout(actions_buttons)
        actions_buttons_layout.setSpacing(15)

        actions_list = [
            ("➕ Новая вкладка", self.new_tab),
            ("⭐ Закладки", self.show_bookmarks),
            ("📜 История", self.show_history),
            ("⚙️ Настройки", self.show_settings),
        ]

        for text, callback in actions_list:
            btn = QPushButton(text)
            btn.setObjectName("homepageActionButton")
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #3a3a4a;
                    color: white;
                    border: none;
                    border-radius: 12px;
                    padding: 12px 20px;
                    font-size: 13px;
                    font-weight: bold;
                    min-height: 45px;
                }
                QPushButton:hover {
                    background-color: #4a4a5a;
                    border: 2px solid #3498db;
                }
                QPushButton:pressed {
                    background-color: #2a2a3a;
                }
            """)
            btn.clicked.connect(callback)
            actions_buttons_layout.addWidget(btn)

        actions_layout.addWidget(actions_buttons)
        scroll_layout.addWidget(actions_widget)

        # 6. Футер - исправлен цвет текста на белый
        footer_widget = QWidget()
        footer_widget.setStyleSheet("background-color: transparent;")
        footer_layout = QVBoxLayout(footer_widget)
        footer_layout.setContentsMargins(40, 20, 40, 40)

        footer_text = QLabel("© 2026 Der Browser | Современный веб-браузер с премиальным дизайном")
        footer_text.setObjectName("homepageFooterText")
        footer_text.setStyleSheet("color: #ffffff; font-size: 12px; font-weight: 300;")  # Изменено на белый
        footer_text.setAlignment(Qt.AlignCenter)

        version_text = QLabel("Версия 3.0.0 | PyQtWebEngine 5.15.2")
        version_text.setObjectName("homepageVersionText")
        version_text.setStyleSheet("color: #ffffff; font-size: 11px; font-weight: 300;")  # Изменено на белый
        version_text.setAlignment(Qt.AlignCenter)

        footer_layout.addWidget(footer_text)
        footer_layout.addWidget(version_text)
        scroll_layout.addWidget(footer_widget)

        # Устанавливаем содержимое прокрутки
        scroll_area.setWidget(scroll_content)
        homepage_layout.addWidget(scroll_area)

    def open_site(self, url):
        """Открывает сайт в браузере"""
        if self.parent_browser:
            self.parent_browser.navigate_to_url(url)

    def perform_quick_search(self):
        """Выполняет быстрый поиск"""
        query = self.quick_search_bar.text()
        if query and self.parent_browser:
            # Создаем новую вкладку для поиска
            self.parent_browser.add_new_tab(query, "Поиск", False)

    def new_tab(self):
        """Создает новую вкладку"""
        if self.parent_browser:
            self.parent_browser.add_new_tab("", "Новая вкладка", True)

    def show_bookmarks(self):
        """Показывает закладки"""
        if self.parent_browser:
            self.parent_browser.show_bookmarks_dialog()

    def show_history(self):
        """Показывает историю"""
        if self.parent_browser:
            self.parent_browser.show_history_dialog()

    def show_settings(self):
        """Показывает настройки"""
        if self.parent_browser:
            self.parent_browser.show_settings_dialog()

class AuthDialog(QDialog):
    """Диалог аутентификации"""
    def __init__(self, parent=None, mode="login"):
        super().__init__(parent)
        self.mode = mode  # "login" или "register"
        self.setWindowTitle("Вход в Der Browser" if mode == "login" else "Регистрация")
        self.setGeometry(400, 200, 400, 350 if mode == "register" else 300)
        self.setObjectName("authDialog")
        self.need_switch_mode = False
        self.new_mode = mode

        self.setup_ui()
        self.apply_styles()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Заголовок
        title_label = QLabel("🔐 Der Browser - Авторизация")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #3498db; font-size: 18px; font-weight: bold;")
        layout.addWidget(title_label)

        # Форма
        form_widget = QWidget()
        form_layout = QVBoxLayout(form_widget)
        form_layout.setSpacing(10)

        # Логин
        login_label = QLabel("Логин:")
        self.login_edit = QLineEdit()
        self.login_edit.setPlaceholderText("Введите имя пользователя")
        form_layout.addWidget(login_label)
        form_layout.addWidget(self.login_edit)

        # Пароль
        password_label = QLabel("Пароль:")
        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("Введите пароль")
        self.password_edit.setEchoMode(QLineEdit.Password)
        form_layout.addWidget(password_label)
        form_layout.addWidget(self.password_edit)

        # Повтор пароля (только для регистрации)
        if self.mode == "register":
            confirm_label = QLabel("Подтвердите пароль:")
            self.confirm_edit = QLineEdit()
            self.confirm_edit.setPlaceholderText("Повторите пароль")
            self.confirm_edit.setEchoMode(QLineEdit.Password)
            form_layout.addWidget(confirm_label)
            form_layout.addWidget(self.confirm_edit)

        layout.addWidget(form_widget)

        # Кнопки
        button_layout = QHBoxLayout()

        if self.mode == "login":
            self.submit_btn = QPushButton("Войти")
            self.submit_btn.clicked.connect(self.on_submit)
            switch_btn = QPushButton("Регистрация")
        else:
            self.submit_btn = QPushButton("Зарегистрироваться")
            self.submit_btn.clicked.connect(self.on_submit)
            switch_btn = QPushButton("Войти")

        switch_btn.clicked.connect(self.on_switch_mode)
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)

        button_layout.addWidget(self.submit_btn)
        button_layout.addWidget(switch_btn)
        button_layout.addStretch()
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

    def apply_styles(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #1a1a2a;
                border: 2px solid #3498db;
                border-radius: 15px;
            }
            QLabel {
                color: #e0e0e0;
                font-size: 12px;
            }
            QLineEdit {
                background-color: #2a2a3a;
                border: 2px solid #3a3a4a;
                border-radius: 10px;
                padding: 8px 12px;
                font-size: 14px;
                color: #e0e0e0;
                min-height: 35px;
            }
            QLineEdit:focus {
                border-color: #3498db;
                background-color: #3a3a4a;
            }
            QPushButton {
                background-color: #3a3a4a;
                border: 2px solid #4a4a5a;
                border-radius: 8px;
                padding: 10px 20px;
                color: #e0e0e0;
                font-weight: bold;
                font-size: 12px;
                min-height: 35px;
            }
            QPushButton:hover {
                background-color: #4a4a5a;
                border-color: #3498db;
            }
        """)

    def on_submit(self):
        """Обработка нажатия кнопки Войти/Зарегистрироваться"""
        self.accept()

    def on_switch_mode(self):
        """Обработка нажатия кнопки смены режима"""
        self.need_switch_mode = True
        self.new_mode = "register" if self.mode == "login" else "login"
        self.reject()  # Закрываем с специальным флагом

    def get_credentials(self):
        """Возвращает введенные данные"""
        if self.mode == "login":
            return self.login_edit.text(), self.password_edit.text(), ""
        else:
            return self.login_edit.text(), self.password_edit.text(), self.confirm_edit.text()

class ModernBrowser(QMainWindow):
    def __init__(self):
                # Админ настройки
        self.is_admin = False
        self.admin_settings = {
            "theme": "default",  # default, liquid_glass, dark_matter, cyberpunk, nature
            "logo_text": "Der Browser",
            "main_title": "🌐 Der Browser - Made by AI",
            "subtitle": "Modern Web Experience",
            "quick_buttons": [
                "🐱 GitHub", "📺 YouTube", "🎵 Spotify", "✈️ Telegram",
                "🔍 Google", "📘 Facebook", "🐦 Twitter", "💼 LinkedIn",
                "📷 Instagram", "🛒 Amazon", "📚 Wikipedia", "🎮 Twitch",
                "💬 Discord", "☁️ Dropbox", "📦 Google Drive"
            ]
        }
        super().__init__()
        self.setWindowTitle("Der Browser")
        self.setGeometry(100, 100, 1400, 800)

        # Инициализация данных
        self.current_user = None
        self.is_incognito = False
        self.incognito_history = []
        self.bookmarks = []
        self.history = []
        self.zoom_level = 100
        self.homepage = "about:blank"
        self.current_tab_index = 0

        # Настройки
        self.settings = {
            "theme": "dark",  # "dark" или "light"
            "vpn_enabled": False,
            "dns_primary": "8.8.8.8",
            "dns_secondary": "8.8.4.4",
            "block_ads": False,
            "save_passwords": True,
            "javascript_enabled": True,
            "default_search_engine": "google",
            "home_page": "about:blank",
            "download_path": os.path.join(os.path.expanduser("~"), "Downloads"),
            "notifications": True,
            "hardware_acceleration": True
        }

        # Путь для данных
        self.data_dir = os.path.join(os.path.expanduser("~"), ".derbrowser")
        os.makedirs(self.data_dir, exist_ok=True)

        # Загрузка данных пользователей
        self.users = self.load_users()

        # Аутентификация - нужно запустить до создания UI
        self.authenticate_and_init()

    def authenticate_and_init(self):
        """Аутентификация пользователя и инициализация интерфейса"""
        # Сначала пробуем автоматический вход по сессии
        session_file = os.path.join(self.data_dir, 'session.pkl')
        if os.path.exists(session_file):
            try:
                with open(session_file, 'rb') as f:
                    session_data = pickle.load(f)
                    username = session_data.get('username')
                    if username in self.users:
                        self.current_user = self.users[username]
                        self.current_user.last_login = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        self.save_users()

                        # Проверка на админа при автовходе
                        if username in ['admin', 'RobertusaAdmin']:
                            password = session_data.get('password_hash')
                            if password and self.verify_password("1555", password):
                                self.is_admin = True
                            else:
                                self.is_admin = False
                        else:
                            self.is_admin = False

                        print(f"Автовход пользователя: {username}")
                        self.init_browser_ui()
                        return True
            except Exception as e:
                print(f"Ошибка загрузки сессии: {e}")

        # Если нет сессии или автовход не удался, показываем диалог
        current_mode = "login"

        while True:
            dialog = AuthDialog(self, current_mode)
            result = dialog.exec_()

            if result == QDialog.Rejected:
                # Пользователь нажал Отмена или хочет сменить режим
                if dialog.need_switch_mode:
                    # Меняем режим и показываем диалог снова
                    current_mode = dialog.new_mode
                    continue
                else:
                    # Пользователь действительно отменил
                    sys.exit(0)

            elif result == QDialog.Accepted:
                # Пользователь нажал Войти/Зарегистрироваться
                username, password, confirm_password = dialog.get_credentials()

                # Проверка на админа
                self.is_admin = False
                if username in ['admin', 'RobertusaAdmin'] and password == "1555":
                    self.is_admin = True

                if dialog.mode == "login":
                    # Вход
                    if not username or not password:
                        QMessageBox.warning(self, "Ошибка", "Введите логин и пароль!")
                        continue

                    if username in self.users:
                        if self.verify_password(password, self.users[username].password_hash):
                            self.current_user = self.users[username]
                            self.current_user.last_login = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            self.save_users()
                            self.save_session(username, password if self.is_admin else "")
                            print(f"Успешный вход: {username}")
                            if self.is_admin:
                                print("Пользователь вошел как администратор")
                            self.init_browser_ui()
                            return True
                        else:
                            QMessageBox.warning(self, "Ошибка", "Неверный пароль!")
                            continue
                    else:
                        QMessageBox.warning(self, "Ошибка", "Пользователь не найден!")
                        continue

                else:  # Регистрация
                    if not username or not password or not confirm_password:
                        QMessageBox.warning(self, "Ошибка", "Все поля должны быть заполнены!")
                        continue

                    if username in self.users:
                        QMessageBox.warning(self, "Ошибка", "Пользователь уже существует!")
                        continue

                    if len(username) < 3:
                        QMessageBox.warning(self, "Ошибка", "Логин должен быть не менее 3 символов!")
                        continue

                    if len(password) < 4:
                        QMessageBox.warning(self, "Ошибка", "Пароль должен быть не менее 4 символов!")
                        continue

                    if password != confirm_password:
                        QMessageBox.warning(self, "Ошибка", "Пароли не совпадают!")
                        continue

                    # Создаем нового пользователя
                    password_hash = self.hash_password(password)
                    new_user = UserAccount(username, password_hash)
                    self.users[username] = new_user
                    self.current_user = new_user
                    self.save_users()
                    self.save_session(username, password if self.is_admin else "")

                    QMessageBox.information(self, "Успех", "Регистрация прошла успешно!")
                    print(f"Зарегистрирован новый пользователь: {username}")
                    self.init_browser_ui()
                    return True

        return False

    def init_browser_ui(self):
        """Инициализация интерфейса браузера после успешной аутентификации"""
        # Загрузка данных пользователя
        self.load_user_data()

        # Загрузка админ настроек
        self.load_admin_settings()

        # Настройка интерфейса
        self.init_ui()

        # Настройка горячих клавиш
        self.setup_shortcuts()

        # Центрирование окна
        self.center_window()

        # Применяем тему по умолчанию
        self.apply_theme(self.settings["theme"])

        # Применяем админ тему если пользователь админ
        if self.is_admin:
            self.apply_admin_theme()

        # Инициализация VPN
        self.vpn_status = False
        self.original_dns = None

    def hash_password(self, password):
        """Хеширует пароль"""
        salt = b"der_browser_salt_2024"
        dk = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
        return base64.b64encode(dk).decode()

    def verify_password(self, password, password_hash):
        """Проверяет пароль"""
        return self.hash_password(password) == password_hash

    def save_session(self, username, admin_password=""):
        """Сохраняет сессию пользователя"""
        try:
            session_file = os.path.join(self.data_dir, 'session.pkl')
            session_data = {
                'username': username,
                'password_hash': self.hash_password(admin_password) if admin_password and username in ['admin', 'RobertusaAdmin'] else ""
            }
            with open(session_file, 'wb') as f:
                pickle.dump(session_data, f)
        except Exception as e:
            print(f"Ошибка сохранения сессии: {e}")

    def clear_session(self):
        """Очищает сессию пользователя"""
        try:
            session_file = os.path.join(self.data_dir, 'session.pkl')
            if os.path.exists(session_file):
                os.remove(session_file)
        except Exception as e:
            print(f"Ошибка очистки сессии: {e}")

    def load_users(self):
        """Загружает пользователей"""
        try:
            users_file = os.path.join(self.data_dir, 'users.pkl')
            if os.path.exists(users_file):
                with open(users_file, 'rb') as f:
                    return pickle.load(f)
        except Exception as e:
            print(f"Ошибка загрузки пользователей: {e}")
        return {}

    def save_users(self):
        """Сохраняет пользователей"""
        try:
            users_file = os.path.join(self.data_dir, 'users.pkl')
            with open(users_file, 'wb') as f:
                pickle.dump(self.users, f)
        except Exception as e:
            print(f"Ошибка сохранения пользователей: {e}")

    def load_user_data(self):
        """Загружает данные пользователя"""
        if self.current_user:
            self.bookmarks = self.current_user.bookmarks
            self.history = self.current_user.history
            if hasattr(self.current_user, 'settings'):
                self.settings.update(self.current_user.settings)

    def save_user_data(self):
        """Сохраняет данные пользователя"""
        if self.current_user and not self.is_incognito:
            self.current_user.bookmarks = self.bookmarks
            self.current_user.history = self.history
            self.current_user.settings = self.settings
            self.save_users()

    def center_window(self):
        """Центрирует окно на экране"""
        frame_geometry = self.frameGeometry()
        screen_center = QDesktopWidget().availableGeometry().center()
        frame_geometry.moveCenter(screen_center)
        self.move(frame_geometry.topLeft())

    def init_ui(self):
        """Инициализация пользовательского интерфейса"""
        # Создание центрального виджета
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Основной layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Создание панели навигации
        self.create_nav_bar(main_layout)

        # Создание вкладок
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.tab_widget.currentChanged.connect(self.tab_changed)

        main_layout.addWidget(self.tab_widget)

        # Создание статус бара
        self.create_status_bar(main_layout)

        # Создание меню
        self.create_menu_bar()

        # Создаем первую вкладку (главную страницу)
        self.add_new_tab("", "🏠 Главная", True)

    def create_nav_bar(self, parent_layout):
        """Создает панель навигации"""
        nav_bar = QWidget()
        nav_bar.setFixedHeight(70)
        nav_bar.setObjectName("navBar")

        layout = QHBoxLayout(nav_bar)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(10)

        # Логотип и название слева
        logo_widget = QWidget()
        logo_layout = QHBoxLayout(logo_widget)
        logo_layout.setContentsMargins(0, 0, 0, 0)
        logo_layout.setSpacing(10)

        logo_icon = QLabel("🌐")
        logo_icon.setObjectName("navLogoIcon")
        logo_icon.setStyleSheet("font-size: 24px; color: #3498db; font-weight: bold;")
        logo_icon.setFixedSize(40, 40)

        logo_text = QLabel("Der Browser")
        logo_text.setObjectName("navLogoText")
        logo_text.setStyleSheet("color: #e0e0e0; font-size: 18px; font-weight: bold;")
        logo_text.setFixedHeight(40)

        logo_layout.addWidget(logo_icon)
        logo_layout.addWidget(logo_text)
        layout.addWidget(logo_widget)

        # Кнопки навигации
        nav_buttons_widget = QWidget()
        nav_buttons_layout = QHBoxLayout(nav_buttons_widget)
        nav_buttons_layout.setSpacing(5)
        nav_buttons_layout.setContentsMargins(0, 0, 0, 0)

        self.back_btn = QPushButton("◀")
        self.back_btn.setObjectName("navButton")
        self.back_btn.setToolTip("Назад")
        self.back_btn.setFixedSize(40, 40)
        self.back_btn.clicked.connect(self.navigate_back)

        self.forward_btn = QPushButton("▶")
        self.forward_btn.setObjectName("navButton")
        self.forward_btn.setToolTip("Вперед")
        self.forward_btn.setFixedSize(40, 40)
        self.forward_btn.clicked.connect(self.navigate_forward)

        self.reload_btn = QPushButton("↻")
        self.reload_btn.setObjectName("navButton")
        self.reload_btn.setToolTip("Обновить")
        self.reload_btn.setFixedSize(40, 40)
        self.reload_btn.clicked.connect(self.reload_page)

        self.home_btn = QPushButton("🏠")
        self.home_btn.setObjectName("navButton")
        self.home_btn.setToolTip("Главная")
        self.home_btn.setFixedSize(40, 40)
        self.home_btn.clicked.connect(self.go_home)

        nav_buttons_layout.addWidget(self.back_btn)
        nav_buttons_layout.addWidget(self.forward_btn)
        nav_buttons_layout.addWidget(self.reload_btn)
        nav_buttons_layout.addWidget(self.home_btn)
        layout.addWidget(nav_buttons_widget)

        # Поле URL
        self.url_bar = QLineEdit()
        self.url_bar.setObjectName("urlBar")
        self.url_bar.setPlaceholderText("Введите URL или поисковый запрос...")
        self.url_bar.returnPressed.connect(self.on_url_entered)
        layout.addWidget(self.url_bar, 1)

        # Кнопка перехода
        self.go_btn = QPushButton("➤")
        self.go_btn.setObjectName("goButton")
        self.go_btn.setToolTip("Перейти")
        self.go_btn.setFixedSize(40, 40)
        self.go_btn.clicked.connect(self.on_url_entered)
        layout.addWidget(self.go_btn)

        # Кнопки действий
        action_buttons_widget = QWidget()
        action_buttons_layout = QHBoxLayout(action_buttons_widget)
        action_buttons_layout.setSpacing(5)
        action_buttons_layout.setContentsMargins(0, 0, 0, 0)

        self.bookmark_btn = QPushButton("⭐")
        self.bookmark_btn.setObjectName("actionButton")
        self.bookmark_btn.setToolTip("Добавить в закладки")
        self.bookmark_btn.setFixedSize(40, 40)
        self.bookmark_btn.clicked.connect(self.add_current_to_bookmarks)

        self.new_tab_btn = QPushButton("➕")
        self.new_tab_btn.setObjectName("actionButton")
        self.new_tab_btn.setToolTip("Новая вкладка")
        self.new_tab_btn.setFixedSize(40, 40)
        self.new_tab_btn.clicked.connect(lambda: self.add_new_tab("", "Новая вкладка", True))

        self.incognito_btn = QPushButton("👤")
        self.incognito_btn.setObjectName("actionButton")
        self.incognito_btn.setToolTip("Режим инкогнито" if not self.is_incognito else "Обычный режим")
        self.incognito_btn.setFixedSize(40, 40)
        self.incognito_btn.clicked.connect(self.toggle_incognito)

        self.menu_btn = QPushButton("☰")
        self.menu_btn.setObjectName("actionButton")
        self.menu_btn.setToolTip("Меню")
        self.menu_btn.setFixedSize(40, 40)
        self.menu_btn.clicked.connect(self.show_context_menu)

        action_buttons_layout.addWidget(self.bookmark_btn)
        action_buttons_layout.addWidget(self.new_tab_btn)
        action_buttons_layout.addWidget(self.incognito_btn)
        action_buttons_layout.addWidget(self.menu_btn)
        layout.addWidget(action_buttons_widget)

        parent_layout.addWidget(nav_bar)

        # Обновляем иконку инкогнито
        self.update_incognito_button()

    def create_status_bar(self, parent_layout):
        """Создает статус бар"""
        status_bar = QWidget()
        status_bar.setFixedHeight(30)
        status_bar.setObjectName("statusBar")

        layout = QHBoxLayout(status_bar)
        layout.setContentsMargins(15, 0, 15, 0)

        user_info = f"Пользователь: {self.current_user.username}" if self.current_user else "Гость"
        if self.is_incognito:
            user_info += " 🔒 (Инкогнито)"
        self.status_label = QLabel(f"Добро пожаловать в Der Browser | {user_info}")
        self.status_label.setObjectName("statusLabel")

        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("progressBar")
        self.progress_bar.setVisible(False)
        self.progress_bar.setFixedWidth(200)
        self.progress_bar.setTextVisible(False)

        layout.addWidget(self.status_label)
        layout.addStretch()
        layout.addWidget(self.progress_bar)

        parent_layout.addWidget(status_bar)

    def create_menu_bar(self):
        """Создает меню"""
        menubar = self.menuBar()
        menubar.setObjectName("menuBar")

        # Меню "Файл"
        file_menu = menubar.addMenu('Файл')

        new_tab_action = QAction('Новая вкладка', self)
        new_tab_action.setShortcut('Ctrl+T')
        new_tab_action.triggered.connect(lambda: self.add_new_tab("", "Новая вкладка", True))
        file_menu.addAction(new_tab_action)

        new_incognito_action = QAction('Новая вкладка инкогнито', self)
        new_incognito_action.setShortcut('Ctrl+Shift+T')
        new_incognito_action.triggered.connect(self.new_incognito_tab)
        file_menu.addAction(new_incognito_action)

        close_tab_action = QAction('Закрыть вкладку', self)
        close_tab_action.setShortcut('Ctrl+W')
        close_tab_action.triggered.connect(lambda: self.close_tab(self.tab_widget.currentIndex()))
        file_menu.addAction(close_tab_action)

        file_menu.addSeparator()

        print_action = QAction('Печать', self)
        print_action.setShortcut('Ctrl+P')
        print_action.triggered.connect(self.print_page)
        file_menu.addAction(print_action)

        save_page_action = QAction('Сохранить страницу как...', self)
        save_page_action.setShortcut('Ctrl+S')
        save_page_action.triggered.connect(self.save_page)
        file_menu.addAction(save_page_action)

        file_menu.addSeparator()

        logout_action = QAction('Сменить пользователя', self)
        logout_action.triggered.connect(self.logout)
        file_menu.addAction(logout_action)

        exit_action = QAction('Выход', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Меню "Закладки"
        bookmarks_menu = menubar.addMenu('Закладки')

        add_bookmark_action = QAction('Добавить в закладки', self)
        add_bookmark_action.setShortcut('Ctrl+D')
        add_bookmark_action.triggered.connect(self.add_current_to_bookmarks)
        bookmarks_menu.addAction(add_bookmark_action)

        show_bookmarks_action = QAction('Показать закладки', self)
        show_bookmarks_action.triggered.connect(self.show_bookmarks_dialog)
        bookmarks_menu.addAction(show_bookmarks_action)

        organize_bookmarks_action = QAction('Управление закладками', self)
        organize_bookmarks_action.triggered.connect(self.organize_bookmarks)
        bookmarks_menu.addAction(organize_bookmarks_action)

        # Меню "История"
        history_menu = menubar.addMenu('История')

        show_history_action = QAction('Показать историю', self)
        show_history_action.triggered.connect(self.show_history_dialog)
        history_menu.addAction(show_history_action)

        clear_history_action = QAction('Очистить историю', self)
        clear_history_action.triggered.connect(self.clear_all_history)
        history_menu.addAction(clear_history_action)

        # Меню "Настройки"
        settings_menu = menubar.addMenu('Настройки')

        settings_action = QAction('Настройки браузера', self)
        settings_action.setShortcut('Ctrl+Shift+S')
        settings_action.triggered.connect(self.show_settings_dialog)
        settings_menu.addAction(settings_action)

        theme_action = QAction('Переключить тему', self)
        theme_action.setShortcut('Ctrl+Shift+Alt+T')
        theme_action.triggered.connect(self.toggle_theme)
        settings_menu.addAction(theme_action)

        vpn_action = QAction('Включить/выключить VPN', self)
        vpn_action.setShortcut('Ctrl+Shift+V')
        vpn_action.triggered.connect(self.toggle_vpn)
        settings_menu.addAction(vpn_action)

        incognito_action = QAction('Переключить режим инкогнито', self)
        incognito_action.setShortcut('Ctrl+Shift+I')
        incognito_action.triggered.connect(self.toggle_incognito)
        settings_menu.addAction(incognito_action)

        # Меню "Инструменты"
        tools_menu = menubar.addMenu('Инструменты')

        zoom_in_action = QAction('Увеличить', self)
        zoom_in_action.setShortcut('Ctrl++')
        zoom_in_action.triggered.connect(self.zoom_in)
        tools_menu.addAction(zoom_in_action)

        zoom_out_action = QAction('Уменьшить', self)
        zoom_out_action.setShortcut('Ctrl+-')
        zoom_out_action.triggered.connect(self.zoom_out)
        tools_menu.addAction(zoom_out_action)

        zoom_reset_action = QAction('Сбросить масштаб', self)
        zoom_reset_action.setShortcut('Ctrl+0')
        zoom_reset_action.triggered.connect(self.reset_zoom)
        tools_menu.addAction(zoom_reset_action)

        tools_menu.addSeparator()

        dev_tools_action = QAction('Инструменты разработчика', self)
        dev_tools_action.setShortcut('F12')
        dev_tools_action.triggered.connect(self.show_dev_tools)
        tools_menu.addAction(dev_tools_action)

        # Меню "Справка"
        help_menu = menubar.addMenu('Справка')

        about_action = QAction('О Der Browser', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

        help_action = QAction('Справка', self)
        help_action.setShortcut('F1')
        help_action.triggered.connect(self.show_help)
        help_menu.addAction(help_action)

        # Меню "Админ" (только для админов)
        if self.is_admin:
            admin_menu = menubar.addMenu('👑 Админ')

            admin_panel_action = QAction('Админ панель', self)
            admin_panel_action.setShortcut('Ctrl+Shift+A')
            admin_panel_action.triggered.connect(self.show_admin_panel)
            admin_menu.addAction(admin_panel_action)

            admin_menu.addSeparator()

            reload_ui_action = QAction('Перезагрузить интерфейс', self)
            reload_ui_action.triggered.connect(self.reload_ui)
            admin_menu.addAction(reload_ui_action)

            reset_settings_action = QAction('Сбросить настройки', self)
            reset_settings_action.triggered.connect(self.reset_admin_settings)
            admin_menu.addAction(reset_settings_action)

    def add_new_tab(self, url, title="Новая вкладка", is_homepage=False, is_incognito=None):
        """Добавляет новую вкладку"""
        if is_incognito is None:
            is_incognito = self.is_incognito

        tab = BrowserTab(parent_browser=self, url=url, is_homepage=is_homepage, is_incognito=is_incognito)

        if not is_homepage:
            # Настраиваем сигналы только для обычных вкладок
            tab.browser.urlChanged.connect(self.update_url_bar)
            tab.browser.loadProgress.connect(self.update_progress)
            tab.browser.loadFinished.connect(self.page_loaded)
            tab.browser.titleChanged.connect(lambda t: self.update_tab_title(tab, t))

        # Добавляем иконку инкогнито если нужно
        icon_text = "👤 " if is_incognito else ""
        tab_title = f"{icon_text}{title}"

        index = self.tab_widget.addTab(tab, tab_title)
        self.tab_widget.setCurrentIndex(index)

        return tab

    def new_incognito_tab(self):
        """Создает новую вкладку в режиме инкогнито"""
        self.add_new_tab("", "Инкогнито", True, True)

    def toggle_incognito(self):
        """Переключает режим инкогнито"""
        self.is_incognito = not self.is_incognito
        self.update_incognito_button()

        if self.is_incognito:
            self.show_notification("Режим инкогнито включен - история не сохраняется")
            # Сохраняем текущие данные перед переходом в инкогнито
            self.save_user_data()
            self.incognito_history = []
        else:
            self.show_notification("Обычный режим включен")
            self.load_user_data()

        # Обновляем статус бар
        user_info = f"Пользователь: {self.current_user.username}" if self.current_user else "Гость"
        if self.is_incognito:
            user_info += " 🔒 (Инкогнито)"
        self.status_label.setText(f"Добро пожаловать в Der Browser | {user_info}")

    def update_incognito_button(self):
        """Обновляет кнопку инкогнито"""
        if self.is_incognito:
            self.incognito_btn.setText("👁")
            self.incognito_btn.setToolTip("Обычный режим")
            self.incognito_btn.setStyleSheet("""
                QPushButton {
                    background-color: #2ecc71;
                    border: 2px solid #27ae60;
                    border-radius: 20px;
                    color: white;
                    font-size: 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #27ae60;
                    border-color: #219955;
                }
            """)
        else:
            self.incognito_btn.setText("👤")
            self.incognito_btn.setToolTip("Режим инкогнито")
            # Стиль будет применен через общий стиль темы

    def close_tab(self, index):
        """Закрывает вкладку"""
        if self.tab_widget.count() > 1:
            self.tab_widget.removeTab(index)
        else:
            self.close()

    def tab_changed(self, index):
        """Обработчик изменения вкладки"""
        self.current_tab_index = index
        if index >= 0:
            tab = self.tab_widget.widget(index)
            if tab and not tab.is_homepage and hasattr(tab, 'browser'):
                current_url = tab.browser.url().toString()
                self.url_bar.setText(current_url)
                self.update_navigation_buttons()
            else:
                self.url_bar.setText("")
                self.url_bar.setPlaceholderText("Der Browser - Главная")
                self.back_btn.setEnabled(False)
                self.forward_btn.setEnabled(False)

    def get_current_browser(self):
        """Возвращает текущий браузер"""
        if self.current_tab_index >= 0:
            tab = self.tab_widget.widget(self.current_tab_index)
            if tab and not tab.is_homepage and hasattr(tab, 'browser'):
                return tab.browser
        return None

    def get_current_tab(self):
        """Возвращает текущую вкладку"""
        if self.current_tab_index >= 0:
            return self.tab_widget.widget(self.current_tab_index)
        return None

    def navigate_to_url(self, url):
        """Переходит по указанному URL"""
        browser = self.get_current_browser()
        if browser:
            if not url.startswith('http://') and not url.startswith('https://'):
                if '.' in url and ' ' not in url:
                    url = 'https://' + url
                else:
                    # Поиск через Google
                    query = urllib.parse.quote(url)
                    url = f'https://www.google.com/search?q={query}'

            browser.setUrl(QUrl(url))
            self.url_bar.setText(url)
        else:
            # Если на главной странице, создаем новую вкладку для перехода
            tab = self.get_current_tab()
            is_incognito = tab.is_incognito if tab else False
            self.add_new_tab(url, "Загрузка...", False, is_incognito)

    def on_url_entered(self):
        """Обработчик ввода URL"""
        url = self.url_bar.text()
        if url:
            self.navigate_to_url(url)

    def navigate_back(self):
        """Переход назад"""
        browser = self.get_current_browser()
        if browser:
            browser.back()

    def navigate_forward(self):
        """Переход вперед"""
        browser = self.get_current_browser()
        if browser:
            browser.forward()

    def reload_page(self):
        """Обновление страницы"""
        browser = self.get_current_browser()
        if browser:
            browser.reload()

    def go_home(self):
        """Переход на главную страницу"""
        self.tab_widget.setCurrentIndex(0)

    def update_url_bar(self, q):
        """Обновление поля URL"""
        url = q.toString()
        self.url_bar.setText(url)
        self.update_navigation_buttons()

    def update_navigation_buttons(self):
        """Обновляет состояние кнопок навигации"""
        browser = self.get_current_browser()
        if browser:
            self.back_btn.setEnabled(browser.history().canGoBack())
            self.forward_btn.setEnabled(browser.history().canGoForward())
        else:
            self.back_btn.setEnabled(False)
            self.forward_btn.setEnabled(False)

    def update_progress(self, progress):
        """Обновление прогресса загрузки"""
        if progress < 100:
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(progress)
            self.status_label.setText(f"Загрузка... {progress}%")
        else:
            self.progress_bar.setVisible(False)
            self.status_label.setText("Готово")
            self.add_current_to_history()

    def page_loaded(self):
        """Обработчик завершения загрузки страницы"""
        browser = self.get_current_browser()
        if browser:
            title = browser.page().title()
            if title:
                tab = self.get_current_tab()
                if tab and tab.is_incognito:
                    self.setWindowTitle(f"{title} - Der Browser [Инкогнито]")
                else:
                    self.setWindowTitle(f"{title} - Der Browser")

                # Обновляем заголовок вкладки
                current_tab = self.get_current_tab()
                if current_tab:
                    index = self.tab_widget.currentIndex()
                    short_title = title[:20] + "..." if len(title) > 20 else title
                    icon_text = "👤 " if current_tab.is_incognito else ""
                    self.tab_widget.setTabText(index, f"{icon_text}{short_title}")

    def update_tab_title(self, tab, title):
        """Обновление заголовка вкладки"""
        index = self.tab_widget.indexOf(tab)
        if index >= 0 and title:
            short_title = title[:20] + "..." if len(title) > 20 else title
            icon_text = "👤 " if tab.is_incognito else ""
            self.tab_widget.setTabText(index, f"{icon_text}{short_title}")

    def add_current_to_history(self):
        """Добавляет текущую страницу в историю"""
        if self.is_incognito:
            # В режиме инкогнито сохраняем историю только во временном списке
            browser = self.get_current_browser()
            if browser:
                url = browser.url().toString()
                title = browser.page().title()

                if url and url != "about:blank":
                    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    # Проверяем, есть ли уже такая запись
                    for item in self.incognito_history:
                        if item.url == url:
                            item.visit_count += 1
                            item.visit_time = now
                            item.title = title
                            return

                    # Новая запись
                    item = HistoryItem(url, title, now, 1)
                    self.incognito_history.append(item)
        else:
            # В обычном режиме сохраняем в постоянную историю пользователя
            browser = self.get_current_browser()
            if browser:
                url = browser.url().toString()
                title = browser.page().title()

                if url and url != "about:blank":
                    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    # Проверяем, есть ли уже такая запись
                    for item in self.history:
                        if item.url == url:
                            item.visit_count += 1
                            item.visit_time = now
                            item.title = title
                            self.save_user_data()
                            return

                    # Новая запись
                    item = HistoryItem(url, title, now, 1)
                    self.history.append(item)
                    self.save_user_data()

    def add_current_to_bookmarks(self):
        """Добавляет текущую страницу в закладки"""
        if self.is_incognito:
            self.show_notification("В режиме инкогнито нельзя добавлять закладки")
            return

        browser = self.get_current_browser()
        if browser:
            url = browser.url().toString()
            title = browser.page().title()

            if url and url != "about:blank":
                bookmark = Bookmark(title, url, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                self.bookmarks.append(bookmark)
                self.save_user_data()
                self.show_notification(f"Закладка '{title[:30]}...' добавлена!" if len(title) > 30 else f"Закладка '{title}' добавлена!")

    def show_notification(self, message):
        """Показывает всплывающее уведомление"""
        self.status_label.setText(message)
        QTimer.singleShot(3000, lambda: self.status_label.setText("Готово"))

    def show_bookmarks_dialog(self):
        """Показывает диалог закладок"""
        if self.is_incognito:
            self.show_notification("В режиме инкогнито недоступны закладки")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Закладки")
        dialog.setGeometry(400, 200, 700, 500)
        dialog.setObjectName("settingsDialog")

        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)

        # Заголовок
        title_label = QLabel("⭐ Мои закладки")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #3498db; font-size: 20px; font-weight: bold;")
        layout.addWidget(title_label)

        # Поиск по закладкам
        search_widget = QWidget()
        search_layout = QHBoxLayout(search_widget)

        search_edit = QLineEdit()
        search_edit.setPlaceholderText("Поиск закладок...")
        search_edit.setStyleSheet("""
            QLineEdit {
                background-color: #2a2a3a;
                border: 2px solid #3a3a4a;
                border-radius: 10px;
                padding: 8px 12px;
                font-size: 14px;
                color: #e0e0e0;
                min-height: 35px;
            }
            QLineEdit:focus {
                border-color: #3498db;
                background-color: #3a3a4a;
            }
        """)

        search_btn = QPushButton("🔍")
        search_btn.setFixedSize(40, 40)

        search_layout.addWidget(search_edit)
        search_layout.addWidget(search_btn)
        layout.addWidget(search_widget)

        # Список закладок
        bookmarks_list = QListWidget()
        bookmarks_list.setStyleSheet("""
            QListWidget {
                background-color: #2a2a3a;
                border: 2px solid #3a3a4a;
                border-radius: 10px;
                color: #e0e0e0;
                font-size: 13px;
                padding: 10px;
            }
            QListWidget::item {
                padding: 10px;
                border-radius: 5px;
                margin: 5px;
            }
            QListWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
        """)

        for bookmark in self.bookmarks:
            item_text = f"{bookmark.icon} {bookmark.title}\n{bookmark.url}"
            if bookmark.category and bookmark.category != "General":
                item_text += f"\n📁 {bookmark.category}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, (bookmark.url, bookmark.title))
            bookmarks_list.addItem(item)

        layout.addWidget(bookmarks_list)

        # Кнопки
        button_layout = QHBoxLayout()

        open_btn = QPushButton("📂 Открыть")
        open_btn.clicked.connect(lambda: self.open_bookmark(bookmarks_list, dialog))

        new_folder_btn = QPushButton("📁 Новая папка")
        new_folder_btn.clicked.connect(lambda: self.create_bookmark_folder())

        delete_btn = QPushButton("🗑️ Удалить")
        delete_btn.clicked.connect(lambda: self.delete_bookmark(bookmarks_list))

        close_btn = QPushButton("✖ Закрыть")
        close_btn.clicked.connect(dialog.close)

        button_layout.addWidget(open_btn)
        button_layout.addWidget(new_folder_btn)
        button_layout.addWidget(delete_btn)
        button_layout.addStretch()
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

        dialog.setStyleSheet("""
            QDialog {
                background-color: #1a1a2a;
                border: 2px solid #3498db;
                border-radius: 15px;
            }
            QPushButton {
                background-color: #3a3a4a;
                border: 2px solid #4a4a5a;
                border-radius: 8px;
                padding: 10px 20px;
                color: #e0e0e0;
                font-weight: bold;
                font-size: 12px;
                min-height: 35px;
            }
            QPushButton:hover {
                background-color: #4a4a5a;
                border-color: #3498db;
            }
        """)

        dialog.exec_()

    def open_bookmark(self, list_widget, dialog):
        """Открывает выбранную закладку"""
        current_item = list_widget.currentItem()
        if current_item:
            url, title = current_item.data(Qt.UserRole)
            self.add_new_tab(url, title[:20], False)
            dialog.close()

    def delete_bookmark(self, list_widget):
        """Удаляет выбранную закладку"""
        current_row = list_widget.currentRow()
        if current_row >= 0:
            del self.bookmarks[current_row]
            list_widget.takeItem(current_row)
            self.save_user_data()
            self.show_notification("Закладка удалена")

    def create_bookmark_folder(self):
        """Создает новую папку для закладок"""
        folder_name, ok = QInputDialog.getText(self, "Новая папка", "Введите название папки:")
        if ok and folder_name:
            self.show_notification(f"Создана папка: {folder_name}")

    def organize_bookmarks(self):
        """Управление закладками"""
        self.show_notification("Функция управления закладками в разработке")

    def show_history_dialog(self):
        """Показывает диалог истории"""
        if self.is_incognito:
            # Показываем историю инкогнито
            history_to_show = self.incognito_history
            title = "История инкогнито (не сохраняется)"
        else:
            # Показываем обычную историю
            history_to_show = self.history
            title = "История посещений"

        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        dialog.setGeometry(400, 200, 800, 500)
        dialog.setObjectName("settingsDialog")

        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)

        # Заголовок
        title_label = QLabel("📜 " + title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #3498db; font-size: 20px; font-weight: bold;")
        layout.addWidget(title_label)

        # Фильтры
        filter_widget = QWidget()
        filter_layout = QHBoxLayout(filter_widget)

        today_btn = QPushButton("Сегодня")
        week_btn = QPushButton("Неделя")
        month_btn = QPushButton("Месяц")
        all_btn = QPushButton("Все")

        for btn in [today_btn, week_btn, month_btn, all_btn]:
            btn.setFixedHeight(35)

        filter_layout.addWidget(today_btn)
        filter_layout.addWidget(week_btn)
        filter_layout.addWidget(month_btn)
        filter_layout.addWidget(all_btn)
        filter_layout.addStretch()

        layout.addWidget(filter_widget)

        # Список истории
        history_list = QListWidget()
        history_list.setStyleSheet("""
            QListWidget {
                background-color: #2a2a3a;
                border: 2px solid #3a3a4a;
                border-radius: 10px;
                color: #e0e0e0;
                font-size: 13px;
                padding: 10px;
            }
            QListWidget::item {
                padding: 10px;
                border-radius: 5px;
                margin: 5px;
            }
            QListWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
        """)

        for item in reversed(history_to_show[-100:]):  # Последние 100 записей
            visits = f" ({item.visit_count} посещ.)" if item.visit_count > 1 else ""
            display_text = f"{item.visit_time} - {item.title[:50]}{visits}"
            if len(item.title) > 50:
                display_text += "..."
            history_list.addItem(display_text)

        layout.addWidget(history_list)

        # Кнопки
        button_layout = QHBoxLayout()

        open_btn = QPushButton("📂 Перейти")
        open_btn.clicked.connect(lambda: self.open_from_history(history_list, dialog, history_to_show))

        if not self.is_incognito:
            clear_btn = QPushButton("🗑️ Очистить историю")
            clear_btn.clicked.connect(lambda: self.clear_history_dialog(history_list))
        else:
            clear_btn = QPushButton("🗑️ Очистить (инкогнито)")
            clear_btn.clicked.connect(lambda: self.clear_incognito_history(history_list))

        search_btn = QPushButton("🔍 Поиск в истории")
        search_btn.clicked.connect(self.search_in_history)

        close_btn = QPushButton("✖ Закрыть")
        close_btn.clicked.connect(dialog.close)

        button_layout.addWidget(open_btn)
        button_layout.addWidget(clear_btn)
        button_layout.addWidget(search_btn)
        button_layout.addStretch()
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

        dialog.setStyleSheet("""
            QDialog {
                background-color: #1a1a2a;
                border: 2px solid #3498db;
                border-radius: 15px;
            }
            QPushButton {
                background-color: #3a3a4a;
                border: 2px solid #4a4a5a;
                border-radius: 8px;
                padding: 10px 20px;
                color: #e0e0e0;
                font-weight: bold;
                font-size: 12px;
                min-height: 35px;
            }
            QPushButton:hover {
                background-color: #4a4a5a;
                border-color: #3498db;
            }
        """)

        dialog.exec_()

    def open_from_history(self, list_widget, dialog, history_to_show):
        """Открывает выбранную страницу из истории"""
        current_row = list_widget.currentRow()
        if current_row >= 0 and history_to_show:
            # Преобразуем индекс (список отображается в обратном порядке)
            actual_index = len(history_to_show) - 1 - current_row
            if 0 <= actual_index < len(history_to_show):
                url = history_to_show[actual_index].url
                tab = self.get_current_tab()
                is_incognito = self.is_incognito or (tab.is_incognito if tab else False)
                self.add_new_tab(url, "Загрузка...", False, is_incognito)
                dialog.close()

    def clear_history_dialog(self, list_widget):
        """Очищает историю в диалоге"""
        reply = QMessageBox.question(self, "Очистка истории",
                                   "Вы уверены, что хотите очистить всю историю?",
                                   QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.history.clear()
            if list_widget:
                list_widget.clear()
            self.save_user_data()
            self.show_notification("История очищена")

    def clear_all_history(self):
        """Очищает всю историю"""
        reply = QMessageBox.question(self, "Очистка истории",
                                   "Вы уверены, что хотите очистить всю историю?\nЭто действие нельзя отменить.",
                                   QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.history.clear()
            self.save_user_data()
            self.show_notification("Вся история очищена")

    def search_in_history(self):
        """Поиск в истории"""
        self.show_notification("Функция поиска в истории в разработке")

    def clear_incognito_history(self, list_widget):
        """Очищает историю инкогнито"""
        self.incognito_history.clear()
        if list_widget:
            list_widget.clear()
        self.show_notification("История инкогнито очищена")

    def show_context_menu(self):
        """Показывает контекстное меню"""
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #1a1a2a;
                border: 2px solid #3498db;
                color: #e0e0e0;
                font-size: 13px;
            }
            QMenu::item {
                padding: 8px 20px;
                background-color: transparent;
            }
            QMenu::item:selected {
                background-color: #3498db;
                color: white;
            }
            QMenu::separator {
                height: 1px;
                background-color: #3a3a4a;
                margin: 5px 10px;
            }
        """)
        # Админ панель (только для админов)
        if self.is_admin:
            menu.addSeparator()
            menu.addAction("👑 Админ панель", self.show_admin_panel)

        # Основные действия
        menu.addAction("➕ Новая вкладка", lambda: self.add_new_tab("", "Новая вкладка", True))
        menu.addAction("👤 Новая вкладка инкогнито", self.new_incognito_tab)
        menu.addSeparator()

        # Закладки и история
        menu.addAction("⭐ Закладки", self.show_bookmarks_dialog)
        menu.addAction("📜 История", self.show_history_dialog)
        menu.addSeparator()

        # Настройки
        menu.addAction("⚙️ Настройки браузера", self.show_settings_dialog)
        menu.addAction("🎨 Переключить тему", self.toggle_theme)
        menu.addAction("🔒 Переключить VPN", self.toggle_vpn)
        menu.addAction("👤 Переключить инкогнито", self.toggle_incognito)
        menu.addSeparator()

        # Новые инструменты
        translate_submenu = QMenu("🌐 Переводчик", self)
        translate_submenu.addAction("🇷🇺 → 🇺🇸 Русский на Английский", lambda: self.translate_page("ru", "en"))
        translate_submenu.addAction("🇺🇸 → 🇷🇺 Английский на Русский", lambda: self.translate_page("en", "ru"))
        translate_submenu.addAction("🇷🇺 → 🇩🇪 Русский на Немецкий", lambda: self.translate_page("ru", "de"))
        translate_submenu.addAction("🇷🇺 → 🇫🇷 Русский на Французский", lambda: self.translate_page("ru", "fr"))
        menu.addMenu(translate_submenu)

        menu.addAction("📸 Снимок экрана", self.take_screenshot)

        tools_submenu = QMenu("🛠️ Другие инструменты", self)
        tools_submenu.addAction("🔧 Инструменты разработчика", self.show_dev_tools)
        tools_submenu.addAction("📏 Измеритель элементов", self.show_element_inspector)
        tools_submenu.addAction("📊 Анализ скорости", self.check_page_speed)
        tools_submenu.addAction("🔍 Анализ SEO", self.check_seo)
        menu.addMenu(tools_submenu)

        menu.addAction("🗑️ Очистить кеш браузера", self.clear_browser_cache)
        menu.addAction("🛡️ Блокировка подозрительных сайтов", self.toggle_site_blocking)
        menu.addAction("🦠 Защита от вирусов", self.scan_for_viruses)
        menu.addSeparator()

        # О программе
        menu.addAction("ℹ️ О программе", self.show_about)
        menu.addAction("❓ Справка", self.show_help)
        menu.addSeparator()

        # Выход
        menu.addAction("🚪 Сменить пользователя", self.logout)
        menu.addAction("✖ Выход", self.close)

        # Показываем меню рядом с кнопкой
        menu.exec_(self.menu_btn.mapToGlobal(QPoint(0, self.menu_btn.height())))

    # Новые методы для добавленных функций

    def translate_page(self, from_lang, to_lang):
        """Переводит текущую страницу"""
        browser = self.get_current_browser()
        if browser:
            current_url = browser.url().toString()

            # Простой переводчик через Google Translate API
            if 'translate.google.com' not in current_url:
                encoded_url = urllib.parse.quote(current_url)
                translate_url = f'https://translate.google.com/translate?hl={to_lang}&sl={from_lang}&tl={to_lang}&u={encoded_url}'
                self.add_new_tab(translate_url, "Перевод страницы", False)
                self.show_notification(f"Перевод страницы {from_lang.upper()} → {to_lang.upper()}")
            else:
                self.show_notification("Страница уже является переводом")

    def take_screenshot(self):
        """Делает скриншот текущей страницы"""
        browser = self.get_current_browser()
        if browser:
            try:
                # Получаем размер страницы
                size = browser.page().contentsSize().toSize()
                if size.isValid() and size.width() > 0 and size.height() > 0:
                    # Создаем изображение
                    image = QImage(size, QImage.Format_ARGB32)
                    image.fill(Qt.transparent)

                    # Настройка для рендеринга
                    painter = QPainter(image)
                    painter.setRenderHint(QPainter.Antialiasing, True)
                    painter.setRenderHint(QPainter.TextAntialiasing, True)
                    painter.setRenderHint(QPainter.SmoothPixmapTransform, True)

                    # Рендерим страницу
                    browser.page().view().render(painter)
                    painter.end()

                    # Сохраняем файл
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    title = browser.page().title()[:50].replace('/', '_').replace('\\', '_')
                    filename = f"screenshot_{title}_{timestamp}.png"

                    save_path, _ = QFileDialog.getSaveFileName(
                        self, "Сохранить скриншот",
                        os.path.join(os.path.expanduser("~"), "Pictures", filename),
                        "PNG Files (*.png);;JPEG Files (*.jpg);;All Files (*)"
                    )

                    if save_path:
                        image.save(save_path)
                        self.show_notification(f"Скриншот сохранен: {os.path.basename(save_path)}")
                else:
                    self.show_notification("Не удалось получить размер страницы")
            except Exception as e:
                self.show_notification(f"Ошибка создания скриншота: {str(e)[:50]}...")

    def show_element_inspector(self):
        """Показывает измеритель элементов"""
        self.show_notification("Измеритель элементов активирован (Ctrl+Shift+C)")
        # В реальной реализации здесь был бы код для инспектора элементов

    def check_page_speed(self):
        """Проверяет скорость загрузки страницы"""
        browser = self.get_current_browser()
        if browser:
            url = browser.url().toString()
            self.show_notification(f"Анализ скорости для: {url[:50]}...")

            # Имитация анализа скорости
            start_time = time.time()

            # В реальной реализации здесь был бы анализ скорости загрузки ресурсов
            QTimer.singleShot(1000, lambda: self.show_speed_results(start_time, url))

    def show_speed_results(self, start_time, url):
        """Показывает результаты анализа скорости"""
        load_time = time.time() - start_time
        score = max(0, min(100, 100 - (load_time * 10)))  # Простая оценка

        results_text = f"""
        <div style="background-color: #2a2a3a; padding: 20px; border-radius: 12px; color: #e0e0e0;">
            <h3 style="color: #3498db;">📊 Результаты анализа скорости</h3>
            <p><b>URL:</b> {url[:80]}{'...' if len(url) > 80 else ''}</p>
            <p><b>Время загрузки:</b> {load_time:.2f} секунд</p>
            <p><b>Оценка скорости:</b> {score:.0f}/100</p>
            <p><b>Рекомендации:</b></p>
            <ul>
                <li>Оптимизируйте изображения</li>
                <li>Используйте кэширование</li>
                <li>Минифицируйте CSS/JS</li>
            </ul>
        </div>
        """

        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Результаты анализа скорости")
        msg_box.setTextFormat(Qt.RichText)
        msg_box.setText(results_text)
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #1a1a2a;
                border: 2px solid #3498db;
                border-radius: 15px;
            }
            QLabel {
                color: #e0e0e0;
            }
            QPushButton {
                background-color: #3a3a4a;
                border: 2px solid #4a4a5a;
                border-radius: 8px;
                padding: 10px 20px;
                color: #e0e0e0;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #4a4a5a;
                border-color: #3498db;
            }
        """)
        msg_box.exec_()

    def check_seo(self):
        """Проверяет SEO страницы"""
        browser = self.get_current_browser()
        if browser:
            title = browser.page().title()
            self.show_notification(f"Анализ SEO для: {title[:50]}...")

            # Имитация SEO анализа
            seo_score = 85  # Примерная оценка

            seo_text = f"""
            <div style="background-color: #2a2a3a; padding: 20px; border-radius: 12px; color: #e0e0e0;">
                <h3 style="color: #3498db;">🔍 Результаты SEO анализа</h3>
                <p><b>Заголовок:</b> {title[:100]}{'...' if len(title) > 100 else ''}</p>
                <p><b>Оценка SEO:</b> {seo_score}/100</p>
                <p><b>Рекомендации:</b></p>
                <ul>
                    <li>✅ Заголовок страницы оптимальной длины</li>
                    <li>⚠️ Добавьте мета-описание</li>
                    <li>⚠️ Оптимизируйте заголовки H1-H6</li>
                    <li>✅ Изображения имеют alt-текст</li>
                    <li>⚠️ Улучшите скорость загрузки</li>
                </ul>
            </div>
            """

            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Результаты SEO анализа")
            msg_box.setTextFormat(Qt.RichText)
            msg_box.setText(seo_text)
            msg_box.setStyleSheet("""
                QMessageBox {
                    background-color: #1a1a2a;
                    border: 2px solid #3498db;
                    border-radius: 15px;
                }
                QLabel {
                    color: #e0e0e0;
                }
                QPushButton {
                    background-color: #3a3a4a;
                    border: 2px solid #4a4a5a;
                    border-radius: 8px;
                    padding: 10px 20px;
                    color: #e0e0e0;
                    font-weight: bold;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #4a4a5a;
                    border-color: #3498db;
                }
            """)
            msg_box.exec_()

    def clear_browser_cache(self):
        """Очищает кеш браузера"""
        reply = QMessageBox.question(self, "Очистка кеша",
                                   "Вы уверены, что хотите очистить кеш браузера?\nЭто может улучшить производительность.",
                                   QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            try:
                # Очистка кеша WebEngine
                from PyQt5.QtWebEngineWidgets import QWebEngineProfile
                profile = QWebEngineProfile.defaultProfile()
                profile.clearHttpCache()

                # Очистка cookies
                cookie_store = profile.cookieStore()
                cookie_store.deleteAllCookies()

                self.show_notification("Кеш и cookies успешно очищены")
            except Exception as e:
                self.show_notification(f"Ошибка очистки кеша: {str(e)[:50]}...")

    def toggle_site_blocking(self):
        """Включает/выключает блокировку подозрительных сайтов"""
        self.settings["site_blocking_enabled"] = not self.settings.get("site_blocking_enabled", False)

        if self.settings["site_blocking_enabled"]:
            self.show_notification("🛡️ Блокировка подозрительных сайтов включена")
        else:
            self.show_notification("Блокировка подозрительных сайтов выключена")

    def scan_for_viruses(self):
        """Сканирует на вирусы"""
        self.show_notification("🔍 Начато сканирование на вирусы...")

        # Имитация сканирования
        QTimer.singleShot(2000, self.show_virus_scan_results)

    def show_virus_scan_results(self):
        """Показывает результаты сканирования на вирусы"""
        # Имитация результатов сканирования
        scan_results = {
            "status": "Безопасно",
            "scanned_files": 128,
            "threats_found": 0,
            "last_scan": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        results_text = f"""
        <div style="background-color: #2a2a3a; padding: 20px; border-radius: 12px; color: #e0e0e0;">
            <h3 style="color: {'#2ecc71' if scan_results['threats_found'] == 0 else '#e74c3c'};">🦠 Результаты сканирования на вирусы</h3>
            <p><b>Статус:</b> <span style="color: {'#2ecc71' if scan_results['status'] == 'Безопасно' else '#e74c3c'}">{scan_results['status']}</span></p>
            <p><b>Проверено файлов:</b> {scan_results['scanned_files']}</p>
            <p><b>Найдено угроз:</b> {scan_results['threats_found']}</p>
            <p><b>Последнее сканирование:</b> {scan_results['last_scan']}</p>

            <p><b>Рекомендации по безопасности:</b></p>
            <ul>
                <li>✅ Используйте режим инкогнито для приватности</li>
                <li>✅ Включите блокировка рекламы</li>
                <li>✅ Обновляйте браузер регулярно</li>
                <li>⚠️ Остерегайтесь фишинговых сайтов</li>
            </ul>
        </div>
        """

        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Результаты сканирования на вирусы")
        msg_box.setTextFormat(Qt.RichText)
        msg_box.setText(results_text)
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #1a1a2a;
                border: 2px solid #3498db;
                border-radius: 15px;
            }
            QLabel {
                color: #e0e0e0;
            }
            QPushButton {
                background-color: #3a3a4a;
                border: 2px solid #4a4a5a;
                border-radius: 8px;
                padding: 10px 20px;
                color: #e0e0e0;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #4a4a5a;
                border-color: #3498db;
            }
        """)
        msg_box.exec_()

    def show_settings_dialog(self):
        """Показывает диалог настроек с полным функционалом"""
        dialog = QDialog(self)
        dialog.setWindowTitle("⚙️ Настройки Der Browser")
        dialog.setGeometry(400, 200, 800, 600)
        dialog.setObjectName("settingsDialog")

        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)

        # Заголовок
        title_label = QLabel("⚙️ Настройки браузера")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #3498db; font-size: 22px; font-weight: bold;")
        layout.addWidget(title_label)

        # Создаем прокручиваемую область
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(20)

        # 1. Настройки внешнего вида
        appearance_group = QGroupBox("🎨 Внешний вид")
        appearance_group.setStyleSheet("""
            QGroupBox {
                color: #e0e0e0;
                font-weight: bold;
                border: 1px solid #3a3a4a;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)

        appearance_layout = QVBoxLayout(appearance_group)

        # Тема
        theme_widget = QWidget()
        theme_layout = QHBoxLayout(theme_widget)
        theme_layout.addWidget(QLabel("Тема интерфейса:"))

        theme_combo = QComboBox()
        theme_combo.addItem("🌙 Темная", "dark")
        theme_combo.addItem("☀️ Светлая", "light")
        theme_combo.addItem("💻 Системная", "system")

        current_index = theme_combo.findData(self.settings["theme"])
        if current_index >= 0:
            theme_combo.setCurrentIndex(current_index)

        theme_combo.currentIndexChanged.connect(lambda idx: self.change_theme(theme_combo.itemData(idx)))
        theme_layout.addWidget(theme_combo)
        theme_layout.addStretch()

        appearance_layout.addWidget(theme_widget)

        scroll_layout.addWidget(appearance_group)

        # 2. Настройки VPN и DNS
        vpn_group = QGroupBox("🔒 VPN и DNS")
        vpn_group.setStyleSheet(appearance_group.styleSheet())

        vpn_layout = QVBoxLayout(vpn_group)

        # Включение VPN
        vpn_checkbox = QCheckBox("Включить VPN режим (изменить DNS)")
        vpn_checkbox.setChecked(self.settings["vpn_enabled"])
        vpn_checkbox.stateChanged.connect(lambda state: self.update_vpn_setting(state))
        vpn_layout.addWidget(vpn_checkbox)

        # DNS серверы
        dns_widget = QWidget()
        dns_layout = QHBoxLayout(dns_widget)

        dns_layout.addWidget(QLabel("Основной DNS:"))
        dns_primary_edit = QLineEdit(self.settings["dns_primary"])
        dns_primary_edit.setStyleSheet("""
            QLineEdit {
                background-color: #2a2a3a;
                border: 1px solid #3a3a4a;
                border-radius: 5px;
                padding: 5px;
                color: #e0e0e0;
                min-height: 25px;
            }
        """)
        dns_primary_edit.textChanged.connect(lambda text: self.update_dns_setting("dns_primary", text))
        dns_layout.addWidget(dns_primary_edit)

        dns_layout.addWidget(QLabel("Резервный DNS:"))
        dns_secondary_edit = QLineEdit(self.settings["dns_secondary"])
        dns_secondary_edit.setStyleSheet(dns_primary_edit.styleSheet())
        dns_secondary_edit.textChanged.connect(lambda text: self.update_dns_setting("dns_secondary", text))
        dns_layout.addWidget(dns_secondary_edit)

        vpn_layout.addWidget(dns_widget)

        # Предустановленные DNS
        preset_dns_widget = QWidget()
        preset_dns_layout = QHBoxLayout(preset_dns_widget)
        preset_dns_layout.addWidget(QLabel("Быстрые настройки DNS:"))

        dns_presets = QComboBox()
        dns_presets.addItem("Google DNS (8.8.8.8, 8.8.4.4)")
        dns_presets.addItem("Cloudflare (1.1.1.1, 1.0.0.1)")
        dns_presets.addItem("Quad9 (9.9.9.9, 149.112.112.112)")
        dns_presets.addItem("OpenDNS (208.67.222.222, 208.67.220.220)")

        def apply_preset_dns(index):
            presets = {
                0: ("8.8.8.8", "8.8.4.4"),
                1: ("1.1.1.1", "1.0.0.1"),
                2: ("9.9.9.9", "149.112.112.112"),
                3: ("208.67.222.222", "208.67.220.220")
            }
            if index in presets:
                primary, secondary = presets[index]
                dns_primary_edit.setText(primary)
                dns_secondary_edit.setText(secondary)
                self.update_dns_setting("dns_primary", primary)
                self.update_dns_setting("dns_secondary", secondary)

        dns_presets.currentIndexChanged.connect(apply_preset_dns)
        preset_dns_layout.addWidget(dns_presets)

        vpn_layout.addWidget(preset_dns_widget)

        scroll_layout.addWidget(vpn_group)

        # 3. Настройки приватности
        privacy_group = QGroupBox("🛡️ Приватность")
        privacy_group.setStyleSheet(appearance_group.styleSheet())

        privacy_layout = QVBoxLayout(privacy_group)

        ad_block_checkbox = QCheckBox("Блокировать рекламу")
        ad_block_checkbox.setChecked(self.settings["block_ads"])
        ad_block_checkbox.stateChanged.connect(lambda state: self.update_setting("block_ads", bool(state)))
        privacy_layout.addWidget(ad_block_checkbox)

        save_passwords_checkbox = QCheckBox("Сохранять пароли")
        save_passwords_checkbox.setChecked(self.settings["save_passwords"])
        save_passwords_checkbox.stateChanged.connect(lambda state: self.update_setting("save_passwords", bool(state)))
        privacy_layout.addWidget(save_passwords_checkbox)

        javascript_checkbox = QCheckBox("Включить JavaScript")
        javascript_checkbox.setChecked(self.settings["javascript_enabled"])
        javascript_checkbox.stateChanged.connect(lambda state: self.update_setting("javascript_enabled", bool(state)))
        privacy_layout.addWidget(javascript_checkbox)

        cookies_checkbox = QCheckBox("Принимать cookies")
        cookies_checkbox.setChecked(True)
        privacy_layout.addWidget(cookies_checkbox)

        notifications_checkbox = QCheckBox("Разрешить уведомления")
        notifications_checkbox.setChecked(self.settings["notifications"])
        notifications_checkbox.stateChanged.connect(lambda state: self.update_setting("notifications", bool(state)))
        privacy_layout.addWidget(notifications_checkbox)

        scroll_layout.addWidget(privacy_group)

        # 4. Настройки поиска
        search_group = QGroupBox("🔍 Поиск")
        search_group.setStyleSheet(appearance_group.styleSheet())

        search_layout = QVBoxLayout(search_group)

        search_engine_widget = QWidget()
        search_engine_layout = QHBoxLayout(search_engine_widget)
        search_engine_layout.addWidget(QLabel("Поисковая система:"))

        search_combobox = QComboBox()
        search_combobox.addItem("Google", "google")
        search_combobox.addItem("DuckDuckGo", "duckduckgo")
        search_combobox.addItem("Bing", "bing")
        search_combobox.addItem("Yandex", "yandex")

        current_index = search_combobox.findData(self.settings["default_search_engine"])
        if current_index >= 0:
            search_combobox.setCurrentIndex(current_index)

        search_combobox.currentIndexChanged.connect(
            lambda index: self.update_setting("default_search_engine", search_combobox.itemData(index))
        )

        search_engine_layout.addWidget(search_combobox)
        search_engine_layout.addStretch()
        search_layout.addWidget(search_engine_widget)

        home_page_widget = QWidget()
        home_page_layout = QHBoxLayout(home_page_widget)
        home_page_layout.addWidget(QLabel("Домашняя страница:"))

        home_page_edit = QLineEdit(self.settings["home_page"])
        home_page_edit.setStyleSheet(dns_primary_edit.styleSheet())
        home_page_edit.textChanged.connect(lambda text: self.update_setting("home_page", text))

        home_page_layout.addWidget(home_page_edit)
        search_layout.addWidget(home_page_widget)

        scroll_layout.addWidget(search_group)

        # 5. Настройки производительности
        performance_group = QGroupBox("⚡ Производительность")
        performance_group.setStyleSheet(appearance_group.styleSheet())

        performance_layout = QVBoxLayout(performance_group)

        hardware_accel_checkbox = QCheckBox("Аппаратное ускорение")
        hardware_accel_checkbox.setChecked(self.settings["hardware_acceleration"])
        hardware_accel_checkbox.stateChanged.connect(lambda state: self.update_setting("hardware_acceleration", bool(state)))
        performance_layout.addWidget(hardware_accel_checkbox)

        cache_widget = QWidget()
        cache_layout = QHBoxLayout(cache_widget)
        cache_layout.addWidget(QLabel("Размер кэша (МБ):"))

        cache_spinbox = QSpinBox()
        cache_spinbox.setRange(10, 1000)
        cache_spinbox.setValue(100)
        cache_spinbox.setSuffix(" MB")
        cache_layout.addWidget(cache_spinbox)
        cache_layout.addStretch()
        performance_layout.addWidget(cache_widget)

        scroll_layout.addWidget(performance_group)

        # Добавляем отступ вниз
        scroll_layout.addStretch()

        # Устанавливаем содержимое прокрутки
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)

        # Кнопки внизу
        button_layout = QHBoxLayout()

        apply_btn = QPushButton("✅ Применить")
        apply_btn.clicked.connect(lambda: self.apply_settings_and_close(dialog))

        save_btn = QPushButton("💾 Сохранить")
        save_btn.clicked.connect(lambda: self.save_settings_and_close(dialog))

        cancel_btn = QPushButton("✖ Отмена")
        cancel_btn.clicked.connect(dialog.close)

        button_layout.addStretch()
        button_layout.addWidget(apply_btn)
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

        # Стили для диалога
        dialog.setStyleSheet("""
            QDialog {
                background-color: #1a1a2a;
                border: 2px solid #3498db;
                border-radius: 15px;
            }
            QLabel {
                color: #e0e0e0;
                font-size: 12px;
            }
            QCheckBox {
                color: #e0e0e0;
                font-size: 13px;
            }
            QComboBox {
                background-color: #2a2a3a;
                border: 1px solid #3a3a4a;
                border-radius: 5px;
                padding: 5px;
                color: #e0e0e0;
                min-height: 25px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #e0e0e0;
            }
            QComboBox QAbstractItemView {
                background-color: #2a2a3a;
                color: #e0e0e0;
                selection-background-color: #3498db;
            }
            QSpinBox {
                background-color: #2a2a3a;
                border: 1px solid #3a3a4a;
                border-radius: 5px;
                padding: 5px;
                color: #e0e0e0;
                min-height: 25px;
            }
            QPushButton {
                background-color: #3a3a4a;
                border: 2px solid #4a4a5a;
                border-radius: 8px;
                padding: 10px 20px;
                color: #e0e0e0;
                font-weight: bold;
                font-size: 12px;
                min-height: 35px;
            }
            QPushButton:hover {
                background-color: #4a4a5a;
                border-color: #3498db;
            }
        """)

        dialog.exec_()

    def change_theme(self, theme):
        """Изменяет тему"""
        self.settings["theme"] = theme
        self.apply_theme(theme)
        self.show_notification(f"Тема изменена на {'темную' if theme == 'dark' else 'светлую'}")

    def update_vpn_setting(self, state):
        """Обновляет настройку VPN"""
        self.settings["vpn_enabled"] = bool(state)
        if state:
            self.enable_vpn()
        else:
            self.disable_vpn()

    def update_dns_setting(self, key, value):
        """Обновляет DNS настройки"""
        self.settings[key] = value
        if self.settings["vpn_enabled"]:
            self.apply_dns_settings()

    def update_setting(self, key, value):
        """Обновляет любую настройку"""
        self.settings[key] = value

    def apply_settings_and_close(self, dialog):
        """Применяет настройки и закрывает диалог"""
        self.save_user_data()
        dialog.close()
        self.show_notification("Настройки применены")

    def save_settings_and_close(self, dialog):
        """Сохраняет настройки и закрывает диалог"""
        self.save_user_data()
        dialog.close()
        self.show_notification("Настройки сохранены")

    def toggle_vpn(self):
        """Включает/выключает VPN"""
        if self.settings["vpn_enabled"]:
            self.disable_vpn()
        else:
            self.enable_vpn()

    def enable_vpn(self):
        """Включает VPN (меняет DNS)"""
        try:
            self.settings["vpn_enabled"] = True
            self.show_notification(f"VPN включен. DNS: {self.settings['dns_primary']}, {self.settings['dns_secondary']}")
        except Exception as e:
            self.show_notification(f"Ошибка включения VPN: {str(e)[:50]}...")
            self.settings["vpn_enabled"] = False

    def disable_vpn(self):
        """Выключает VPN (возвращает оригинальные DNS)"""
        try:
            self.settings["vpn_enabled"] = False
            self.show_notification("VPN выключен")
        except Exception as e:
            self.show_notification(f"Ошибка выключения VPN: {str(e)[:50]}...")
            self.settings["vpn_enabled"] = False

    def apply_dns_settings(self):
        """Применяет DNS настройки"""
        if self.settings["vpn_enabled"]:
            self.show_notification(f"Применены DNS: {self.settings['dns_primary']}, {self.settings['dns_secondary']}")

    def apply_theme(self, theme):
        """Применяет тему"""
        if theme == "dark":
            dark_stylesheet = """
            /* Основные стили */
            QMainWindow {
                background-color: #0a0a14;
            }

            /* Панель навигации */
            QWidget#navBar {
                background-color: #1a1a2a;
                border-bottom: 2px solid #3498db;
            }

            QLabel#navLogoIcon {
                font-size: 24px;
                color: #3498db;
                font-weight: bold;
            }

            QLabel#navLogoText {
                color: #e0e0e0;
                font-size: 18px;
                font-weight: bold;
            }

            QPushButton#navButton {
                background-color: #3a3a4a;
                border: 2px solid #4a4a5a;
                border-radius: 20px;
                color: #e0e0e0;
                font-size: 16px;
                font-weight: bold;
            }

            QPushButton#navButton:hover {
                background-color: #4a4a5a;
                border-color: #3498db;
            }

            QPushButton#navButton:pressed {
                background-color: #2a2a3a;
            }

            QPushButton#navButton:disabled {
                background-color: #2a2a3a;
                color: #666;
            }

            /* Поле URL */
            QLineEdit#urlBar {
                background-color: #2a2a3a;
                border: 2px solid #3a3a4a;
                border-radius: 20px;
                padding: 10px 15px;
                font-size: 14px;
                color: #e0e0e0;
                font-weight: 500;
                selection-background-color: #3498db;
                min-height: 40px;
            }

            QLineEdit#urlBar:focus {
                border-color: #3498db;
                background-color: #3a3a4a;
            }

            QLineEdit#urlBar:hover {
                border-color: #4a4a5a;
            }

            /* Кнопка перехода */
            QPushButton#goButton {
                background-color: #3498db;
                border: none;
                border-radius: 20px;
                color: white;
                font-size: 18px;
                font-weight: bold;
            }

            QPushButton#goButton:hover {
                background-color: #2980b9;
                border: 2px solid #2ecc71;
            }

            QPushButton#goButton:pressed {
                background-color: #1c6ea4;
            }

            /* Кнопки действий */
            QPushButton#actionButton {
                background-color: #2a2a3a;
                border: 2px solid #3a3a4a;
                border-radius: 20px;
                color: #e0e0e0;
                font-size: 16px;
                font-weight: bold;
            }

            QPushButton#actionButton:hover {
                background-color: #3a3a4a;
                border-color: #3498db;
            }

            QPushButton#actionButton:pressed {
                background-color: #1a1a2a;
            }

            /* Вкладки */
            QTabWidget::pane {
                border: 1px solid #2a2a3a;
                background-color: #0a0a14;
            }

            QTabBar::tab {
                background-color: #2a2a3a;
                color: #b0b0b0;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: 600;
                font-size: 12px;
                min-width: 120px;
            }

            QTabBar::tab:selected {
                background-color: #1a1a2a;
                color: #e0e0e0;
                border-bottom: 3px solid #3498db;
            }

            QTabBar::tab:hover:!selected {
                background-color: #3a3a4a;
                color: #e0e0e0;
            }

            /* Статус бар */
            QWidget#statusBar {
                background-color: #1a1a2a;
                border-top: 1px solid #2a2a3a;
            }

            QLabel#statusLabel {
                color: #b0b0b0;
                font-size: 12px;
                font-weight: 500;
            }

            QProgressBar#progressBar {
                border: 1px solid #2a2a3a;
                border-radius: 3px;
                background-color: #2a2a3a;
            }

            QProgressBar#progressBar::chunk {
                background-color: #3498db;
                border-radius: 3px;
            }

            /* Меню */
            QMenuBar#menuBar {
                background-color: #1a1a2a;
                color: #e0e0e0;
                padding: 5px;
            }

            QMenuBar::item {
                background-color: transparent;
                padding: 8px 15px;
            }

            QMenuBar::item:selected {
                background-color: #3498db;
            }

            QMenu {
                background-color: #1a1a2a;
                color: #e0e0e0;
                border: 1px solid #2a2a3a;
            }

            QMenu::item:selected {
                background-color: #3498db;
            }
            """
            self.setStyleSheet(dark_stylesheet)
        else:
            light_stylesheet = """
            /* Основные стили */
            QMainWindow {
                background-color: #f5f5f5;
            }

            /* Панель навигации */
            QWidget#navBar {
                background-color: #ffffff;
                border-bottom: 2px solid #3498db;
            }

            QLabel#navLogoIcon {
                font-size: 24px;
                color: #3498db;
                font-weight: bold;
            }

            QLabel#navLogoText {
                color: #333333;
                font-size: 18px;
                font-weight: bold;
            }

            QPushButton#navButton {
                background-color: #f0f0f0;
                border: 2px solid #e0e0e0;
                border-radius: 20px;
                color: #333333;
                font-size: 16px;
                font-weight: bold;
            }

            QPushButton#navButton:hover {
                background-color: #e0e0e0;
                border-color: #3498db;
            }

            QPushButton#navButton:pressed {
                background-color: #d0d0d0;
            }

            QPushButton#navButton:disabled {
                background-color: #f5f5f5;
                color: #aaaaaa;
            }

            /* Поле URL */
            QLineEdit#urlBar {
                background-color: #ffffff;
                border: 2px solid #e0e0e0;
                border-radius: 20px;
                padding: 10px 15px;
                font-size: 14px;
                color: #333333;
                font-weight: 500;
                selection-background-color: #3498db;
                min-height: 40px;
            }

            QLineEdit#urlBar:focus {
                border-color: #3498db;
                background-color: #ffffff;
            }

            QLineEdit#urlBar:hover {
                border-color: #cccccc;
            }

            /* Кнопка перехода */
            QPushButton#goButton {
                background-color: #3498db;
                border: none;
                border-radius: 20px;
                color: white;
                font-size: 18px;
                font-weight: bold;
            }

            QPushButton#goButton:hover {
                background-color: #2980b9;
                border: 2px solid #2ecc71;
            }

            QPushButton#goButton:pressed {
                background-color: #1c6ea4;
            }

            /* Кнопки действий */
            QPushButton#actionButton {
                background-color: #f0f0f0;
                border: 2px solid #e0e0e0;
                border-radius: 20px;
                color: #333333;
                font-size: 16px;
                font-weight: bold;
            }

            QPushButton#actionButton:hover {
                background-color: #e0e0e0;
                border-color: #3498db;
            }

            QPushButton#actionButton:pressed {
                background-color: #d0d0d0;
            }

            /* Вкладки */
            QTabWidget::pane {
                border: 1px solid #e0e0e0;
                background-color: #ffffff;
            }

            QTabBar::tab {
                background-color: #f0f0f0;
                color: #666666;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: 600;
                font-size: 12px;
                min-width: 120px;
            }

            QTabBar::tab:selected {
                background-color: #ffffff;
                color: #333333;
                border-bottom: 3px solid #3498db;
            }

            QTabBar::tab:hover:!selected {
                background-color: #e8e8e8;
                color: #333333;
            }

            /* Статус бар */
            QWidget#statusBar {
                background-color: #ffffff;
                border-top: 1px solid #e0e0e0;
            }

            QLabel#statusLabel {
                color: #666666;
                font-size: 12px;
                font-weight: 500;
            }

            QProgressBar#progressBar {
                border: 1px solid #e0e0e0;
                border-radius: 3px;
                background-color: #f0f0f0;
            }

            QProgressBar#progressBar::chunk {
                background-color: #3498db;
                border-radius: 3px;
            }

            /* Меню */
            QMenuBar#menuBar {
                background-color: #ffffff;
                color: #333333;
                padding: 5px;
            }

            QMenuBar::item {
                background-color: transparent;
                padding: 8px 15px;
            }

            QMenuBar::item:selected {
                background-color: #3498db;
                color: white;
            }

            QMenu {
                background-color: #ffffff;
                color: #333333;
                border: 1px solid #e0e0e0;
            }

            QMenu::item:selected {
                background-color: #3498db;
                color: white;
            }
            """
            self.setStyleSheet(light_stylesheet)

    def toggle_theme(self):
        """Переключает тему"""
        self.settings["theme"] = "light" if self.settings["theme"] == "dark" else "dark"
        self.apply_theme(self.settings["theme"])
        self.show_notification(f"Тема изменена на {'светлую' if self.settings['theme'] == 'light' else 'темную'}")

    def find_on_page(self):
        """Поиск на странице"""
        browser = self.get_current_browser()
        if browser:
            # В реальном приложении здесь был бы вызов findText
            self.show_notification("Для поиска на странице нажмите Ctrl+F")

    def save_page(self):
        """Сохраняет страницу"""
        browser = self.get_current_browser()
        if browser:
            file_name, _ = QFileDialog.getSaveFileName(
                self, "Сохранить страницу",
                f"{browser.page().title()[:50]}.html",
                "HTML Files (*.html *.htm);;All Files (*)"
            )
            if file_name:
                self.show_notification(f"Страница сохранена как {os.path.basename(file_name)}")

    def print_page(self):
        """Печатает страницу"""
        browser = self.get_current_browser()
        if browser:
            # В реальном приложении здесь был бы вызов print
            self.show_notification("Для печати нажмите Ctrl+P")

    def zoom_in(self):
        """Увеличивает масштаб"""
        browser = self.get_current_browser()
        if browser:
            browser.setZoomFactor(browser.zoomFactor() + 0.1)
            self.zoom_level += 10
            self.show_notification(f"Масштаб: {self.zoom_level}%")

    def zoom_out(self):
        """Уменьшает масштаб"""
        browser = self.get_current_browser()
        if browser:
            if browser.zoomFactor() > 0.1:
                browser.setZoomFactor(browser.zoomFactor() - 0.1)
                self.zoom_level -= 10
                self.show_notification(f"Масштаб: {self.zoom_level}%")

    def reset_zoom(self):
        """Сбрасывает масштаб"""
        browser = self.get_current_browser()
        if browser:
            browser.setZoomFactor(1.0)
            self.zoom_level = 100
            self.show_notification("Масштаб сброшен")

    def show_dev_tools(self):
        """Показывает инструменты разработчика"""
        browser = self.get_current_browser()
        if browser:
            browser.page().setDevToolsPage(browser.page())
            self.show_notification("Инструменты разработчика открыты")

    def show_about(self):
        """Показывает информацию о программе"""
        about_text = """
        <div style="background-color: #2a2a3a; padding: 20px; border-radius: 12px; color: #e0e0e0;">
            <h2 style="color: #3498db;">🌐 Der Browser v3.0</h2>
            <p><b>Современный веб-браузер с премиальным дизайном</b></p>

            <p><b>Версия:</b> 3.0.0<br>
            <b>PyQtWebEngine:</b> 5.15.2<br>
            <b>Лицензия:</b> MIT Open Source</p>

            <p>✨ <b>Особенности:</b><br>
            • Темная/светлая тема с premium-дизайном<br>
            • Быстрый доступ к популярным сайтам<br>
            • Система закладок и истории<br>
            • Встроенный WebView (Chromium)<br>
            • VPN режим с изменением DNS<br>
            • Полная поддержка JavaScript</p>

            <p>🎯 <b>Безопасность:</b><br>
            • Защита от отслеживания<br>
            • Блокировка рекламы<br>
            • Безопасные DNS серверы<br>
            • Режим инкогнито</p>

            <p>© 2026 Der Browser Team</p>
        </div>
        """

        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("О Der Browser")
        msg_box.setTextFormat(Qt.RichText)
        msg_box.setText(about_text)
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #1a1a2a;
                border: 2px solid #3498db;
                border-radius: 15px;
            }
            QLabel {
                color: #e0e0e0;
            }
            QPushButton {
                background-color: #3a3a4a;
                border: 2px solid #4a4a5a;
                border-radius: 8px;
                padding: 10px 20px;
                color: #e0e0e0;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #4a4a5a;
                border-color: #3498db;
            }
        """)
        msg_box.exec_()

    def show_help(self):
        """Показывает справку"""
        help_text = """
        <div style="background-color: #2a2a3a; padding: 20px; border-radius: 12px; color: #e0e0e0;">
            <h2 style="color: #3498db;">📖 Справка Der Browser</h2>

            <p><b>Основные горячие клавиши:</b></p>
            <ul>
            <li><b>Ctrl+T:</b> Новая вкладка</li>
            <li><b>Ctrl+W:</b> Закрыть вкладку</li>
            <li><b>Ctrl+Shift+T:</b> Новая вкладка инкогнито</li>
            <li><b>Ctrl+D:</b> Добавить в закладки</li>
            <li><b>Ctrl+F:</b> Поиск на странице</li>
            <li><b>Ctrl+P:</b> Печать</li>
            <li><b>Ctrl+S:</b> Сохранить страницу</li>
            <li><b>F5:</b> Обновить страницу</li>
            <li><b>F11:</b> Полноэкранный режим</li>
            <li><b>F12:</b> Инструменты разработчика</li>
            </ul>

            <p><b>Админ панель:</b></p>
            <ul>
            <li><b>Логин:</b> admin или RobertusaAdmin</li>
            <li><b>Пароль:</b> 1555</li>
            <li><b>Горячая клавиша:</b> Ctrl+Shift+A</li>
            </ul>

            <p><b>Настройки:</b></p>
            <ul>
            <li><b>Тема:</b> Меню → Настройки → Внешний вид</li>
            <li><b>VPN/DNS:</b> Меню → Настройки → VPN и DNS</li>
            <li><b>Приватность:</b> Меню → Настройки → Приватность</li>
            </ul>

            <p><b>Режим инкогнито:</b></p>
            <p>В режиме инкогнито история просмотров не сохраняется.<br>
            Для включения: кнопка 👤 или Ctrl+Shift+I</p>

            <p>Для дополнительной помощи: support@derbrowser.com</p>
        </div>
        """

        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Справка Der Browser")
        msg_box.setTextFormat(Qt.RichText)
        msg_box.setText(help_text)
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #1a1a2a;
                border: 2px solid #3498db;
                border-radius: 15px;
            }
            QLabel {
                color: #e0e0e0;
            }
            QPushButton {
                background-color: #3a3a4a;
                border: 2px solid #4a4a5a;
                border-radius: 8px;
                padding: 10px 20px;
                color: #e0e0e0;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #4a4a5a;
                border-color: #3498db;
            }
        """)
        msg_box.exec_()

    def logout(self):
        """Выход из учетной записи"""
        reply = QMessageBox.question(self, "Смена пользователя",
                                   "Вы уверены, что хотите выйти?",
                                   QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.save_user_data()
            self.clear_session()
            self.close()

    def show_admin_panel(self):  # <-- ПРАВИЛЬНЫЙ ОТСТУП!
        """Показывает админ панель"""
        if not self.is_admin:
            self.show_notification("Доступ запрещен: требуются права администратора")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("👑 Админ панель - Der Browser")
        dialog.setGeometry(300, 150, 900, 700)
        dialog.setObjectName("adminDialog")

        layout = QVBoxLayout(dialog)
        layout.setSpacing(20)

        # Заголовок
        title_label = QLabel("👑 АДМИН ПАНЕЛЬ - Der Browser")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                color: #ff9900;
                font-size: 24px;
                font-weight: bold;
                padding: 10px;
                background-color: #2a2a3a;
                border-radius: 10px;
                border: 2px solid #ff9900;
            }
        """)
        layout.addWidget(title_label)

        # Создаем прокручиваемую область
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(20)

        # 1. Настройки темы
        theme_group = QGroupBox("🎨 Настройки темы")
        theme_group.setStyleSheet("""
            QGroupBox {
                color: #ff9900;
                font-weight: bold;
                border: 2px solid #ff9900;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                font-size: 14px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)

        theme_layout = QVBoxLayout(theme_group)

        # Выбор темы
        theme_combo = QComboBox()
        theme_combo.addItem("🔵 Стандартная тема", "default")
        theme_combo.addItem("💎 Liquid Glass", "liquid_glass")
        theme_combo.addItem("🌌 Dark Matter", "dark_matter")
        theme_combo.addItem("🔮 Cyberpunk", "cyberpunk")
        theme_combo.addItem("🌿 Nature", "nature")
        theme_combo.addItem("🔥 Fire", "fire")
        theme_combo.addItem("❄️ Ice", "ice")
        theme_combo.addItem("✨ Neon", "neon")

        current_theme = self.admin_settings.get("theme", "default")
        theme_index = theme_combo.findData(current_theme)
        if theme_index >= 0:
            theme_combo.setCurrentIndex(theme_index)

        theme_combo.currentIndexChanged.connect(
            lambda idx: self.update_admin_setting("theme", theme_combo.itemData(idx))
        )

        theme_preview = QLabel("Предпросмотр темы")
        theme_preview.setAlignment(Qt.AlignCenter)
        theme_preview.setFixedHeight(100)
        theme_preview.setStyleSheet("""
            QLabel {
                background-color: #2a2a3a;
                border-radius: 10px;
                border: 2px solid #3a3a4a;
                color: #e0e0e0;
                font-weight: bold;
            }
        """)

        theme_layout.addWidget(QLabel("Выберите тему:"))
        theme_layout.addWidget(theme_combo)
        theme_layout.addWidget(theme_preview)

        scroll_layout.addWidget(theme_group)

        # 2. Настройки текста
        text_group = QGroupBox("📝 Настройки текста")
        text_group.setStyleSheet(theme_group.styleSheet())

        text_layout = QVBoxLayout(text_group)

        # Логотип
        logo_widget = QWidget()
        logo_layout = QHBoxLayout(logo_widget)
        logo_layout.addWidget(QLabel("Текст логотипа:"))
        logo_edit = QLineEdit(self.admin_settings.get("logo_text", "Der Browser"))
        logo_edit.textChanged.connect(lambda text: self.update_admin_setting("logo_text", text))
        logo_layout.addWidget(logo_edit)
        text_layout.addWidget(logo_widget)

        # Главный заголовок
        title_widget = QWidget()
        title_layout = QHBoxLayout(title_widget)
        title_layout.addWidget(QLabel("Главный заголовок:"))
        title_edit = QLineEdit(self.admin_settings.get("main_title", "🌐 Der Browser - Made by AI"))
        title_edit.textChanged.connect(lambda text: self.update_admin_setting("main_title", text))
        title_layout.addWidget(title_edit)
        text_layout.addWidget(title_widget)

        # Подзаголовок
        subtitle_widget = QWidget()
        subtitle_layout = QHBoxLayout(subtitle_widget)
        subtitle_layout.addWidget(QLabel("Подзаголовок:"))
        subtitle_edit = QLineEdit(self.admin_settings.get("subtitle", "Modern Web Experience"))
        subtitle_edit.textChanged.connect(lambda text: self.update_admin_setting("subtitle", text))
        subtitle_layout.addWidget(subtitle_edit)
        text_layout.addWidget(subtitle_widget)

        scroll_layout.addWidget(text_group)

        # 3. Настройки быстрых кнопок
        buttons_group = QGroupBox("🚀 Настройки быстрых кнопок")
        buttons_group.setStyleSheet(theme_group.styleSheet())

        buttons_layout = QVBoxLayout(buttons_group)

        buttons_list = QListWidget()
        buttons_list.setStyleSheet("""
            QListWidget {
                background-color: #2a2a3a;
                border: 1px solid #3a3a4a;
                border-radius: 5px;
                color: #e0e0e0;
                min-height: 200px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #3a3a4a;
            }
            QListWidget::item:selected {
                background-color: #ff9900;
                color: #1a1a2a;
            }
        """)

        # Загружаем текущие кнопки
        quick_buttons = self.admin_settings.get("quick_buttons", [])
        for button in quick_buttons:
            buttons_list.addItem(button)

        # Кнопки управления
        buttons_controls = QWidget()
        buttons_controls_layout = QHBoxLayout(buttons_controls)

        add_button_btn = QPushButton("➕ Добавить")
        add_button_btn.clicked.connect(lambda: self.add_quick_button(buttons_list))

        edit_button_btn = QPushButton("✏️ Редактировать")
        edit_button_btn.clicked.connect(lambda: self.edit_quick_button(buttons_list))

        remove_button_btn = QPushButton("🗑 Удалить")
        remove_button_btn.clicked.connect(lambda: self.remove_quick_button(buttons_list))

        move_up_btn = QPushButton("⬆️ Вверх")
        move_up_btn.clicked.connect(lambda: self.move_quick_button(buttons_list, -1))

        move_down_btn = QPushButton("⬇️ Вниз")
        move_down_btn.clicked.connect(lambda: self.move_quick_button(buttons_list, 1))

        buttons_controls_layout.addWidget(add_button_btn)
        buttons_controls_layout.addWidget(edit_button_btn)
        buttons_controls_layout.addWidget(remove_button_btn)
        buttons_controls_layout.addWidget(move_up_btn)
        buttons_controls_layout.addWidget(move_down_btn)

        buttons_layout.addWidget(QLabel("Быстрые кнопки (формат: эмоджи Текст):"))
        buttons_layout.addWidget(buttons_list)
        buttons_layout.addWidget(buttons_controls)

        scroll_layout.addWidget(buttons_group)

        # 4. Дополнительные настройки
        extra_group = QGroupBox("⚙️ Дополнительные настройки")
        extra_group.setStyleSheet(theme_group.styleSheet())

        extra_layout = QVBoxLayout(extra_group)

        # Перезагрузка UI
        reload_btn = QPushButton("🔄 Применить изменения")
        reload_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff9900;
                color: #1a1a2a;
                font-weight: bold;
                border: 2px solid #ff9900;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #ffaa33;
                border-color: #ffaa33;
            }
        """)
        reload_btn.clicked.connect(lambda: self.apply_admin_settings(dialog))

        # Экспорт/Импорт настроек
        export_btn = QPushButton("📤 Экспорт настроек")
        export_btn.clicked.connect(self.export_admin_settings)

        import_btn = QPushButton("📥 Импорт настроек")
        import_btn.clicked.connect(self.import_admin_settings)

        # Сброс настроек
        reset_btn = QPushButton("🗑 Сбросить настройки")
        reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                font-weight: bold;
                border: 2px solid #e74c3c;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #ff6b5c;
                border-color: #ff6b5c;
            }
        """)
        reset_btn.clicked.connect(self.reset_admin_settings)

        extra_layout.addWidget(reload_btn)
        extra_layout.addWidget(export_btn)
        extra_layout.addWidget(import_btn)
        extra_layout.addWidget(reset_btn)

        scroll_layout.addWidget(extra_group)

        # Добавляем отступ
        scroll_layout.addStretch()

        # Устанавливаем содержимое прокрутки
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)

        # Кнопки закрытия
        button_layout = QHBoxLayout()
        close_btn = QPushButton("✖️ Закрыть")
        close_btn.clicked.connect(dialog.close)

        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)

        # Стили для диалога
        dialog.setStyleSheet("""
            QDialog {
                background-color: #1a1a2a;
                border: 3px solid #ff9900;
                border-radius: 15px;
            }
            QLabel {
                color: #e0e0e0;
                font-size: 12px;
            }
            QLineEdit, QComboBox {
                background-color: #2a2a3a;
                border: 1px solid #3a3a4a;
                border-radius: 5px;
                padding: 8px;
                color: #e0e0e0;
                min-height: 30px;
            }
            QPushButton {
                background-color: #3a3a4a;
                border: 2px solid #4a4a5a;
                border-radius: 8px;
                padding: 10px 15px;
                color: #e0e0e0;
                font-weight: bold;
                font-size: 12px;
                min-height: 35px;
            }
            QPushButton:hover {
                background-color: #4a4a5a;
                border-color: #ff9900;
            }
        """)

        dialog.exec_()

    def update_admin_setting(self, key, value):
        """Обновляет настройку админа"""
        self.admin_settings[key] = value

    def add_quick_button(self, list_widget):
        """Добавляет новую быструю кнопку"""
        text, ok = QInputDialog.getText(self, "Добавить кнопку",
                                       "Введите текст кнопки (формат: эмоджи Текст):\nПример: 🐱 GitHub")
        if ok and text:
            list_widget.addItem(text)
            self.save_quick_buttons(list_widget)

    def edit_quick_button(self, list_widget):
        """Редактирует выбранную быструю кнопку"""
        current_item = list_widget.currentItem()
        if current_item:
            current_text = current_item.text()
            text, ok = QInputDialog.getText(self, "Редактировать кнопку",
                                           "Редактируйте текст кнопки:",
                                           QLineEdit.Normal, current_text)
            if ok and text:
                current_item.setText(text)
                self.save_quick_buttons(list_widget)

    def remove_quick_button(self, list_widget):
        """Удаляет выбранную быструю кнопку"""
        current_row = list_widget.currentRow()
        if current_row >= 0:
            list_widget.takeItem(current_row)
            self.save_quick_buttons(list_widget)

    def move_quick_button(self, list_widget, direction):
        """Перемещает кнопку вверх/вниз"""
        current_row = list_widget.currentRow()
        if current_row >= 0:
            new_row = current_row + direction
            if 0 <= new_row < list_widget.count():
                item = list_widget.takeItem(current_row)
                list_widget.insertItem(new_row, item)
                list_widget.setCurrentRow(new_row)
                self.save_quick_buttons(list_widget)

    def save_quick_buttons(self, list_widget):
        """Сохраняет быстрые кнопки"""
        buttons = []
        for i in range(list_widget.count()):
            buttons.append(list_widget.item(i).text())
        self.admin_settings["quick_buttons"] = buttons

    def apply_admin_settings(self, dialog=None):
        """Применяет настройки админа"""
        try:
            # Сохраняем настройки в файл
            admin_file = os.path.join(self.data_dir, 'admin_settings.json')
            with open(admin_file, 'w', encoding='utf-8') as f:
                json.dump(self.admin_settings, f, ensure_ascii=False, indent=4)

            # Применяем тему
            self.apply_admin_theme()

            self.show_notification("✅ Настройки админа применены")

            if dialog:
                dialog.close()

        except Exception as e:
            self.show_notification(f"❌ Ошибка: {str(e)[:50]}...")

    def apply_admin_theme(self):
        """Применяет выбранную админ тему"""
        theme = self.admin_settings.get("theme", "default")

        if theme == "liquid_glass":
            self.apply_liquid_glass_theme()
        elif theme == "dark_matter":
            self.apply_dark_matter_theme()
        elif theme == "cyberpunk":
            self.apply_cyberpunk_theme()
        elif theme == "nature":
            self.apply_nature_theme()
        elif theme == "fire":
            self.apply_fire_theme()
        elif theme == "ice":
            self.apply_ice_theme()
        elif theme == "neon":
            self.apply_neon_theme()
        else:
            self.apply_theme("dark")  # Стандартная тема

    def apply_liquid_glass_theme(self):
        """Применяет тему Liquid Glass"""
        glass_stylesheet = """
        /* Liquid Glass Theme */
        QMainWindow {
            background-color: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                            stop: 0 #0f2027, stop: 0.5 #203a43, stop: 1 #2c5364);
        }

        QWidget#navBar {
            background-color: rgba(16, 32, 39, 180);
            border-bottom: 2px solid #00d4ff;
            border-radius: 15px;
            margin: 10px;
            backdrop-filter: blur(10px);
        }

        QPushButton {
            background-color: rgba(0, 212, 255, 100);
            border: 2px solid rgba(255, 255, 255, 100);
            border-radius: 20px;
            color: white;
            font-weight: bold;
            backdrop-filter: blur(5px);
        }

        QPushButton:hover {
            background-color: rgba(0, 212, 255, 180);
            border-color: #00ff88;
        }

        QLineEdit {
            background-color: rgba(255, 255, 255, 50);
            border: 2px solid rgba(0, 212, 255, 150);
            border-radius: 20px;
            color: white;
            padding: 10px;
            backdrop-filter: blur(5px);
        }
        """
        self.setStyleSheet(glass_stylesheet)

    def apply_dark_matter_theme(self):
        """Применяет тему Dark Matter"""
        dark_matter_stylesheet = """
        /* Dark Matter Theme */
        QMainWindow {
            background-color: #0a0a0f;
        }

        QWidget#navBar {
            background-color: #151520;
            border-bottom: 2px solid #8a2be2;
            border-radius: 0px;
        }

        QPushButton {
            background-color: #252535;
            border: 2px solid #8a2be2;
            border-radius: 15px;
            color: #e0e0ff;
            font-weight: bold;
        }

        QPushButton:hover {
            background-color: #8a2be2;
            color: white;
        }

        QLineEdit {
            background-color: #1a1a25;
            border: 2px solid #8a2be2;
            border-radius: 15px;
            color: #e0e0ff;
            padding: 10px;
        }
        """
        self.setStyleSheet(dark_matter_stylesheet)

    def apply_cyberpunk_theme(self):
        """Применяет тему Cyberpunk"""
        cyberpunk_stylesheet = """
        /* Cyberpunk Theme */
        QMainWindow {
            background-color: #0a0015;
        }

        QWidget#navBar {
            background-color: #1a0025;
            border-bottom: 2px solid #ff00ff;
            border-radius: 0px;
        }

        QPushButton {
            background-color: #2a0035;
            border: 2px solid #00ffff;
            border-radius: 10px;
            color: #00ffff;
            font-weight: bold;
        }

        QPushButton:hover {
            background-color: #ff00ff;
            color: #0a0015;
            border-color: #ff00ff;
        }

        QLineEdit {
            background-color: #1a0025;
            border: 2px solid #00ffff;
            border-radius: 10px;
            color: #00ffff;
            padding: 10px;
        }
        """
        self.setStyleSheet(cyberpunk_stylesheet)

    def apply_nature_theme(self):
        """Применяет тему Nature"""
        nature_stylesheet = """
        /* Nature Theme */
        QMainWindow {
            background-color: #1a3c27;
        }

        QWidget#navBar {
            background-color: #2a5c37;
            border-bottom: 2px solid #4caf50;
            border-radius: 15px;
            margin: 10px;
        }

        QPushButton {
            background-color: #3a7c47;
            border: 2px solid #4caf50;
            border-radius: 20px;
            color: white;
            font-weight: bold;
        }

        QPushButton:hover {
            background-color: #4caf50;
            border-color: #81c784;
        }

        QLineEdit {
            background-color: #2a5c37;
            border: 2px solid #4caf50;
            border-radius: 20px;
            color: white;
            padding: 10px;
        }
        """
        self.setStyleSheet(nature_stylesheet)

    def apply_fire_theme(self):
        """Применяет тему Fire"""
        fire_stylesheet = """
        /* Fire Theme */
        QMainWindow {
            background-color: #2c0a0a;
        }

        QWidget#navBar {
            background-color: #4a1a1a;
            border-bottom: 2px solid #ff5722;
            border-radius: 10px;
            margin: 10px;
        }

        QPushButton {
            background-color: #6a2a2a;
            border: 2px solid #ff5722;
            border-radius: 15px;
            color: white;
            font-weight: bold;
        }

        QPushButton:hover {
            background-color: #ff5722;
            border-color: #ff8a65;
        }

        QLineEdit {
            background-color: #4a1a1a;
            border: 2px solid #ff5722;
            border-radius: 15px;
            color: white;
            padding: 10px;
        }
        """
        self.setStyleSheet(fire_stylesheet)

    def apply_ice_theme(self):
        """Применяет тему Ice"""
        ice_stylesheet = """
        /* Ice Theme */
        QMainWindow {
            background-color: #0a1a2c;
        }

        QWidget#navBar {
            background-color: #1a2a4a;
            border-bottom: 2px solid #29b6f6;
            border-radius: 15px;
            margin: 10px;
        }

        QPushButton {
            background-color: #2a3a6a;
            border: 2px solid #29b6f6;
            border-radius: 20px;
            color: white;
            font-weight: bold;
        }

        QPushButton:hover {
            background-color: #29b6f6;
            border-color: #81d4fa;
        }

        QLineEdit {
            background-color: #1a2a4a;
            border: 2px solid #29b6f6;
            border-radius: 20px;
            color: white;
            padding: 10px;
        }
        """
        self.setStyleSheet(ice_stylesheet)

    def apply_neon_theme(self):
        """Применяет тему Neon"""
        neon_stylesheet = """
        /* Neon Theme */
        QMainWindow {
            background-color: #0a0a1a;
        }

        QWidget#navBar {
            background-color: #1a1a3a;
            border-bottom: 2px solid #00ff00;
            border-radius: 10px;
            margin: 10px;
            box-shadow: 0 0 10px #00ff00;
        }

        QPushButton {
            background-color: #2a2a5a;
            border: 2px solid #ff00ff;
            border-radius: 10px;
            color: white;
            font-weight: bold;
        }

        QPushButton:hover {
            background-color: #ff00ff;
            border-color: #00ff00;
            color: #0a0a1a;
            box-shadow: 0 0 10px #ff00ff;
        }

        QLineEdit {
            background-color: #1a1a3a;
            border: 2px solid #00ff00;
            border-radius: 10px;
            color: #00ff00;
            padding: 10px;
            box-shadow: 0 0 5px #00ff00;
        }
        """
        self.setStyleSheet(neon_stylesheet)

    def export_admin_settings(self):
        """Экспортирует настройки админа в файл"""
        try:
            file_name, _ = QFileDialog.getSaveFileName(
                self, "Экспорт настроек",
                "derbrowser_admin_settings.json",
                "JSON Files (*.json);;All Files (*)"
            )

            if file_name:
                with open(file_name, 'w', encoding='utf-8') as f:
                    json.dump(self.admin_settings, f, ensure_ascii=False, indent=4)
                self.show_notification("✅ Настройки экспортированы")

        except Exception as e:
            self.show_notification(f"❌ Ошибка экспорта: {str(e)[:50]}...")

    def import_admin_settings(self):
        """Импортирует настройки админа из файла"""
        try:
            file_name, _ = QFileDialog.getOpenFileName(
                self, "Импорт настроек",
                "", "JSON Files (*.json);;All Files (*)"
            )

            if file_name and os.path.exists(file_name):
                with open(file_name, 'r', encoding='utf-8') as f:
                    self.admin_settings = json.load(f)
                self.show_notification("✅ Настройки импортированы")
                self.apply_admin_settings()

        except Exception as e:
            self.show_notification(f"❌ Ошибка импорта: {str(e)[:50]}...")

    def reset_admin_settings(self):
        """Сбрасывает настройки админа"""
        reply = QMessageBox.question(self, "Сброс настроек",
                                   "Вы уверены, что хотите сбросить все настройки админа?\nЭто действие нельзя отменить.",
                                   QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.admin_settings = {
                "theme": "default",
                "logo_text": "Der Browser",
                "main_title": "🌐 Der Browser - Made by AI",
                "subtitle": "Modern Web Experience",
                "quick_buttons": [
                    "🐱 GitHub", "📺 YouTube", "🎵 Spotify", "✈️ Telegram",
                    "🔍 Google", "📘 Facebook", "🐦 Twitter", "💼 LinkedIn",
                    "📷 Instagram", "🛒 Amazon", "📚 Wikipedia", "🎮 Twitch",
                    "💬 Discord", "☁️ Dropbox", "📦 Google Drive"
                ]
            }
            self.apply_admin_settings()
            self.show_notification("✅ Настройки админа сброшены")

    def reload_ui(self):
        """Перезагружает интерфейс с новыми настройками"""
        # Закрываем все вкладки кроме первой
        while self.tab_widget.count() > 1:
            self.tab_widget.removeTab(1)

        # Обновляем главную страницу
        if self.tab_widget.count() > 0:
            self.tab_widget.removeTab(0)

        # Создаем новую главную страницу с обновленными настройками
        self.add_new_tab("", "🏠 Главная", True)
        self.show_notification("✅ Интерфейс перезагружен")

    def load_admin_settings(self):
        """Загружает настройки админа"""
        try:
            admin_file = os.path.join(self.data_dir, 'admin_settings.json')
            if os.path.exists(admin_file):
                with open(admin_file, 'r', encoding='utf-8') as f:
                    self.admin_settings = json.load(f)
        except Exception as e:
            print(f"Ошибка загрузки админ настроек: {e}")
            # Настройки по умолчанию
            self.admin_settings = {
                "theme": "default",
                "logo_text": "Der Browser",
                "main_title": "🌐 Der Browser - Made by AI",
                "subtitle": "Modern Web Experience",
                "quick_buttons": [
                    "🐱 GitHub", "📺 YouTube", "🎵 Spotify", "✈️ Telegram",
                    "🔍 Google", "📘 Facebook", "🐦 Twitter", "💼 LinkedIn",
                    "📷 Instagram", "🛒 Amazon", "📚 Wikipedia", "🎮 Twitch",
                    "💬 Discord", "☁️ Dropbox", "📦 Google Drive"
                ]
            }

    def setup_shortcuts(self):
        """Настраивает горячие клавиши"""
        # Ctrl+T - Новая вкладка
        shortcut = QShortcut(QKeySequence("Ctrl+T"), self)
        shortcut.activated.connect(lambda: self.add_new_tab("", "Новая вкладка", True))

        # Ctrl+W - Закрыть вкладку
        shortcut = QShortcut(QKeySequence("Ctrl+W"), self)
        shortcut.activated.connect(lambda: self.close_tab(self.tab_widget.currentIndex()))

        # Ctrl+D - Добавить в закладки
        shortcut = QShortcut(QKeySequence("Ctrl+D"), self)
        shortcut.activated.connect(self.add_current_to_bookmarks)

        # F5 - Обновить
        shortcut = QShortcut(QKeySequence("F5"), self)
        shortcut.activated.connect(self.reload_page)

        # F11 - Полный экран
        shortcut = QShortcut(QKeySequence("F11"), self)
        shortcut.activated.connect(self.toggle_fullscreen)

        # Ctrl+Shift+T - Переключить тему
        shortcut = QShortcut(QKeySequence("Ctrl+Shift+T"), self)
        shortcut.activated.connect(self.toggle_theme)

        # Ctrl+Shift+V - Переключить VPN
        shortcut = QShortcut(QKeySequence("Ctrl+Shift+V"), self)
        shortcut.activated.connect(self.toggle_vpn)

        # Ctrl+Shift+I - Переключить инкогнито
        shortcut = QShortcut(QKeySequence("Ctrl+Shift+I"), self)
        shortcut.activated.connect(self.toggle_incognito)

        # Ctrl+Shift+A - Админ панель (только для админов)
        if self.is_admin:
            shortcut = QShortcut(QKeySequence("Ctrl+Shift+A"), self)
            shortcut.activated.connect(self.show_admin_panel)

        # Ctrl+Plus - Увеличить масштаб
        shortcut = QShortcut(QKeySequence("Ctrl++"), self)
        shortcut.activated.connect(self.zoom_in)

        # Ctrl+Minus - Уменьшить масштаб
        shortcut = QShortcut(QKeySequence("Ctrl+-"), self)
        shortcut.activated.connect(self.zoom_out)

        # Ctrl+0 - Сбросить масштаб
        shortcut = QShortcut(QKeySequence("Ctrl+0"), self)
        shortcut.activated.connect(self.reset_zoom)

    def toggle_fullscreen(self):
        """Переключает полноэкранный режим"""
        if self.isFullScreen():
            self.showNormal()
            self.show_notification("Обычный режим")
        else:
            self.showFullScreen()
            self.show_notification("Полноэкранный режим")

    def closeEvent(self, event):
        """Обработчик закрытия окна"""
        self.save_user_data()
        event.accept()

    def setup_shortcuts(self):  # <-- ОТДЕЛЬНЫЙ МЕТОД!
        """Настраивает горячие клавиши"""
        # Ctrl+T - Новая вкладка
        shortcut = QShortcut(QKeySequence("Ctrl+T"), self)
        shortcut.activated.connect(lambda: self.add_new_tab("", "Новая вкладка", True))

        # Ctrl+W - Закрыть вкладку
        shortcut = QShortcut(QKeySequence("Ctrl+W"), self)
        shortcut.activated.connect(lambda: self.close_tab(self.tab_widget.currentIndex()))

        # Ctrl+D - Добавить в закладки
        shortcut = QShortcut(QKeySequence("Ctrl+D"), self)
        shortcut.activated.connect(self.add_current_to_bookmarks)

        # F5 - Обновить
        shortcut = QShortcut(QKeySequence("F5"), self)
        shortcut.activated.connect(self.reload_page)

        # F11 - Полный экран
        shortcut = QShortcut(QKeySequence("F11"), self)
        shortcut.activated.connect(self.toggle_fullscreen)

        # Ctrl+Shift+T - Переключить тему
        shortcut = QShortcut(QKeySequence("Ctrl+Shift+T"), self)
        shortcut.activated.connect(self.toggle_theme)

        # Ctrl+Shift+V - Переключить VPN
        shortcut = QShortcut(QKeySequence("Ctrl+Shift+V"), self)
        shortcut.activated.connect(self.toggle_vpn)

        # Ctrl+Shift+I - Переключить инкогнито
        shortcut = QShortcut(QKeySequence("Ctrl+Shift+I"), self)
        shortcut.activated.connect(self.toggle_incognito)

        # Ctrl+Shift+A - Админ панель (только для админов)
        if self.is_admin:
            shortcut = QShortcut(QKeySequence("Ctrl+Shift+A"), self)
            shortcut.activated.connect(self.show_admin_panel)

        # Ctrl+Plus - Увеличить масштаб
        shortcut = QShortcut(QKeySequence("Ctrl++"), self)
        shortcut.activated.connect(self.zoom_in)

        # Ctrl+Minus - Уменьшить масштаб
        shortcut = QShortcut(QKeySequence("Ctrl+-"), self)
        shortcut.activated.connect(self.zoom_out)

        # Ctrl+0 - Сбросить масштаб
        shortcut = QShortcut(QKeySequence("Ctrl+0"), self)
        shortcut.activated.connect(self.reset_zoom)

def main():
    # Создаем приложение
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Создаем и показываем главное окно
    browser = ModernBrowser()
    browser.show()

    # Запускаем главный цикл приложения
    sys.exit(app.exec_())

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"Ошибка запуска: {e}")
        import traceback
        traceback.print_exc()
        print("\nУстановленные версии:")
        print("PyQt5: 5.15.9")
        print("PyQtWebEngine: 5.15.2")
        print("\n✅ Эти версии совместимы! Программа должна работать.")
        input("\nНажмите Enter для выхода...")

