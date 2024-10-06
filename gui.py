'''
TODO :

https://doc.qt.io/qtforpython-6.2/PySide6/QtWidgets/QDockWidget.html
https://www.pythonguis.com/tutorials/pyqt6-actions-toolbars-menus/

'''

# Imports :
import sys
import csv
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (QApplication, QLabel, QListWidget, QListWidgetItem, QMainWindow, QPushButton, QWidget, QVBoxLayout, QHBoxLayout, QFrame, QSizePolicy, QSpacerItem)
import subprocess

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
        self.title_label = QLabel("Nebula")
        self.title_label.setObjectName("title_label")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.status_label = QLabel(f"Connection status: {self.connected_status}")
        self.status_label.setObjectName("status_label")

        self.address_label = QLabel(f"Connected to : {self.vpn_address}")
        self.address_label.setObjectName("address_label")

        self.location_label = QLabel(f"Location: {self.server_location}")
        self.location_label.setObjectName("location_label")

        self.connect_button = QPushButton("Connect")
        self.connect_button.setFixedSize(150, 100)
        self.connect_button.setObjectName("connect_button")
        self.connect_button.clicked.connect(self.toggle_connection)

        self.horizontal_spacer = QSpacerItem(0, 40, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.address_list = QListWidget()
        self.address_list.setSortingEnabled(True)
        self.initial_vpn_list = self.list_vpns()
        self.add_items_to_list(self.address_list, [{"text": vpn} for vpn in self.initial_vpn_list])

        self.vertical_spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        # Define layouts :
        self.main_layout = QVBoxLayout()
        self.top_layout = QVBoxLayout()
        self.bottom_layout = QHBoxLayout()
        self.top_sub_layout = QHBoxLayout()
        self.top_sub_left_layout = QVBoxLayout()
        self.top_sub_right_layout = QVBoxLayout()

        # Nest layouts and add widgets :
        self.main_layout.addLayout(self.top_layout)
        self.main_layout.addSpacerItem(self.horizontal_spacer)
        self.main_layout.addLayout(self.bottom_layout)
        self.top_layout.addWidget(self.title_label)
        self.top_layout.addLayout(self.top_sub_layout)
        self.top_sub_layout.addLayout(self.top_sub_left_layout)
        self.top_sub_layout.addLayout(self.top_sub_right_layout)
        self.top_sub_left_layout.addWidget(self.status_label)
        self.top_sub_left_layout.addWidget(self.address_label)
        self.top_sub_left_layout.addWidget(self.location_label)
        self.top_sub_right_layout.addWidget(self.connect_button, alignment=Qt.AlignmentFlag.AlignRight)
        self.bottom_layout.addWidget(self.address_list)
        self.bottom_layout.addSpacerItem(self.vertical_spacer)

        # Define central widget :
        self.central_widget = QWidget()
        self.central_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.central_widget)

    def add_items_to_list(self, list_widget, items):
        """
        Add one or multiple items to the VPN list
        """
        for item in items:
            address = item['text']
            list_item = QListWidgetItem()
            list_item.setText(address)
            try:
                icon = QIcon(f"flags/{address[:2]}.png")  # Path to the flag icon
                list_item.setIcon(icon)
            except:
                pass
            list_item.setSizeHint(QSize(200, 40))  # Set item size
            list_widget.setIconSize(QSize(20, 20))  # Set icon size
            list_widget.addItem(list_item)

    def list_vpns(self):
        """
        Use subprocess.run() to execute the command : ls /etc/openvpn -Iserver -Iclient -Iconfigurations
        and return the list of vpns
        """
        output = subprocess.run(['/bin/ls', '/etc/openvpn', '-Iclient', '-Iserver', '-Iconfigurations'], capture_output=True, text=True)
        vpn_list = output.stdout.splitlines()
        return vpn_list

    def toggle_connection(self):
        """
        Connect or disconnect the VPN when connect_button is pressed
        """
        selected_item = self.get_selected_item()  # get the selected VPN in the list
        if selected_item:
            if not self.connected:  # Connect
                self.connected = True
                self.vpn_address = selected_item.text()
                self.connected_item = selected_item
                self.connected_status = "on"

                # Retrieve server location
                self.server_location = "unknown"
                with open('country_codes.csv', 'rt') as country_codes:
                    reader = csv.reader(country_codes, delimiter=',')
                    for row in reader:
                        if self.vpn_address[:2].upper() == row[1]:
                            self.server_location = row[0]
                            break

                # Update button appearance:
                self.connect_button.setText("Disconnect")
                self.connect_button.setStyleSheet("background-color: #f44336;")

                # Move connected item to top:
                self.move_item_to_top(selected_item)

            else:  # Disconnect
                self.connected = False
                self.vpn_address = ""
                self.connected_item = None
                self.connected_status = "off"
                self.server_location = ""

                # Update button appearance:
                self.connect_button.setText("Connect")
                self.connect_button.setStyleSheet("background-color: #4CAF50;")

                # Remove separator and re-sort list:
                self.reset_list_order()

            self.update_connection_status()

    def get_selected_item(self):
        """
        Return the selected VPN from the left list
        """
        item = None
        if self.address_list.selectedItems():
            item = self.address_list.selectedItems()[0]
        return item

    def update_connection_status(self):
        """
        Update the status, address, and location labels
        """
        self.status_label.setText(f"Connection status: {self.connected_status}")
        self.address_label.setText(f"Connected to : {self.vpn_address}" if self.vpn_address else "Connected to :")
        self.location_label.setText(f"Location: {self.server_location}" if self.server_location else "Location:")

    def move_item_to_top(self, item):
        """
        Move the connected VPN to the top and add a separator
        """
        # Remove sorting temporarily
        self.address_list.setSortingEnabled(False)

        # Create a separator item if not already created
        if self.separator_item is None:
            self.separator_item = QListWidgetItem("᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆᠆")
            self.separator_item.setFlags(Qt.ItemFlag.NoItemFlags)  # Make it non-selectable
            #self.separator_item.setSizeHint(QSize(200, 10))  # Smaller size for separator
            self.address_list.insertItem(0, self.separator_item)

        # Move the connected item to the top (right under the separator)
        self.address_list.takeItem(self.address_list.row(item))  # Remove from the current position
        self.address_list.insertItem(0, item)  # Insert at the top
        self.address_list.setCurrentItem(item)  # Ensure it stays selected

    def reset_list_order(self):
        """
        Remove the separator and sort items alphabetically when disconnected
        """
        # Remove sorting temporarily
        self.address_list.setSortingEnabled(False)

        # Remove the connected item and reinsert it to trigger sorting
        if self.connected_item:
            self.address_list.takeItem(self.address_list.row(self.connected_item))
            self.address_list.addItem(self.connected_item)

        # Remove the separator item if it exists
        if self.separator_item:
            self.address_list.takeItem(self.address_list.row(self.separator_item))
            self.separator_item = None

        # Enable sorting
        self.address_list.setSortingEnabled(True)

    '''
    def handle_selection(self):
        """
        Handle selection of items in the list
        """
        pass
    '''


# Start the application :
if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    # Start the event loop
    sys.exit(app.exec())