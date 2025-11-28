"""
松材线虫病知识图谱系统 - FastAPI后端
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import pymysql
import logging
from contextlib import contextmanager
import os
from pathlib import Path

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
    'password': 'xyd123456',
    'database': 'kproject',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}


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
        
        conn.commit()
        logger.info("数据库初始化完成")


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
            
            # 转换节点格式
            nodes = [{"name": node, "id": node} for node in nodes_set]
            
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
                WHERE head_entity = ? OR tail_entity = ?
            """, (node.name, node.name))
            
            deleted_count = cursor.rowcount
            conn.commit()
            
            logger.info(f"删除节点 {node.name}, 删除了 {deleted_count} 条记录")
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
                SET head_entity = ? 
                WHERE head_entity = ?
            """, (update.new_name, update.old_name))
            
            # 更新尾实体
            cursor.execute("""
                UPDATE knowledge_triples 
                SET tail_entity = ? 
                WHERE tail_entity = ?
            """, (update.new_name, update.old_name))
            
            updated_count = cursor.rowcount
            conn.commit()
            
            logger.info(f"更新节点 {update.old_name} -> {update.new_name}")
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
            
            cursor.execute("DELETE FROM knowledge_triples WHERE id = ?", (edge_id,))
            
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
                SET head_entity = ?, relation = ?, tail_entity = ?
                WHERE id = ?
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
            
            # 使用Word2Vec找更多相似词（获取更多候选）
            word2vec = get_word2vec_service()
            similar_words = word2vec.find_most_similar_topn(entity_name, topn=topn * 3)  # 获取3倍数量
            
            if not similar_words:
                raise HTTPException(status_code=404, detail="未找到相似实体")
            
            # 分类：图谱内和图谱外
            in_graph_entities = []
            out_graph_entities = []
            
            for word, similarity in similar_words:
                cursor.execute("""
                    SELECT COUNT(*) as cnt FROM knowledge_triples 
                    WHERE head_entity = %s OR tail_entity = %s
                """, (word, word))
                
                in_graph = cursor.fetchone()["cnt"] > 0
                
                entity_data = {
                    "entity": word,
                    "similarity": float(similarity),
                    "in_graph": in_graph
                }
                
                if in_graph:
                    in_graph_entities.append(entity_data)
                else:
                    out_graph_entities.append(entity_data)
            
            # 优先返回图谱内的实体，不足时补充图谱外的
            result = in_graph_entities[:topn]
            if len(result) < topn:
                result.extend(out_graph_entities[:topn - len(result)])
            
            if not result:
                raise HTTPException(status_code=404, detail="未找到相似实体")
            
            logger.info(f"找到相似实体: 图谱内 {len(in_graph_entities)} 个, 图谱外 {len(out_graph_entities)} 个, 返回 {len(result)} 个")
            
            return {
                "input": entity_name,
                "similar_entities": result,
                "stats": {
                    "in_graph_count": len(in_graph_entities),
                    "out_graph_count": len(out_graph_entities),
                    "total_returned": len(result)
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
