# 松材线虫病知识图谱系统

一个基于 **Vue 3** + **FastAPI** 的知识图谱可视化系统,支持智能推理新增节点。

## 🌟 功能特性

- ✨ **知识图谱可视化** - 使用 ECharts 力导向图展示实体和关系
- 🤖 **智能节点推理** - 结合 Word2Vec 和 Kimi API 自动推理新实体关系
- 📊 **完整的增删改查** - 支持节点和边的全面管理
- 🎨 **现代化UI** - 基于 Element Plus 的美观界面
- 🔄 **实时交互** - 支持拖拽、缩放、点击查看详情

## 📦 技术栈

### 后端
- **FastAPI** - 现代化的 Python Web 框架
- **MySQL** - 关系型数据库 (kproject数据库)
- **gensim** - Word2Vec 词向量模型
- **OpenAI SDK** - 调用 Kimi (Moonshot AI) API

### 前端
- **Vue 3** - 采用 Composition API
- **Element Plus** - UI 组件库
- **ECharts** - 数据可视化
- **Axios** - HTTP 客户端

## 🚀 快速开始

### 1. 环境要求

- Python 3.9+
- Node.js 14+
- npm 或 yarn
- **MySQL 8.0+** (已安装并运行)

### 2. MySQL数据库配置

**当前配置**:
- 主机: localhost:3306
- 数据库: kproject（使用时可以改成你自己的，下面同理）
- 用户: root
- 密码: xyd123456

如需修改,请编辑 `src/main.py` 和 `src/init_db.py` 中的 `DB_CONFIG`

详细配置说明见 [MYSQL_CONFIG.md](MYSQL_CONFIG.md)

### 3. 后端安装与运行

```powershell
# 进入后端目录
cd src

# 安装依赖
pip install -r requirements.txt

# 初始化数据库(创建表和示例数据)
python init_db.py

# (可选) 配置 Kimi API 密钥
# 复制 .env.example 为 .env 并填入你的 API 密钥
# $env:MOONSHOT_API_KEY="your_api_key_here"

# 启动后端服务
python main.py
```

后端服务将在 `http://localhost:8000` 启动

### 4. 前端安装与运行

```powershell
# 进入前端目录
cd ui

# 安装依赖
npm install

# 启动开发服务器
npm run serve
```

前端服务将在 `http://localhost:8080` 启动

### 5. 访问系统

在浏览器中打开 `http://localhost:8080`

## 📖 使用说明

### 查看知识图谱

- 打开页面后自动加载完整图谱
- 可以拖拽节点调整位置
- 可以缩放和平移画布

### 智能添加节点

1. 在顶部搜索框输入新实体名称(如"湿地松")
2. 点击"智能添加"按钮
3. 系统将:
   - 使用 Word2Vec 找到相似实体
   - 查询图谱中的关联实体
   - 调用 Kimi API 推理关系
   - 自动添加到图谱中

### 编辑节点

- 点击图谱中的节点
- 在弹出对话框中可以:
  - 修改节点名称
  - 删除节点(会删除所有相关关系)

### 编辑关系

- 点击图谱中的连线(边)
- 在弹出对话框中可以:
  - 修改关系类型
  - 删除该关系

## 🔧 配置说明

### Kimi API 配置

如果你有 Moonshot AI 的 API 密钥:

1. 在 `src/` 目录创建 `.env` 文件
2. 添加配置:
```
MOONSHOT_API_KEY=your_moonshot_api_key_here
```

或者在启动前设置环境变量:
```powershell
$env:MOONSHOT_API_KEY="your_api_key_here"
```

**注意**: 如果没有配置 API 密钥,系统会使用内置的规则推理,仍可正常使用。

### Word2Vec 模型配置

如果你有训练好的 Word2Vec 模型:

1. 将模型文件放在 `src/models/` 目录
2. 在 `.env` 中配置:
```
WORD2VEC_MODEL_PATH=./models/word2vec.bin
```

