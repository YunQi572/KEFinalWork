"""
图像识别服务模块
处理松材线虫病相关的图像识别、特征提取和分析
"""
import logging
import os
from typing import Dict, List, Optional, Tuple, Any
import json
import base64
from io import BytesIO
from pathlib import Path
import numpy as np
from PIL import Image
import cv2

logger = logging.getLogger(__name__)


class EntityRecognitionResult:
    """实体识别结果"""
    def __init__(self, entity_type: str, entity_name: str, confidence: float, features: Dict[str, Any], bbox: Optional[Tuple] = None):
        self.entity_type = entity_type  # insect, leaf, disease_symptom, tree
        self.entity_name = entity_name  # 具体名称，如"松墨天牛"、"松针发黄"
        self.confidence = confidence    # 识别置信度 0-1
        self.features = features        # 特征字典
        self.bbox = bbox               # 边界框 (x, y, w, h)


class ImageAnalysisService:
    """图像分析服务"""
    
    def __init__(self):
        """初始化图像分析服务"""
        self.confidence_threshold = 0.5  # 识别置信度阈值
        self.similarity_threshold = 0.6  # 特征相似度阈值
        
        # 松材线虫病相关实体的标准特征库
        self.entity_features_db = self._load_entity_features()
        
        logger.info("图像分析服务初始化完成")
    
    def _load_entity_features(self) -> Dict[str, Dict[str, Any]]:
        """加载实体特征数据库"""
        # 这里定义了松材线虫病相关实体的标准特征
        features_db = {
            # 昆虫类
            "松墨天牛": {
                "type": "insect",
                "features": {
                    "body_color": ["黑色", "黑褐色"],
                    "body_length": "13-25mm",
                    "antennae": "长触角",
                    "elytra": "鞘翅黑褐色",
                    "size": "中等偏大",
                    "habitat": "松树枝干"
                },
                "keywords": ["天牛", "昆虫", "黑色", "长触角", "鞘翅"]
            },
            "日本长小蠹": {
                "type": "insect", 
                "features": {
                    "body_color": ["黄褐色", "棕褐色"],
                    "body_length": "3-4mm",
                    "size": "小型",
                    "habitat": "松树皮下"
                },
                "keywords": ["小蠹", "昆虫", "黄褐色", "小型"]
            },
            
            # 病害症状类
            "松针发黄": {
                "type": "disease_symptom",
                "features": {
                    "color": ["黄色", "黄绿色", "褐黄色"],
                    "part": "松针",
                    "stage": "初期症状",
                    "distribution": "局部或整体"
                },
                "keywords": ["松针", "发黄", "变色", "黄色"]
            },
            "松针变红": {
                "type": "disease_symptom",
                "features": {
                    "color": ["红色", "红褐色", "锈红色"],
                    "part": "松针",
                    "stage": "中期症状",
                    "distribution": "明显"
                },
                "keywords": ["松针", "变红", "红色", "红褐色"]
            },
            "松针脱落": {
                "type": "disease_symptom",
                "features": {
                    "condition": "枯萎脱落",
                    "part": "松针",
                    "stage": "后期症状",
                    "severity": "严重"
                },
                "keywords": ["松针", "脱落", "枯萎", "掉落"]
            },
            "树干流脂": {
                "type": "disease_symptom",
                "features": {
                    "substance": "树脂",
                    "color": ["透明", "琥珀色", "黄色"],
                    "part": "树干",
                    "texture": "粘稠"
                },
                "keywords": ["流脂", "树脂", "树干", "粘稠"]
            },
            
            # 树种类
            "马尾松": {
                "type": "tree",
                "features": {
                    "needle_length": "8-12cm",
                    "needle_count": "2针一束",
                    "bark": "红褐色",
                    "tree_shape": "高大乔木",
                    "susceptibility": "高易感性"
                },
                "keywords": ["马尾松", "松树", "2针", "红褐色树皮"]
            },
            "黑松": {
                "type": "tree",
                "features": {
                    "needle_length": "6-12cm",
                    "needle_count": "2针一束",
                    "bark": "灰黑色",
                    "tree_shape": "中等乔木",
                    "susceptibility": "中等易感性"
                },
                "keywords": ["黑松", "松树", "2针", "灰黑色树皮"]
            }
        }
        
        return features_db
    
    async def analyze_image(self, image_data: bytes) -> Dict[str, Any]:
        """
        分析图像，识别其中的松材线虫病相关实体
        
        Args:
            image_data: 图像二进制数据
            
        Returns:
            包含识别结果的字典
        """
        try:
            # 1. 图像预处理
            image = self._preprocess_image(image_data)
            
            # 2. 实体识别（模拟实现）
            entities = await self._recognize_entities(image)
            
            # 3. 特征提取
            for entity in entities:
                entity.features = self._extract_features(image, entity)
            
            # 4. 与知识库特征对比
            all_entities = []
            matched_entities = []
            
            for entity in entities:
                similarity = self._calculate_feature_similarity(entity)
                matched_kb_entity = self._find_best_match(entity) if similarity >= self.similarity_threshold else None
                
                # 添加调试日志
                logger.info(f"实体: {entity.entity_name}, 置信度: {entity.confidence}, 相似度: {similarity}")
                
                entity_data = {
                    "entity": entity,
                    "similarity": similarity,
                    "matched_kb_entity": matched_kb_entity
                }
                
                all_entities.append(entity_data)
                if similarity >= self.similarity_threshold:
                    matched_entities.append(entity_data)
            
            # 5. 构建分析结果
            result = {
                "image_info": {
                    "size": image.shape[:2],
                    "channels": image.shape[2] if len(image.shape) > 2 else 1
                },
                "detected_entities": [
                    {
                        "type": entity["entity"].entity_type,
                        "name": entity["entity"].entity_name,
                        "confidence": entity["entity"].confidence,
                        "similarity": entity["similarity"],
                        "features": entity["entity"].features,
                        "bbox": entity["entity"].bbox,
                        "matched_kb_entity": entity["matched_kb_entity"]
                    }
                    for entity in all_entities  # 显示所有检测到的实体，不只是匹配的
                ],
                "analysis_summary": {
                    "total_entities": len(entities),
                    "matched_entities": len(matched_entities),
                    "avg_confidence": np.mean([e["entity"].confidence for e in all_entities]) if all_entities else 0
                }
            }
            
            logger.info(f"图像分析完成: 检测到 {len(entities)} 个实体, 匹配 {len(matched_entities)} 个")
            return result
            
        except Exception as e:
            logger.error(f"图像分析失败: {e}")
            raise
    
    def _preprocess_image(self, image_data: bytes) -> np.ndarray:
        """图像预处理"""
        # 将bytes转换为PIL Image
        image = Image.open(BytesIO(image_data))
        
        # 转换为RGB格式
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # 转换为OpenCV格式
        cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # 调整大小（如果图像太大）
        height, width = cv_image.shape[:2]
        if max(height, width) > 1024:
            scale = 1024 / max(height, width)
            new_width = int(width * scale)
            new_height = int(height * scale)
            cv_image = cv2.resize(cv_image, (new_width, new_height))
        
        return cv_image
    
    async def _recognize_entities(self, image: np.ndarray) -> List[EntityRecognitionResult]:
        """
        使用AI进行真正的图像实体识别
        """
        entities = []
        
        # 1. 首先使用AI分析图像内容
        ai_recognized_objects = await self._ai_recognize_image_content(image)
        
        # 2. 在终端输出AI识别的原始结果
        logger.info("=" * 60)
        logger.info("🤖 AI图像识别原始结果:")
        for obj in ai_recognized_objects:
            logger.info(f"  识别对象: {obj['name']}")
            logger.info(f"  置信度: {obj['confidence']:.3f}")
            logger.info(f"  类别: {obj['category']}")
            logger.info(f"  描述: {obj['description']}")
            if obj.get('location'):
                logger.info(f"  位置: {obj['location']}")
            logger.info("-" * 40)
        
        # 3. 分析图像基本特征作为补充
        height, width = image.shape[:2]
        total_pixels = height * width
        
        # 计算颜色分布
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        pixels = image_rgb.reshape(-1, 3)
        avg_color = np.mean(pixels, axis=0)
        
        # 计算图像亮度
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        brightness = np.mean(gray)
        
        # 计算颜色方差（用于判断颜色复杂度）
        color_variance = np.var(pixels, axis=0)
        color_complexity = np.mean(color_variance)
        
        # 4. 将AI识别结果与知识库实体进行匹配
        logger.info("🔍 开始将AI识别结果与知识库实体进行匹配:")
        
        for ai_obj in ai_recognized_objects:
            # 尝试匹配知识库实体
            matched_entity = await self._match_with_knowledge_base(ai_obj)
            
            if matched_entity:
                # 创建匹配的实体结果
                bbox = self._parse_location_to_bbox(ai_obj.get('location', ''), width, height)
                
                entity_result = EntityRecognitionResult(
                    entity_type=matched_entity['type'],
                    entity_name=f"{matched_entity['name']} (AI识别: {ai_obj['name']})",
                    confidence=round(ai_obj['confidence'] * matched_entity['similarity'], 1),
                    features={
                        "ai_detected": ai_obj['name'],
                        "ai_confidence": ai_obj['confidence'],
                        "ai_description": ai_obj['description'],
                        "matched_kb_entity": matched_entity['name'],
                        "similarity_score": matched_entity['similarity'],
                        "match_reason": matched_entity['reason']
                    },
                    bbox=bbox
                )
                
                entities.append(entity_result)
                
                logger.info(f"✅ 成功匹配: AI识别'{ai_obj['name']}' -> 知识库'{matched_entity['name']}' (相似度: {matched_entity['similarity']:.3f})")
            else:
                # 未匹配到知识库实体，创建新的实体
                bbox = self._parse_location_to_bbox(ai_obj.get('location', ''), width, height)
                
                entity_result = EntityRecognitionResult(
                    entity_type=ai_obj['category'],
                    entity_name=f"未知实体: {ai_obj['name']}",
                    confidence=round(ai_obj['confidence'], 1),
                    features={
                        "ai_detected": ai_obj['name'],
                        "ai_confidence": ai_obj['confidence'],
                        "ai_description": ai_obj['description'],
                        "is_unknown": True
                    },
                    bbox=bbox
                )
                
                entities.append(entity_result)
                
                logger.info(f"⚠️  未匹配到知识库实体: '{ai_obj['name']}' (类别: {ai_obj['category']})")
        
        # 如果AI没有识别到任何对象，使用基础图像特征分析作为后备
        if not ai_recognized_objects:
            logger.info("⚡ AI未识别到对象，使用图像特征分析作为后备方案")
            backup_entities = await self._fallback_feature_analysis(image, avg_color, brightness, color_complexity)
            entities.extend(backup_entities)
        
        logger.info(f"🎯 AI图像识别完成: 检测到 {len(entities)} 个实体")
        return entities
    
    async def _ai_recognize_image_content(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """
        使用AI服务识别图像中的具体对象
        """
        try:
            # 导入AI服务
            from ai_service import get_kimi_service
            kimi_service = get_kimi_service()
            
            # 分析图像基本特征用于提示
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            pixels = image_rgb.reshape(-1, 3)
            avg_color = np.mean(pixels, axis=0)
            brightness = np.mean(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY))
            
            # 检查是否有可用的AI客户端
            if not kimi_service.client:
                logger.warning("Kimi客户端不可用，跳过AI图像识别")
                return []
            
            # 构造AI分析提示
            analysis_prompt = f"""基于图像颜色信息识别图像中的所有对象：
平均颜色: RGB({avg_color[0]:.0f}, {avg_color[1]:.0f}, {avg_color[2]:.0f})
平均亮度: {brightness:.0f}

请识别图像中可能存在的对象，包括但不限于：
1. 松材线虫病相关：昆虫（天牛、小蠹等）、病症（松针发黄/变红、流脂等）、树种（马尾松、黑松等）
2. 交通工具：汽车、卡车、货车、拖车等
3. 建筑设施：房屋、仓库、道路、桥梁等  
4. 自然环境：树木、森林、草地、天空、水体等
5. 工业物品：原木、木材、集装箱、机械等
6. 其他明显对象

请识别最可能的5个对象，每行一个，格式：
对象名称|置信度数值|类别|简短描述|center

类别选项：insect、plant、disease_symptom、tree、vehicle、building、natural、industrial、other
置信度范围：0.0-1.0

示例：
运输卡车|0.9|vehicle|大型货运车辆|center
原木堆|0.8|industrial|堆积的木材|center
森林背景|0.7|natural|绿色植被|center

请严格按照示例格式返回，不要添加其他说明文字："""
            
            # 调用AI分析
            response = kimi_service.client.chat.completions.create(
                model="moonshot-v1-8k",
                messages=[
                    {
                        "role": "system", 
                        "content": "你是一个松材线虫病识别专家，基于图像的颜色和亮度信息识别相关对象。"
                    },
                    {
                        "role": "user",
                        "content": analysis_prompt
                    }
                ],
                temperature=0.5,
                max_tokens=300
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            # 解析响应
            return self._parse_ai_response(ai_response)
            
        except Exception as e:
            logger.error(f"AI图像识别失败: {e}")
            # 返回空列表，后续会使用备用分析
            return []
    
    def _parse_ai_response(self, ai_response: str) -> List[Dict[str, Any]]:
        """
        解析AI的格式化响应，支持多种格式
        """
        objects = []
        
        try:
            lines = ai_response.strip().split('\n')
            for line in lines:
                line = line.strip()
                if not line or line.startswith('#') or line.startswith('根据'):
                    continue
                
                # 尝试解析管道分隔格式: 名称|置信度|类别|描述|位置
                if '|' in line:
                    parts = line.split('|')
                    if len(parts) >= 3:
                        try:
                            name = parts[0].strip()
                            confidence_str = parts[1].strip()
                            
                            # 提取数字部分
                            import re
                            confidence_match = re.search(r'(\d+\.?\d*)', confidence_str)
                            confidence = float(confidence_match.group(1)) if confidence_match else 0.7
                            
                            # 如果置信度大于1，假设是百分比，转换为0-1范围
                            if confidence > 1:
                                confidence = confidence / 100
                            
                            category = parts[2].strip() if len(parts) > 2 else 'other'
                            description = parts[3].strip() if len(parts) > 3 else f"AI识别的{name}"
                            location = parts[4].strip() if len(parts) > 4 else 'center'
                            
                            objects.append({
                                'name': name,
                                'confidence': confidence,
                                'category': category,
                                'description': description,
                                'location': location
                            })
                        except (ValueError, IndexError) as e:
                            logger.debug(f"解析管道格式失败: {e}, 跳过行: {line}")
                            continue
                
                # 尝试解析自然语言格式
                elif any(keyword in line for keyword in ['松针', '天牛', '小蠹', '马尾松', '黑松', '流脂', '发黄', '变红', 
                                                        '卡车', '货车', '车辆', '汽车', '运输', '原木', '木材', '森林', 
                                                        '树木', '道路', '建筑', '仓库', '机械']):
                    # 提取对象名称
                    name = None
                    confidence = 0.7  # 默认置信度
                    
                    # 松材线虫病相关对象
                    for keyword in ['松针发黄', '松针变红', '松墨天牛', '日本长小蠹', '马尾松', '黑松', '树干流脂']:
                        if keyword in line:
                            name = keyword
                            break
                    
                    # 交通工具
                    if not name:
                        for keyword in ['运输卡车', '货运卡车', '重型卡车', '拖车', '半挂车', '货车', '卡车', '汽车', '车辆']:
                            if keyword in line:
                                name = keyword
                                break
                    
                    # 工业物品
                    if not name:
                        for keyword in ['原木堆', '木材堆', '原木', '木材', '集装箱', '货物']:
                            if keyword in line:
                                name = keyword
                                break
                    
                    # 自然环境
                    if not name:
                        for keyword in ['森林背景', '树林', '森林', '绿色植被', '树木', '植被']:
                            if keyword in line:
                                name = keyword
                                break
                    
                    # 建筑设施
                    if not name:
                        for keyword in ['道路', '公路', '建筑', '仓库', '厂房']:
                            if keyword in line:
                                name = keyword
                                break
                    
                    # 通用关键词匹配
                    if not name:
                        for keyword in ['松针', '天牛', '小蠹', '马尾松', '黑松', '流脂']:
                            if keyword in line:
                                name = f"疑似{keyword}"
                                break
                    
                    if name:
                        # 确定类别
                        if any(k in name for k in ['松针', '流脂']):
                            category = 'disease_symptom'
                        elif any(k in name for k in ['天牛', '小蠹']):
                            category = 'insect'
                        elif any(k in name for k in ['松', '树']):
                            category = 'tree'
                        elif any(k in name for k in ['卡车', '货车', '车辆', '汽车', '运输', '拖车']):
                            category = 'vehicle'
                        elif any(k in name for k in ['原木', '木材', '集装箱', '货物']):
                            category = 'industrial'
                        elif any(k in name for k in ['森林', '树林', '植被']):
                            category = 'natural'
                        elif any(k in name for k in ['道路', '建筑', '仓库', '厂房']):
                            category = 'building'
                        else:
                            category = 'other'
                        
                        # 尝试提取置信度
                        import re
                        confidence_match = re.search(r'(\d+\.?\d*)%?', line)
                        if confidence_match:
                            confidence = float(confidence_match.group(1))
                            if confidence > 1:
                                confidence = confidence / 100
                        
                        objects.append({
                            'name': name,
                            'confidence': confidence,
                            'category': category,
                            'description': line,
                            'location': 'center'
                        })
                        
        except Exception as e:
            logger.warning(f"AI响应解析失败: {e}, 使用文本解析")
            return self._parse_ai_text_response(ai_response)
        
        # 如果没有解析到任何对象，尝试文本解析
        if not objects:
            return self._parse_ai_text_response(ai_response)
        
        return objects
    
    def _parse_ai_text_response(self, text: str) -> List[Dict[str, Any]]:
        """
        解析AI的文本响应，提取对象信息
        """
        objects = []
        
        # 简单的文本解析逻辑
        lines = text.split('\n')
        current_obj = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # 查找对象名称
            if '识别' in line or '发现' in line or '检测' in line:
                if current_obj:
                    objects.append(current_obj)
                    current_obj = {}
                
                # 提取对象名称
                for keyword in ['松针', '天牛', '小蠹', '马尾松', '黑松', '流脂', '发黄', '变红']:
                    if keyword in line:
                        current_obj['name'] = keyword
                        current_obj['confidence'] = 0.7  # 默认置信度
                        if keyword in ['松针', '马尾松', '黑松']:
                            current_obj['category'] = 'plant'
                        elif keyword in ['天牛', '小蠹']:
                            current_obj['category'] = 'insect'
                        else:
                            current_obj['category'] = 'disease_symptom'
                        current_obj['description'] = line
                        current_obj['location'] = 'center'
                        break
        
        if current_obj:
            objects.append(current_obj)
        
        return objects
    
    async def _match_with_knowledge_base(self, ai_obj: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        将AI识别的对象与知识库实体进行匹配
        """
        best_match = None
        best_similarity = 0.0
        
        ai_name = ai_obj['name'].lower()
        ai_category = ai_obj.get('category', '')
        
        for kb_name, kb_entity in self.entity_features_db.items():
            similarity = 0.0
            
            # 名称相似度
            if ai_name in kb_name.lower() or any(keyword in ai_name for keyword in kb_entity.get('keywords', [])):
                similarity += 0.6
            
            # 类别匹配
            if ai_category == kb_entity.get('type'):
                similarity += 0.3
            
            # 描述匹配
            ai_desc = ai_obj.get('description', '').lower()
            if any(keyword in ai_desc for keyword in kb_entity.get('keywords', [])):
                similarity += 0.1
            
            if similarity > best_similarity and similarity > 0.5:  # 最低匹配阈值
                best_similarity = similarity
                best_match = {
                    'name': kb_name,
                    'type': kb_entity.get('type', 'unknown'),
                    'similarity': similarity,
                    'reason': f"名称匹配度: {similarity:.2f}"
                }
        
        return best_match
    
    def _parse_location_to_bbox(self, location: str, width: int, height: int) -> Tuple[int, int, int, int]:
        """
        将位置描述转换为边界框
        """
        location = location.lower()
        
        if 'left' in location:
            return (0, height//4, width//2, height//2)
        elif 'right' in location:
            return (width//2, height//4, width//2, height//2)
        elif 'top' in location:
            return (width//4, 0, width//2, height//2)
        elif 'bottom' in location:
            return (width//4, height//2, width//2, height//2)
        else:  # center or unknown
            return (width//4, height//4, width//2, height//2)
    
    async def _fallback_feature_analysis(self, image: np.ndarray, avg_color: np.ndarray, brightness: float, color_complexity: float) -> List[EntityRecognitionResult]:
        """
        备用的图像特征分析方法
        """
        entities = []
        height, width = image.shape[:2]
        total_pixels = height * width
        
        logger.info("使用备用图像特征分析...")
        
        # 基于图像特征生成实体
        detected_entities = []
        
        # 1. 根据颜色特征判断可能的对象
        
        # 车辆检测（基于金属色调和几何特征）
        if avg_color[0] > 80 and avg_color[1] > 80 and avg_color[2] > 80:  # 较亮的颜色，可能是车辆
            if brightness > 120 and color_complexity > 800:  # 亮度高且复杂度适中
                detected_entities.append({
                    "type": "vehicle",
                    "name": f"疑似运输车辆 (亮度:{brightness:.1f})",
                    "confidence": min(0.9, 0.6 + brightness / 300),
                    "bbox": (width//4, height//3, width//2, height//3),
                    "raw_features": {
                        "dominant_color": "金属色调",
                        "size_estimate": "大型",
                        "detection_basis": f"高亮度特征,亮度:{brightness:.0f}"
                    }
                })
        
        # 工业原木检测（基于棕色调）
        brown_score = avg_color[0] * 0.6 + avg_color[1] * 0.8 - avg_color[2] * 0.4
        if brown_score > 50 and avg_color[0] > 100:
            detected_entities.append({
                "type": "industrial",
                "name": f"疑似原木堆 (棕色评分:{brown_score:.1f})",
                "confidence": min(0.85, 0.5 + brown_score / 200),
                "bbox": (0, height//3, width, height//3),
                "raw_features": {
                    "dominant_color": "棕木色",
                    "texture": "粗糙",
                    "detection_basis": f"木材色彩特征,评分:{brown_score:.1f}"
                }
            })
        
        # 昆虫检测（基于暗色特征）
        if avg_color[0] < 100 and avg_color[1] < 100:  # 暗色调
            if color_complexity > 1000:  # 颜色变化较多
                detected_entities.append({
                    "type": "insect",
                    "name": f"疑似松墨天牛 (置信度基于暗色特征)",
                    "confidence": min(0.95, 0.6 + color_complexity / 5000),
                    "bbox": self._find_dark_regions(image),
                    "raw_features": {
                        "dominant_color": "黑褐色",
                        "size_estimate": "中等",
                        "detection_basis": f"暗色区域检测,复杂度:{color_complexity:.0f}"
                    }
                })
        
        # 自然环境检测（基于绿色特征）
        if avg_color[1] > avg_color[0] and avg_color[1] > avg_color[2]:  # 绿色占主导
            detected_entities.append({
                "type": "natural",
                "name": f"疑似森林背景 (绿色特征)",
                "confidence": 0.8,
                "bbox": (0, 0, width, height//2),
                "raw_features": {
                    "dominant_color": "绿色",
                    "environment_type": "森林",
                    "detection_basis": "绿色植被特征"
                }
            })
        
        # 2. 根据红色/橙色判断病害症状
        red_ratio = avg_color[0] / (avg_color[1] + avg_color[2] + 1)
        if red_ratio > 1.2 or avg_color[0] > 150:  # 红色或橙色占主导
            detected_entities.append({
                "type": "disease_symptom",
                "name": f"疑似松材线虫病症状 (红色比率:{red_ratio:.2f})",
                "confidence": min(0.9, 0.5 + red_ratio * 0.3),
                "bbox": self._find_colored_regions(image, "red"),
                "raw_features": {
                    "dominant_color": "红橙色",
                    "intensity": f"高 (比率:{red_ratio:.2f})",
                    "distribution": "局部" if color_complexity > 2000 else "广泛"
                }
            })
        
        # 3. 根据黄色特征判断松针发黄
        yellow_score = (avg_color[0] + avg_color[1]) / 2 - avg_color[2]
        if yellow_score > 20:
            detected_entities.append({
                "type": "disease_symptom",
                "name": f"疑似松针发黄 (黄色评分:{yellow_score:.1f})",
                "confidence": min(0.85, 0.4 + yellow_score / 100),
                "bbox": self._find_colored_regions(image, "yellow"), 
                "raw_features": {
                    "dominant_color": "黄色",
                    "severity": "中等" if yellow_score < 50 else "严重",
                    "pattern": "针状"
                }
            })
        
        # 4. 根据棕色/绿色判断树木
        if avg_color[1] > avg_color[0] * 0.7:  # 有一定绿色成分
            tree_confidence = 0.6 + (avg_color[1] - avg_color[0]) / 255 * 0.3
            tree_type = self._classify_tree_type(avg_color, color_complexity)
            detected_entities.append({
                "type": "tree",
                "name": f"疑似{tree_type} (绿色特征)",
                "confidence": min(0.9, tree_confidence),
                "bbox": (0, 0, width, height),
                "raw_features": {
                    "bark_pattern": "纵向" if color_complexity > 1500 else "光滑",
                    "size_category": "大型" if total_pixels > 500000 else "中型",
                    "health_status": "健康" if avg_color[1] > 120 else "可疑"
                }
            })
        
        # 5. 如果是暗色调图像，可能有环境因子
        if brightness < 100:
            detected_entities.append({
                "type": "environment",
                "name": f"阴暗环境因子 (亮度:{brightness:.1f})",
                "confidence": 0.7,
                "bbox": None,
                "raw_features": {
                    "light_condition": "低光照",
                    "humidity_indicator": "可能偏高",
                    "risk_factor": "病害传播风险增加"
                }
            })
        
        # 如果没有检测到任何特征，返回默认实体
        if not detected_entities:
            detected_entities.append({
                "type": "tree", 
                "name": f"未分类植物 (图像特征不明显)",
                "confidence": 0.5,
                "bbox": (0, 0, width, height),
                "raw_features": {
                    "avg_brightness": f"{brightness:.1f}",
                    "color_complexity": f"{color_complexity:.1f}",
                    "analysis_note": "需要更清晰的图像"
                }
            })
        
        # 转换为EntityRecognitionResult对象
        for detection in detected_entities:
            entity = EntityRecognitionResult(
                entity_type=detection["type"],
                entity_name=detection["name"],
                confidence=detection["confidence"],
                features=detection["raw_features"],
                bbox=detection["bbox"]
            )
            entities.append(entity)
        
        logger.info(f"基于图像特征检测到 {len(entities)} 个实体")
        return entities
    
    def _find_dark_regions(self, image: np.ndarray) -> Tuple[int, int, int, int]:
        """找到图像中的暗色区域"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 找到最暗的区域
        _, dark_mask = cv2.threshold(gray, 80, 255, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(dark_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            # 找到最大的暗色区域
            largest_contour = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(largest_contour)
            return (x, y, w, h)
        
        # 如果没找到，返回图像中央的一个区域
        h, w = image.shape[:2]
        return (w//4, h//4, w//2, h//2)
    
    def _find_colored_regions(self, image: np.ndarray, color_type: str) -> Tuple[int, int, int, int]:
        """找到特定颜色的区域"""
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        if color_type == "red":
            # 红色的HSV范围
            lower1 = np.array([0, 50, 50])
            upper1 = np.array([10, 255, 255])
            lower2 = np.array([170, 50, 50])
            upper2 = np.array([180, 255, 255])
            mask1 = cv2.inRange(hsv, lower1, upper1)
            mask2 = cv2.inRange(hsv, lower2, upper2)
            mask = cv2.bitwise_or(mask1, mask2)
        elif color_type == "yellow":
            # 黄色的HSV范围
            lower = np.array([20, 50, 50])
            upper = np.array([30, 255, 255])
            mask = cv2.inRange(hsv, lower, upper)
        else:
            # 默认返回图像中央区域
            h, w = image.shape[:2]
            return (w//4, h//4, w//2, h//2)
        
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            # 找到最大的颜色区域
            largest_contour = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(largest_contour)
            return (x, y, w, h)
        
        # 如果没找到，返回图像中央的一个区域
        h, w = image.shape[:2]
        return (w//3, h//3, w//3, h//3)
    
    def _classify_tree_type(self, avg_color: np.ndarray, color_complexity: float) -> str:
        """根据颜色特征分类树种"""
        red, green, blue = avg_color
        
        # 马尾松特征：偏红褐色
        if red > green and red > 100:
            return "马尾松"
        
        # 黑松特征：偏暗色
        elif red < 80 and green < 80 and blue < 80:
            return "黑松"
        
        # 湿地松特征：颜色较亮
        elif green > 120 and color_complexity < 1000:
            return "湿地松"
        
        # 落叶松特征：如果有黄色倾向
        elif red > 100 and green > 100 and blue < 80:
            return "落叶松"
        
        # 默认
        else:
            return "未知松树"
    
    def _extract_features(self, image: np.ndarray, entity: EntityRecognitionResult) -> Dict[str, Any]:
        """特征提取"""
        features = entity.features.copy()
        
        # 如果有边界框，提取该区域的特征
        if entity.bbox:
            x, y, w, h = entity.bbox
            roi = image[y:y+h, x:x+w]
            
            # 提取颜色特征
            features.update(self._extract_color_features(roi))
            
            # 提取形状特征
            features.update(self._extract_shape_features(roi))
            
            # 提取纹理特征
            features.update(self._extract_texture_features(roi))
        
        return features
    
    def _extract_color_features(self, roi: np.ndarray) -> Dict[str, Any]:
        """提取颜色特征"""
        # 计算主要颜色
        roi_rgb = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)
        pixels = roi_rgb.reshape(-1, 3)
        
        # 计算平均颜色
        avg_color = np.mean(pixels, axis=0)
        
        # 将RGB值转换为颜色描述
        color_name = self._rgb_to_color_name(avg_color)
        
        return {
            "avg_rgb": avg_color.tolist(),
            "dominant_color": color_name,
            "color_variance": np.var(pixels, axis=0).tolist()
        }
    
    def _extract_shape_features(self, roi: np.ndarray) -> Dict[str, Any]:
        """提取形状特征"""
        # 转换为灰度图
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        
        # 二值化
        _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        
        # 查找轮廓
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            # 找到最大轮廓
            max_contour = max(contours, key=cv2.contourArea)
            
            # 计算形状特征
            area = cv2.contourArea(max_contour)
            perimeter = cv2.arcLength(max_contour, True)
            
            # 长宽比
            x, y, w, h = cv2.boundingRect(max_contour)
            aspect_ratio = w / h if h > 0 else 1
            
            return {
                "area": area,
                "perimeter": perimeter,
                "aspect_ratio": aspect_ratio,
                "compactness": (4 * np.pi * area) / (perimeter ** 2) if perimeter > 0 else 0
            }
        
        return {"area": 0, "perimeter": 0, "aspect_ratio": 1, "compactness": 0}
    
    def _extract_texture_features(self, roi: np.ndarray) -> Dict[str, Any]:
        """提取纹理特征"""
        # 转换为灰度图
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        
        # 计算梯度
        grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        
        # 梯度幅值
        gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
        
        return {
            "texture_roughness": np.std(gradient_magnitude),
            "texture_uniformity": 1.0 / (1.0 + np.var(gray)),
            "brightness": np.mean(gray)
        }
    
    def _rgb_to_color_name(self, rgb: np.ndarray) -> str:
        """将RGB值转换为颜色名称"""
        r, g, b = rgb
        
        # 简单的颜色分类
        if r > 200 and g > 200 and b < 100:
            return "黄色"
        elif r > 200 and g < 100 and b < 100:
            return "红色"
        elif r < 100 and g > 150 and b < 100:
            return "绿色"
        elif r < 100 and g < 100 and b > 150:
            return "蓝色"
        elif r < 100 and g < 100 and b < 100:
            return "黑色"
        elif r > 200 and g > 200 and b > 200:
            return "白色"
        elif r > 100 and g < 80 and b < 80:
            return "红褐色"
        elif r > 150 and g > 100 and b < 80:
            return "黄褐色"
        elif r < 80 and g < 80 and b < 80:
            return "黑褐色"
        else:
            return "褐色"
    
    def _calculate_feature_similarity(self, entity: EntityRecognitionResult) -> float:
        """计算实体特征与知识库的相似度"""
        best_similarity = 0.0
        
        # 根据实体类型，与对应的知识库实体比较
        for kb_name, kb_entity in self.entity_features_db.items():
            if kb_entity["type"] == entity.entity_type:
                similarity = self._compare_features(entity.features, kb_entity["features"])
                best_similarity = max(best_similarity, similarity)
        
        return best_similarity
    
    def _compare_features(self, features1: Dict[str, Any], features2: Dict[str, Any]) -> float:
        """比较两个特征字典的相似度"""
        similarity_scores = []
        
        # 比较颜色特征
        if "dominant_color" in features1 and "body_color" in features2:
            color1 = features1["dominant_color"]
            colors2 = features2["body_color"] if isinstance(features2["body_color"], list) else [features2["body_color"]]
            color_match = 1.0 if color1 in colors2 else 0.5 if any(c in color1 for c in colors2) else 0.0
            similarity_scores.append(color_match)
        
        # 比较大小特征
        if "area" in features1 and "body_length" in features2:
            # 这里可以基于面积推断大小类别
            area = features1["area"]
            if area > 10000:
                size_category = "大型"
            elif area > 5000:
                size_category = "中等"
            else:
                size_category = "小型"
            
            # 简单匹配
            if "小型" in features2["body_length"] and size_category == "小型":
                similarity_scores.append(0.8)
            elif "中等" in str(features2) and size_category == "中等":
                similarity_scores.append(0.8)
            else:
                similarity_scores.append(0.3)
        
        # 如果没有找到可比较的特征，返回基础相似度
        if not similarity_scores:
            return 0.5
        
        return np.mean(similarity_scores)
    
    def _find_best_match(self, entity: EntityRecognitionResult) -> Optional[str]:
        """找到最佳匹配的知识库实体"""
        best_match = None
        best_similarity = 0.0
        
        for kb_name, kb_entity in self.entity_features_db.items():
            if kb_entity["type"] == entity.entity_type:
                similarity = self._compare_features(entity.features, kb_entity["features"])
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = kb_name
        
        return best_match if best_similarity > self.similarity_threshold else None


class KnowledgeInferenceService:
    """知识推理服务"""
    
    def __init__(self, db_config: Dict[str, Any]):
        """
        初始化知识推理服务
        
        Args:
            db_config: 数据库配置
        """
        self.db_config = db_config
        self.confidence_threshold = 0.5
        
    async def analyze_disease_prediction(self, detected_entities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        基于检测到的实体进行病害预测分析
        
        Args:
            detected_entities: 检测到的实体列表
            
        Returns:
            预测分析结果
        """
        from ai_service import get_kimi_service
        import pymysql
        
        try:
            # 1. 实体分类
            insects = [e for e in detected_entities if e["type"] == "insect"]
            symptoms = [e for e in detected_entities if e["type"] == "disease_symptom"]
            trees = [e for e in detected_entities if e["type"] == "tree"]
            
            # 2. 从知识图谱中查询相关信息
            with self._get_db_connection() as conn:
                cursor = conn.cursor()
                
                # 查询相关的疾病信息
                disease_info = await self._query_disease_info(cursor, detected_entities)
                
                # 查询传播路径
                transmission_info = await self._query_transmission_paths(cursor, insects)
                
                # 查询防治措施
                treatment_info = await self._query_treatment_methods(cursor, disease_info)
            
            # 3. 使用AI进行深度分析
            kimi = get_kimi_service()
            ai_analysis = await self._get_ai_analysis(kimi, detected_entities, disease_info)
            
            # 4. 生成预测结果
            prediction = {
                "detected_summary": {
                    "insects_count": len(insects),
                    "symptoms_count": len(symptoms), 
                    "trees_count": len(trees),
                    "entities": detected_entities
                },
                "disease_prediction": {
                    "likely_diseases": disease_info.get("diseases", []),
                    "confidence": self._calculate_prediction_confidence(detected_entities, disease_info),
                    "risk_level": self._assess_risk_level(detected_entities, disease_info)
                },
                "transmission_analysis": transmission_info,
                "recommended_actions": treatment_info,
                "ai_insights": ai_analysis,
                "knowledge_gaps": await self._identify_knowledge_gaps(detected_entities)
            }
            
            return prediction
            
        except Exception as e:
            logger.error(f"病害预测分析失败: {e}")
            raise
    
    def _get_db_connection(self):
        """获取数据库连接"""
        import pymysql
        return pymysql.connect(**self.db_config)
    
    async def _query_disease_info(self, cursor, entities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """查询疾病相关信息"""
        diseases = []
        
        # 根据症状查询可能的疾病
        for entity in entities:
            if entity["type"] == "disease_symptom":
                entity_name = entity["matched_kb_entity"] or entity["name"]
                
                # 查询与症状相关的疾病
                cursor.execute("""
                    SELECT DISTINCT tail_entity as disease
                    FROM knowledge_triples 
                    WHERE head_entity = %s AND relation IN ('症状', '表现', '导致')
                """, (entity_name,))
                
                for row in cursor.fetchall():
                    if row["disease"] not in diseases:
                        diseases.append(row["disease"])
        
        return {"diseases": diseases}
    
    async def _query_transmission_paths(self, cursor, insects: List[Dict[str, Any]]) -> Dict[str, Any]:
        """查询传播路径信息"""
        transmission_paths = []
        
        for insect in insects:
            insect_name = insect["matched_kb_entity"] or insect["name"]
            
            # 查询昆虫的传播作用
            cursor.execute("""
                SELECT head_entity, relation, tail_entity
                FROM knowledge_triples 
                WHERE head_entity = %s AND relation IN ('传播', '携带', '媒介')
            """, (insect_name,))
            
            for row in cursor.fetchall():
                transmission_paths.append({
                    "vector": row["head_entity"],
                    "relation": row["relation"], 
                    "pathogen": row["tail_entity"]
                })
        
        return {"paths": transmission_paths}
    
    async def _query_treatment_methods(self, cursor, disease_info: Dict[str, Any]) -> Dict[str, Any]:
        """查询防治方法"""
        treatments = []
        
        for disease in disease_info.get("diseases", []):
            # 查询防治方法
            cursor.execute("""
                SELECT tail_entity as treatment
                FROM knowledge_triples 
                WHERE head_entity = %s AND relation IN ('防治', '治疗', '控制')
            """, (disease,))
            
            for row in cursor.fetchall():
                treatments.append({
                    "disease": disease,
                    "treatment": row["treatment"]
                })
        
        return {"treatments": treatments}
    
    async def _get_ai_analysis(self, kimi_service, entities: List[Dict[str, Any]], disease_info: Dict[str, Any]) -> str:
        """获取AI深度分析"""
        try:
            # 构建分析prompt
            entities_desc = ", ".join([f"{e['name']}({e['confidence']:.2f})" for e in entities])
            diseases_desc = ", ".join(disease_info.get("diseases", ["未知"]))
            
            prompt = f"""作为松材线虫病专家，请分析以下情况：

检测到的实体：{entities_desc}
可能的疾病：{diseases_desc}

请提供：
1. 综合诊断意见
2. 风险评估
3. 紧急程度评级
4. 建议的下一步行动

请用简洁专业的语言回答，不超过200字。"""

            if hasattr(kimi_service, 'client') and kimi_service.client:
                response = kimi_service.client.chat.completions.create(
                    model="moonshot-v1-8k",
                    messages=[
                        {"role": "system", "content": "你是松材线虫病领域的专家。"},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    max_tokens=300
                )
                return response.choices[0].message.content.strip()
            else:
                # Mock分析
                return f"基于检测结果，发现{len(entities)}个相关实体。建议进一步监测并采取相应防治措施。"
                
        except Exception as e:
            logger.error(f"AI分析失败: {e}")
            return "AI分析暂时不可用，请基于检测结果进行人工分析。"
    
    def _calculate_prediction_confidence(self, entities: List[Dict[str, Any]], disease_info: Dict[str, Any]) -> float:
        """计算预测置信度"""
        if not entities:
            return 0.0
        
        # 基于实体识别置信度和疾病关联度计算
        entity_confidences = [e["confidence"] for e in entities]
        avg_confidence = np.mean(entity_confidences)
        
        # 如果找到相关疾病，增加置信度
        disease_bonus = 0.2 if disease_info.get("diseases") else 0.0
        
        return round(min(avg_confidence + disease_bonus, 1.0), 1)
    
    def _assess_risk_level(self, entities: List[Dict[str, Any]], disease_info: Dict[str, Any]) -> str:
        """评估风险等级"""
        high_risk_symptoms = ["松针变红", "松针脱落", "树干流脂"]
        high_risk_insects = ["松墨天牛"]
        
        # 检查是否有高风险指标
        has_high_risk = any(
            entity["matched_kb_entity"] in high_risk_symptoms or 
            entity["matched_kb_entity"] in high_risk_insects
            for entity in entities
            if entity.get("matched_kb_entity")
        )
        
        if has_high_risk and disease_info.get("diseases"):
            return "高风险"
        elif has_high_risk or disease_info.get("diseases"):
            return "中风险"
        else:
            return "低风险"
    
    async def _identify_knowledge_gaps(self, entities: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """识别知识缺口"""
        gaps = []
        
        for entity in entities:
            # 如果相似度较低，可能是新的实体或变种
            if entity["similarity"] < self.confidence_threshold:
                gaps.append({
                    "type": "低匹配实体",
                    "entity": entity["name"],
                    "similarity": entity["similarity"],
                    "suggestion": f"建议将'{entity['name']}'添加到知识库中"
                })
        
        return gaps


# 全局服务实例
image_analysis_service = None
knowledge_inference_service = None


def init_image_services(db_config: Dict[str, Any]):
    """
    初始化图像服务
    
    Args:
        db_config: 数据库配置
    """
    global image_analysis_service, knowledge_inference_service
    
    image_analysis_service = ImageAnalysisService()
    knowledge_inference_service = KnowledgeInferenceService(db_config)
    
    logger.info("图像服务初始化完成")


def get_image_analysis_service() -> ImageAnalysisService:
    """获取图像分析服务实例"""
    if image_analysis_service is None:
        raise RuntimeError("图像分析服务未初始化")
    return image_analysis_service


def get_knowledge_inference_service() -> KnowledgeInferenceService:
    """获取知识推理服务实例"""
    if knowledge_inference_service is None:
        raise RuntimeError("知识推理服务未初始化")
    return knowledge_inference_service