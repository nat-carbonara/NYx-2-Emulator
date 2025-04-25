import sys
from PyQt5.QtWidgets import QMessageBox
import os
import json
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel,
    QHBoxLayout, QPushButton, QFileDialog, QScrollArea,
    QMenuBar, QAction, QInputDialog
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

GAMES_FILE = "games.json"
ASSETS_FOLDER = "assets/covers"

class GameItem(QWidget):
    def __init__(self, title, image_path):
        super().__init__()
        layout = QVBoxLayout()
        img = QLabel()
        pixmap = QPixmap(image_path).scaled(128, 128, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        img.setPixmap(pixmap)
        img.setAlignment(Qt.AlignCenter)
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(img)
        layout.addWidget(title_label)
        self.setLayout(layout)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NYx 2 Emu (v1)")
        self.setGeometry(100, 100, 900, 600)

        self.games = self.load_games()
        self.dark_theme = False

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QHBoxLayout()
        self.central_widget.setLayout(self.main_layout)

        self.create_menu_bar()
        self.create_game_list()
        self.create_game_details()

    def create_menu_bar(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu("File")
        install_os_action = QAction("Install OS", self)
        install_os_action.triggered.connect(self.install_os)
        file_menu.addAction(install_os_action)
        
        add_game_action = QAction("Add game", self)
        add_game_action.triggered.connect(self.add_game)
        file_menu.addAction(add_game_action)

        quit_action = QAction("Exit", self)
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        settings_menu = menubar.addMenu("Settings")
        toggle_os_action = QAction("OS Settings", self)
        toggle_os_action.triggered.connect(self.show_os_settings)
        settings_menu.addAction(toggle_os_action)

    def install_os(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select OS file", "", "OS Files (*.nspos *.os *.nsp)")
        
        if file_path:
            title, ok = QInputDialog.getText(self, "OS Version", "Insert OS Version:")
            
            if ok and title:
                os.makedirs(ASSETS_FOLDER, exist_ok=True)
                dest_path = os.path.join(ASSETS_FOLDER, os.path.basename(file_path))
                
                with open(file_path, 'rb') as fsrc:
                    with open(dest_path, 'wb') as fdst:
                        fdst.write(fsrc.read())
                
                self.os_installed = {"title": title, "image": dest_path}

                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)
                msg.setText(f"OS {title} installed successfully!")
                msg.setWindowTitle("OS Installation")
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()

    def show_os_settings(self):
        if self.os_installed:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText(f"Installed OS: {self.os_installed['title']}")
            msg.setWindowTitle("OS Settings")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("No OS Installed")
            msg.setWindowTitle("OS Settings")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()

    def toggle_os(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("No OS Found")
        msg.setWindowTitle("Error")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def create_game_list(self):
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.games_container = QWidget()
        self.games_layout = QHBoxLayout()
        self.games_container.setLayout(self.games_layout)

        for game in self.games:
            item = GameItem(game['title'], game['image'])
            item.mousePressEvent = lambda event, g=game: self.show_game_details(g)
            self.games_layout.addWidget(item)

        self.scroll_area.setWidget(self.games_container)
        self.main_layout.addWidget(self.scroll_area, 3)

    def create_game_details(self):
        self.details_panel = QWidget()
        self.details_layout = QVBoxLayout()
        self.details_panel.setLayout(self.details_layout)

        self.details_img = QLabel("No game selected")
        self.details_img.setAlignment(Qt.AlignCenter)
        self.details_title = QLabel("")
        self.details_title.setAlignment(Qt.AlignCenter)

        self.details_layout.addWidget(self.details_img)
        self.details_layout.addWidget(self.details_title)

        self.main_layout.addWidget(self.details_panel, 2)

    def show_game_details(self, game):
        pixmap = QPixmap(game['image']).scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.details_img.setPixmap(pixmap)
        self.details_title.setText(game['title'])

    def add_game(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select game cover", "", "Images (*.png *.jpg *.bmp)")
        if file_path:
            title, ok = QInputDialog.getText(self, "Game title", "Insert the game title:")
            if ok and title:
                os.makedirs(ASSETS_FOLDER, exist_ok=True)
                dest_path = os.path.join(ASSETS_FOLDER, os.path.basename(file_path))
                with open(file_path, 'rb') as fsrc:
                    with open(dest_path, 'wb') as fdst:
                        fdst.write(fsrc.read())
                new_game = {"title": title, "image": dest_path}
                self.games.append(new_game)
                self.save_games()
                self.refresh_game_list()

    def refresh_game_list(self):
        for i in reversed(range(self.games_layout.count())):
            widget = self.games_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        for game in self.games:
            item = GameItem(game['title'], game['image'])
            item.mousePressEvent = lambda event, g=game: self.show_game_details(g)
            self.games_layout.addWidget(item)

    def load_games(self):
        if os.path.exists(GAMES_FILE):
            with open(GAMES_FILE, 'r') as f:
                try:
                    data = f.read().strip()
                    if not data:
                        return []
                    return json.loads(data)
                except json.JSONDecodeError:
                    return []
        return []

    def save_games(self):
        with open(GAMES_FILE, 'w') as f:
            json.dump(self.games, f, indent=4)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
