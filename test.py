import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QScrollArea
from PyQt6.QtCore import Qt

class MultiLineTextWidget(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Multi-Line Text Display")

        # Create a central widget
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        # Create a QLabel widget for displaying multi-line text
        self.label = QLabel(self)
        self.label.setWordWrap(True)  # Enable word wrap
        self.label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)  # Align to top-left
        self.label.setSizePolicy(self.label.sizePolicy().horizontalPolicy(),
                                 self.label.sizePolicy().verticalPolicy().Expanding)

        # Initialize with some text
        self.lines = ["This is a PyQt6 QLabel widget.",
                      "You can easily display multiple lines of text."]
        self.update_text()

        # Create a QScrollArea and put QLabel inside it
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.label)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.scroll_area)
        self.central_widget.setLayout(layout)

    def update_text(self):
        """Update the label text to display all lines."""
        self.label.setText("<br>".join(self.lines))

    def add_line(self, text):
        """Add a new line of text to the display."""
        self.lines.append(text)
        self.update_text()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Create and show the main window
    main_window = MultiLineTextWidget()
    main_window.resize(400, 300)
    main_window.show()

    # Example: dynamically adding a new line of text
    main_window.add_line("This is a dynamically added line.")

    sys.exit(app.exec())
