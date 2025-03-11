# Mistral OCR 应用

一个简洁现代的PDF OCR处理应用，基于Mistral AI API，提供PDF文档的光学字符识别功能。

## 下载

Windows用户可以直接下载可执行文件：
- [下载 MistralOCR.exe](https://github.com/zsy1207/mistral-ocr/releases/download/v1.0.0/MistralOCR.exe)

或访问[Releases页面](https://github.com/zsy1207/mistral-ocr/releases)获取最新版本。

## 功能特点

- 简洁现代的用户界面，结合苹果和谷歌的设计风格
- 支持通过文件路径或拖放方式导入PDF
- 自动将PDF内容转换为Markdown格式
- 保存并提取PDF中的图片
- 支持自定义输出路径
- API密钥本地安全存储
- API连通性检测
- 响应式界面设计，适配各种窗口大小

## 安装

1. 克隆该仓库：
```
git clone https://github.com/yourusername/mistral-ocr.git
cd mistral-ocr
```

2. 安装依赖：
```
pip install -r requirements.txt
```

## 使用方法

1. 运行应用：
```
python app.py
```

2. 设置Mistral AI API密钥（首次运行时）
3. 选择PDF文件（输入路径或拖放文件）
4. 设置输出路径（可选）
5. 点击"开始处理"按钮
6. 处理完成后，可在指定的输出目录查看结果

## 打包为可执行文件(EXE)

如果需要将应用打包为Windows可执行文件(.exe)，可以使用提供的打包脚本：

1. 确保已安装所有依赖：
```
pip install -r requirements.txt
pip install pyinstaller pillow
```

2. 运行打包脚本：
```
python package_app.py
```

3. 打包完成后，可在`dist`目录中找到可执行文件`MistralOCR.exe`

## 输出结果

应用将在指定的输出目录中生成：
- 一个与原PDF同名的Markdown文件
- 一个images文件夹，包含从PDF中提取的所有图片

## 系统要求

- Python 3.8 或更高版本
- 支持Windows、macOS和Linux操作系统

## 获取Mistral AI API密钥

使用本应用程序需要Mistral AI的API密钥，您可以通过以下步骤获取：

1. 访问Mistral AI官方网站 [https://auth.mistral.ai/ui/registration](https://auth.mistral.ai/ui/registration) 注册账号或登录
2. 注册/登录成功后，前往API密钥页面：[https://console.mistral.ai/api-keys/](https://console.mistral.ai/api-keys/)
3. 点击"Create new key"（创建新密钥）按钮
4. 为您的密钥命名并设置过期日期
## 许可证

[MIT License](LICENSE) 
