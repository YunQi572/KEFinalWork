"""
AI服务模块：Word2Vec和Kimi API集成
"""
import logging
from typing import Optional, List
import os
from openai import OpenAI

logger = logging.getLogger(__name__)


class Word2VecService:
    """Word2Vec服务"""
    
    def __init__(self, model_path: Optional[str] = None):
        """
        初始化Word2Vec模型
        
        Args:
            model_path: Word2Vec模型文件路径（.bin或.model）
        """
        self.model = None
        self.model_path = model_path
        
        if model_path and os.path.exists(model_path):
            try:
                from gensim.models import KeyedVectors
                logger.info(f"正在加载Word2Vec模型: {model_path}")
                self.model = KeyedVectors.load_word2vec_format(model_path, binary=True)
                logger.info("Word2Vec模型加载成功")
            except Exception as e:
                logger.warning(f"Word2Vec模型加载失败: {e}, 将使用Mock模式")
                self.model = None
        else:
            logger.warning("未提供Word2Vec模型路径或文件不存在，将使用Mock模式")
    
    def find_most_similar(self, word: str, topn: int = 1) -> Optional[str]:
        """
        找到与给定词最相似的词
        
        Args:
            word: 输入词
            topn: 返回前N个相似词
            
        Returns:
            最相似的词，如果找不到返回None
        """
        if self.model is not None:
            try:
                similar_words = self.model.most_similar(word, topn=topn)
                if similar_words:
                    most_similar_word = similar_words[0][0]
                    similarity_score = similar_words[0][1]
                    logger.info(f"Word2Vec找到相似词: {word} -> {most_similar_word} (相似度: {similarity_score:.4f})")
                    return most_similar_word
            except KeyError:
                logger.warning(f"词 '{word}' 不在Word2Vec模型词汇表中")
            except Exception as e:
                logger.error(f"Word2Vec查询失败: {e}")
        
        # Mock模式：返回一个预设的相似词
        return self._mock_similar_word(word)
    
    def find_most_similar_topn(self, word: str, topn: int = 10) -> List[tuple]:
        """
        找到与给定词最相似的Top-N个词
        
        Args:
            word: 输入词
            topn: 返回前N个相似词
            
        Returns:
            [(词, 相似度), ...] 列表，如果找不到返回空列表
        """
        if self.model is not None:
            try:
                similar_words = self.model.most_similar(word, topn=topn)
                logger.info(f"Word2Vec找到{len(similar_words)}个相似词: {word}")
                return similar_words
            except KeyError:
                logger.warning(f"词 '{word}' 不在Word2Vec模型词汇表中")
            except Exception as e:
                logger.error(f"Word2Vec查询失败: {e}")
        
        # Mock模式：返回预设的相似词列表
        return self._mock_similar_words_topn(word, topn)
    
    def _mock_similar_word(self, word: str) -> str:
        """
        Mock函数：模拟返回相似词
        在没有真实Word2Vec模型时使用
        """
        # 预设一些松材线虫病相关的映射关系
        mock_mappings = {
            "湿地松": "马尾松",
            "黑松": "马尾松",
            "红松": "马尾松",
            "赤松": "黑松",
            "日本松": "黑松",
            "华山松": "马尾松",
            "落叶松": "马尾松",
            "雪松": "松树",
            "云杉": "松树",
            "冷杉": "松树",
            "天牛": "松墨天牛",
            "媒介昆虫": "松墨天牛",
            "传播媒介": "松墨天牛",
            "线虫": "松材线虫",
            "病原体": "松材线虫",
            "病原": "松材线虫",
            "高温": "温度",
            "低温": "温度",
            "湿度": "温度",
            "气候": "温度",
            "森林": "松林",
            "林区": "松林",
            "山区": "松林",
        }
        
        similar = mock_mappings.get(word, "松树")  # 默认返回"松树"
        logger.info(f"Mock模式: {word} -> {similar}")
        return similar
    
    def _mock_similar_words_topn(self, word: str, topn: int = 10) -> List[tuple]:
        """
        Mock函数：模拟返回Top-N相似词
        在没有真实Word2Vec模型时使用
        """
        # 预设一些松材线虫病相关的相似词组
        mock_similar_groups = {
            "湿地松": [
                ("马尾松", 0.89), ("黑松", 0.85), ("赤松", 0.82), ("华山松", 0.79),
                ("落叶松", 0.76), ("红松", 0.74), ("云杉", 0.71), ("冷杉", 0.68),
                ("雪松", 0.65), ("松树", 0.62)
            ],
            "天牛": [
                ("松墨天牛", 0.92), ("媒介昆虫", 0.87), ("传播媒介", 0.84), ("昆虫", 0.79),
                ("害虫", 0.76), ("虫媒", 0.73), ("天敌", 0.70), ("寄主", 0.67),
                ("载体", 0.64), ("中间宿主", 0.61)
            ],
            "线虫": [
                ("松材线虫", 0.95), ("病原体", 0.90), ("病原", 0.87), ("寄生虫", 0.83),
                ("微生物", 0.78), ("致病菌", 0.75), ("病菌", 0.72), ("虫害", 0.68),
                ("病害", 0.65), ("病原物", 0.62)
            ],
            "高温": [
                ("温度", 0.88), ("气候", 0.85), ("环境温度", 0.82), ("热量", 0.78),
                ("气温", 0.75), ("湿度", 0.72), ("低温", 0.69), ("温差", 0.66),
                ("环境条件", 0.63), ("气候条件", 0.60)
            ],
        }
        
        # 如果word在预设组中，返回对应的相似词
        if word in mock_similar_groups:
            result = mock_similar_groups[word][:topn]
            logger.info(f"Mock模式: {word} -> {len(result)}个相似词")
            return result
        
        # 默认返回一组通用的松材线虫病相关词
        default_similar = [
            ("松树", 0.75), ("马尾松", 0.72), ("松材线虫", 0.70), ("松墨天牛", 0.67),
            ("感染", 0.64), ("传播", 0.61), ("防治", 0.58), ("病害", 0.55),
            ("林木", 0.52), ("疫情", 0.50)
        ]
        
        result = default_similar[:topn]
        logger.info(f"Mock模式(默认): {word} -> {len(result)}个相似词")
        return result


