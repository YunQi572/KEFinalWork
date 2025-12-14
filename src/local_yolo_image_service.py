"""
本地化图像识别服务 - 基于 YOLOv8
替代 moonshot-v1-8k-vision-preview 的本地部署方案
"""
import base64
from typing import Dict, Any, List
from io import BytesIO
from PIL import Image
import numpy as np
import cv2
import logging
from image_service import ImageAnalysisService, EntityRecognitionResult

logger = logging.getLogger("local_yolo")


class LocalYOLOImageAnalysisService(ImageAnalysisService):
    """
    使用本地 YOLOv8 模型进行图像识别
    完全离线运行，不依赖任何云端服务
    """
    
    def __init__(self, model_path: str = "yolov8n.pt", use_custom_model: bool = False):
        """
        初始化本地 YOLO 服务
        
        Args:
            model_path: YOLO 模型文件路径
                - "yolov8n.pt": 纳米版（最快，准确率较低）
                - "yolov8s.pt": 小型版（平衡）
                - "yolov8m.pt": 中型版（推荐）
                - "yolov8l.pt": 大型版（高精度）
                - "yolov8x.pt": 超大版（最高精度，最慢）
                - 或自定义训练的模型路径
            use_custom_model: 是否使用自定义训练的模型
        """
        super().__init__()
        self.model_path = model_path
        self.use_custom_model = use_custom_model
        self.model = None
        self._load_model()
        
        # 类别映射：将 YOLO 识别的类别映射到我们的领域
        self.category_mapping = {
            # 动物/昆虫类
            "insect": "insect",
            "beetle": "insect",
            "bee": "beneficial_insect",
            "ladybug": "beneficial_insect",
            "butterfly": "beneficial_insect",
            "bug": "insect",
            "fly": "insect",
            
            # 植物类
            "tree": "tree",
            "plant": "plant",
            "leaf": "plant",
            "grass": "plant",
            "flower": "plant",
            "branch": "plant",
            
            # 环境类
            "sky": "natural",
            "cloud": "natural",
            "water": "natural",
            "ground": "natural",
            "soil": "natural",
            
            # 人造物品
            "car": "vehicle",
            "truck": "vehicle",
            "vehicle": "vehicle",
            "building": "building",
            "house": "building",
            "road": "building",
            
            # 其他
            "person": "other",
            "animal": "other",
        }
        
        # 关键物种的中文名称映射（可根据实际训练模型调整）
        self.species_names = {
            "beetle": "天牛",
            "ladybug": "瓢虫",
            "insect": "昆虫",
            "tree": "树木",
            "leaf": "叶片",
            "pine": "松树",
        }
        
    def _load_model(self):
        """加载 YOLO 模型"""
        try:
            from ultralytics import YOLO
            logger.info(f"正在加载 YOLO 模型: {self.model_path}")
            self.model = YOLO(self.model_path)
            logger.info("YOLO 模型加载成功")
        except ImportError:
            logger.error("未安装 ultralytics 库，请运行: pip install ultralytics")
            raise
        except Exception as e:
            logger.error(f"模型加载失败: {e}")
            raise
    
    async def _ai_recognize_image_content(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """
        使用本地 YOLO 模型进行图像识别
        
        Args:
            image: OpenCV 格式的图像 (BGR)
            
        Returns:
            识别结果列表
        """
        print("使用本地 YOLOv8 模型进行图像识别")
        
        if self.model is None:
            logger.warning("YOLO 模型未加载，跳过识别")
            return []
        
        try:
            # 运行 YOLO 推理
            # 降低置信度阈值以检测更多物体
            results = self.model(
                image, 
                conf=0.15,        # 置信度阈值（默认0.25，降低到0.15）
                iou=0.45,         # NMS IOU阈值
                max_det=300,      # 最大检测数量
                verbose=False
            )
            
            objects = []
            
            # 处理每个检测结果
            if len(results) > 0:
                result = results[0]
                boxes = result.boxes
                
                for box in boxes:
                    # 获取类别和置信度
                    cls_id = int(box.cls[0])
                    class_name = self.model.names[cls_id]
                    confidence = float(box.conf[0])
                    
                    # 获取边界框信息（用于判断位置）
                    xyxy = box.xyxy[0].cpu().numpy()
                    x1, y1, x2, y2 = xyxy
                    
                    # 计算中心位置
                    center_x = (x1 + x2) / 2
                    center_y = (y1 + y2) / 2
                    img_h, img_w = image.shape[:2]
                    
                    # 判断物体在图像中的位置
                    location = self._determine_location(center_x, center_y, img_w, img_h)
                    
                    # 映射类别
                    category = self.category_mapping.get(class_name.lower(), "other")
                    
                    # 获取中文名称
                    chinese_name = self.species_names.get(class_name.lower(), class_name)
                    
                    # 生成描述
                    description = f"检测到的{chinese_name}"
                    
                    # 特殊处理：如果是松树相关
                    if "pine" in class_name.lower() or "树" in chinese_name:
                        category = "tree"
                        description = f"可能的松树或针叶树"
                    
                    objects.append({
                        "name": chinese_name,
                        "confidence": confidence,
                        "category": category,
                        "description": description,
                        "location": location,
                        "bbox": {
                            "x1": float(x1),
                            "y1": float(y1),
                            "x2": float(x2),
                            "y2": float(y2)
                        }
                    })
            
            # 如果没有检测到物体，添加一些基础分析
            if len(objects) == 0:
                logger.info("未检测到特定物体，添加通用背景分析")
                objects = self._fallback_analysis(image)
            
            # 按置信度排序
            objects.sort(key=lambda x: x["confidence"], reverse=True)
            
            logger.info(f"YOLO 识别完成，共检测到 {len(objects)} 个物体")
            return objects
            
        except Exception as e:
            logger.error(f"YOLO 识别失败: {e}", exc_info=True)
            return []
    
    def _determine_location(self, center_x: float, center_y: float, 
                          img_w: float, img_h: float) -> str:
        """
        根据物体中心位置判断在图像中的位置
        
        Args:
            center_x, center_y: 物体中心坐标
            img_w, img_h: 图像宽高
            
        Returns:
            位置描述: center, top, bottom, left, right, top-left, 等
        """
        x_ratio = center_x / img_w
        y_ratio = center_y / img_h
        
        # 定义区域
        if 0.33 < x_ratio < 0.67 and 0.33 < y_ratio < 0.67:
            return "center"
        elif y_ratio < 0.33:
            if x_ratio < 0.33:
                return "top-left"
            elif x_ratio > 0.67:
                return "top-right"
            else:
                return "top"
        elif y_ratio > 0.67:
            if x_ratio < 0.33:
                return "bottom-left"
            elif x_ratio > 0.67:
                return "bottom-right"
            else:
                return "bottom"
        elif x_ratio < 0.33:
            return "left"
        else:
            return "right"
    
    def _fallback_analysis(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """
        当 YOLO 未检测到物体时的后备分析
        基于颜色、纹理等基础特征进行分析
        
        Args:
            image: OpenCV 图像
            
        Returns:
            基础分析结果
        """
        results = []
        
        try:
            # 分析主要颜色
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            h, s, v = cv2.split(hsv)
            
            # 统计颜色分布
            green_mask = cv2.inRange(hsv, (35, 40, 40), (85, 255, 255))
            brown_mask = cv2.inRange(hsv, (10, 40, 40), (25, 255, 255))
            blue_mask = cv2.inRange(hsv, (100, 40, 40), (130, 255, 255))
            
            green_ratio = cv2.countNonZero(green_mask) / (image.shape[0] * image.shape[1])
            brown_ratio = cv2.countNonZero(brown_mask) / (image.shape[0] * image.shape[1])
            blue_ratio = cv2.countNonZero(blue_mask) / (image.shape[0] * image.shape[1])
            
            # 根据颜色比例推断场景
            if green_ratio > 0.3:
                results.append({
                    "name": "植被",
                    "confidence": min(green_ratio * 2, 0.8),
                    "category": "plant",
                    "description": "图像包含大量绿色植被",
                    "location": "background"
                })
            
            if brown_ratio > 0.2:
                results.append({
                    "name": "树干或土壤",
                    "confidence": min(brown_ratio * 2, 0.7),
                    "category": "natural",
                    "description": "图像包含棕色区域，可能是树干或土壤",
                    "location": "background"
                })
            
            if blue_ratio > 0.2:
                results.append({
                    "name": "天空",
                    "confidence": min(blue_ratio * 2, 0.8),
                    "category": "natural",
                    "description": "图像包含蓝色区域，可能是天空",
                    "location": "background"
                })
            
            # 如果仍然没有结果，添加默认分析
            if len(results) == 0:
                results.append({
                    "name": "自然场景",
                    "confidence": 0.5,
                    "category": "natural",
                    "description": "户外自然环境",
                    "location": "background"
                })
            
        except Exception as e:
            logger.error(f"后备分析失败: {e}")
            results.append({
                "name": "未知场景",
                "confidence": 0.3,
                "category": "other",
                "description": "无法详细分析",
                "location": "unknown"
            })
        
        return results


# ============= 自定义模型训练说明 =============
"""
如果需要针对松材线虫病进行专门的模型训练，可以按照以下步骤：

1. 准备数据集
   - 收集松墨天牛、松树、病症等图像
   - 使用 labelImg 或 LabelStudio 进行标注
   - 按照 YOLO 格式组织数据集

2. 训练模型
   ```python
   from ultralytics import YOLO
   
   # 加载预训练模型
   model = YOLO('yolov8n.pt')
   
   # 训练
   results = model.train(
       data='pine_disease.yaml',  # 数据集配置文件
       epochs=100,
       imgsz=640,
       batch=16,
       name='pine_disease_detector'
   )
   ```

3. 使用自定义模型
   ```python
   service = LocalYOLOImageAnalysisService(
       model_path='runs/detect/pine_disease_detector/weights/best.pt',
       use_custom_model=True
   )
   ```
"""


# 用法示例
if __name__ == "__main__":
    import asyncio
    
    async def test_local_yolo():
        # 初始化服务（使用默认的 YOLOv8n 模型）
        service = LocalYOLOImageAnalysisService(model_path="yolov8n.pt")
        
        # 读取测试图像
        test_image_path = "test_image.jpg"
        if os.path.exists(test_image_path):
            image = cv2.imread(test_image_path)
            
            # 进行识别
            results = await service._ai_recognize_image_content(image)
            
            print(f"识别结果：")
            for obj in results:
                print(f"- {obj['name']}: {obj['confidence']:.2f} ({obj['category']}) - {obj['description']}")
        else:
            print(f"测试图像不存在: {test_image_path}")
    
    asyncio.run(test_local_yolo())
