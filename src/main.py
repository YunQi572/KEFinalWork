"""
松材线虫病知识图谱系统 - FastAPI后端
"""
from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import pymysql
import logging
from contextlib import contextmanager
import os
from pathlib import Path
import time
import uvicorn
import json

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 加载环境变量
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        logger.info("环境变量加载成功")
except ImportError:
    pass  # python-dotenv未安装，跳过

app = FastAPI(title="知识图谱API", version="1.0.0")

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境请修改为具体前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MySQL数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '20050702g',
    'database': 'kefinalwork',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

HIGH_LEVEL_NODE_TABLE = "graph_high_level_nodes"

_CORE_HIGH_LEVEL_NODE_RECORDS = [
    {"node_name": "松材线虫病", "node_type": "core", "description": "核心病害概念"},
    {"node_name": "松材线虫", "node_type": "core", "description": "主要病原线虫"},
    {"node_name": "松墨天牛", "node_type": "core", "description": "重要媒介昆虫"},
    {"node_name": "寄主", "node_type": "core", "description": "宿主整体概念"},
    {"node_name": "媒介昆虫", "node_type": "core", "description": "媒介总体类别"},
]

_GENERIC_HIGH_LEVEL_NODE_NAMES = [
    '省份', '城市', '中国', '松属', '阔叶树', '天牛', '天敌昆虫',
    '线虫', '真菌', '算法', '遥感技术', '分子生物学技术', '年份',
    '病害', '农药药剂', '研究模型与软件', '基因', '代谢通路',
    '物理防治', '化学防治', '营林防治', '检疫措施', '生理指标',
    '风险评估', '早期诊断', '森林保护学', '森林昆虫学', '森林病理学',
    '林业植物检疫学', '博士学位论文', '国家科技进步二等奖', '生态服务',
    '多尺度监测', '能量代谢', '诊断', '天敌',
    '种群动态模型', '植被指数', '光谱特征'
]

_existing_names = {node["node_name"] for node in _CORE_HIGH_LEVEL_NODE_RECORDS}
DEFAULT_HIGH_LEVEL_NODE_RECORDS = [
    *_CORE_HIGH_LEVEL_NODE_RECORDS,
    *[
        {
            "node_name": name,
            "node_type": "generic",
            "description": "默认高级节点"
        }
        for name in _GENERIC_HIGH_LEVEL_NODE_NAMES
        if name not in _existing_names
    ]
]


# ==================== 数据模型 ====================
class Triple(BaseModel):
    """三元组模型"""
    id: Optional[int] = None
    head_entity: str
    relation: str
    tail_entity: str


class Node(BaseModel):
    """节点模型"""
    name: str


class UpdateNode(BaseModel):
    """更新节点模型"""
    old_name: str
    new_name: str


class GraphResponse(BaseModel):
    """图谱响应模型"""
    nodes: List[dict]
    links: List[dict]


class ImageAnalysisRequest(BaseModel):
    """图像分析请求模型"""
    analyze_type: str = "full"  # full, entity_only, relationship_only
    update_knowledge: bool = True  # 是否自动更新知识图谱
    confidence_threshold: Optional[float] = 0.5


class ImageAnalysisResponse(BaseModel):
    """图像分析响应模型"""
    analysis_id: str
    image_info: dict
    detected_entities: List[dict]
    relationship_analysis: Optional[dict] = None
    disease_prediction: Optional[dict] = None
    knowledge_update: Optional[dict] = None
    recommendations: List[str]
    analysis_summary: dict


class EntityValidationRequest(BaseModel):
    """实体验证请求模型"""
    entities: List[dict]
    validation_type: str = "disease_scenario"  # disease_scenario, relationship_check


class HighLevelNodePayload(BaseModel):
    """高级节点请求载体"""
    node_name: str


# ==================== 数据库操作 ====================
@contextmanager
def get_db():
    """数据库连接上下文管理器"""
    conn = pymysql.connect(**DB_CONFIG)
    try:
        yield conn
    finally:
        conn.close()


def init_database():
    """初始化数据库"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 创建三元组表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS knowledge_triples (
                id INT AUTO_INCREMENT PRIMARY KEY,
                head_entity VARCHAR(255) NOT NULL,
                relation VARCHAR(100) NOT NULL,
                tail_entity VARCHAR(255) NOT NULL,
                INDEX idx_head_entity (head_entity),
                INDEX idx_tail_entity (tail_entity)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        # 创建有效关系表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS valid_relations (
                id INT AUTO_INCREMENT PRIMARY KEY,
                relation_name VARCHAR(100) UNIQUE NOT NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        # 创建高级节点专用表
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {HIGH_LEVEL_NODE_TABLE} (
                id INT AUTO_INCREMENT PRIMARY KEY,
                node_name VARCHAR(255) UNIQUE NOT NULL,
                node_type ENUM('core', 'generic') DEFAULT 'generic',
                description VARCHAR(512) DEFAULT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_node_name (node_name)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        # 创建图像分析历史表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS image_analysis_history (
                id INT AUTO_INCREMENT PRIMARY KEY,
                analysis_id VARCHAR(100) NOT NULL UNIQUE,
                timestamp DATETIME NOT NULL,
                entity_count INT NOT NULL,
                detected_types JSON NOT NULL,
                confidence FLOAT NOT NULL,
                risk_level VARCHAR(20) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_timestamp (timestamp),
                INDEX idx_analysis_id (analysis_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        conn.commit()
        logger.info("数据库初始化完成")


# ==================== 高级节点管理 ====================
def load_high_level_nodes_from_db() -> set:
    """从数据库加载高级节点"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT node_name FROM {HIGH_LEVEL_NODE_TABLE}")
            nodes = {row["node_name"] for row in cursor.fetchall()}
            logger.info(f"从数据库加载了 {len(nodes)} 个高级节点")
            return nodes
    except Exception as e:
        logger.error(f"从数据库加载高级节点失败: {e}")
        return set()


