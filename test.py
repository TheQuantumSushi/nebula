# Imports :
import sys
import csv
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QPalette, QColor
from PyQt6.QtWidgets import (QApplication, QLabel, QSizePolicy, QListWidget, QListWidgetItem, QMainWindow, QPushButton, QWidget, QVBoxLayout, QHBoxLayout, QFrame, QSpacerItem)

class Color(QWidget):

    def __init__(self, color):
        super(Color, self).__init__()
        self.setAutoFillBackground(True)

        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(color))
        self.setPalette(palette)

# Main window :
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Window style :
        self.setWindowTitle(' ')
        self.showMaximized()
        self.setStyleSheet("""
            QWidget#central_widget {
                background-color: #2c2c2c; /* Background color */
            }
            QListWidget {
                background-color: #2c2c2c; /* List background color */
                border:1px solid #FFFFFF;
                padding: 5px;
            }
            QListWidget::item {
                background-color: #2c2c2c; /* Item background color */
                margin: 5px;
                padding: 10px;
                border-radius: 10px;
                color: white; /* Item text color */
            }
            QListWidget::item:selected {
                background-color: #595454; /* Selected item background color */
            }
            QLabel#title_label {
                font-size: 28px;
                font-weight: bold;
                color: white; /* Main title text color */
            }
            QLabel#status_label {
                font-size: 18px;
                font-weight: bold;
                color: white; /* Small title text color */
            }
            QLabel#address_label {
                font-size: 14px;
                color: white; /* Text line color */
            }
            QLabel#location_label {
                font-size: 14px;
                color: white; /* Text line color */
            }
            QPushButton {
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
                border-radius: 10px;
            }
            QPushButton#connect_button {
                background-color: #4CAF50;  /* Green for connect */
                color: white; /* Button text color */
            }
            QPushButton#disconnect_button {
                background-color: #f44336;  /* Red for disconnect */
                color: white; /* Button text color */
            }
        """)

        # Variables :
        self.connected = False
        self.connected_status = "off"
        self.vpn_address = ""
        self.server_location = ""
        self.separator_item = None
        self.connected_item = None

        # Define widgets :

        title_label = QLabel("Skynet portal")
        title_label.setObjectName("title_label")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        status_label = QLabel(f"Connection status: {self.connected_status}")
        status_label.setObjectName("status_label")

        address_label = QLabel(f"Connected to : {self.vpn_address}")
        address_label.setObjectName("address_label")

        location_label = QLabel(f"Location: {self.server_location}")
        location_label.setObjectName("location_label")

        connect_button = QPushButton("Connect")
        connect_button.setFixedSize(150, 100)
        connect_button.setObjectName("connect_button")

        horizontal_spacer = QSpacerItem(0, 40, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        address_list = QListWidget()
        address_list.setSortingEnabled(True)

        vertical_spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        # Define layouts :

        main_layout = QVBoxLayout()
        top_layout = QVBoxLayout()
        bottom_layout = QHBoxLayout()
        top_sub_layout = QHBoxLayout()
        top_sub_left_layout = QVBoxLayout()
        top_sub_right_layout = QVBoxLayout()

        # Nest layouts and add widgets :

        main_layout.addLayout(top_layout)
        main_layout.addSpacerItem(horizontal_spacer)
        main_layout.addLayout(bottom_layout)
        top_layout.addWidget(title_label)
        top_layout.addLayout(top_sub_layout)
        top_sub_layout.addLayout(top_sub_left_layout)
        top_sub_layout.addLayout(top_sub_right_layout)
        top_sub_left_layout.addWidget(status_label)
        top_sub_left_layout.addWidget(address_label)
        top_sub_left_layout.addWidget(location_label)
        top_sub_right_layout.addWidget(connect_button, alignment=Qt.AlignmentFlag.AlignRight)
        bottom_layout.addWidget(address_list)
        bottom_layout.addSpacerItem(vertical_spacer)

        # Define central widget :

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)



# Start the application :
if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    # Start the event loop
    sys.exit(app.exec())