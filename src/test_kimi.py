"""
Kimi API 连接测试脚本
用于验证 Kimi API 是否正常工作
"""
from openai import OpenAI
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 获取API Key
api_key = os.getenv("MOONSHOT_API_KEY")

if not api_key:
    print("❌ 未找到 MOONSHOT_API_KEY，请检查 .env 文件")
    exit(1)

print(f"📝 使用API Key: {api_key[:20]}...")
print(f"🔗 连接到: https://api.moonshot.cn/v1")

try:
    # 初始化客户端（按照官方示例）
    client = OpenAI(
        api_key=api_key,
        base_url="https://api.moonshot.cn/v1"
    )
    
    print("✅ OpenAI客户端初始化成功!")
    
    # 测试API调用
    print("\n🧪 测试API调用...")
    response = client.chat.completions.create(
        model="moonshot-v1-8k",
        messages=[
            {
                "role": "system",
                "content": "你是一个松材线虫病领域的专家。"
            },
            {
                "role": "user",
                "content": "马尾松和松材线虫之间是什么关系？请从这些选项中选择：寄主、传播、防治、感染、致病。只返回一个关系词。"
            }
        ],
        temperature=0.3,
        max_tokens=50
    )
    
    result = response.choices[0].message.content.strip()
    print(f"✅ Kimi API 调用成功!")
    print(f"📤 返回结果: {result}")
    
    # 显示详细信息
    print(f"\n📊 详细信息:")
    print(f"   - 模型: {response.model}")
    print(f"   - 使用Token: {response.usage.total_tokens}")
    print(f"   - 提示Token: {response.usage.prompt_tokens}")
    print(f"   - 完成Token: {response.usage.completion_tokens}")
    
except Exception as e:
    print(f"\n❌ 错误: {e}")
    print(f"\n💡 建议:")
    print(f"   1. 检查openai包版本: pip install --upgrade openai>=1.3.0")
    print(f"   2. 验证API Key是否有效")
    print(f"   3. 检查网络连接")
    print(f"   4. 清除代理设置: $env:HTTP_PROXY=''")