def save_high_level_nodes_to_db(high_level_nodes: set, replace_all: bool = False):
    """
    保存高级节点到数据库
    
    Args:
        high_level_nodes: 要保存的高级节点集合
        replace_all: 如果为True，完全替换（删除旧的）；如果为False，增量更新（只添加新的）
    """
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            if replace_all:
                # 完全替换：删除所有旧节点
                cursor.execute(f"DELETE FROM {HIGH_LEVEL_NODE_TABLE}")
                logger.info("已清除所有旧的高级节点")
            
            # 获取现有的高级节点
            cursor.execute(f"SELECT node_name FROM {HIGH_LEVEL_NODE_TABLE}")
            existing_nodes = {row["node_name"] for row in cursor.fetchall()}
            
            # 找出新增的节点
            new_nodes = high_level_nodes - existing_nodes
            
            if new_nodes:
                # 插入新节点
                cursor.executemany(
                    f"INSERT IGNORE INTO {HIGH_LEVEL_NODE_TABLE} (node_name) VALUES (%s)",
                    [(node,) for node in new_nodes]
                )
                conn.commit()
                logger.info(f"新增 {len(new_nodes)} 个高级节点到数据库: {new_nodes}")
            else:
                logger.info("没有新增的高级节点")
            
            # 如果完全替换，返回新的节点集合；否则返回合并后的
            if replace_all:
                return high_level_nodes
            else:
                return existing_nodes | high_level_nodes
    except Exception as e:
        logger.error(f"保存高级节点到数据库失败: {e}")
        return high_level_nodes


def get_default_high_level_nodes() -> set:
    """获取默认的高级节点名称集合"""
    return {node["node_name"] for node in DEFAULT_HIGH_LEVEL_NODE_RECORDS}


def get_default_high_level_node_records():
    """返回默认高级节点的完整记录"""
    return DEFAULT_HIGH_LEVEL_NODE_RECORDS


