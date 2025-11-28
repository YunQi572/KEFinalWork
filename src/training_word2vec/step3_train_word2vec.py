"""
步骤3: 训练Word2Vec模型
基于分词后的文本训练词向量模型
"""
import os
from pathlib import Path
from gensim.models import Word2Vec
import logging

# 配置日志
logging.basicConfig(
    format='%(asctime)s : %(levelname)s : %(message)s',
    level=logging.INFO
)


class SentenceIterator:
    """句子迭代器 - 用于大文件的内存友好读取"""
    
    def __init__(self, file_paths):
        self.file_paths = file_paths
    
    def __iter__(self):
        for file_path in self.file_paths:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    words = line.strip().split()
                    if words:  # 跳过空行
                        yield words


def train_word2vec_model(segmented_files, output_model_path):
    """训练Word2Vec模型"""
    
    print("=" * 60)
    print("开始训练Word2Vec模型")
    print("=" * 60)
    print()
    
    # 创建句子迭代器
    print("加载训练数据...")
    sentences = SentenceIterator(segmented_files)
    
    # 训练参数
    params = {
        'vector_size': 100,      # 词向量维度
        'window': 5,             # 上下文窗口大小
        'min_count': 2,          # 最小词频(出现次数少于此值的词会被忽略)
        'workers': 4,            # 训练并行数
        'sg': 1,                 # 1=Skip-gram, 0=CBOW
        'epochs': 10,            # 训练轮数
        'seed': 42               # 随机种子(保证可复现)
    }
    
    print("训练参数:")
    for key, value in params.items():
        print(f"  {key}: {value}")
    print()
    
    # 训练模型
    print("正在训练模型...")
    model = Word2Vec(sentences, **params)
    
    print()
    print("=" * 60)
    print("训练完成!")
    print("=" * 60)
    print()
    
    # 模型信息
    print("模型统计:")
    print(f"  词汇表大小: {len(model.wv)} 个词")
    print(f"  向量维度: {model.wv.vector_size}")
    print()
    
    # 保存模型
    print(f"保存模型到: {output_model_path}")
    model.wv.save_word2vec_format(output_model_path, binary=True)
    print("✓ 模型保存成功!")
    print()
    
    return model


def test_model(model):
    """测试模型效果"""
    print("=" * 60)
    print("模型效果测试")
    print("=" * 60)
    print()
    
    # 测试词汇
    test_words = [
        '松材线虫',
        '马尾松',
        '松墨天牛',
        '防治',
        '温度',
        '森林',
        '病害',
        '检疫'
    ]
    
    print("相似词查询:")
    print("-" * 60)
    
    for word in test_words:
        if word in model.wv:
            print(f"\n'{word}' 的相似词:")
            similar_words = model.wv.most_similar(word, topn=5)
            for similar_word, score in similar_words:
                print(f"  {similar_word}: {score:.4f}")
        else:
            print(f"\n'{word}' 不在词汇表中")
    
    print()
    print("-" * 60)
    
    # 词汇关系测试
    print("\n词汇关系测试:")
    print("-" * 60)
    
    # 计算词对相似度
    word_pairs = [
        ('松材线虫', '线虫'),
        ('马尾松', '黑松'),
        ('松墨天牛', '天牛'),
        ('防治', '治理'),
    ]
    
    for word1, word2 in word_pairs:
        if word1 in model.wv and word2 in model.wv:
            similarity = model.wv.similarity(word1, word2)
            print(f"  '{word1}' 与 '{word2}' 的相似度: {similarity:.4f}")
        else:
            missing = []
            if word1 not in model.wv:
                missing.append(word1)
            if word2 not in model.wv:
                missing.append(word2)
            print(f"  '{word1}' 与 '{word2}': 词汇不在表中 {missing}")
    
    print()


def main():
    """主函数"""
    
    # 设置路径
    current_dir = Path(__file__).parent
    segmented_dir = current_dir / "segmented_files"
    model_dir = current_dir / "model"
    
    # 检查输入目录
    if not segmented_dir.exists():
        print(f"错误: 找不到目录 {segmented_dir}")
        print("请先运行 step2_text_preprocessing.py")
        return
    
    # 创建模型输出目录
    model_dir.mkdir(exist_ok=True)
    
    # 查找所有分词文件
    segmented_files = list(segmented_dir.glob("*_seg.txt"))
    
    if not segmented_files:
        print(f"在 {segmented_dir} 中未找到分词文件!")
        return
    
    print(f"找到 {len(segmented_files)} 个训练文件:")
    for f in segmented_files:
        print(f"  - {f.name}")
    print()
    
    # 训练模型
    output_model_path = model_dir / "pinewood_nematode_word2vec.bin"
    model = train_word2vec_model(segmented_files, output_model_path)
    
    # 测试模型
    test_model(model)
    
    print("=" * 60)
    print("全部完成!")
    print(f"模型文件: {output_model_path}")
    print()
    print("使用方法:")
    print("  在 .env 文件中设置:")
    print(f"  WORD2VEC_MODEL_PATH={output_model_path.absolute()}")
    print("=" * 60)


if __name__ == "__main__":
    main()
