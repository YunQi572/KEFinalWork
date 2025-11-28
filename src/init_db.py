"""
数据库初始化脚本
创建示例数据用于测试
"""
import pymysql
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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


def init_database():
    """初始化数据库并插入示例数据"""
    
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
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
        logger.info("创建knowledge_triples表")
        
        # 创建有效关系表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS valid_relations (
                id INT AUTO_INCREMENT PRIMARY KEY,
                relation_name VARCHAR(100) UNIQUE NOT NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        logger.info("创建valid_relations表")
        
        # 插入有效关系
        relations = [
            "引起", "传播", "易感", "属于", "影响", 
            "防治", "寄生", "媒介", "危害", "分布于"
        ]
        
        for relation in relations:
            try:
                cursor.execute(
                    "INSERT INTO valid_relations (relation_name) VALUES (%s)",
                    (relation,)
                )
            except pymysql.err.IntegrityError:
                # 关系已存在，跳过
                pass
        
        logger.info(f"插入 {len(relations)} 个有效关系")
        
        # 插入示例三元组数据
        sample_triples = [
            # 病原与寄主
            ("松材线虫", "寄生", "松树"),
            ("松材线虫", "引起", "松材线虫病"),
            ("马尾松", "易感", "松材线虫"),
            ("黑松", "易感", "松材线虫"),
            
            # 树种分类
            ("马尾松", "属于", "松树"),
            ("黑松", "属于", "松树"),
            ("赤松", "属于", "松树"),
            
            # 传播媒介
            ("松墨天牛", "传播", "松材线虫"),
            ("松墨天牛", "媒介", "松材线虫病"),
            
            # 环境因素
            ("温度", "影响", "松材线虫"),
            ("温度", "影响", "松墨天牛"),
            ("湿度", "影响", "松材线虫病"),
            
            # 地理分布
            ("松材线虫病", "分布于", "松林"),
            ("松墨天牛", "分布于", "松林"),
            
            # 防治方法
            ("化学防治", "防治", "松墨天牛"),
            ("生物防治", "防治", "松材线虫"),
            ("检疫措施", "防治", "松材线虫病"),
            
            # 症状
            ("萎蔫", "属于", "松材线虫病"),
            ("针叶变色", "属于", "松材线虫病"),
            ("树脂分泌异常", "属于", "松材线虫病"),
        ]
        
        # 检查是否已有数据
        cursor.execute("SELECT COUNT(*) FROM knowledge_triples")
        count = cursor.fetchone()[0]
        
        if count == 0:
            # 插入示例数据
            cursor.executemany(
                "INSERT INTO knowledge_triples (head_entity, relation, tail_entity) VALUES (%s, %s, %s)",
                sample_triples
            )
            logger.info(f"插入 {len(sample_triples)} 条示例三元组")
        else:
            logger.info(f"数据库已有 {count} 条数据，跳过示例数据插入")
        
        conn.commit()
        logger.info("数据库初始化完成！")
        
        # 显示统计信息
        cursor.execute("SELECT COUNT(*) FROM knowledge_triples")
        triple_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM valid_relations")
        relation_count = cursor.fetchone()[0]
        
        logger.info(f"统计: 三元组 {triple_count} 条, 有效关系 {relation_count} 个")
        
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    print("=" * 50)
    print("松材线虫病知识图谱 - 数据库初始化")
    print("=" * 50)
    print(f"数据库: {DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")
    print("=" * 50)
    init_database()
    print("\n初始化完成！MySQL数据库: kproject")
