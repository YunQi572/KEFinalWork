"""
步骤1: PDF转TXT文本提取
从PDF文件中提取文本内容并保存为TXT文件
"""
import os
from pathlib import Path

def extract_text_from_pdf(pdf_path, output_txt_path):
    """
    从PDF提取文本
    支持两种方法: PyPDF2 (纯文本PDF) 和 pdfplumber (更强大)
    """
    try:
        # 方法1: 使用 pdfplumber (推荐,效果更好)
        import pdfplumber
        
        print(f"正在提取: {os.path.basename(pdf_path)}")
        
        text_content = []
        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)
            print(f"  总页数: {total_pages}")
            
            for i, page in enumerate(pdf.pages, 1):
                text = page.extract_text()
                if text:
                    text_content.append(text)
                if i % 10 == 0:
                    print(f"  已处理: {i}/{total_pages} 页")
        
        # 合并并保存
        full_text = '\n'.join(text_content)
        
        with open(output_txt_path, 'w', encoding='utf-8') as f:
            f.write(full_text)
        
        print(f"  ✓ 提取成功! 字符数: {len(full_text)}")
        return True
        
    except ImportError:
        print("  ! pdfplumber未安装,尝试使用PyPDF2...")
        
        try:
            # 方法2: 使用 PyPDF2 (备选方案)
            from PyPDF2 import PdfReader
            
            print(f"正在提取: {os.path.basename(pdf_path)}")
            
            reader = PdfReader(pdf_path)
            total_pages = len(reader.pages)
            print(f"  总页数: {total_pages}")
            
            text_content = []
            for i, page in enumerate(reader.pages, 1):
                text = page.extract_text()
                if text:
                    text_content.append(text)
                if i % 10 == 0:
                    print(f"  已处理: {i}/{total_pages} 页")
            
            # 合并并保存
            full_text = '\n'.join(text_content)
            
            with open(output_txt_path, 'w', encoding='utf-8') as f:
                f.write(full_text)
            
            print(f"  ✓ 提取成功! 字符数: {len(full_text)}")
            return True
            
        except ImportError:
            print("  ✗ 错误: 请先安装 PDF 处理库")
            print("  pip install pdfplumber")
            print("  或者")
            print("  pip install PyPDF2")
            return False
    
    except Exception as e:
        print(f"  ✗ 提取失败: {e}")
        return False


def batch_convert_pdfs():
    """批量转换所有PDF文件"""
    
    # 设置路径
    current_dir = Path(__file__).parent
    pdf_dir = current_dir
    txt_dir = current_dir / "txt_files"
    
    # 创建输出目录
    txt_dir.mkdir(exist_ok=True)
    
    # 查找所有PDF文件
    pdf_files = list(pdf_dir.glob("*.pdf"))
    
    if not pdf_files:
        print("未找到PDF文件!")
        return
    
    print("=" * 60)
    print(f"找到 {len(pdf_files)} 个PDF文件")
    print("=" * 60)
    print()
    
    success_count = 0
    fail_count = 0
    
    for pdf_file in pdf_files:
        # 生成输出文件名
        txt_filename = pdf_file.stem + ".txt"
        txt_path = txt_dir / txt_filename
        
        # 提取文本
        if extract_text_from_pdf(pdf_file, txt_path):
            success_count += 1
        else:
            fail_count += 1
        
        print()
    
    print("=" * 60)
    print(f"转换完成! 成功: {success_count}, 失败: {fail_count}")
    print(f"文本文件保存在: {txt_dir}")
    print("=" * 60)


if __name__ == "__main__":
    print("松材线虫病文献 - PDF转TXT")
    print()
    
    # 检查依赖
    try:
        import pdfplumber
        print("✓ pdfplumber 已安装")
    except ImportError:
        try:
            from PyPDF2 import PdfReader
            print("✓ PyPDF2 已安装")
        except ImportError:
            print("✗ 请先安装 PDF 处理库:")
            print("  pip install pdfplumber  (推荐)")
            print("  或")
            print("  pip install PyPDF2")
            exit(1)
    
    print()
    batch_convert_pdfs()
