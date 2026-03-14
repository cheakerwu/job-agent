#!/usr/bin/env python
"""
使用示例 - 演示如何编程方式使用系统
"""
import asyncio
import sys
import os

# 添加 src 到路径
sys.path.insert(0, 'src')

from src.controller import JobAgentController
from src.utils import load_config, load_user_profile


async def example_workflow():
    """完整工作流程示例"""

    # 1. 加载配置
    print("=" * 50)
    print("1. 加载配置")
    print("=" * 50)

    config = load_config()
    profile = load_user_profile()
    api_key = os.getenv('ANTHROPIC_API_KEY')

    print(f"用户: {profile['basic_info']['name']}")
    print(f"技能: {', '.join(profile['skills'][:5])}")

    # 2. 初始化控制器
    print("\n" + "=" * 50)
    print("2. 初始化控制器")
    print("=" * 50)

    controller = JobAgentController(config, api_key)
    print("✓ 控制器初始化成功")

    # 3. 爬取岗位
    print("\n" + "=" * 50)
    print("3. 爬取岗位")
    print("=" * 50)

    keyword = "Python实习"
    city = "北京"
    max_pages = 2  # 测试用,只爬2页

    print(f"关键词: {keyword}")
    print(f"城市: {city}")
    print(f"页数: {max_pages}")

    count = await controller.crawl_jobs(keyword, city, max_pages)
    print(f"✓ 新增 {count} 个岗位")

    # 4. 列出岗位
    print("\n" + "=" * 50)
    print("4. 列出岗位")
    print("=" * 50)

    jobs = controller.list_jobs(status='new', limit=10)
    print(f"找到 {len(jobs)} 个新岗位:")

    for job in jobs[:5]:
        print(f"  [{job.id}] {job.title} - {job.company} ({job.salary})")

    # 5. 筛选岗位
    print("\n" + "=" * 50)
    print("5. 筛选岗位")
    print("=" * 50)

    prefs = profile['filter_preferences']
    filtered_jobs = controller.filter_jobs(
        cities=prefs['cities'],
        salary_min=prefs['salary_min'],
        salary_max=prefs['salary_max'],
        keywords=prefs['keywords'],
        exclude_keywords=prefs['exclude_keywords'],
        user_skills=profile['skills']
    )

    print(f"筛选后: {len(filtered_jobs)} 个匹配岗位")
    print("\nTop 5 匹配岗位:")

    for job in filtered_jobs[:5]:
        print(f"  [{job.id}] {job.title} - {job.company}")
        print(f"      匹配度: {job.match_score}% | 薪资: {job.salary}")

    # 6. 查看详情
    if filtered_jobs:
        print("\n" + "=" * 50)
        print("6. 查看岗位详情")
        print("=" * 50)

        top_job = filtered_jobs[0]
        print(f"岗位: {top_job.title}")
        print(f"公司: {top_job.company}")
        print(f"链接: {top_job.url}")
        print(f"\n描述:\n{top_job.description[:200]}...")

    # 7. 优化简历(可选,需要API Key)
    if api_key and filtered_jobs:
        print("\n" + "=" * 50)
        print("7. 优化简历")
        print("=" * 50)

        # 只优化前3个岗位
        job_ids = [job.id for job in filtered_jobs[:3]]
        print(f"为 {len(job_ids)} 个岗位优化简历...")

        results = controller.optimize_resumes(job_ids, profile)

        success_count = sum(1 for r in results if r['success'])
        print(f"✓ 成功优化 {success_count}/{len(results)} 个简历")

        for result in results:
            if result['success']:
                print(f"  ✓ {result['job_title']}")
                print(f"     {result['resume_path']}")

    # 8. 查看投递历史
    print("\n" + "=" * 50)
    print("8. 投递历史")
    print("=" * 50)

    applications = controller.get_applications(limit=5)
    print(f"共 {len(applications)} 条投递记录")

    for app in applications:
        print(f"  [{app.id}] {app.job.title} - {app.job.company}")
        print(f"      时间: {app.applied_at.strftime('%Y-%m-%d %H:%M')}")

    # 9. 清理
    print("\n" + "=" * 50)
    print("9. 清理资源")
    print("=" * 50)

    controller.close()
    print("✓ 资源已释放")

    print("\n" + "=" * 50)
    print("示例完成!")
    print("=" * 50)


def main():
    """主函数"""
    print("AI Agent 求职助手 - 使用示例\n")

    # 检查环境
    if not os.path.exists('config/config.yaml'):
        print("错误: 未找到配置文件 config/config.yaml")
        return

    if not os.path.exists('config/user_profile.json'):
        print("错误: 未找到用户配置 config/user_profile.json")
        return

    # 运行示例
    try:
        asyncio.run(example_workflow())
    except KeyboardInterrupt:
        print("\n\n用户中断")
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