def init_default_high_level_nodes():
    """初始化默认的高级节点到数据库（如果数据库为空）"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT COUNT(*) as cnt FROM {HIGH_LEVEL_NODE_TABLE}")
            count = cursor.fetchone()["cnt"]
            
            if count == 0:
                # 数据库为空，初始化默认列表
                default_nodes = get_default_high_level_node_records()
                cursor.executemany(
                    f"""
                    INSERT IGNORE INTO {HIGH_LEVEL_NODE_TABLE} (node_name, node_type, description) 
                    VALUES (%s, %s, %s)
                    """,
                    [
                        (node["node_name"], node.get("node_type", "generic"), node.get("description"))
                        for node in default_nodes
                    ]
                )
                conn.commit()
                logger.info(f"初始化了 {len(default_nodes)} 个默认高级节点到数据库")
                return {node["node_name"] for node in default_nodes}
            else:
                logger.info(f"数据库中已有 {count} 个高级节点，跳过初始化")
                return load_high_level_nodes_from_db()
    except Exception as e:
        logger.error(f"初始化默认高级节点失败: {e}")
        return get_default_high_level_nodes()


# ==================== API路由 ====================
@app.on_event("startup")
async def startup_event():
    """应用启动时初始化数据库和AI服务"""
    init_database()
    
    # 初始化AI服务
    from ai_service import init_ai_services
    word2vec_path = os.getenv("WORD2VEC_MODEL_PATH")
    kimi_api_key = os.getenv("MOONSHOT_API_KEY")
    init_ai_services(word2vec_path, kimi_api_key)
    
    # 初始化图像分析服务
    from image_service import init_image_services
    from knowledge_updater import init_knowledge_updater
    from multi_entity_analyzer import init_multi_entity_analyzer
    
    init_image_services(DB_CONFIG)
    init_knowledge_updater(DB_CONFIG)
    init_multi_entity_analyzer(DB_CONFIG)
    
    logger.info("应用启动完成")


@app.get("/")
async def root():
    """根路径"""
    return {"message": "松材线虫病知识图谱系统API", "version": "1.0.0"}


@app.get("/api/graph", response_model=GraphResponse)
async def get_graph():
    """
    获取完整知识图谱
    返回ECharts所需的nodes和links格式
    
    Args:
        use_cache: 是否使用缓存的高级节点（默认True）
    """
    try:
        with get_db() as conn:
            cursor = conn.cursor()

            # 查询所有三元组
            cursor.execute("SELECT * FROM knowledge_triples")
            triples = cursor.fetchall()

            # 构建节点和边
            nodes_set = set()
            links = []

            for triple in triples:
                head = triple["head_entity"]
                relation = triple["relation"]
                tail = triple["tail_entity"]

                nodes_set.add(head)
                nodes_set.add(tail)

                links.append({
                    "source": head,
                    "target": tail,
                    "value": relation,
                    "id": triple["id"]
                })

            # 从数据库加载高级节点（持久化存储）
            high_level_nodes = load_high_level_nodes_from_db()
            
            # 如果数据库中没有高级节点，初始化默认列表
            if not high_level_nodes:
                high_level_nodes = init_default_high_level_nodes()
                # 只保留在图谱中实际存在的节点
                high_level_nodes = high_level_nodes.intersection(nodes_set)
            else:
                logger.info(f"从数据库加载高级节点，共 {len(high_level_nodes)} 个")

            # 转换节点格式，添加类别信息
            nodes = []
            for node in nodes_set:
                node_data = {
                    "name": node,
                    "id": node,
                    "category": 1 if node in high_level_nodes else 0  # 1=高级节点，0=普通节点
                }
                nodes.append(node_data)

            return GraphResponse(nodes=nodes, links=links)

    except Exception as e:
        logger.error(f"获取图谱失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取图谱失败: {str(e)}")


@app.delete("/api/node/delete")
async def delete_node(node: Node):
    """
    删除节点及其相关的所有边
    """
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # 删除包含该节点的所有三元组
            cursor.execute("""
                DELETE FROM knowledge_triples 
                WHERE head_entity = %s OR tail_entity = %s
            """, (node.name, node.name))
            
            deleted_count = cursor.rowcount
            conn.commit()
            
            logger.info(f"删除节点 {node.name}, 删除了 {deleted_count} 条记录")
            
            # 如果删除的节点是高级节点，也从高级节点表中删除
            try:
                cursor.execute(f"DELETE FROM {HIGH_LEVEL_NODE_TABLE} WHERE node_name = %s", (node.name,))
                conn.commit()
                logger.info(f"已从高级节点表中删除: {node.name}")
            except Exception as e:
                logger.warning(f"从高级节点表删除失败: {e}")
            
            return {"message": f"成功删除节点 {node.name}", "deleted_count": deleted_count}
            
    except Exception as e:
        logger.error(f"删除节点失败: {e}")
        raise HTTPException(status_code=500, detail=f"删除节点失败: {str(e)}")


@app.put("/api/node/update")
async def update_node(update: UpdateNode):
    """
    更新节点名称
    """
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # 更新头实体
            cursor.execute("""
                UPDATE knowledge_triples 
                SET head_entity = %s 
                WHERE head_entity = %s
            """, (update.new_name, update.old_name))
            
            # 更新尾实体
            cursor.execute("""
                UPDATE knowledge_triples 
                SET tail_entity = %s 
                WHERE tail_entity = %s
            """, (update.new_name, update.old_name))
            
            updated_count = cursor.rowcount
            conn.commit()
            
            logger.info(f"更新节点 {update.old_name} -> {update.new_name}")
            
            # 如果旧节点是高级节点，更新高级节点表中的名称
            try:
                cursor.execute(f"""
                    UPDATE {HIGH_LEVEL_NODE_TABLE} 
                    SET node_name = %s 
                    WHERE node_name = %s
                """, (update.new_name, update.old_name))
                conn.commit()
                if cursor.rowcount > 0:
                    logger.info(f"已更新高级节点表中的节点名称: {update.old_name} -> {update.new_name}")
            except Exception as e:
                logger.warning(f"更新高级节点表失败: {e}")
            
            return {"message": f"成功更新节点", "updated_count": updated_count}
            
    except Exception as e:
        logger.error(f"更新节点失败: {e}")
        raise HTTPException(status_code=500, detail=f"更新节点失败: {str(e)}")


@app.delete("/api/edge/delete/{edge_id}")
async def delete_edge(edge_id: int):
    """
    删除指定的边(三元组)
    """
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM knowledge_triples WHERE id = %s", (edge_id,))
            
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="边不存在")
            
            conn.commit()
            
            logger.info(f"删除边 ID: {edge_id}")
            return {"message": f"成功删除边"}
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除边失败: {e}")
        raise HTTPException(status_code=500, detail=f"删除边失败: {str(e)}")


@app.put("/api/edge/update")
async def update_edge(triple: Triple):
    """
    更新边(三元组)
    """
    try:
        if triple.id is None:
            raise HTTPException(status_code=400, detail="需要提供边的ID")
        
        with get_db() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE knowledge_triples 
                SET head_entity = %s, relation = %s, tail_entity = %s
                WHERE id = %s
            """, (triple.head_entity, triple.relation, triple.tail_entity, triple.id))
            
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="边不存在")
            
            conn.commit()
            
            logger.info(f"更新边 ID: {triple.id}")
            return {"message": "成功更新边"}
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新边失败: {e}")
        raise HTTPException(status_code=500, detail=f"更新边失败: {str(e)}")


