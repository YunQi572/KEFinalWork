import base64
from typing import Dict, Any, List
from io import BytesIO
from PIL import Image
import numpy as np
import cv2
import logging
from image_service import ImageAnalysisService, EntityRecognitionResult

logger = logging.getLogger("vision_ai")

class VisionAIImageAnalysisService(ImageAnalysisService):
    """
    使用 moonshot-v1-8k-vision-preview 支持图片输入的图像分析服务
    """
    async def _ai_recognize_image_content(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """
        直接将图片传给AI进行识别
        """
        print("使用moonshot-v1-8k-vision-preview进行图像识别")
        try:
            from ai_service import get_kimi_service
            kimi_service = get_kimi_service()

            # 将OpenCV图像转为PIL并编码为base64
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(image_rgb)
            buf = BytesIO()
            pil_img.save(buf, format='PNG')
            img_bytes = buf.getvalue()
            img_base64 = base64.b64encode(img_bytes).decode('utf-8')

            if not kimi_service.client:
                logger.warning("Kimi客户端不可用，跳过AI图像识别")
                return []

            # 构造AI分析提示（扩展为识别所有明显对象，包括益虫、瓢虫等）
            analysis_prompt = (
                "请仔细观察图像，识别出图像中的所有明显对象。\n\n"
                "【识别范围】包括但不限于：\n"
                "1. 昆虫类：瓢虫、七星瓢虫、天牛、松墨天牛、小蠹、蜜蜂、蝴蝶、螳螂、蚂蚁等\n"
                "2. 植物类：树木、松树、马尾松、黑松、叶片、花朵、草地、森林等\n"
                "3. 病症类：松针发黄、松针变红、树干流脂、叶片枯萎等\n"
                "4. 交通工具：汽车、卡车、货车、拖车、自行车等\n"
                "5. 建筑设施：房屋、仓库、道路、桥梁、围栏等\n"
                "6. 工业物品：原木、木材、集装箱、机械设备等\n"
                "7. 自然环境：天空、云朵、水体、土壤等\n"
                "8. 其他所有能看到的物体\n\n"
                "【重要提示】\n"
                "- 请特别注意识别小型昆虫，如瓢虫、七星瓢虫等益虫\n"
                "- 如果图像中有明显的红色昆虫或带黑点的昆虫，请优先识别\n"
                "- 请尽可能多地识别对象，不要遗漏任何明显物体\n\n"
                "【输出格式】\n"
                "请返回所有识别到的对象（至少5个），每行一个，严格按照以下格式：\n"
                "对象名称|置信度|类别|简短描述|位置\n\n"
                "类别选项：beneficial_insect、insect、plant、disease_symptom、tree、vehicle、building、natural、industrial、other\n"
                "置信度范围：0.0-1.0\n\n"
                "【输出示例】\n"
                "七星瓢虫|0.95|beneficial_insect|红色鞘翅带7个黑点的小型甲虫|center\n"
                "绿叶|0.90|plant|鲜绿色的叶片|center\n"
                "松墨天牛|0.85|insect|黑色大型甲虫|left\n"
                "马尾松|0.80|tree|针叶树种|background\n"
                "天空|0.75|natural|蓝色背景|top\n\n"
                "请严格按照示例格式返回，不要添加任何其他说明文字或解释。"
            )

            response = kimi_service.client.chat.completions.create(
                model="moonshot-v1-8k-vision-preview",
                messages=[
                    {"role": "system", "content": "你是一个松材线虫病识别专家，直接分析用户上传的图片。"},
                    {"role": "user", "content": analysis_prompt, "image": img_base64}
                ],
                temperature=0.5,
                max_tokens=300
            )

            ai_response = response.choices[0].message.content.strip()
            return self._parse_ai_response(ai_response)
        except Exception as e:
            logger.error(f"AI图像识别失败: {e}")
            return []

# 用法示例（异步环境下）
# service = VisionAIImageAnalysisService()
# result = await service.analyze_image(image_bytes)
# print(result)
