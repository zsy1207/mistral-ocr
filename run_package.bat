@echo off
echo 正在准备打包 Mistral OCR 应用...

rem 确保依赖已安装
echo 安装必要依赖...
pip install -r requirements.txt

rem 运行打包脚本
echo 开始打包应用...
python package_app.py

echo.
echo 如果打包成功，可执行文件位于 dist 目录中。
echo 按任意键退出...
pause > nul 