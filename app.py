#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt
from main_window import MainWindow

def main():
    """应用程序入口函数"""
    # 设置Qt属性
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # 创建应用程序实例
    app = QApplication(sys.argv)
    app.setApplicationName("Mistral OCR")
    app.setOrganizationName("MistralAI")
    
    # 设置应用程序图标
    icon_path = os.path.join(os.path.dirname(__file__), "resources/icons/app_icon.png")
    
    # 对于PyInstaller打包的应用
    if hasattr(sys, '_MEIPASS'):
        icon_path = os.path.join(sys._MEIPASS, "resources/icons/app_icon.png")
    
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    # 创建并显示主窗口
    window = MainWindow()
    window.show()
    
    # 启动事件循环
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 