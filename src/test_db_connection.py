"""
测试MySQL数据库连接
"""
import pymysql
import sys

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'xyd123456',
    'database': 'kproject',
    'charset': 'utf8mb4'
}

def test_connection():
    """测试数据库连接"""
    print("=" * 60)
    print("MySQL数据库连接测试")
    print("=" * 60)
    print(f"\n配置信息:")
    print(f"  主机: {DB_CONFIG['host']}:{DB_CONFIG['port']}")
    print(f"  数据库: {DB_CONFIG['database']}")
    print(f"  用户: {DB_CONFIG['user']}")
    print(f"  密码: {'*' * len(DB_CONFIG['password'])}")
    print("\n" + "-" * 60)
    
    try:
        # 尝试连接
        print("\n[1/4] 正在连接数据库...")
        conn = pymysql.connect(**DB_CONFIG)
        print("✓ 连接成功!")
        
        # 测试查询
        print("\n[2/4] 测试查询...")
        cursor = conn.cursor()
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()[0]
        print(f"✓ MySQL版本: {version}")
        
        # 检查数据库
        print("\n[3/4] 检查数据库...")
        cursor.execute("SHOW DATABASES LIKE 'kproject'")
        result = cursor.fetchone()
        if result:
            print(f"✓ 数据库 'kproject' 存在")
        else:
            print("✗ 数据库 'kproject' 不存在")
            print("\n请先创建数据库:")
            print("  mysql -u root -p")
            print("  CREATE DATABASE kproject DEFAULT CHARACTER SET utf8mb4;")
            cursor.close()
            conn.close()
            return False
        
        # 检查表
        print("\n[4/4] 检查数据表...")
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        if tables:
            print(f"✓ 找到 {len(tables)} 个表:")
            for table in tables:
                table_name = table[0]
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                print(f"  - {table_name}: {count} 条记录")
        else:
            print("! 数据库中还没有表")
            print("  请运行: python init_db.py")
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 60)
        print("✓ 数据库连接测试通过!")
        print("=" * 60)
        return True
        
    except pymysql.err.OperationalError as e:
        print(f"\n✗ 连接失败: {e}")
        print("\n可能的原因:")
        print("  1. MySQL服务未启动")
        print("  2. 用户名或密码错误")
        print("  3. 数据库不存在")
        print("  4. 端口号错误")
        print("\n解决方法:")
        print("  检查MySQL服务: Get-Service MySQL*")
        print("  启动MySQL服务: Start-Service MySQL80")
        return False
        
    except Exception as e:
        print(f"\n✗ 错误: {e}")
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