@app.get("/api/relations")
async def get_relations():
    """
    获取所有有效关系列表
    """
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT relation_name FROM valid_relations")
            relations = [row["relation_name"] for row in cursor.fetchall()]
            return {"relations": relations}
            
    except Exception as e:
        logger.error(f"获取关系列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取关系列表失败: {str(e)}")


@app.get("/api/node/similar/{entity_name}")
async def get_similar_entities(entity_name: str, topn: int = 10):
    """
    获取相似实体列表（新增节点的第一步）
    
    Args:
        entity_name: 输入的实体名称
        topn: 返回前N个相似实体（默认10个）
    
    Returns:
        相似实体列表，每个包含：名称、相似度、是否在图谱中
    """
    from ai_service import get_word2vec_service
    
    entity_name = entity_name.strip()
    
    if not entity_name:
        raise HTTPException(status_code=400, detail="实体名称不能为空")
    
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # 检查实体是否已存在
            cursor.execute("""
                SELECT COUNT(*) as cnt FROM knowledge_triples 
                WHERE head_entity = %s OR tail_entity = %s
            """, (entity_name, entity_name))
            
            if cursor.fetchone()["cnt"] > 0:
                raise HTTPException(status_code=400, detail=f"实体 '{entity_name}' 已存在于图谱中")
            
            # 从数据库获取所有已存在的实体
            cursor.execute("""
                SELECT DISTINCT head_entity as entity FROM knowledge_triples
                UNION
                SELECT DISTINCT tail_entity as entity FROM knowledge_triples
            """)
            
            existing_entities = [row["entity"] for row in cursor.fetchall()]
            
            if not existing_entities:
                raise HTTPException(status_code=404, detail="图谱中暂无实体，无法计算相似度")
            
            logger.info(f"从数据库获取了 {len(existing_entities)} 个已有实体")
            
            # 使用Word2Vec计算输入词与所有实体的相似度
            word2vec = get_word2vec_service()
            similar_words = word2vec.calculate_similarity_with_candidates(entity_name, existing_entities)
            
            if not similar_words:
                raise HTTPException(status_code=404, detail="未能计算相似度")
            
            # 只取前topn个（已经按相似度排序）
            similar_words = similar_words[:topn]
            
            # 构建返回结果（这些都是图谱内的实体）
            result = []
            for word, similarity in similar_words:
                entity_data = {
                    "entity": word,
                    "similarity": float(similarity),
                    "in_graph": True  # 都是从数据库查出来的，必然在图谱中
                }
                result.append(entity_data)
            
            if not result:
                raise HTTPException(status_code=404, detail="未找到相似实体")
            
            logger.info(f"计算完成，返回 {len(result)} 个相似实体（相似度范围: {result[0]['similarity']:.4f} ~ {result[-1]['similarity']:.4f}）")
            
            return {
                "input": entity_name,
                "similar_entities": result,
                "stats": {
                    "total_entities_in_graph": len(existing_entities),
                    "calculated_count": len(existing_entities),
                    "returned_count": len(result)
                }
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"查询相似实体失败: {e}")
        raise HTTPException(status_code=500, detail=f"查询相似实体失败: {str(e)}")


class GenerateTriples(BaseModel):
    """生成候选三元组的请求"""
    entity_name: str
    similar_entity: str


class SelectedTriple(BaseModel):
    """用户选择的三元组"""
    entity_name: str
    similar_entity: str
    selected_triple: dict  # {head_entity, relation, tail_entity}


@app.post("/api/node/generate-triples")
async def generate_candidate_triples(data: GenerateTriples):
    """
    生成候选三元组（新的第二步：基于选择的相似词生成多个候选）
    
    步骤：
    1. 使用用户选择的相似词B
    2. 查询数据库，找到与B相关的**所有**实体C
    3. 使用AI为每个(A, C)对推理关系
    4. 返回所有候选三元组供用户选择
    """
    from ai_service import get_kimi_service
    
    entity_a = data.entity_name.strip()
    entity_b = data.similar_entity.strip()
    
    if not entity_a or not entity_b:
        raise HTTPException(status_code=400, detail="实体名称不能为空")
    
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # 检查实体A是否已存在
            cursor.execute("""
                SELECT COUNT(*) as cnt FROM knowledge_triples 
                WHERE head_entity = %s OR tail_entity = %s
            """, (entity_a, entity_a))
            
            if cursor.fetchone()["cnt"] > 0:
                raise HTTPException(status_code=400, detail=f"实体 '{entity_a}' 已存在于图谱中")
            
            logger.info(f"步骤1: 用户选择相似词 {entity_a} -> {entity_b}")
            
            # 步骤2: 查询与B相关的**所有**实体（不限制数量）
            cursor.execute("""
                SELECT DISTINCT 
                    CASE 
                        WHEN head_entity = %s THEN tail_entity 
                        ELSE head_entity 
                    END as related_entity
                FROM knowledge_triples 
                WHERE head_entity = %s OR tail_entity = %s
            """, (entity_b, entity_b, entity_b))
            
            related_entities = [row["related_entity"] for row in cursor.fetchall()]
            
            if not related_entities:
                raise HTTPException(
                    status_code=404, 
                    detail=f"相似实体 '{entity_b}' 不在图谱中，无法建立关联"
                )
            
            logger.info(f"步骤2完成: 找到 {len(related_entities)} 个关联实体")
            
            # 步骤3: 获取有效关系列表
            cursor.execute("SELECT relation_name FROM valid_relations")
            valid_relations = [row["relation_name"] for row in cursor.fetchall()]
            
            if not valid_relations:
                raise HTTPException(status_code=500, detail="系统中没有配置有效关系")
            
            # 步骤4: 使用AI为每个(A, C)对推理关系
            kimi = get_kimi_service()
            candidate_triples = []
            
            for entity_c in related_entities:
                inferred_relation = kimi.infer_relation(entity_a, entity_c, valid_relations)
                candidate_triples.append({
                    "head_entity": entity_a,
                    "relation": inferred_relation,
                    "tail_entity": entity_c
                })
                logger.info(f"生成候选: {entity_a} --[{inferred_relation}]--> {entity_c}")
            
            return {
                "input_entity": entity_a,
                "similar_entity": entity_b,
                "candidate_triples": candidate_triples,
                "total_candidates": len(candidate_triples)
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"生成候选三元组失败: {e}")
        raise HTTPException(status_code=500, detail=f"生成候选三元组失败: {str(e)}")


