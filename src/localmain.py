"""
本地模型运行主程序
使用 YOLOv8 进行图像识别，替代 moonshot-v1-8k-vision-preview
"""
import asyncio
import cv2
import os
import sys
from pathlib import Path
import logging
from datetime import datetime

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.local_yolo_image_service import LocalYOLOImageAnalysisService

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def visualize_results(image, results, output_path: str):
    """
    在图像上绘制识别结果
    
    Args:
        image: OpenCV 图像
        results: 识别结果列表
        output_path: 输出路径
    """
    vis_image = image.copy()
    
    # 定义颜色（BGR 格式）
    colors = {
        'insect': (0, 0, 255),           # 红色
        'beneficial_insect': (0, 255, 0), # 绿色
        'plant': (0, 200, 0),            # 深绿色
        'tree': (0, 150, 0),             # 更深绿色
        'disease_symptom': (0, 0, 255),  # 红色
        'natural': (255, 200, 100),      # 浅蓝色
        'vehicle': (255, 0, 0),          # 蓝色
        'building': (128, 128, 128),     # 灰色
        'other': (200, 200, 200)         # 浅灰色
    }
    
    for obj in results:
        if 'bbox' in obj:
            bbox = obj['bbox']
            x1, y1 = int(bbox['x1']), int(bbox['y1'])
            x2, y2 = int(bbox['x2']), int(bbox['y2'])
            
            # 获取颜色
            color = colors.get(obj['category'], (0, 255, 0))
            
            # 绘制边界框
            cv2.rectangle(vis_image, (x1, y1), (x2, y2), color, 2)
            
            # 准备标签文本
            label = f"{obj['name']} {obj['confidence']:.2f}"
            
            # 计算文本大小
            (text_width, text_height), baseline = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2
            )
            
            # 绘制文本背景
            cv2.rectangle(
                vis_image,
                (x1, y1 - text_height - baseline - 5),
                (x1 + text_width, y1),
                color,
                -1
            )
            
            # 绘制文本
            cv2.putText(
                vis_image,
                label,
                (x1, y1 - baseline - 2),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                2
            )
    
    # 保存结果
    cv2.imwrite(output_path, vis_image)
    logger.info(f"可视化结果已保存: {output_path}")


async def analyze_single_image(service: LocalYOLOImageAnalysisService, 
                               image_path: str, 
                               visualize: bool = True):
    """
    分析单张图像
    
    Args:
        service: 图像分析服务
        image_path: 图像路径
        visualize: 是否生成可视化结果
    """
    logger.info(f"正在分析图像: {image_path}")
    
    # 读取图像
    image = cv2.imread(image_path)
    if image is None:
        logger.error(f"无法读取图像: {image_path}")
        return
    
    logger.info(f"图像尺寸: {image.shape[1]}x{image.shape[0]}")
    
    # 进行识别
    try:
        results = await service._ai_recognize_image_content(image)
        
        # 输出结果
        print("\n" + "="*80)
        print(f"识别结果 - {os.path.basename(image_path)}")
        print("="*80)
        print(f"共检测到 {len(results)} 个对象:\n")
        
        for i, obj in enumerate(results, 1):
            print(f"{i}. {obj['name']}")
            print(f"   ├─ 置信度: {obj['confidence']:.2%}")
            print(f"   ├─ 类别: {obj['category']}")
            print(f"   ├─ 描述: {obj['description']}")
            print(f"   ├─ 位置: {obj['location']}")
            
            if 'bbox' in obj:
                bbox = obj['bbox']
                print(f"   └─ 边界框: ({bbox['x1']:.0f}, {bbox['y1']:.0f}) -> "
                      f"({bbox['x2']:.0f}, {bbox['y2']:.0f})")
            print()
        
        print("="*80 + "\n")
        
        # 可视化
        if visualize and len(results) > 0:
            # 检查是否有边界框
            has_bbox = any('bbox' in obj for obj in results)
            if has_bbox:
                output_dir = Path(image_path).parent
                output_filename = Path(image_path).stem + "_result.jpg"
                output_path = str(output_dir / output_filename)
                visualize_results(image, results, output_path)
                print(f"✅ 可视化结果已保存: {output_path}\n")
            else:
                print("ℹ️  检测结果无边界框信息，跳过可视化\n")
        
        return results
        
    except Exception as e:
        logger.error(f"分析失败: {e}", exc_info=True)
        return None


