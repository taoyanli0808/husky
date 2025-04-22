
import os
import re

import fitz  # PyMuPDF
import pdfplumber

class Pdf:

    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.text = self._extract_text()
        self.sections = self._parse_sections()
        self.images = []
        self.content = ""
    
    def _extract_text(self):
        """提取PDF文本内容"""
        try:
            text = ""
            with pdfplumber.open(self.pdf_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() + "\n"
            return text.lower()
        except Exception as e:
            raise RuntimeError(f"PDF解析失败: {str(e)}")

    def _parse_sections(self):
        """优化的章节解析方法"""
        sections = {}
        current_section = None
        # 增强版正则表达式，匹配更复杂的标题格式
        section_pattern = re.compile(
            r'^(?:[#]*\s*)?'          # 匹配 # 号或编号
            r'(?:\d+[\.、]?\s*)?'     # 匹配数字编号（1. 或 1、）
            r'([\u4e00-\u9fa5a-zA-Z]{2,20})'  # 捕获核心标题文字
            r'[\s　]*$',              # 结尾空白
            re.IGNORECASE
        )

        for line in self.text.split('\n'):
            line = line.strip()
            if len(line) > 50:  # 过滤过长的内容行
                continue
                
            match = section_pattern.match(line)
            if match:
                # 提取核心标题文字（如"1.1 功能需求" -> "功能需求"）
                current_section = match.group(1).strip()
                sections[current_section] = []
            elif current_section:
                sections[current_section].append(line)
        
        # 合并章节内容并保留原始大小写
        return {k: '\n'.join(v) for k, v in sections.items()}

    def pdf_to_markdown_with_images(self):
        """
        生成带图片位置的Markdown文件
        """
        # 如果支持静态服务，本地存储改为上传CDN
        image_folder = os.path.join("static", "images")
        if not os.path.exists(image_folder):
            os.makedirs(image_folder)
        markdown, page_heights = [], {}  # 记录每页高度用于坐标换算
        
        with pdfplumber.open(self.pdf_path) as pdf:
            # 先处理文本
            for page_num, page in enumerate(pdf.pages):
                page_height = page.height
                page_heights[page_num] = page_height
                
                # 提取带坐标的文本
                words = page.extract_words(extra_attrs=["x0", "top", "x1", "bottom"])
                lines = {}
                for word in words:
                    y = round(word['top'])
                    lines.setdefault(y, []).append(word)
                
                # 按坐标排序
                for y in sorted(lines.keys()):
                    line_words = sorted(lines[y], key=lambda w: w['x0'])
                    line_text = "".join(w['text'] for w in line_words)
                    markdown.append({
                        "type": "text",
                        "content": line_text,
                        "page": page_num,
                        "y": y,
                        "x0": line_words[0]['x0']
                    })
        
        # 提取并合并图片信息
        self.pdf_path.seek(0)  # 确保指针在起始位置
        bytes_data = self.pdf_path.read()
        doc = fitz.open(stream=bytes_data, filetype="pdf")
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            img_list = page.get_images(full=True)
            
            for img_index, img_info in enumerate(img_list):
                xref = img_info[0]
                base_image = doc.extract_image(xref)
                image_data = base_image["image"]
                
                # 获取图片坐标
                pix = fitz.Pixmap(doc, xref)
                img_rect = page.get_image_bbox(img_info)
                
                # 转换为PDFPlumber坐标系
                pdfplumber_height = page_heights[page_num]
                y_top = pdfplumber_height - img_rect.y1
                y_bottom = pdfplumber_height - img_rect.y0
                img_path = f"{image_folder}/page{page_num+1}_img{img_index+1}.{base_image['ext']}"
                markdown.append({
                    "type": "image",
                    "path": img_path,
                    "page": page_num,
                    "y": (y_top + y_bottom) / 2,  # 取图片中心Y坐标
                    "x0": img_rect.x0,
                    "width": img_rect.width,
                    "height": img_rect.height
                })
                
                # 保存图片
                self.images.append(img_path)
                with open(markdown[-1]["path"], "wb") as f:
                    f.write(image_data)
        
        # 按页面和坐标排序所有元素
        sorted_elements = sorted(markdown, key=lambda x: (x["page"], x["y"]))
        
        # 生成Markdown内容
        output = []
        current_page = -1
        for elem in sorted_elements:
            if elem["page"] != current_page:
                output.append(f"\n\n# 第 {elem['page']+1} 页\n\n")
                current_page = elem["page"]
            
            if elem["type"] == "text":
                # 计算缩进（假设每40px为一级缩进）
                indent_level = int(elem["x0"] // 40)
                output.append(f"{'    ' * indent_level}{elem['content']}\n")
            else:
                # 图片用相对路径和注释标记位置
                output.append(
                    f"\n<!-- 图片位置: X={elem['x0']:.1f}px, 宽度={elem['width']:.1f}px -->\n"
                    f"![]({os.path.relpath(elem['path'], start=os.getcwd())})\n\n"
                )
        self.content = '\n'.join(output)
        
        return self.content, self.images
