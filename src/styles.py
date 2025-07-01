# Shared styling constants for Qt and CustomTkinter views

# Base colors
BG_DARK = "#18191A"
BG_DARK_SECONDARY = "#242526"
ENTRY_BG = "#23272F"
TEXT_COLOR = "#F5F6FA"
PRIMARY_COLOR = "#3A86FF"
PRIMARY_COLOR_DARK = "#265DAB"
BORDER_COLOR = "#3A3B3C"

# Qt style sheet built from the above colors
MODERN_QSS = f"""
QMainWindow, QWidget {{
    background-color: {BG_DARK};
    color: {TEXT_COLOR};
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 15px;
}}
QMenuBar, QMenu {{
    background-color: {BG_DARK_SECONDARY};
    color: {TEXT_COLOR};
}}
QMenuBar::item:selected, QMenu::item:selected {{
    background: {PRIMARY_COLOR};
    color: white;
}}
QTabWidget::pane {{
    border: 1px solid {BORDER_COLOR};
    border-radius: 8px;
    background: {BG_DARK};
}}
QTabBar::tab {{
    background: {BG_DARK_SECONDARY};
    color: {TEXT_COLOR};
    border-radius: 8px;
    padding: 8px 20px;
    margin: 2px;
}}
QTabBar::tab:selected {{
    background: {PRIMARY_COLOR};
    color: white;
}}
QPushButton {{
    background-color: {PRIMARY_COLOR};
    color: white;
    border: none;
    border-radius: 8px;
    padding: 8px 0px;
    font-size: 15px;
}}
QPushButton:hover {{
    background-color: {PRIMARY_COLOR_DARK};
}}
QLineEdit, QTextEdit, QComboBox, QSpinBox {{
    background-color: {ENTRY_BG};
    color: {TEXT_COLOR};
    border: 1px solid {BORDER_COLOR};
    border-radius: 8px;
    padding: 6px;
}}
QStatusBar {{
    background: {ENTRY_BG};
    color: {TEXT_COLOR};
    border-top: 1px solid {BORDER_COLOR};
}}
"""