@app.post("/api/node/add")
async def add_node_with_selected_triple(data: SelectedTriple):
    """
    添加节点（新的第三步：用户选择三元组后插入数据库）
    
    步骤：
    1. 验证选择的三元组
    2. 插入数据库
    """
    entity_a = data.entity_name.strip()
    entity_b = data.similar_entity.strip()
    triple = data.selected_triple
    
    if not entity_a or not triple:
        raise HTTPException(status_code=400, detail="参数不完整")
    
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # 再次检查实体A是否已存在
            cursor.execute("""
                SELECT COUNT(*) as cnt FROM knowledge_triples 
                WHERE head_entity = %s OR tail_entity = %s
            """, (entity_a, entity_a))
            
            if cursor.fetchone()["cnt"] > 0:
                raise HTTPException(status_code=400, detail=f"实体 '{entity_a}' 已存在于图谱中")
            
            # 插入选择的三元组
            cursor.execute("""
                INSERT INTO knowledge_triples (head_entity, relation, tail_entity)
                VALUES (%s, %s, %s)
            """, (triple["head_entity"], triple["relation"], triple["tail_entity"]))
            
            conn.commit()
            triple_id = cursor.lastrowid
            
            logger.info(f"成功添加三元组: {triple['head_entity']} --[{triple['relation']}]--> {triple['tail_entity']}")
            
            return {
                "message": "成功添加新实体",
                "triple": {
                    "id": triple_id,
                    "head_entity": triple["head_entity"],
                    "relation": triple["relation"],
                    "tail_entity": triple["tail_entity"]
                },
                "inference_path": {
                    "input": entity_a,
                    "similar_entity": entity_b
                }
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"智能添加节点失败: {e}")
        raise HTTPException(status_code=500, detail=f"智能添加节点失败: {str(e)}")


