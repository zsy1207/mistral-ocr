from mistralai import Mistral
from mistralai import DocumentURLChunk
from mistralai.models import OCRResponse
from pathlib import Path
import os
import base64
import time
from typing import Callable, Optional, Dict, Any, List

class OCREngine:
    """Mistral OCR引擎，负责PDF文件的OCR处理"""
    
    def __init__(self, api_key: str):
        """
        初始化OCR引擎
        
        Args:
            api_key: Mistral API密钥
        """
        self.api_key = api_key
        self.client = Mistral(api_key=api_key)
        
    def replace_images_in_markdown(self, markdown_str: str, images_dict: dict) -> str:
        """
        替换Markdown中的图片引用
        
        Args:
            markdown_str: Markdown字符串
            images_dict: 图片ID到图片路径的映射
            
        Returns:
            替换后的Markdown字符串
        """
        for img_name, img_path in images_dict.items():
            markdown_str = markdown_str.replace(f"![{img_name}]({img_name})", f"![{img_name}]({img_path})")
        return markdown_str
    
    def save_ocr_results(self, ocr_response: OCRResponse, output_dir: str, pdf_name: str) -> str:
        """
        保存OCR结果
        
        Args:
            ocr_response: OCR响应对象
            output_dir: 输出目录
            pdf_name: PDF文件名（不含扩展名）
            
        Returns:
            结果Markdown文件的路径
        """
        # 创建输出目录
        output_dir = Path(output_dir)
        os.makedirs(output_dir, exist_ok=True)
        images_dir = output_dir / "images"
        os.makedirs(images_dir, exist_ok=True)
        
        all_markdowns = []
        for page in ocr_response.pages:
            # 保存图片
            page_images = {}
            for img in page.images:
                try:
                    img_data = base64.b64decode(img.image_base64.split(',')[1])
                    img_path = images_dir / f"{img.id}.png"
                    with open(img_path, 'wb') as f:
                        f.write(img_data)
                    page_images[img.id] = f"images/{img.id}.png"
                except Exception as e:
                    print(f"保存图片时出错: {e}")
            
            # 处理markdown内容
            page_markdown = self.replace_images_in_markdown(page.markdown, page_images)
            all_markdowns.append(page_markdown)
        
        # 保存完整markdown，使用PDF文件名
        md_file_path = output_dir / f"{pdf_name}.md"
        with open(md_file_path, 'w', encoding='utf-8') as f:
            f.write("\n\n".join(all_markdowns))
            
        return str(md_file_path)
    
    def process_pdf(self, pdf_path: str, output_dir: str, progress_callback: Optional[Callable[[str, float], None]] = None) -> Dict[str, Any]:
        """
        处理PDF文件
        
        Args:
            pdf_path: PDF文件路径
            output_dir: 输出目录
            progress_callback: 进度回调函数，接收状态消息和进度百分比
            
        Returns:
            处理结果信息的字典
        """
        result = {
            "success": False,
            "message": "",
            "output_file": "",
            "output_dir": ""
        }
        
        try:
            # 确认PDF文件存在
            pdf_file = Path(pdf_path)
            if not pdf_file.is_file():
                raise FileNotFoundError(f"PDF文件不存在: {pdf_path}")
            
            # 通知进度：开始处理
            if progress_callback:
                progress_callback("正在准备PDF文件...", 0.1)
            
            # 上传文件
            try:
                uploaded_file = self.client.files.upload(
                    file={
                        "file_name": pdf_file.stem,
                        "content": pdf_file.read_bytes(),
                    },
                    purpose="ocr",
                )
            except Exception as e:
                raise Exception(f"上传PDF文件失败: {str(e)}")
            
            # 通知进度：上传完成
            if progress_callback:
                progress_callback("PDF上传完成，正在处理...", 0.3)
            
            # 获取签名URL
            try:
                signed_url = self.client.files.get_signed_url(file_id=uploaded_file.id, expiry=1)
            except Exception as e:
                raise Exception(f"获取签名URL失败: {str(e)}")
            
            # 通知进度：开始OCR
            if progress_callback:
                progress_callback("正在进行OCR处理...", 0.5)
            
            # 处理PDF
            try:
                pdf_response = self.client.ocr.process(
                    document=DocumentURLChunk(document_url=signed_url.url), 
                    model="mistral-ocr-latest", 
                    include_image_base64=True
                )
            except Exception as e:
                raise Exception(f"OCR处理失败: {str(e)}")
            
            # 通知进度：OCR完成，保存结果
            if progress_callback:
                progress_callback("OCR处理完成，正在保存结果...", 0.8)
            
            # 保存结果
            output_dir = output_dir or f"ocr_results_{pdf_file.stem}"
            output_file = self.save_ocr_results(pdf_response, output_dir, pdf_file.stem)
            
            # 通知进度：处理完成
            if progress_callback:
                progress_callback("处理完成！", 1.0)
            
            result["success"] = True
            result["message"] = "PDF处理成功"
            result["output_file"] = output_file
            result["output_dir"] = output_dir
            
        except FileNotFoundError as e:
            result["message"] = str(e)
        except Exception as e:
            result["message"] = f"处理PDF时出错: {str(e)}"
            
        return result
    
    def validate_connection(self) -> bool:
        """
        验证API连接是否有效
        
        Returns:
            连接有效返回True，否则返回False
        """
        try:
            self.client.models.list()
            return True
        except Exception:
            return False 