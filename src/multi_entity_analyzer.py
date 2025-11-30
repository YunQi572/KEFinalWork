"""
多实体关联分析服务
处理图像中多个实体的关系验证和发现
"""
import logging
from typing import Dict, List, Optional, Any, Tuple
import itertools
from contextlib import contextmanager
import pymysql

logger = logging.getLogger(__name__)


class MultiEntityAnalyzer:
    """多实体关联分析器"""
    
    def __init__(self, db_config: Dict[str, Any]):
        """
        初始化多实体分析器
        
        Args:
            db_config: 数据库配置
        """
        self.db_config = db_config
        
        # 预定义的实体关系规则
        self.relationship_rules = {
            ("insect", "disease_symptom"): ["传播", "携带", "引起"],
            ("insect", "tree"): ["寄主", "感染", "攻击"], 
            ("tree", "disease_symptom"): ["表现", "易感", "出现"],
            ("disease_symptom", "disease_symptom"): ["伴随", "导致", "发展"],
            ("insect", "insect"): ["竞争", "协同", "替代"]
        }
        
        # 相互验证的实体组合
        self.validation_combinations = {
            "松材线虫病": {
                "required_types": ["insect", "tree"],
                "expected_entities": {
                    "insect": ["松墨天牛", "天牛"],
                    "tree": ["马尾松", "黑松", "松树"],
                    "disease_symptom": ["松针发黄", "松针变红", "松针脱落"]
                },
                "validation_rules": [
                    {
                        "condition": "有松墨天牛且有松树",
                        "confidence_boost": 0.3,
                        "risk_level": "高"
                    },
                    {
                        "condition": "有松针症状且有松树", 
                        "confidence_boost": 0.2,
                        "risk_level": "中"
                    }
                ]
            }
        }
        
        logger.info("多实体关联分析器初始化完成")
    
    @contextmanager
    def get_db(self):
        """数据库连接上下文管理器"""
        conn = pymysql.connect(**self.db_config)
        try:
            yield conn
        finally:
            conn.close()
    
    async def analyze_entity_relationships(self, detected_entities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        分析检测到的多个实体间的关系
        
        Args:
            detected_entities: 检测到的实体列表
            
        Returns:
            关系分析结果
        """
        if len(detected_entities) < 2:
            return {
                "entity_count": len(detected_entities),
                "relationships": [],
                "validation_result": None,
                "confidence": 0.0,
                "recommendations": ["需要检测到至少2个实体才能进行关系分析"]
            }
        
        try:
            # 1. 查询已知关系
            existing_relationships = await self._query_existing_relationships(detected_entities)
            
            # 2. 推理潜在关系
            potential_relationships = await self._infer_potential_relationships(detected_entities)
            
            # 3. 实体组合验证
            validation_result = await self._validate_entity_combinations(detected_entities)
            
            # 4. 关系置信度评估
            relationship_confidence = self._calculate_relationship_confidence(
                existing_relationships, potential_relationships, validation_result
            )
            
            # 5. 生成建议
            recommendations = await self._generate_recommendations(
                detected_entities, existing_relationships, potential_relationships, validation_result
            )
            
            result = {
                "entity_count": len(detected_entities),
                "detected_entities": detected_entities,
                "existing_relationships": existing_relationships,
                "potential_relationships": potential_relationships,
                "validation_result": validation_result,
                "relationship_confidence": relationship_confidence,
                "recommendations": recommendations,
                "analysis_summary": self._generate_analysis_summary(
                    detected_entities, existing_relationships, validation_result
                )
            }
            
            logger.info(f"多实体关系分析完成: {len(detected_entities)}个实体, {len(existing_relationships)}个已知关系, {len(potential_relationships)}个潜在关系")
            return result
            
        except Exception as e:
            logger.error(f"多实体关系分析失败: {e}")
            raise
    
    async def _query_existing_relationships(self, detected_entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """查询已知关系"""
        relationships = []
        
        with self.get_db() as conn:
            cursor = conn.cursor()
            
            # 获取实体名称列表
            entity_names = []
            for entity in detected_entities:
                name = entity.get("matched_kb_entity") or entity["name"]
                entity_names.append(name)
            
            # 查询实体间的直接关系
            for i, entity_a in enumerate(entity_names):
                for entity_b in entity_names[i+1:]:
                    # 查询双向关系
                    cursor.execute("""
                        SELECT head_entity, relation, tail_entity, 'existing' as source
                        FROM knowledge_triples 
                        WHERE (head_entity = %s AND tail_entity = %s) 
                           OR (head_entity = %s AND tail_entity = %s)
                    """, (entity_a, entity_b, entity_b, entity_a))
                    
                    for row in cursor.fetchall():
                        relationships.append({
                            "head_entity": row["head_entity"],
                            "relation": row["relation"],
                            "tail_entity": row["tail_entity"],
                            "source": row["source"],
                            "confidence": 1.0  # 已存在关系置信度为1
                        })
        
        return relationships
    
    async def _infer_potential_relationships(self, detected_entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """推理潜在关系"""
        from ai_service import get_kimi_service
        
        potential_relationships = []
        
        # 获取有效关系列表
        with self.get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT relation_name FROM valid_relations")
            valid_relations = [row["relation_name"] for row in cursor.fetchall()]
        
        if len(valid_relations) == 0:
            logger.warning("没有找到有效关系列表")
            return potential_relationships
        
        kimi = get_kimi_service()
        
        # 对实体两两配对进行关系推理
        for entity_a, entity_b in itertools.combinations(detected_entities, 2):
            name_a = entity_a.get("matched_kb_entity") or entity_a["name"]
            name_b = entity_b.get("matched_kb_entity") or entity_b["name"]
            type_a = entity_a["type"]
            type_b = entity_b["type"]
            
            # 检查是否有预定义的关系规则
            rule_key = (type_a, type_b) if (type_a, type_b) in self.relationship_rules else (type_b, type_a)
            suggested_relations = self.relationship_rules.get(rule_key, valid_relations)
            
            # 使用AI推理最可能的关系
            try:
                inferred_relation = kimi.infer_relation(name_a, name_b, suggested_relations)
                if inferred_relation in valid_relations:
                    # 计算推理置信度
                    confidence = self._calculate_inference_confidence(entity_a, entity_b, inferred_relation)
                    
                    potential_relationships.append({
                        "head_entity": name_a,
                        "relation": inferred_relation,
                        "tail_entity": name_b,
                        "source": "ai_inference",
                        "confidence": confidence,
                        "entity_a_type": type_a,
                        "entity_b_type": type_b,
                        "reasoning": f"基于{type_a}和{type_b}的典型关系模式推理"
                    })
                    
            except Exception as e:
                logger.warning(f"关系推理失败: {name_a} <-> {name_b}, 错误: {e}")
        
        return potential_relationships
    
    def _calculate_inference_confidence(self, entity_a: Dict[str, Any], entity_b: Dict[str, Any], relation: str) -> float:
        """计算推理置信度"""
        base_confidence = 0.6  # 基础置信度
        
        # 实体识别置信度越高，关系推理置信度越高
        entity_conf_factor = (entity_a["confidence"] + entity_b["confidence"]) / 2
        
        # 如果实体在知识库中有匹配，增加置信度
        kb_match_factor = 0.0
        if entity_a.get("matched_kb_entity"):
            kb_match_factor += 0.1
        if entity_b.get("matched_kb_entity"):
            kb_match_factor += 0.1
        
        # 特定关系的置信度调整
        relation_confidence_boost = {
            "传播": 0.2,  # 传播关系在松材线虫病场景中很重要
            "感染": 0.2,
            "易感": 0.15,
            "寄主": 0.15
        }.get(relation, 0.0)
        
        final_confidence = min(
            base_confidence + entity_conf_factor * 0.2 + kb_match_factor + relation_confidence_boost,
            1.0
        )
        
        return round(final_confidence, 1)
    
    async def _validate_entity_combinations(self, detected_entities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """验证实体组合"""
        validation_results = []
        
        # 检查松材线虫病的典型组合
        pine_disease_validation = self._validate_pine_disease_combination(detected_entities)
        if pine_disease_validation:
            validation_results.append(pine_disease_validation)
        
        # 检查其他疾病模式（可扩展）
        
        return {
            "validated_scenarios": validation_results,
            "highest_confidence_scenario": max(validation_results, key=lambda x: x["confidence"]) if validation_results else None,
            "validation_summary": {
                "total_scenarios": len(validation_results),
                "max_confidence": max([v["confidence"] for v in validation_results]) if validation_results else 0.0
            }
        }
    
    def _validate_pine_disease_combination(self, detected_entities: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """验证松材线虫病组合"""
        entity_types = [entity["type"] for entity in detected_entities]
        entity_names = [entity.get("matched_kb_entity") or entity["name"] for entity in detected_entities]
        
        # 检查是否包含松材线虫病的关键实体
        has_insect = any("天牛" in name or entity["type"] == "insect" for entity, name in zip(detected_entities, entity_names))
        has_pine = any("松" in name or entity["type"] == "tree" for entity, name in zip(detected_entities, entity_names))
        has_symptom = any(entity["type"] == "disease_symptom" for entity in detected_entities)
        
        if not (has_insect or has_pine or has_symptom):
            return None
        
        # 计算验证置信度
        confidence = 0.0
        evidence = []
        
        if has_insect and has_pine:
            confidence += 0.4
            evidence.append("检测到昆虫媒介和宿主植物")
        
        if has_symptom:
            confidence += 0.3
            evidence.append("检测到疾病症状")
        
        if has_insect and has_symptom:
            confidence += 0.2
            evidence.append("媒介昆虫与疾病症状共现")
        
        # 特定实体组合的额外加分
        specific_combinations = [
            ("松墨天牛", "马尾松", 0.3),
            ("松墨天牛", "松针发黄", 0.25),
            ("松针变红", "马尾松", 0.2)
        ]
        
        for entity1, entity2, bonus in specific_combinations:
            if any(entity1 in name for name in entity_names) and any(entity2 in name for name in entity_names):
                confidence += bonus
                evidence.append(f"检测到关键组合: {entity1} + {entity2}")
        
        confidence = min(confidence, 1.0)
        
        if confidence > 0.3:  # 最低阈值
            return {
                "scenario": "松材线虫病",
                "confidence": round(confidence, 1),
                "evidence": evidence,
                "risk_assessment": "高风险" if confidence > 0.7 else "中风险" if confidence > 0.5 else "低风险",
                "recommendation": self._get_pine_disease_recommendation(confidence)
            }
        
        return None
    
    def _get_pine_disease_recommendation(self, confidence: float) -> str:
        """获取松材线虫病建议"""
        if confidence > 0.8:
            return "极可能是松材线虫病，建议立即采取隔离和防治措施"
        elif confidence > 0.6:
            return "疑似松材线虫病，建议进行专业检测确认"
        else:
            return "存在松材线虫病风险，建议加强监测"
    
    def _calculate_relationship_confidence(self, existing_rels: List, potential_rels: List, validation: Dict) -> float:
        """计算整体关系置信度"""
        if not existing_rels and not potential_rels:
            return 0.0
        
        # 已知关系的权重
        existing_weight = len(existing_rels) * 0.3
        
        # 潜在关系的权重
        potential_weight = sum(rel["confidence"] for rel in potential_rels) * 0.2
        
        # 验证结果的权重
        validation_weight = 0.0
        if validation.get("highest_confidence_scenario"):
            validation_weight = validation["highest_confidence_scenario"]["confidence"] * 0.5
        
        total_confidence = min(existing_weight + potential_weight + validation_weight, 1.0)
        return round(total_confidence, 1)
    
    async def _generate_recommendations(self, entities: List, existing_rels: List, potential_rels: List, validation: Dict) -> List[str]:
        """生成建议"""
        recommendations = []
        
        # 基于验证结果的建议
        if validation.get("highest_confidence_scenario"):
            scenario = validation["highest_confidence_scenario"]
            recommendations.append(f"检测结果提示可能是{scenario['scenario']}，{scenario['recommendation']}")
        
        # 基于缺失关系的建议
        if potential_rels:
            high_conf_potential = [rel for rel in potential_rels if rel["confidence"] > 0.7]
            if high_conf_potential:
                recommendations.append(f"发现{len(high_conf_potential)}个高置信度的潜在关系，建议添加到知识库")
        
        # 基于实体类型的建议
        entity_types = set(entity["type"] for entity in entities)
        if "insect" in entity_types and "tree" in entity_types:
            recommendations.append("检测到昆虫和植物，建议监测传播风险")
        
        if "disease_symptom" in entity_types:
            recommendations.append("检测到疾病症状，建议及时采取防治措施")
        
        return recommendations
    
    def _generate_analysis_summary(self, entities: List, existing_rels: List, validation: Dict) -> str:
        """生成分析摘要"""
        entity_count = len(entities)
        relation_count = len(existing_rels)
        
        summary = f"检测到{entity_count}个实体，发现{relation_count}个已知关系。"
        
        if validation.get("highest_confidence_scenario"):
            scenario = validation["highest_confidence_scenario"]
            summary += f"最可能的场景是{scenario['scenario']}（置信度: {scenario['confidence']:.2f}）。"
        else:
            summary += "未识别出明确的疾病场景。"
        
        return summary


# 全局服务实例
multi_entity_analyzer = None


def init_multi_entity_analyzer(db_config: Dict[str, Any]):
    """
    初始化多实体分析器
    
    Args:
        db_config: 数据库配置
    """
    global multi_entity_analyzer
    
    multi_entity_analyzer = MultiEntityAnalyzer(db_config)
    logger.info("多实体分析器初始化完成")


def get_multi_entity_analyzer() -> MultiEntityAnalyzer:
    """获取多实体分析器实例"""
    if multi_entity_analyzer is None:
        raise RuntimeError("多实体分析器未初始化")
    return multi_entity_analyzer