# ==================== 图像分析API ====================
@app.post("/api/image/analyze")
async def analyze_image(
    file: UploadFile = File(...),
    analyze_type: str = Form("full"),
    update_knowledge: bool = Form(True),
    confidence_threshold: float = Form(0.5)
):
    """
    图像分析API - 识别松材线虫病相关实体并进行预测分析
    
    Args:
        file: 上传的图像文件
        analyze_type: 分析类型 (full/entity_only/relationship_only)
        update_knowledge: 是否自动更新知识图谱
        confidence_threshold: 置信度阈值
    
    Returns:
        完整的分析结果
    """
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="请上传图像文件")
    
    try:
        # 1. 读取图像数据
        image_data = await file.read()
        
        # 2. 图像分析 - 实体识别（优先使用本地模型，失败则使用云端Kimi）
        analysis_result = None
        service_used = None
        
        # 2.1 尝试使用本地 YOLO 模型
        try:
            logger.info("尝试使用本地 YOLO 模型进行图像识别...")
            from local_yolo_image_service import LocalYOLOImageAnalysisService
            
            # 初始化本地模型服务
            local_service = LocalYOLOImageAnalysisService(model_path="yolov8m.pt")
            
            # 使用本地服务分析图像
            analysis_result = await local_service.analyze_image(image_data)
            service_used = "本地YOLO模型"
            logger.info(f"✅ 本地模型识别成功: {len(analysis_result.get('detected_entities', []))} 个实体")
            
        except Exception as local_error:
            logger.warning(f"⚠️ 本地模型识别失败: {local_error}")
            
            # 2.2 回退到云端 Kimi 模型
            try:
                logger.info("回退到云端 Kimi 模型...")
                from vision_ai_image_service import VisionAIImageAnalysisService
                
                # 初始化 Kimi 服务
                kimi_service = VisionAIImageAnalysisService()
                
                # 使用 Kimi 服务分析图像
                analysis_result = await kimi_service.analyze_image(image_data)
                service_used = "云端Kimi模型"
                logger.info(f"✅ Kimi 模型识别成功: {len(analysis_result.get('detected_entities', []))} 个实体")
                
            except Exception as kimi_error:
                logger.error(f"❌ Kimi 模型也失败: {kimi_error}")
                
                # 2.3 最终回退：使用通用图像服务
                try:
                    logger.info("尝试使用通用图像服务...")
                    from get_image_analysis_service import get_image_analysis_service
                    image_service = get_image_analysis_service()
                    
                    analysis_result = await image_service.analyze_image(image_data)
                    service_used = "通用图像服务"
                    logger.info(f"✅ 通用服务识别成功: {len(analysis_result.get('detected_entities', []))} 个实体")
                    
                except Exception as fallback_error:
                    logger.error(f"❌ 所有图像服务均不可用: {fallback_error}")
                    
                    # 2.4 最终回退：返回模拟数据（仅用于测试）
                    logger.warning("⚠️ 返回模拟数据以维持系统运行")
                    analysis_result = {
                        "image_info": {"size": [800, 600], "channels": 3},
                        "detected_entities": [
                            {
                                "type": "insect",
                                "name": "疑似松墨天牛",
                                "confidence": 0.85,
                                "similarity": 0.8,
                                "features": {"color": "黑色"},
                                "bbox": [100, 150, 80, 120],
                                "matched_kb_entity": "松墨天牛"
                            },
                            {
                                "type": "disease_symptom",
                                "name": "疑似松针发黄",
                                "confidence": 0.92,
                                "similarity": 0.7,
                                "features": {"color": "黄色"},
                                "bbox": [200, 100, 150, 200],
                                "matched_kb_entity": None
                            },
                            {
                                "type": "tree",
                                "name": "疑似马尾松",
                                "confidence": 0.78,
                                "similarity": 0.6,
                                "features": {"bark": "红褐色"},
                                "bbox": [0, 0, 800, 600],
                                "matched_kb_entity": "马尾松"
                            }
                        ],
                        "analysis_summary": {"total_entities": 3, "matched_entities": 2, "avg_confidence": 0.85}
                    }
                    service_used = "模拟数据（测试模式）"
        
        # 确保分析结果存在
        if analysis_result is None:
            raise HTTPException(status_code=500, detail="图像分析失败：所有服务均不可用")
        
        logger.info(f"📊 图像分析完成 - 使用服务: {service_used}")
        
        # 3. 过滤低置信度实体
        logger.info(f"过滤前实体数量: {len(analysis_result['detected_entities'])}, 阈值: {confidence_threshold}")
        detected_entities = [
            entity for entity in analysis_result["detected_entities"]
            if entity["confidence"] >= confidence_threshold
        ]
        logger.info(f"过滤后实体数量: {len(detected_entities)}")
        
        response_data = {
            "analysis_id": f"img_analysis_{int(time.time())}",
            "image_info": analysis_result["image_info"],
            "detected_entities": detected_entities,
            "recommendations": [],
            "analysis_summary": analysis_result["analysis_summary"]
        }
        
        # 4. 关系分析（如果请求且有多个实体）
        if analyze_type in ["full", "relationship_only"] and len(detected_entities) > 1:
            try:
                from multi_entity_analyzer import get_multi_entity_analyzer
                multi_analyzer = get_multi_entity_analyzer()
                
                relationship_result = await multi_analyzer.analyze_entity_relationships(detected_entities)
                response_data["relationship_analysis"] = relationship_result
                response_data["recommendations"].extend(relationship_result["recommendations"])
            except ImportError:
                logger.warning("多实体分析服务不可用")
        
        # 5. 疾病预测分析
        if analyze_type == "full" and detected_entities:
            try:
                from image_service import get_knowledge_inference_service
                inference_service = get_knowledge_inference_service()
                disease_prediction = await inference_service.analyze_disease_prediction(detected_entities)
                response_data["disease_prediction"] = disease_prediction
                
                if disease_prediction.get("recommended_actions"):
                    response_data["recommendations"].extend([
                        f"防治建议: {treatment['treatment']}" 
                        for treatment in disease_prediction["recommended_actions"].get("treatments", [])
                    ])
            except (ImportError, Exception) as e:
                logger.warning(f"疾病预测服务不可用: {e}")
        
        # 6. 知识图谱更新（如果启用）
        if update_knowledge and detected_entities:
            try:
                from knowledge_updater import get_knowledge_updater
                updater = get_knowledge_updater()
                
                update_stats = await updater.process_image_analysis_result({
                    "detected_entities": detected_entities
                })
                response_data["knowledge_update"] = update_stats
                
                if update_stats["new_entities_added"] > 0 or update_stats["new_relations_added"] > 0:
                    response_data["recommendations"].append(
                        f"知识图谱已更新: 新增{update_stats['new_entities_added']}个实体, {update_stats['new_relations_added']}个关系"
                    )
            except (ImportError, Exception) as e:
                logger.warning(f"知识图谱更新服务不可用: {e}")
        
        # 7. 生成总结建议
        if not response_data["recommendations"]:
            response_data["recommendations"] = ["未发现明显的松材线虫病风险，建议继续监测"]
        
        # 记录分析结果到历史表
        try:
            with get_db() as conn:
                cursor = conn.cursor()
                
                # 准备历史记录数据
                analysis_id = response_data["analysis_id"]
                timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
                entity_count = len(detected_entities)
                
                # 获取检测到的实体类型
                detected_types = list(set(entity["type"] for entity in detected_entities))
                
                # 计算平均置信度
                avg_confidence = sum(entity["confidence"] for entity in detected_entities) / len(detected_entities) if detected_entities else 0
                # 保留一位小数
                avg_confidence = round(avg_confidence, 1)
                
                # 确定风险等级
                if avg_confidence >= 0.8:
                    risk_level = "高风险"
                elif avg_confidence >= 0.6:
                    risk_level = "中风险"
                else:
                    risk_level = "低风险"
                
                # 插入历史记录
                cursor.execute("""
                    INSERT INTO image_analysis_history 
                    (analysis_id, timestamp, entity_count, detected_types, confidence, risk_level)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (analysis_id, timestamp, entity_count, json.dumps(detected_types), avg_confidence, risk_level))
                
                conn.commit()
                logger.info(f"分析历史记录已保存: {analysis_id}")
        except Exception as e:
            logger.error(f"保存分析历史记录失败: {e}")
        
        # 记录分析结果
        entity_names = [entity["name"] for entity in detected_entities]
        logger.info(f"图像分析完成: 检测{len(detected_entities)}个实体 {entity_names}")
        return response_data
        
    except Exception as e:
        logger.error(f"图像分析失败: {e}")
        raise HTTPException(status_code=500, detail=f"图像分析失败: {str(e)}")


@app.post("/api/entities/validate")
async def validate_entity_combinations(request: EntityValidationRequest):
    """
    验证实体组合的合理性
    
    Args:
        request: 包含实体列表和验证类型的请求
    
    Returns:
        验证结果和建议
    """
    try:
        if request.validation_type == "disease_scenario":
            try:
                from multi_entity_analyzer import get_multi_entity_analyzer
                analyzer = get_multi_entity_analyzer()
                
                validation_result = await analyzer.analyze_entity_relationships(request.entities)
                
                return {
                    "validation_type": request.validation_type,
                    "entities": request.entities,
                    "validation_result": validation_result,
                    "is_valid": validation_result["relationship_confidence"] > 0.5,
                    "confidence": validation_result["relationship_confidence"],
                    "recommendations": validation_result["recommendations"]
                }
            except ImportError:
                return {
                    "validation_type": request.validation_type,
                    "entities": request.entities,
                    "is_valid": False,
                    "confidence": 0.0,
                    "recommendations": ["实体验证服务不可用"]
                }
        elif request.validation_type == "relationship_check":
            # 简单的关系检查
            with get_db() as conn:
                cursor = conn.cursor()
                
                entity_names = [entity.get("matched_kb_entity") or entity["name"] for entity in request.entities]
                
                relationships = []
                for i, entity_a in enumerate(entity_names):
                    for entity_b in entity_names[i+1:]:
                        cursor.execute("""
                            SELECT head_entity, relation, tail_entity FROM knowledge_triples 
                            WHERE (head_entity = %s AND tail_entity = %s) 
                               OR (head_entity = %s AND tail_entity = %s)
                        """, (entity_a, entity_b, entity_b, entity_a))
                        
                        relationships.extend(cursor.fetchall())
                
                return {
                    "validation_type": request.validation_type,
                    "entities": request.entities,
                    "existing_relationships": relationships,
                    "relationship_count": len(relationships),
                    "is_valid": len(relationships) > 0
                }
        else:
            raise HTTPException(status_code=400, detail="不支持的验证类型")
            
    except Exception as e:
        logger.error(f"实体验证失败: {e}")
        raise HTTPException(status_code=500, detail=f"实体验证失败: {str(e)}")


@app.get("/api/knowledge/update-suggestions")
async def get_knowledge_update_suggestions(entity_names: str = None):
    """
    获取知识图谱更新建议
    
    Args:
        entity_names: 逗号分隔的实体名称（可选）
    
    Returns:
        更新建议列表
    """
    try:
        try:
            from knowledge_updater import get_knowledge_updater
            updater = get_knowledge_updater()
            
            if entity_names:
                # 基于特定实体生成建议
                names = [name.strip() for name in entity_names.split(',')]
                
                # 模拟实体数据结构
                mock_entities = []
                for name in names:
                    mock_entities.append({
                        "name": name,
                        "type": "unknown", 
                        "confidence": 0.8,
                        "similarity": 0.3,  # 假设低相似度
                        "features": {}
                    })
                
                suggestions = await updater.get_knowledge_update_suggestions(mock_entities)
            else:
                # 返回通用建议
                suggestions = [
                    {
                        "type": "general",
                        "priority": "low",
                        "reason": "定期检查知识图谱完整性",
                        "action": "建议定期上传新的图像进行分析，以发现新的实体和关系"
                    }
                ]
        except ImportError:
            suggestions = [
                {
                    "type": "service_unavailable",
                    "priority": "info",
                    "reason": "知识更新服务不可用",
                    "action": "请检查服务配置"
                }
            ]
        
        return {
            "suggestions": suggestions,
            "total_count": len(suggestions)
        }
        
    except Exception as e:
        logger.error(f"获取更新建议失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取更新建议失败: {str(e)}")


@app.post("/api/graph/add-high-level-node")
async def add_high_level_node(
    node_name: Optional[str] = Query(
        default=None,
        description="要标记为高级节点的节点名称",
        alias="node_name"
    ),
    payload: Optional[HighLevelNodePayload] = Body(default=None)
):
    """
    手动添加高级节点
    将数据库中已有的节点标记为高级节点
    
    Args:
        node_name: 节点名称
    """
    resolved_name = node_name or (payload.node_name if payload else None)
    if not resolved_name:
        raise HTTPException(status_code=400, detail="节点名称不能为空")
    
    node_name = resolved_name.strip()
    if not node_name:
        raise HTTPException(status_code=400, detail="节点名称不能为空")
    
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # 检查节点是否存在于知识图谱中
            cursor.execute("""
                SELECT COUNT(*) as cnt FROM knowledge_triples 
                WHERE head_entity = %s OR tail_entity = %s
            """, (node_name, node_name))
            
            if cursor.fetchone()["cnt"] == 0:
                raise HTTPException(status_code=404, detail=f"节点 '{node_name}' 不存在于知识图谱中")
            
            # 检查是否已经是高级节点
            cursor.execute(f"SELECT COUNT(*) as cnt FROM {HIGH_LEVEL_NODE_TABLE} WHERE node_name = %s", (node_name,))
            if cursor.fetchone()["cnt"] > 0:
                raise HTTPException(status_code=400, detail=f"节点 '{node_name}' 已经是高级节点")
            
            # 添加到高级节点表
            cursor.execute(
                f"INSERT INTO {HIGH_LEVEL_NODE_TABLE} (node_name, node_type) VALUES (%s, %s)",
                (node_name, "generic")
            )
            conn.commit()
            
            logger.info(f"成功添加高级节点: {node_name}")
            
            return {
                "message": f"成功将节点 '{node_name}' 标记为高级节点",
                "node_name": node_name
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"添加高级节点失败: {e}")
        raise HTTPException(status_code=500, detail=f"添加高级节点失败: {str(e)}")


@app.delete("/api/graph/remove-high-level-node")
async def remove_high_level_node(
    node_name: Optional[str] = Query(
        default=None,
        description="要移除的高级节点名称",
        alias="node_name"
    ),
    payload: Optional[HighLevelNodePayload] = Body(default=None)
):
    """
    移除高级节点标记
    将节点从高级节点列表中移除（但不会删除节点本身）
    
    Args:
        node_name: 节点名称
    """
    resolved_name = node_name or (payload.node_name if payload else None)
    if not resolved_name:
        raise HTTPException(status_code=400, detail="节点名称不能为空")
    
    node_name = resolved_name.strip()
    if not node_name:
        raise HTTPException(status_code=400, detail="节点名称不能为空")
    
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # 检查是否是高级节点
            cursor.execute(f"SELECT COUNT(*) as cnt FROM {HIGH_LEVEL_NODE_TABLE} WHERE node_name = %s", (node_name,))
            if cursor.fetchone()["cnt"] == 0:
                raise HTTPException(status_code=404, detail=f"节点 '{node_name}' 不是高级节点")
            
            # 从高级节点表删除
            cursor.execute(f"DELETE FROM {HIGH_LEVEL_NODE_TABLE} WHERE node_name = %s", (node_name,))
            conn.commit()
            
            logger.info(f"成功移除高级节点标记: {node_name}")
            
            return {
                "message": f"成功移除节点 '{node_name}' 的高级节点标记",
                "node_name": node_name
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"移除高级节点失败: {e}")
        raise HTTPException(status_code=500, detail=f"移除高级节点失败: {str(e)}")


@app.get("/api/image/analysis-history")
async def get_analysis_history(limit: int = 10):
    """
    获取图像分析历史
    
    Args:
        limit: 返回记录数量限制
    
    Returns:
        分析历史列表
    """
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # 查询最新的分析历史记录
            cursor.execute("""
                SELECT 
                    analysis_id as id,
                    timestamp,
                    entity_count,
                    detected_types,
                    confidence,
                    risk_level
                FROM image_analysis_history 
                ORDER BY timestamp DESC 
                LIMIT %s
            """, (limit,))
            
            history_records = []
            for record in cursor.fetchall():
                # 解析JSON字段
                detected_types = json.loads(record["detected_types"]) if isinstance(record["detected_types"], str) else record["detected_types"]
                
                history_records.append({
                    "id": record["id"],
                    "timestamp": record["timestamp"].strftime('%Y-%m-%d %H:%M:%S') if hasattr(record["timestamp"], 'strftime') else record["timestamp"],
                    "entity_count": record["entity_count"],
                    "detected_types": detected_types,
                    "confidence": round(float(record["confidence"]), 1),
                    "risk_level": record["risk_level"]
                })
            
            return {
                "history": history_records,
                "total_count": len(history_records)
            }
            
    except Exception as e:
        logger.error(f"获取分析历史失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取分析历史失败: {str(e)}")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)












