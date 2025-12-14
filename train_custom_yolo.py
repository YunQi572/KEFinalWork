"""
自定义 YOLOv8 模型训练脚本
针对松材线虫病相关物种识别
"""
import os
from pathlib import Path
from ultralytics import YOLO
import yaml

def create_dataset_config():
    """
    创建数据集配置文件
    
    数据集目录结构应该是：
    pine_disease_dataset/
    ├── images/
    │   ├── train/
    │   │   ├── img001.jpg
    │   │   ├── img002.jpg
    │   │   └── ...
    │   └── val/
    │       ├── img101.jpg
    │       └── ...
    └── labels/
        ├── train/
        │   ├── img001.txt
        │   ├── img002.txt
        │   └── ...
        └── val/
            ├── img101.txt
            └── ...
    
    标注文件格式（YOLO格式）：
    每行一个对象：class_id center_x center_y width height
    坐标都是归一化的 (0-1)
    
    例如 img001.txt:
    0 0.45 0.52 0.12 0.18
    1 0.78 0.34 0.08 0.10
    """
    
    # 数据集配置
    dataset_config = {
        'path': r'D:\datasets\pine_disease_dataset',  # 修改为你的数据集路径
        'train': 'images/train',
        'val': 'images/val',
        'test': 'images/test',  # 可选
        
        # 类别定义 - 根据你的需求调整
        'names': {
            0: '七星瓢虫',        # 益虫
            1: '瓢虫',           # 通用瓢虫
            2: '松墨天牛',       # 主要害虫
            3: '天牛',           # 通用天牛
            4: '小蠹',           # 害虫
            5: '马尾松',         # 寄主植物
            6: '黑松',           # 寄主植物
            7: '松树',           # 通用松树
            8: '松针发黄',       # 病症
            9: '松针变红',       # 病症
            10: '树干流脂',      # 病症
            11: '健康松针',      # 正常状态
            12: '枯萎松针',      # 病症
        },
        
        'nc': 13  # 类别数量
    }
    
    # 保存配置文件
    config_path = 'pine_disease_data.yaml'
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(dataset_config, f, allow_unicode=True, sort_keys=False)
    
    print(f"✅ 数据集配置已保存到: {config_path}")
    return config_path


def train_model(
    data_yaml='pine_disease_data.yaml',
    base_model='yolov8m.pt',
    epochs=100,
    imgsz=640,
    batch=16,
    device=0,  # 0 表示第一个GPU，'cpu' 表示使用CPU
    project='pine_disease_models',
    name='pine_detector_v1'
):
    """
    训练自定义 YOLOv8 模型
    
    Args:
        data_yaml: 数据集配置文件路径
        base_model: 基础模型（预训练权重）
        epochs: 训练轮数
        imgsz: 输入图像大小
        batch: 批次大小（根据显存调整）
        device: 设备 (0, 1, 2, ... 或 'cpu')
        project: 项目名称
        name: 运行名称
    """
    
    print("="*80)
    print("开始训练自定义 YOLOv8 模型")
    print("="*80)
    
    # 检查数据集配置文件
    if not os.path.exists(data_yaml):
        print(f"❌ 数据集配置文件不存在: {data_yaml}")
        print("正在创建默认配置文件...")
        data_yaml = create_dataset_config()
    
    # 加载预训练模型
    print(f"\n📦 加载基础模型: {base_model}")
    model = YOLO(base_model)
    
    # 开始训练
    print(f"\n🚀 开始训练...")
    print(f"   数据集: {data_yaml}")
    print(f"   训练轮数: {epochs}")
    print(f"   图像大小: {imgsz}")
    print(f"   批次大小: {batch}")
    print(f"   设备: {device}")
    print()
    
    results = model.train(
        data=data_yaml,
        epochs=epochs,
        imgsz=imgsz,
        batch=batch,
        device=device,
        project=project,
        name=name,
        
        # 训练参数
        patience=50,          # 早停耐心值
        save=True,            # 保存检查点
        save_period=10,       # 每10轮保存一次
        cache=False,          # 不缓存图像（如果内存不足）
        
        # 优化器参数
        optimizer='Adam',
        lr0=0.01,            # 初始学习率
        lrf=0.01,            # 最终学习率
        momentum=0.937,
        weight_decay=0.0005,
        warmup_epochs=3.0,
        warmup_momentum=0.8,
        
        # 损失权重
        box=7.5,             # 边界框损失
        cls=0.5,             # 分类损失
        dfl=1.5,             # DFL损失
        
        # 数据增强
        hsv_h=0.015,         # HSV色调增强
        hsv_s=0.7,           # HSV饱和度增强
        hsv_v=0.4,           # HSV明度增强
        degrees=0.0,         # 旋转角度
        translate=0.1,       # 平移
        scale=0.5,           # 缩放
        shear=0.0,           # 剪切
        perspective=0.0,     # 透视变换
        flipud=0.0,          # 上下翻转
        fliplr=0.5,          # 左右翻转
        mosaic=1.0,          # Mosaic增强
        mixup=0.0,           # Mixup增强
        
        # 其他
        plots=True,          # 保存训练图表
        verbose=True,        # 详细输出
        seed=0,              # 随机种子
        deterministic=True,  # 确定性训练
        single_cls=False,    # 多类别
        rect=False,          # 矩形训练
        cos_lr=False,        # 余弦学习率
        close_mosaic=10,     # 最后10轮关闭mosaic
        amp=True,            # 自动混合精度
        fraction=1.0,        # 使用全部数据
        profile=False,       # 性能分析
        freeze=None,         # 冻结层
        
        # 验证参数
        val=True,            # 训练时验证
        split='val',         # 验证集划分
        
        # 多GPU训练（如果有多个GPU）
        # device=[0, 1],     # 使用多个GPU
    )
    
    print("\n" + "="*80)
    print("✅ 训练完成!")
    print("="*80)
    print(f"\n📁 模型保存位置: {project}/{name}/weights/")
    print(f"   - best.pt    : 最佳模型（推荐使用）")
    print(f"   - last.pt    : 最后一轮模型")
    print(f"\n📊 训练结果:")
    print(f"   - results.csv : 训练指标")
    print(f"   - results.png : 训练曲线图")
    print(f"   - confusion_matrix.png : 混淆矩阵")
    
    return results


