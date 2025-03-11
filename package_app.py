#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Mistral OCR 应用打包脚本
使用PyInstaller将应用打包为EXE文件
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def ensure_pyinstaller():
    """确保PyInstaller已安装"""
    try:
        import PyInstaller
        print("PyInstaller已安装，版本:", PyInstaller.__version__)
    except ImportError:
        print("正在安装PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("PyInstaller安装完成")

def create_icon():
    """创建临时图标文件（如果不存在）"""
    icon_dir = Path("resources/icons")
    icon_path = icon_dir / "app_icon.ico"
    
    if not icon_dir.exists():
        os.makedirs(icon_dir)
    
    if not icon_path.exists():
        # 如果没有图标，尝试从PNG转换或使用简单图标
        png_icon = icon_dir / "app_icon.png"
        if png_icon.exists():
            try:
                from PIL import Image
                img = Image.open(png_icon)
                img.save(icon_path)
                print(f"已将PNG图标转换为ICO: {icon_path}")
            except Exception as e:
                print(f"无法转换图标: {e}")
                print("使用默认图标")
        else:
            print("未找到图标文件，使用默认图标")
    
    return icon_path if icon_path.exists() else None

def run_pyinstaller(icon_path=None):
    """运行PyInstaller打包应用"""
    print("开始打包应用...")
    
    # 基本命令
    cmd = [
        "pyinstaller",
        "--name=MistralOCR",
        "--onefile",
        "--windowed",
        "--clean",
        "--noconfirm",
        "--add-data=resources;resources"
    ]
    
    # 添加图标参数（如果有）
    if icon_path:
        cmd.append(f"--icon={icon_path}")
    
    # 添加主程序
    cmd.append("app.py")
    
    # 执行PyInstaller
    subprocess.check_call(cmd)
    
    print("应用打包完成！")
    print(f"可执行文件位置: {os.path.abspath('dist/MistralOCR.exe')}")

def cleanup_after_build():
    """清理打包后的临时文件"""
    print("清理临时文件...")
    
    # 仅保留dist目录，删除build和spec文件
    if os.path.exists("build"):
        shutil.rmtree("build")
    
    if os.path.exists("MistralOCR.spec"):
        os.remove("MistralOCR.spec")
    
    print("清理完成")

def main():
    """主打包流程"""
    print("=" * 50)
    print("Mistral OCR 应用打包工具")
    print("=" * 50)
    
    # 确保PyInstaller已安装
    ensure_pyinstaller()
    
    # 创建或检查图标
    icon_path = create_icon()
    
    # 运行PyInstaller
    run_pyinstaller(icon_path)
    
    # 清理
    cleanup_after_build()
    
    print("\n打包过程完成！应用程序已准备好分发。")
    print("您可以在'dist'目录中找到可执行文件。")

if __name__ == "__main__":
    main() 