async def analyze_directory(service: LocalYOLOImageAnalysisService,
                            directory: str,
                            visualize: bool = True):
    """
    批量分析目录下的所有图像
    
    Args:
        service: 图像分析服务
        directory: 图像目录
        visualize: 是否生成可视化结果
    """
    logger.info(f"正在扫描目录: {directory}")
    
    # 支持的图像格式
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
    
    # 查找所有图像文件
    dir_path = Path(directory)
    image_files = [
        str(f) for f in dir_path.iterdir()
        if f.is_file() and f.suffix.lower() in image_extensions
    ]
    
    if not image_files:
        logger.warning(f"目录中没有找到图像文件: {directory}")
        return
    
    logger.info(f"找到 {len(image_files)} 张图像")
    
    # 批量处理
    all_results = {}
    for i, image_path in enumerate(image_files, 1):
        print(f"\n处理进度: {i}/{len(image_files)}")
        results = await analyze_single_image(service, image_path, visualize)
        all_results[image_path] = results
    
    # 统计摘要
    print("\n" + "="*80)
    print("批量分析完成 - 统计摘要")
    print("="*80)
    
    total_objects = sum(len(r) for r in all_results.values() if r)
    print(f"处理图像数: {len(image_files)}")
    print(f"检测对象总数: {total_objects}")
    print(f"平均每张图: {total_objects/len(image_files):.1f} 个对象")
    print("="*80 + "\n")
    
    return all_results


async def interactive_mode(service: LocalYOLOImageAnalysisService):
    """
    交互式模式 - 让用户输入图像路径进行分析
    
    Args:
        service: 图像分析服务
    """
    print("\n" + "="*80)
    print("本地模型图像识别 - 交互模式")
    print("="*80)
    print("输入图像文件路径或目录路径进行分析")
    print("输入 'q' 或 'quit' 退出程序")
    print("="*80 + "\n")
    
    while True:
        try:
            # 获取用户输入
            user_input = input("请输入图像路径或目录: ").strip()
            
            # 检查退出命令
            if user_input.lower() in ['q', 'quit', 'exit']:
                print("退出程序")
                break
            
            # 检查路径是否存在
            if not os.path.exists(user_input):
                print(f"❌ 路径不存在: {user_input}\n")
                continue
            
            # 判断是文件还是目录
            if os.path.isfile(user_input):
                await analyze_single_image(service, user_input, visualize=True)
            elif os.path.isdir(user_input):
                await analyze_directory(service, user_input, visualize=True)
            else:
                print(f"❌ 无效的路径类型: {user_input}\n")
                
        except KeyboardInterrupt:
            print("\n\n程序被用户中断")
            break
        except Exception as e:
            logger.error(f"发生错误: {e}", exc_info=True)


async def main():
    """主函数"""
    print("\n" + "="*80)
    print("本地模型图像识别系统")
    print("基于 YOLOv8 - 替代 moonshot-v1-8k-vision-preview")
    print("="*80 + "\n")
    
    # 配置参数
    MODEL_PATH = "yolov8m.pt"  # 可选: yolov8n.pt, yolov8s.pt, yolov8m.pt, yolov8l.pt, yolov8x.pt
    
    # 初始化服务
    logger.info(f"正在加载模型: {MODEL_PATH}")
    try:
        service = LocalYOLOImageAnalysisService(model_path=MODEL_PATH)
        logger.info("✅ 模型加载成功!\n")
    except Exception as e:
        logger.error(f"❌ 模型加载失败: {e}")
        print("\n请确保已安装依赖:")
        print("  pip install -r requirements_local_model.txt\n")
        return
    
    # 检查命令行参数
    if len(sys.argv) > 1:
        # 命令行模式
        target_path = sys.argv[1]
        
        if not os.path.exists(target_path):
            logger.error(f"路径不存在: {target_path}")
            return
        
        if os.path.isfile(target_path):
            await analyze_single_image(service, target_path, visualize=True)
        elif os.path.isdir(target_path):
            await analyze_directory(service, target_path, visualize=True)
    else:
        # 交互式模式
        await interactive_mode(service)


if __name__ == "__main__":
    # 运行主程序
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n程序被用户中断")
    except Exception as e:
        logger.error(f"程序异常: {e}", exc_info=True)
