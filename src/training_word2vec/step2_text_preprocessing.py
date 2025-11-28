"""
步骤2: 文本预处理和分词
使用jieba进行中文分词,并清洗文本
"""
import os
import re
import jieba
from pathlib import Path


def load_custom_words():
    """加载专业词汇表"""
    # 松材线虫病相关专业词汇
    custom_words = [
        '松材线虫', '松材线虫病', '松墨天牛', '马尾松', '黑松', '赤松',
        '湿地松', '华山松', '白皮松', '樟子松', '落叶松',
        '天牛', '媒介昆虫', '传播媒介', '病原体', '病原线虫',
        '萎蔫', '针叶变色', '树脂分泌', '导管堵塞',
        '疫木', '疫区', '病死木', '枯死木',
        '防治措施', '检疫', '化学防治', '生物防治', '物理防治',
        '松林', '森林病害', '林业有害生物', '森林生态',
        '寄主植物', '易感树种', '抗性树种',
        '温度', '湿度', '气候因子', '环境因素',
        '传播途径', '侵染', '致病机理', '危害症状',
        '监测预警', '早期诊断', '遥感监测',
        '伐除', '熏蒸', '焚烧', '除治',
    ]
    
    # 添加到jieba词典
    for word in custom_words:
        jieba.add_word(word)
    
    print(f"✓ 加载了 {len(custom_words)} 个专业词汇")


def clean_text(text):
    """清洗文本"""
    # 移除特殊字符和多余空白
    text = re.sub(r'\s+', ' ', text)  # 多个空白符替换为单个空格
    text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\s]', '', text)  # 只保留中英文和数字
    
    return text.strip()


def segment_text(text):
    """中文分词"""
    # 分词
    words = jieba.cut(text)
    
    # 过滤停用词和短词
    stop_words = {'的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', 
                  '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', 
                  '会', '着', '没有', '看', '好', '自己', '这', '等', '为', '与',
                  '及', '对', '等', '通过', '进行', '研究', '分析', '结果', '表明'}
    
    filtered_words = [
        word.strip() for word in words 
        if len(word.strip()) > 1 and word.strip() not in stop_words
    ]
    
    return filtered_words


def process_txt_file(txt_path, output_path):
    """处理单个TXT文件"""
    print(f"正在处理: {os.path.basename(txt_path)}")
    
    try:
        # 读取文本
        with open(txt_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        print(f"  原始文本长度: {len(text)} 字符")
        
        # 清洗文本
        cleaned_text = clean_text(text)
        print(f"  清洗后长度: {len(cleaned_text)} 字符")
        
        # 分词
        words = segment_text(cleaned_text)
        print(f"  分词结果: {len(words)} 个词")
        
        # 保存分词结果(每行一句,词之间用空格分隔)
        # 将词列表按句子重新组织
        sentences = []
        current_sentence = []
        
        for word in words:
            current_sentence.append(word)
            # 每50个词作为一句
            if len(current_sentence) >= 50:
                sentences.append(' '.join(current_sentence))
                current_sentence = []
        
        if current_sentence:
            sentences.append(' '.join(current_sentence))
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(sentences))
        
        print(f"  ✓ 保存成功! 共 {len(sentences)} 句")
        return True
        
    except Exception as e:
        print(f"  ✗ 处理失败: {e}")
        return False


def batch_process_texts():
    """批量处理所有TXT文件"""
    
    # 设置路径
    current_dir = Path(__file__).parent
    txt_dir = current_dir / "txt_files"
    output_dir = current_dir / "segmented_files"
    
    # 检查输入目录
    if not txt_dir.exists():
        print(f"错误: 找不到目录 {txt_dir}")
        print("请先运行 step1_pdf_to_txt.py")
        return
    
    # 创建输出目录
    output_dir.mkdir(exist_ok=True)
    
    # 加载自定义词典
    print("加载专业词汇...")
    load_custom_words()
    print()
    
    # 查找所有TXT文件
    txt_files = list(txt_dir.glob("*.txt"))
    
    if not txt_files:
        print(f"在 {txt_dir} 中未找到TXT文件!")
        return
    
    print("=" * 60)
    print(f"找到 {len(txt_files)} 个文本文件")
    print("=" * 60)
    print()
    
    success_count = 0
    
    for txt_file in txt_files:
        # 生成输出文件名
        output_filename = txt_file.stem + "_seg.txt"
        output_path = output_dir / output_filename
        
        # 处理文件
        if process_txt_file(txt_file, output_path):
            success_count += 1
        
        print()
    
    print("=" * 60)
    print(f"处理完成! 成功: {success_count}/{len(txt_files)}")
    print(f"分词文件保存在: {output_dir}")
    print("=" * 60)


if __name__ == "__main__":
    print("文本预处理和分词")
    print()
    
    # 检查依赖
    try:
        import jieba
        print("✓ jieba 已安装")
    except ImportError:
        print("✗ 请先安装 jieba:")
        print("  pip install jieba")
        exit(1)
    
    print()
    batch_process_texts()
