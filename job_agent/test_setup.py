#!/usr/bin/env python
"""
测试脚本 - 验证系统安装
"""
import sys
import os

def test_imports():
    """测试依赖包导入"""
    print("测试依赖包导入...")

    try:
        import click
        print("  ✓ click")
    except ImportError:
        print("  ✗ click - 请运行: pip install click")
        return False

    try:
        import rich
        print("  ✓ rich")
    except ImportError:
        print("  ✗ rich - 请运行: pip install rich")
        return False

    try:
        import yaml
        print("  ✓ pyyaml")
    except ImportError:
        print("  ✗ pyyaml - 请运行: pip install pyyaml")
        return False

    try:
        import sqlalchemy
        print("  ✓ sqlalchemy")
    except ImportError:
        print("  ✗ sqlalchemy - 请运行: pip install sqlalchemy")
        return False

    try:
        from dotenv import load_dotenv
        print("  ✓ python-dotenv")
    except ImportError:
        print("  ✗ python-dotenv - 请运行: pip install python-dotenv")
        return False

    print("\n所有依赖包导入成功!")
    return True


def test_config():
    """测试配置文件"""
    print("\n测试配置文件...")

    if not os.path.exists('config/config.yaml'):
        print("  ✗ config/config.yaml 不存在")
        return False
    print("  ✓ config/config.yaml")

    if not os.path.exists('config/user_profile.json'):
        print("  ✗ config/user_profile.json 不存在")
        return False
    print("  ✓ config/user_profile.json")

    print("\n配置文件检查通过!")
    return True


def test_database():
    """测试数据库"""
    print("\n测试数据库...")

    try:
        sys.path.insert(0, 'src')
        from storage import DatabaseManager

        db = DatabaseManager('data/test.db')
        print("  ✓ 数据库创建成功")

        # 清理测试数据库
        os.remove('data/test.db')
        print("  ✓ 数据库测试通过")

        return True

    except Exception as e:
        print(f"  ✗ 数据库测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("=" * 50)
    print("AI Agent 求职助手 - 系统测试")
    print("=" * 50)

    results = []

    # 测试导入
    results.append(test_imports())

    # 测试配置
    results.append(test_config())

    # 测试数据库
    results.append(test_database())

    # 总结
    print("\n" + "=" * 50)
    if all(results):
        print("✓ 所有测试通过! 系统已就绪")
        print("\n快速开始:")
        print("  1. 配置 .env 文件中的 ANTHROPIC_API_KEY")
        print("  2. 编辑 config/user_profile.json")
        print("  3. 运行: python cli.py crawl -k 'Python实习' -c '北京'")
    else:
        print("✗ 部分测试失败,请检查上述错误")
    print("=" * 50)


if __name__ == '__main__':
    main()