**注意**: 如果没有配置模型,系统会使用内置的 Mock 映射,仍可正常使用。

## 📊 数据库结构

### knowledge_triples 表
```sql
CREATE TABLE knowledge_triples (
    id INT AUTO_INCREMENT PRIMARY KEY,
    head_entity VARCHAR(255) NOT NULL,   -- 头实体
    relation VARCHAR(100) NOT NULL,      -- 关系
    tail_entity VARCHAR(255) NOT NULL,   -- 尾实体
    INDEX idx_head_entity (head_entity),
    INDEX idx_tail_entity (tail_entity)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### valid_relations 表
```sql
CREATE TABLE valid_relations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    relation_name VARCHAR(100) UNIQUE NOT NULL  -- 有效关系名称
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

## 🔌 API 接口

### 获取完整图谱
```
GET /api/graph
```

### 智能新增节点
```
POST /api/node/add
Body: { "name": "实体名称" }
```

### 删除节点
```
DELETE /api/node/delete
Body: { "name": "节点名称" }
```

### 更新节点
```
PUT /api/node/update
Body: { "old_name": "旧名称", "new_name": "新名称" }
```

### 删除边
```
DELETE /api/edge/delete/{edge_id}
```

### 更新边
```
PUT /api/edge/update
Body: { "id": 1, "head_entity": "A", "relation": "关系", "tail_entity": "B" }
```

### 获取有效关系列表
```
GET /api/relations
```

## 📁 项目结构

```
KEFinalWork/
├── src/                    # 后端代码
│   ├── main.py            # FastAPI 主应用
│   ├── ai_service.py      # AI 服务(Word2Vec + Kimi)
│   ├── db_manager.py      # 数据库管理器(原有)
│   ├── init_db.py         # 数据库初始化脚本
│   ├── requirements.txt   # Python 依赖
│   └── .env.example       # 环境变量示例
├── ui/                     # 前端代码
│   ├── src/
│   │   ├── api/           # API 接口封装
│   │   ├── components/    # Vue 组件
│   │   │   └── KnowledgeGraph.vue  # 图谱组件
│   │   ├── views/         # 页面视图
│   │   │   └── HomeView.vue        # 主页面
│   │   ├── App.vue        # 根组件
│   │   └── main.js        # 应用入口
│   └── package.json       # 前端依赖
└── README.md              # 项目文档
```

## 🎯 智能推理流程

当用户输入新实体 A (如"湿地松")时:

1. **相似度分析**: Word2Vec 找到最相似的词 B (如"马尾松")
2. **图谱遍历**: 查询数据库找到与 B 相关的实体 C (如"松材线虫")
3. **关系推理**: Kimi API 从有效关系列表中选择最合适的关系 (如"易感")
4. **数据入库**: 将三元组 (湿地松, 易感, 松材线虫) 存入数据库
5. **图谱更新**: 前端自动刷新显示新增的节点和关系

## 🐛 常见问题

### Q: 后端启动失败

- 确保已安装所有 Python 依赖: `pip install -r requirements.txt`
- 确保 MySQL 服务正在运行
- 检查数据库配置是否正确 (用户名、密码、数据库名)
- 检查端口 8000 是否被占用

### 2. 前端连接失败

- 确保后端服务已启动
- 检查 `ui/src/api/index.js` 中的 baseURL 是否正确

### 3. 智能添加失败

- 如果没有配置 Kimi API,系统会使用内置规则
- 确保数据库中有足够的数据支持推理
- 查看后端日志了解具体错误

## 📝 开发说明

### 添加新的关系类型

1. 编辑 `src/init_db.py` 中的 `relations` 列表
2. 重新运行 `python init_db.py`

### 自定义图谱样式

编辑 `ui/src/components/KnowledgeGraph.vue` 中的 ECharts 配置

## 📄 许可证

MIT License

## 👥 作者

Knowledge Engineering Final Project

---

如有问题,请查看项目文档或提交 Issue。
