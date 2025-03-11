import os
import sys
from pathlib import Path
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QLineEdit, QFileDialog, QProgressBar, 
    QGroupBox, QMessageBox, QSizePolicy, QSpacerItem, QStackedWidget
)
from PySide6.QtCore import Qt, QSize, Signal, QUrl, QMimeData, QTimer, QFileInfo
from PySide6.QtGui import QDrag, QDragEnterEvent, QDropEvent, QIcon, QPixmap
from config_manager import ConfigManager
from ocr_engine import OCREngine

class DropArea(QWidget):
    """自定义拖放区域，支持PDF文件拖放"""
    
    fileDropped = Signal(str)  # 文件拖放信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setObjectName("dropArea")
        
        # 设置固定高度但允许水平伸展
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setMinimumHeight(120)
        
        # 创建布局和标签
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        
        self.icon_label = QLabel(self)
        self.icon_label.setAlignment(Qt.AlignCenter)
        # 这里可以添加自定义图标
        # self.icon_label.setPixmap(QPixmap("resources/icons/pdf_icon.png").scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        
        self.text_label = QLabel("拖放PDF文件到这里，或点击选择文件", self)
        self.text_label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(self.icon_label)
        layout.addWidget(self.text_label)
        
        # 选择文件按钮
        self.browse_button = QPushButton("选择PDF文件", self)
        self.browse_button.setObjectName("secondaryButton")
        self.browse_button.clicked.connect(self.browse_file)
        layout.addWidget(self.browse_button, 0, Qt.AlignCenter)
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """处理拖拽进入事件"""
        mime_data = event.mimeData()
        if mime_data.hasUrls() and self._is_valid_drop(mime_data):
            self.setProperty("dragOver", True)
            self.style().polish(self)  # 更新样式
            event.acceptProposedAction()
        else:
            event.ignore()
    
    def dragLeaveEvent(self, event):
        """处理拖拽离开事件"""
        self.setProperty("dragOver", False)
        self.style().polish(self)  # 更新样式
        super().dragLeaveEvent(event)
    
    def dropEvent(self, event: QDropEvent):
        """处理拖放事件"""
        self.setProperty("dragOver", False)
        self.style().polish(self)  # 更新样式
        
        mime_data = event.mimeData()
        if mime_data.hasUrls() and self._is_valid_drop(mime_data):
            file_path = mime_data.urls()[0].toLocalFile()
            self.fileDropped.emit(file_path)
            event.acceptProposedAction()
        else:
            event.ignore()
    
    def _is_valid_drop(self, mime_data: QMimeData) -> bool:
        """检查拖放的是否为有效的PDF文件"""
        if not mime_data.hasUrls() or len(mime_data.urls()) != 1:
            return False
        
        file_url = mime_data.urls()[0]
        if not file_url.isLocalFile():
            return False
        
        file_path = file_url.toLocalFile()
        return file_path.lower().endswith('.pdf')
    
    def browse_file(self):
        """打开文件选择对话框"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择PDF文件", "", "PDF文件 (*.pdf)"
        )
        if file_path:
            self.fileDropped.emit(file_path)


class MainWindow(QMainWindow):
    """主窗口类"""
    
    def __init__(self):
        super().__init__()
        
        # 初始化配置管理器
        self.config_manager = ConfigManager()
        
        # 设置窗口属性
        self.setWindowTitle("Mistral OCR")
        self.setMinimumSize(700, 500)
        self.resize(800, 600)
        
        # 应用主题
        self.theme = self.config_manager.get_theme()
        if self.theme == "dark":
            self.setProperty("theme", "dark")
        
        # 加载样式表
        self._load_stylesheet()
        
        # 设置中央窗口部件
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # 创建主布局
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(20)
        
        # 初始化UI组件
        self._init_ui()
        
        # 加载保存的配置
        self._load_config()
        
        # OCR引擎实例
        self.ocr_engine = None
        
        # 保持打开文件的路径
        self.current_pdf_path = ""
    
    def _load_stylesheet(self):
        """加载应用样式表"""
        try:
            # 首先尝试常规路径
            style_path = os.path.join(os.path.dirname(__file__), "resources/styles/style.qss")
            
            # 检查路径是否存在
            if not os.path.exists(style_path):
                # 如果不存在，尝试打包后的路径
                base_path = os.path.dirname(os.path.abspath(sys.argv[0]))
                style_path = os.path.join(base_path, "resources/styles/style.qss")
                
                # 对于PyInstaller打包的应用
                if hasattr(sys, '_MEIPASS'):
                    style_path = os.path.join(sys._MEIPASS, "resources/styles/style.qss")
            
            if os.path.exists(style_path):
                with open(style_path, "r") as f:
                    self.setStyleSheet(f.read())
            else:
                print(f"样式表文件不存在: {style_path}")
        except Exception as e:
            print(f"加载样式表时出错: {e}")
    
    def _init_ui(self):
        """初始化UI组件"""
        # 标题和介绍
        title_label = QLabel("Mistral OCR", self)
        title_label.setObjectName("titleLabel")
        
        intro_label = QLabel("一个简洁现代的PDF OCR处理工具，基于Mistral AI API", self)
        
        self.main_layout.addWidget(title_label)
        self.main_layout.addWidget(intro_label)
        
        # ===== PDF导入区域 =====
        file_group = QGroupBox("选择PDF文件", self)
        file_layout = QVBoxLayout(file_group)
        
        # 创建拖放区域
        self.drop_area = DropArea(self)
        self.drop_area.fileDropped.connect(self.handle_file_dropped)
        file_layout.addWidget(self.drop_area)
        
        # 文件路径显示
        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel("PDF路径:", self))
        self.pdf_path_input = QLineEdit(self)
        self.pdf_path_input.setPlaceholderText("输入PDF文件路径或拖放文件")
        path_layout.addWidget(self.pdf_path_input, 1)
        
        file_layout.addLayout(path_layout)
        
        self.main_layout.addWidget(file_group)
        
        # ===== 设置区域 =====
        settings_group = QGroupBox("设置", self)
        settings_layout = QVBoxLayout(settings_group)
        
        # API密钥设置
        api_layout = QHBoxLayout()
        api_layout.addWidget(QLabel("API密钥:", self))
        self.api_key_input = QLineEdit(self)
        self.api_key_input.setPlaceholderText("输入Mistral AI API密钥")
        self.api_key_input.setEchoMode(QLineEdit.Password)
        api_layout.addWidget(self.api_key_input, 1)
        
        self.validate_api_button = QPushButton("验证", self)
        self.validate_api_button.setObjectName("secondaryButton")
        self.validate_api_button.clicked.connect(self.validate_api_key)
        api_layout.addWidget(self.validate_api_button)
        
        settings_layout.addLayout(api_layout)
        
        # 输出目录设置
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("输出目录:", self))
        self.output_dir_input = QLineEdit(self)
        self.output_dir_input.setPlaceholderText("选择OCR结果输出目录")
        output_layout.addWidget(self.output_dir_input, 1)
        
        self.browse_output_button = QPushButton("浏览", self)
        self.browse_output_button.setObjectName("secondaryButton")
        self.browse_output_button.clicked.connect(self.browse_output_dir)
        output_layout.addWidget(self.browse_output_button)
        
        settings_layout.addLayout(output_layout)
        
        self.main_layout.addWidget(settings_group)
        
        # ===== 处理控制区域 =====
        control_group = QGroupBox("操作", self)
        control_layout = QVBoxLayout(control_group)
        
        # 进度条和状态
        progress_layout = QVBoxLayout()
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(10)
        
        self.status_label = QLabel("准备就绪", self)
        self.status_label.setObjectName("statusLabel")
        self.status_label.setAlignment(Qt.AlignCenter)
        
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.status_label)
        
        control_layout.addLayout(progress_layout)
        
        # 处理按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch(1)
        
        self.theme_button = QPushButton("切换主题", self)
        self.theme_button.setObjectName("secondaryButton")
        self.theme_button.clicked.connect(self.toggle_theme)
        button_layout.addWidget(self.theme_button)
        
        self.process_button = QPushButton("开始处理", self)
        self.process_button.clicked.connect(self.process_pdf)
        button_layout.addWidget(self.process_button)
        
        control_layout.addLayout(button_layout)
        
        self.main_layout.addWidget(control_group)
        
        # 底部间距
        self.main_layout.addStretch(1)
    
    def _load_config(self):
        """加载保存的配置"""
        self.api_key_input.setText(self.config_manager.get_api_key())
        self.output_dir_input.setText(self.config_manager.get_output_dir())
    
    def handle_file_dropped(self, file_path: str):
        """处理拖放的文件"""
        self.pdf_path_input.setText(file_path)
        self.current_pdf_path = file_path
        self.status_label.setText(f"已选择文件: {Path(file_path).name}")
    
    def browse_output_dir(self):
        """浏览并选择输出目录"""
        output_dir = QFileDialog.getExistingDirectory(
            self, "选择输出目录", self.output_dir_input.text()
        )
        if output_dir:
            self.output_dir_input.setText(output_dir)
            self.config_manager.set_output_dir(output_dir)
    
    def validate_api_key(self):
        """验证API密钥是否有效"""
        api_key = self.api_key_input.text().strip()
        if not api_key:
            QMessageBox.warning(self, "验证失败", "请输入API密钥")
            return
        
        self.status_label.setText("正在验证API密钥...")
        self.validate_api_button.setEnabled(False)
        self.validate_api_button.setText("验证中...")
        
        # 创建OCR引擎并验证
        try:
            temp_engine = OCREngine(api_key)
            valid = temp_engine.validate_connection()
            
            if valid:
                QMessageBox.information(self, "验证成功", "API密钥有效")
                self.config_manager.set_api_key(api_key)
                self.status_label.setText("API密钥验证成功")
            else:
                QMessageBox.warning(self, "验证失败", "API密钥无效或网络连接问题")
                self.status_label.setText("API密钥验证失败")
        except Exception as e:
            QMessageBox.critical(self, "验证错误", f"验证过程中出错: {str(e)}")
            self.status_label.setText("API密钥验证出错")
        
        self.validate_api_button.setEnabled(True)
        self.validate_api_button.setText("验证")
    
    def process_pdf(self):
        """处理PDF文件"""
        # 检查PDF路径
        pdf_path = self.pdf_path_input.text().strip()
        if not pdf_path:
            QMessageBox.warning(self, "路径错误", "请选择PDF文件")
            return
        
        # 检查API密钥
        api_key = self.api_key_input.text().strip()
        if not api_key:
            QMessageBox.warning(self, "API密钥错误", "请输入API密钥")
            return
        
        # 检查输出目录
        output_dir = self.output_dir_input.text().strip()
        if not output_dir:
            # 使用默认输出目录
            output_dir = self.config_manager.get_output_dir()
            self.output_dir_input.setText(output_dir)
        
        # 禁用处理按钮
        self.process_button.setEnabled(False)
        self.process_button.setText("处理中...")
        
        # 保存API密钥和输出目录
        self.config_manager.set_api_key(api_key)
        self.config_manager.set_output_dir(output_dir)
        
        # 创建OCR引擎
        self.ocr_engine = OCREngine(api_key)
        
        # 开始处理
        try:
            self.status_label.setText("开始处理PDF...")
            self.progress_bar.setValue(0)
            
            def progress_callback(message, progress):
                self.status_label.setText(message)
                self.progress_bar.setValue(int(progress * 100))
            
            # 处理PDF
            result = self.ocr_engine.process_pdf(pdf_path, output_dir, progress_callback)
            
            if result["success"]:
                self.status_label.setText(f"处理成功: {result['message']}")
                QMessageBox.information(
                    self, 
                    "处理成功", 
                    f"PDF处理成功！\n\n结果保存在: {result['output_dir']}"
                )
            else:
                self.status_label.setText(f"处理失败: {result['message']}")
                QMessageBox.warning(self, "处理失败", f"PDF处理失败: {result['message']}")
        except Exception as e:
            self.status_label.setText(f"处理出错: {str(e)}")
            QMessageBox.critical(self, "处理错误", f"处理过程中出错: {str(e)}")
        
        # 重新启用处理按钮
        self.process_button.setEnabled(True)
        self.process_button.setText("开始处理")
    
    def toggle_theme(self):
        """切换明亮/暗黑主题"""
        if self.theme == "light":
            self.theme = "dark"
            self.setProperty("theme", "dark")
        else:
            self.theme = "light"
            self.setProperty("theme", "")
        
        # 更新所有子控件的主题属性
        for widget in self.findChildren(QWidget):
            if self.theme == "dark":
                widget.setProperty("theme", "dark")
            else:
                widget.setProperty("theme", "")
            widget.style().polish(widget)
        
        # 保存主题设置
        self.config_manager.set_theme(self.theme)
        
        # 重新应用样式表，确保所有组件都刷新
        self._load_stylesheet() 