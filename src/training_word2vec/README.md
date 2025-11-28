# Word2Vec 模型训练指南

本目录用于训练松材线虫病领域的Word2Vec词向量模型。

## 📁 文件说明

- **PDF文件** - 6篇松材线虫病相关文献
- **step1_pdf_to_txt.py** - PDF转文本
- **step2_text_preprocessing.py** - 文本预处理和分词
- **step3_train_word2vec.py** - 训练Word2Vec模型
- **train_all.py** - 一键运行全部步骤
- **requirements.txt** - 训练所需依赖

## 🚀 快速开始

### 方式一: 一键运行(推荐)

```powershell
# 1. 安装依赖
pip install -r requirements.txt

# 2. 运行训练
python train_all.py
```

### 方式二: 分步运行

```powershell
# 1. 安装依赖
pip install pdfplumber jieba

# 2. PDF转TXT
python step1_pdf_to_txt.py

# 3. 文本预处理和分词
python step2_text_preprocessing.py

# 4. 训练模型
python step3_train_word2vec.py
```

## 📊 训练流程

### 步骤1: PDF提取文本
- 从6篇PDF文献中提取文本
- 输出到 `txt_files/` 目录

### 步骤2: 文本预处理
- 使用jieba进行中文分词
- 加载松材线虫病专业词汇
- 清洗和过滤停用词
- 输出到 `segmented_files/` 目录

### 步骤3: 训练模型
- 使用gensim训练Word2Vec
- 参数配置:
  - 词向量维度: 100
  - 窗口大小: 5
  - 最小词频: 2
  - 训练轮数: 10
  - 算法: Skip-gram
- 输出到 `model/` 目录

## 📝 训练参数

在 `step3_train_word2vec.py` 中可修改:

```python
params = {
    'vector_size': 100,    # 词向量维度
    'window': 5,           # 上下文窗口大小
    'min_count': 2,        # 最小词频
    'workers': 4,          # 并行数
    'sg': 1,               # Skip-gram
    'epochs': 10,          # 训练轮数
}
```

## 🎯 使用训练好的模型

### 1. 配置环境变量

在 `src/.env` 文件中添加:
```
WORD2VEC_MODEL_PATH=D:\Desktop_Files\知识工程\KEFinalWork\src\training_word2vec\model\pinewood_nematode_word2vec.bin
```

### 2. 重启后端服务

```powershell
cd src
python main.py
```

### 3. 测试效果

在前端页面输入新实体,系统会使用你训练的模型进行相似度计算!

## 📋 专业词汇表

模型已预加载以下专业词汇:
- 病原: 松材线虫、线虫病
- 寄主: 马尾松、黑松、赤松、湿地松等
- 媒介: 松墨天牛、天牛
- 症状: 萎蔫、针叶变色、树脂分泌
- 防治: 化学防治、生物防治、检疫措施
- 环境: 温度、湿度、气候因子

## 🔧 常见问题

### Q: PDF提取失败?
A: 安装 `pip install pdfplumber`

### Q: 分词效果不好?
A: 在 `step2_text_preprocessing.py` 中添加更多专业词汇

### Q: 模型训练时间长?
A: 可以减少 `epochs` 参数或增加 `min_count`

### Q: 模型文件太大?
A: 减小 `vector_size` 参数

## 📈 模型评估

训练完成后会自动测试常见词汇的相似度,例如:
- 松材线虫 → 线虫、病原体
- 马尾松 → 黑松、赤松
- 松墨天牛 → 天牛、媒介

## 💾 输出目录结构

```
training_word2vec/
├── txt_files/              # 提取的文本
├── segmented_files/        # 分词后的文本
└── model/                  # 训练的模型
    └── pinewood_nematode_word2vec.bin
```

---

祝训练顺利! 🎉
