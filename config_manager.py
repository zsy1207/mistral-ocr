import os
import json
import base64
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from mistralai import Mistral

class ConfigManager:
    """配置管理类，负责API密钥和应用设置的存储和验证"""
    
    def __init__(self):
        """初始化配置管理器，创建必要的目录和文件"""
        self.app_data_dir = self._get_app_data_dir()
        self.config_file = self.app_data_dir / "config.json"
        self.key_file = self.app_data_dir / "key.bin"
        
        # 确保应用数据目录存在
        os.makedirs(self.app_data_dir, exist_ok=True)
        
        # 初始化或加载加密密钥
        if not self.key_file.exists():
            self._generate_encryption_key()
        
        # 加载或创建默认配置
        self.config = self._load_config()
    
    def _get_app_data_dir(self) -> Path:
        """获取应用数据目录路径"""
        if os.name == 'nt':  # Windows
            app_data = os.environ.get('APPDATA', '')
            return Path(app_data) / "MistralOCR"
        else:  # macOS / Linux
            home = os.environ.get('HOME', '')
            return Path(home) / ".mistral-ocr"
    
    def _generate_encryption_key(self):
        """生成并保存新的加密密钥"""
        # 使用随机盐生成密钥
        salt = os.urandom(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(b"MistralOCR"))
        
        # 保存密钥和盐
        with open(self.key_file, 'wb') as f:
            f.write(salt + key)
    
    def _get_encryption_key(self):
        """获取加密密钥"""
        with open(self.key_file, 'rb') as f:
            data = f.read()
        
        # 前16字节是盐
        salt = data[:16]
        key = data[16:]
        return key
    
    def _load_config(self) -> dict:
        """加载配置，如果不存在则创建默认配置"""
        if not self.config_file.exists():
            default_config = {
                "api_key": "",
                "output_dir": str(Path.home() / "MistralOCR_Results"),
                "theme": "light"
            }
            self._save_config(default_config)
            return default_config
        
        # 加载已有配置
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 解密API密钥
            if config.get("api_key"):
                key = self._get_encryption_key()
                fernet = Fernet(key)
                encrypted_api_key = config["api_key"].encode()
                config["api_key"] = fernet.decrypt(encrypted_api_key).decode()
            
            return config
        except Exception as e:
            print(f"加载配置时出错: {e}")
            # 发生错误时返回默认配置
            return {
                "api_key": "",
                "output_dir": str(Path.home() / "MistralOCR_Results"),
                "theme": "light"
            }
    
    def _save_config(self, config: dict):
        """保存配置到文件"""
        # 创建一个副本以避免修改原始配置
        config_to_save = config.copy()
        
        # 加密API密钥
        if config_to_save.get("api_key"):
            key = self._get_encryption_key()
            fernet = Fernet(key)
            encrypted_api_key = fernet.encrypt(config_to_save["api_key"].encode())
            config_to_save["api_key"] = encrypted_api_key.decode()
        
        # 保存配置
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config_to_save, f, indent=2)
    
    def get_api_key(self) -> str:
        """获取API密钥"""
        return self.config.get("api_key", "")
    
    def set_api_key(self, api_key: str):
        """设置API密钥"""
        self.config["api_key"] = api_key
        self._save_config(self.config)
    
    def get_output_dir(self) -> str:
        """获取输出目录"""
        return self.config.get("output_dir", str(Path.home() / "MistralOCR_Results"))
    
    def set_output_dir(self, output_dir: str):
        """设置输出目录"""
        self.config["output_dir"] = output_dir
        self._save_config(self.config)
    
    def get_theme(self) -> str:
        """获取主题设置"""
        return self.config.get("theme", "light")
    
    def set_theme(self, theme: str):
        """设置主题"""
        self.config["theme"] = theme
        self._save_config(self.config)
    
    def validate_api_key(self, api_key: str = None) -> bool:
        """验证API密钥是否有效"""
        if api_key is None:
            api_key = self.get_api_key()
        
        if not api_key:
            return False
        
        try:
            # 创建Mistral客户端并尝试一个简单请求
            client = Mistral(api_key=api_key)
            # 获取模型列表
            client.models.list()
            return True
        except Exception:
            return False 