class KimiService:
    """Kimi (Moonshot AI) API服务"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化Kimi API客户端
        
        Args:
            api_key: Moonshot API密钥
        """
        self.api_key = api_key or os.getenv("MOONSHOT_API_KEY", "")
        self.model = "moonshot-v1-8k"  # 默认模型
        
        if not self.api_key:
            logger.warning("未设置MOONSHOT_API_KEY，Kimi API将无法使用")
            self.client = None
        else:
            try:
                # 按照官方示例初始化，只使用 api_key 和 base_url 参数
                self.client = OpenAI(
                    api_key=self.api_key,
                    base_url="https://api.moonshot.cn/v1"
                )
                logger.info("Kimi API客户端初始化成功")
            except Exception as e:
                logger.error(f"Kimi API客户端初始化失败: {e}")
                logger.warning("将使用Mock模式进行关系推理")
                self.client = None
    
    def infer_relation(self, entity_a: str, entity_c: str, valid_relations: List[str]) -> str:
        """
        使用Kimi API推理两个实体之间的关系
        
        Args:
            entity_a: 实体A（新增的实体）
            entity_c: 实体C（已存在的实体）
            valid_relations: 有效关系列表
            
        Returns:
            推理出的关系名称
        """
        if not self.client or not valid_relations:
            # 如果API不可用或没有有效关系，使用Mock模式
            return self._mock_relation(entity_a, entity_c, valid_relations)
        
        try:
            # 构建prompt
            relations_str = "、".join(valid_relations)
            prompt = f"""我有两个与松材线虫病相关的实体："{entity_a}" 和 "{entity_c}"。

请从以下关系列表中选择一个最合理的关系来描述它们之间的联系：
{relations_str}

要求：
1. 只返回关系名称，不要返回其他内容
2. 必须从给定的关系列表中选择
3. 如果多个关系都合理，选择最直接、最重要的那个

关系名称："""
            
            logger.info(f"正在调用Kimi API推理关系: {entity_a} <-> {entity_c}")
            
            # 调用Kimi API
            response = self.client.chat.completions.create(
                model="moonshot-v1-8k",
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个松材线虫病领域的专家，擅长分析实体之间的关系。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=50
            )
            
            # 提取关系
            relation = response.choices[0].message.content.strip()
            
            # 验证关系是否在有效列表中
            if relation in valid_relations:
                logger.info(f"Kimi API推理成功: {entity_a} --[{relation}]--> {entity_c}")
                return relation
            else:
                logger.warning(f"Kimi返回的关系 '{relation}' 不在有效列表中，使用Mock模式")
                return self._mock_relation(entity_a, entity_c, valid_relations)
                
        except Exception as e:
            logger.error(f"Kimi API调用失败: {e}")
            return self._mock_relation(entity_a, entity_c, valid_relations)
    
    def _mock_relation(self, entity_a: str, entity_c: str, valid_relations: List[str]) -> str:
        """
        Mock函数：基于规则推理关系
        在API不可用时使用
        """
        if not valid_relations:
            return "相关"
        
        # 预设一些规则
        # 如果entity_a是树种，entity_c是松树/马尾松等，关系可能是"属于"
        tree_keywords = ["松", "树", "林"]
        insect_keywords = ["天牛", "昆虫", "媒介"]
        disease_keywords = ["线虫", "病", "症状"]
        env_keywords = ["温度", "湿度", "气候", "环境"]
        
        # 简单的规则匹配
        if any(k in entity_a for k in tree_keywords):
            if "易感" in valid_relations and any(k in entity_c for k in disease_keywords):
                relation = "易感"
            elif "属于" in valid_relations and any(k in entity_c for k in tree_keywords):
                relation = "属于"
            else:
                relation = valid_relations[0]
        elif any(k in entity_a for k in insect_keywords):
            if "传播" in valid_relations:
                relation = "传播"
            else:
                relation = valid_relations[0]
        elif any(k in entity_a for k in env_keywords):
            if "影响" in valid_relations:
                relation = "影响"
            else:
                relation = valid_relations[0]
        else:
            # 默认使用第一个关系
            relation = valid_relations[0]
        
        logger.info(f"Mock推理: {entity_a} --[{relation}]--> {entity_c}")
        return relation


# 全局服务实例
word2vec_service = None
kimi_service = None


def init_ai_services(word2vec_model_path: Optional[str] = None, kimi_api_key: Optional[str] = None):
    """
    初始化AI服务
    
    Args:
        word2vec_model_path: Word2Vec模型路径
        kimi_api_key: Kimi API密钥
    """
    global word2vec_service, kimi_service
    
    word2vec_service = Word2VecService(word2vec_model_path)
    kimi_service = KimiService(kimi_api_key)
    
    logger.info("AI服务初始化完成")


def get_word2vec_service() -> Word2VecService:
    """获取Word2Vec服务实例"""
    if word2vec_service is None:
        init_ai_services()
    return word2vec_service


def get_kimi_service() -> KimiService:
    """获取Kimi服务实例"""
    if kimi_service is None:
        init_ai_services()
    return kimi_service
