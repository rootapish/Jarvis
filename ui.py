import sys
import threading
from voice import listen, speak
from commands import handle_command
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QHBoxLayout, QPushButton, QLabel, QScrollArea, 
    QFrame, QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import Qt, QTimer, QSize, pyqtSignal
from PyQt5.QtGui import QFont, QColor

class MessageBubble(QFrame):
    def __init__(self, text, m_type="jarvis", data=None):
        super().__init__()
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(15, 12, 15, 12)
        
        # Style based on message type
        if m_type == "user":
            self.setStyleSheet("""
                QFrame {
                    background-color: #ec5b13;
                    border-radius: 15px;
                    border-top-right-radius: 0px;
                }
            """)
            label_color = "#ffffff"
            font_family = "Segoe UI, Arial"
            align = Qt.AlignRight
        elif m_type == "technical":
            self.setStyleSheet("""
                QFrame {
                    background-color: rgba(34, 22, 16, 150);
                    border: 1px solid rgba(236, 91, 19, 50);
                    border-radius: 15px;
                    border-top-left-radius: 0px;
                }
            """)
            label_color = "#d4cfc4"
            font_family = "Consolas, Monaco, monospace"
            align = Qt.AlignLeft
        else: # jarvis
            self.setStyleSheet("""
                QFrame {
                    background-color: rgba(34, 22, 16, 150);
                    border: 1px solid rgba(255, 255, 255, 20);
                    border-radius: 15px;
                    border-top-left-radius: 0px;
                }
            """)
            label_color = "#d4cfc4"
            font_family = "Consolas, Monaco, monospace"
            align = Qt.AlignLeft

        self.label = QLabel(text)
        self.label.setWordWrap(True)
        self.label.setStyleSheet(f"color: {label_color}; font-family: '{font_family}'; font-size: 13px; background: transparent; border: none;")
        self.layout.addWidget(self.label)

        if data:
            data_box = QFrame()
            data_box.setStyleSheet("background-color: rgba(0,0,0,80); border-radius: 8px; padding: 10px; border: none;")
            data_layout = QVBoxLayout(data_box)
            for k, v in data.items():
                row = QLabel(f"{k}: {v}")
                row.setStyleSheet("color: rgba(236, 91, 19, 200); font-family: 'Consolas'; font-size: 11px; background: transparent;")
                data_layout.addWidget(row)
            self.layout.addWidget(data_box)

        self.setLayout(self.layout)
        self.setFixedWidth(450)

class JarvisWindow(QMainWindow):
    message_signal = pyqtSignal(str, str)
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Jarvis AI Interface")
        self.setMinimumSize(700, 900)
        self.setStyleSheet("background-color: #0a0a0f;")
        self.setup_ui()
        self.message_signal.connect(self.add_message)
        
    def setup_ui(self):
        central = QWidget()
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # --- Header ---
        header = QFrame()
        header.setFixedHeight(80)
        header.setStyleSheet("background-color: rgba(10, 10, 15, 200); border-bottom: 1px solid rgba(236, 91, 19, 30);")
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(30, 0, 30, 0)
        
        title_container = QVBoxLayout()
        title = QLabel("JARVIS")
        title.setStyleSheet("color: #ec5b13; font-size: 22px; font-weight: 900; letter-spacing: 3px; border: none;")
        
        self.status_lbl = QLabel("● ACTIVE")
        self.status_lbl.setStyleSheet("color: #ec5b13; font-size: 10px; font-weight: bold; letter-spacing: 2px; border: none;")
        
        title_container.addWidget(title)
        title_container.addWidget(self.status_lbl)
        h_layout.addLayout(title_container)
        h_layout.addStretch()
        
        self.main_layout.addWidget(header)
        
        # --- Chat Area ---
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        self.scroll_content = QWidget()
        self.scroll_content.setStyleSheet("background-color: transparent;")
        self.chat_layout = QVBoxLayout(self.scroll_content)
        self.chat_layout.setContentsMargins(40, 40, 40, 40)
        self.chat_layout.setSpacing(25)
        self.chat_layout.addStretch()
        
        self.scroll.setWidget(self.scroll_content)
        self.main_layout.addWidget(self.scroll)
        
        # --- Footer Interaction ---
        footer = QFrame()
        footer.setFixedHeight(180)
        footer.setStyleSheet("background: transparent;")
        f_layout = QVBoxLayout(footer)
        
        # Mic Button
        self.mic_btn = QPushButton("HOLD TO SPEAK")
        self.mic_btn.setFixedSize(180, 60)
        self.mic_btn.setCursor(Qt.PointingHandCursor)
        self.mic_btn.setStyleSheet("""
            QPushButton {
                background-color: #ec5b13;
                color: white;
                font-weight: bold;
                font-size: 12px;
                border-radius: 30px;
                letter-spacing: 2px;
            }
            QPushButton:hover { background-color: #ff6b23; }
            QPushButton:pressed { background-color: #c94a0d; }
        """)
        self.mic_btn.clicked.connect(self.on_listen)
        
        btn_container = QHBoxLayout()
        btn_container.addStretch()
        btn_container.addWidget(self.mic_btn)
        btn_container.addStretch()
        f_layout.addLayout(btn_container)
        
        # Sub-labels
        sub_layout = QHBoxLayout()
        sub_layout.setContentsMargins(0, 10, 0, 20)
        type_btn = QLabel("⌨ TYPE")
        attach_btn = QLabel("📎 ATTACH")
        for btn in [type_btn, attach_btn]:
            btn.setStyleSheet("color: #444; font-size: 10px; font-weight: bold; letter-spacing: 1px;")
            sub_layout.addStretch()
            sub_layout.addWidget(btn)
        sub_layout.addStretch()
        f_layout.addLayout(sub_layout)
        
        self.main_layout.addWidget(footer)
        
        central.setLayout(self.main_layout)
        self.setCentralWidget(central)
        
        # Initial Message
        self.add_message("Core systems initialized. Multi-spectral analysis module is online and ready for input. How can I assist you today?", "jarvis")

    def add_message(self, text, m_type="jarvis", data=None):
        bubble = MessageBubble(text, m_type, data)
        
        container = QWidget()
        container_layout = QHBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        
        if m_type == "user":
            container_layout.addStretch()
            container_layout.addWidget(bubble)
        else:
            container_layout.addWidget(bubble)
            container_layout.addStretch()
            
        # Insert before the stretch at the end
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, container)
        
        # Scroll to bottom
        QTimer.singleShot(100, lambda: self.scroll.verticalScrollBar().setValue(self.scroll.verticalScrollBar().maximum()))

    def on_listen(self):
        self.status_lbl.setText("● LISTENING")
        self.status_lbl.setStyleSheet("color: #ff4444; font-size: 10px; font-weight: bold; letter-spacing: 2px;")
        self.mic_btn.setText("LISTENING...")
        self.mic_btn.setEnabled(False)
        
        thread = threading.Thread(target=self.listen_worker)
        thread.start()

    def listen_worker(self):
        text = listen()
        
        if text:
            self.message_signal.emit(text, "user")
            response = handle_command(text)
            self.message_signal.emit(response, "jarvis")
            speak(response)
        else:
            self.message_signal.emit("I didn't catch that. Please try again.", "jarvis")
        
        self.status_lbl.setText("● ACTIVE")
        self.status_lbl.setStyleSheet("color: #ec5b13; font-size: 10px; font-weight: bold; letter-spacing: 2px;")
        self.mic_btn.setText("HOLD TO SPEAK")
        self.mic_btn.setEnabled(True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = JarvisWindow()
    window.show()
    sys.exit(app.exec_())