def evaluate_model(model_path, data_yaml='pine_disease_data.yaml'):
    """
    评估训练好的模型
    
    Args:
        model_path: 模型权重路径
        data_yaml: 数据集配置文件
    """
    print("\n" + "="*80)
    print("评估模型性能")
    print("="*80)
    
    model = YOLO(model_path)
    
    # 在验证集上评估
    metrics = model.val(data=data_yaml)
    
    print(f"\n📊 评估结果:")
    print(f"   mAP50      : {metrics.box.map50:.4f}")
    print(f"   mAP50-95   : {metrics.box.map:.4f}")
    print(f"   Precision  : {metrics.box.mp:.4f}")
    print(f"   Recall     : {metrics.box.mr:.4f}")
    
    return metrics


def test_inference(model_path, image_path):
    """
    测试模型推理
    
    Args:
        model_path: 模型路径
        image_path: 测试图像路径
    """
    print("\n" + "="*80)
    print("测试模型推理")
    print("="*80)
    
    model = YOLO(model_path)
    
    # 推理
    results = model(image_path, conf=0.25)
    
    # 显示结果
    for r in results:
        print(f"\n检测到 {len(r.boxes)} 个对象:")
        for box in r.boxes:
            cls = int(box.cls[0])
            conf = float(box.conf[0])
            name = model.names[cls]
            print(f"  - {name}: {conf:.2%}")
        
        # 保存可视化结果
        output_path = str(Path(image_path).with_name(
            Path(image_path).stem + '_detected.jpg'
        ))
        r.save(filename=output_path)
        print(f"\n✅ 结果已保存: {output_path}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='训练自定义YOLOv8模型')
    parser.add_argument('--mode', type=str, default='train', 
                       choices=['train', 'eval', 'test', 'config'],
                       help='运行模式')
    parser.add_argument('--data', type=str, default='pine_disease_data.yaml',
                       help='数据集配置文件')
    parser.add_argument('--model', type=str, default='yolov8m.pt',
                       help='基础模型或训练好的模型路径')
    parser.add_argument('--epochs', type=int, default=100,
                       help='训练轮数')
    parser.add_argument('--batch', type=int, default=16,
                       help='批次大小')
    parser.add_argument('--imgsz', type=int, default=640,
                       help='图像大小')
    parser.add_argument('--device', default=0,
                       help='设备: 0, 1, 2, ... 或 cpu')
    parser.add_argument('--image', type=str, default=None,
                       help='测试图像路径')
    
    args = parser.parse_args()
    
    if args.mode == 'config':
        # 只创建配置文件
        create_dataset_config()
        
    elif args.mode == 'train':
        # 训练模型
        train_model(
            data_yaml=args.data,
            base_model=args.model,
            epochs=args.epochs,
            batch=args.batch,
            imgsz=args.imgsz,
            device=args.device
        )
        
    elif args.mode == 'eval':
        # 评估模型
        if not os.path.exists(args.model):
            print(f"❌ 模型文件不存在: {args.model}")
            exit(1)
        evaluate_model(args.model, args.data)
        
    elif args.mode == 'test':
        # 测试推理
        if not args.image:
            print("❌ 请提供测试图像路径: --image /path/to/image.jpg")
            exit(1)
        if not os.path.exists(args.model):
            print(f"❌ 模型文件不存在: {args.model}")
            exit(1)
        test_inference(args.model, args.image)


"""
使用示例：

1. 创建数据集配置文件
   python train_custom_yolo.py --mode config

2. 训练模型
   python train_custom_yolo.py --mode train --epochs 100 --batch 16

3. 评估模型
   python train_custom_yolo.py --mode eval --model pine_disease_models/pine_detector_v1/weights/best.pt

4. 测试推理
   python train_custom_yolo.py --mode test --model pine_disease_models/pine_detector_v1/weights/best.pt --image test.jpg
"""
