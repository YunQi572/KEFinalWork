"""
一键运行: 完整的Word2Vec训练流程
从PDF到模型的完整pipeline
"""
import sys
from pathlib import Path

def print_header(title):
    """打印标题"""
    print("\n")
    print("=" * 70)
    print(f"  {title}")
    print("=" * 70)
    print()


def check_dependencies():
    """检查依赖库"""
    print_header("检查依赖库")
    
    dependencies = {
        'pdfplumber': False,
        'PyPDF2': False,
        'jieba': False,
        'gensim': False,
    }
    
    # 检查PDF处理库
    try:
        import pdfplumber
        dependencies['pdfplumber'] = True
        print("✓ pdfplumber 已安装")
    except ImportError:
        try:
            from PyPDF2 import PdfReader
            dependencies['PyPDF2'] = True
            print("✓ PyPDF2 已安装")
        except ImportError:
            print("✗ PDF处理库未安装")
            print("  请运行: pip install pdfplumber")
    
    # 检查jieba
    try:
        import jieba
        dependencies['jieba'] = True
        print("✓ jieba 已安装")
    except ImportError:
        print("✗ jieba 未安装")
        print("  请运行: pip install jieba")
    
    # 检查gensim
    try:
        import gensim
        dependencies['gensim'] = True
        print("✓ gensim 已安装")
    except ImportError:
        print("✗ gensim 未安装")
        print("  请运行: pip install gensim")
    
    print()
    
    # 检查是否所有依赖都满足
    if not (dependencies['pdfplumber'] or dependencies['PyPDF2']):
        print("缺少必要依赖!")
        print("\n请安装:")
        print("  pip install pdfplumber jieba gensim")
        return False
    
    if not (dependencies['jieba'] and dependencies['gensim']):
        print("缺少必要依赖!")
        print("\n请安装:")
        print("  pip install jieba gensim")
        return False
    
    return True


def run_step1():
    """步骤1: PDF转TXT"""
    print_header("步骤 1/3: PDF转TXT文本提取")
    
    try:
        import step1_pdf_to_txt
        step1_pdf_to_txt.batch_convert_pdfs()
        return True
    except Exception as e:
        print(f"✗ 步骤1失败: {e}")
        return False


def run_step2():
    """步骤2: 文本预处理和分词"""
    print_header("步骤 2/3: 文本预处理和分词")
    
    try:
        import step2_text_preprocessing
        step2_text_preprocessing.batch_process_texts()
        return True
    except Exception as e:
        print(f"✗ 步骤2失败: {e}")
        return False


def run_step3():
    """步骤3: 训练Word2Vec模型"""
    print_header("步骤 3/3: 训练Word2Vec模型")
    
    try:
        import step3_train_word2vec
        step3_train_word2vec.main()
        return True
    except Exception as e:
        print(f"✗ 步骤3失败: {e}")
        return False


def main():
    """主函数"""
    
    print()
    print("*" * 70)
    print("*" + " " * 68 + "*")
    print("*" + "  松材线虫病 Word2Vec 模型训练 - 一键运行".center(66) + "*")
    print("*" + " " * 68 + "*")
    print("*" * 70)
    
    # 检查依赖
    if not check_dependencies():
        print("\n请先安装依赖库,然后重新运行此脚本!")
        sys.exit(1)
    
    # 运行步骤1
    if not run_step1():
        print("\n训练流程中断!")
        sys.exit(1)
    
    input("\n按回车键继续到步骤2...")
    
    # 运行步骤2
    if not run_step2():
        print("\n训练流程中断!")
        sys.exit(1)
    
    input("\n按回车键继续到步骤3...")
    
    # 运行步骤3
    if not run_step3():
        print("\n训练流程中断!")
        sys.exit(1)
    
    # 完成
    print()
    print("*" * 70)
    print("*" + " " * 68 + "*")
    print("*" + "  全部完成! 🎉".center(66) + "*")
    print("*" + " " * 68 + "*")
    print("*" * 70)
    print()
    
    model_path = Path(__file__).parent / "model" / "pinewood_nematode_word2vec.bin"
    print(f"模型位置: {model_path.absolute()}")
    print()
    print("下一步:")
    print("  1. 在 src/.env 文件中配置模型路径")
    print(f"     WORD2VEC_MODEL_PATH={model_path.absolute()}")
    print("  2. 重启后端服务即可使用!")
    print()


if __name__ == "__main__":
    main()
