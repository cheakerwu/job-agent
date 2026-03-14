#!/usr/bin/env python
"""
AI Agent 求职助手 - CLI 入口
"""
import os
import sys
import asyncio
import click
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# 加载环境变量
load_dotenv()

# 添加src到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.controller import JobAgentController
from src.utils import load_config, load_user_profile, save_user_profile, format_job_info

console = Console()


@click.group()
def cli():
    """AI Agent 求职助手 - 智能化求职工具"""
    pass


@cli.command()
@click.option('--keyword', '-k', required=True, help='搜索关键词')
@click.option('--city', '-c', default='北京', help='城市')
@click.option('--limit', '-l', default=30, help='爬取数量(页数)')
def crawl(keyword, city, limit):
    """爬取岗位信息"""
    try:
        config = load_config()
        controller = JobAgentController(config)

        # 计算页数
        max_pages = min(limit // 10 + 1, config['crawler']['max_pages'])

        console.print(f"[bold green]开始爬取岗位...[/bold green]")
        console.print(f"关键词: {keyword} | 城市: {city} | 页数: {max_pages}")

        # 执行爬取
        count = asyncio.run(controller.crawl_jobs(keyword, city, max_pages))

        console.print(f"[bold green]✓ 爬取完成! 新增 {count} 个岗位[/bold green]")

    except Exception as e:
        console.print(f"[bold red]✗ 爬取失败: {e}[/bold red]")
    finally:
        controller.close()


@cli.command()
@click.option('--status', '-s', help='状态筛选(new/filtered/applied)')
@click.option('--limit', '-l', default=20, help='显示数量')
def list(status, limit):
    """列出岗位列表"""
    try:
        config = load_config()
        controller = JobAgentController(config)

        jobs = controller.list_jobs(status=status, limit=limit)

        if not jobs:
            console.print("[yellow]暂无岗位数据[/yellow]")
            return

        # 创建表格
        table = Table(title=f"岗位列表 (共 {len(jobs)} 个)")
        table.add_column("ID", style="cyan")
        table.add_column("职位", style="green")
        table.add_column("公司", style="blue")
        table.add_column("城市", style="magenta")
        table.add_column("薪资", style="yellow")
        table.add_column("匹配度", style="red")
        table.add_column("状态", style="white")

        for job in jobs:
            match_score = f"{job.match_score}%" if job.match_score else "-"
            table.add_row(
                str(job.id),
                job.title[:30],
                job.company[:20],
                job.city,
                job.salary,
                match_score,
                job.status
            )

        console.print(table)

    except Exception as e:
        console.print(f"[bold red]✗ 获取列表失败: {e}[/bold red]")
    finally:
        controller.close()


@cli.command()
@click.argument('job_id', type=int)
def detail(job_id):
    """查看岗位详情"""
    try:
        config = load_config()
        controller = JobAgentController(config)

        job = controller.get_job_detail(job_id)

        if not job:
            console.print(f"[yellow]未找到岗位 ID: {job_id}[/yellow]")
            return

        # 显示详情
        panel_content = f"""
[bold green]职位:[/bold green] {job.title}
[bold blue]公司:[/bold blue] {job.company}
[bold magenta]城市:[/bold magenta] {job.city}
[bold yellow]薪资:[/bold yellow] {job.salary}
[bold cyan]链接:[/bold cyan] {job.url}
[bold red]匹配度:[/bold red] {job.match_score}% (如已筛选)

[bold]岗位描述:[/bold]
{job.description}

[bold]任职要求:[/bold]
{job.requirements}
"""
        console.print(Panel(panel_content, title=f"岗位详情 [ID: {job_id}]"))

    except Exception as e:
        console.print(f"[bold red]✗ 获取详情失败: {e}[/bold red]")
    finally:
        controller.close()


@cli.command()
@click.option('--city', '-c', help='城市筛选')
@click.option('--salary-min', type=int, help='最低薪资(K)')
@click.option('--salary-max', type=int, help='最高薪资(K)')
def filter(city, salary_min, salary_max):
    """筛选岗位"""
    try:
        config = load_config()
        profile = load_user_profile()
        controller = JobAgentController(config)

        # 获取用户偏好
        prefs = profile.get('filter_preferences', {})
        cities = [city] if city else prefs.get('cities')
        keywords = prefs.get('keywords')
        exclude_keywords = prefs.get('exclude_keywords')
        user_skills = profile.get('skills')

        console.print("[bold green]开始筛选岗位...[/bold green]")

        # 执行筛选
        jobs = controller.filter_jobs(
            cities=cities,
            salary_min=salary_min or prefs.get('salary_min'),
            salary_max=salary_max or prefs.get('salary_max'),
            keywords=keywords,
            exclude_keywords=exclude_keywords,
            user_skills=user_skills
        )

        console.print(f"[bold green]✓ 筛选完成! 找到 {len(jobs)} 个匹配岗位[/bold green]")

        # 显示前10个
        if jobs:
            console.print("\n[bold]Top 10 匹配岗位:[/bold]")
            for job in jobs[:10]:
                console.print(format_job_info(job))

    except Exception as e:
        console.print(f"[bold red]✗ 筛选失败: {e}[/bold red]")
    finally:
        controller.close()


@cli.command()
@click.argument('job_ids', nargs=-1, type=int, required=True)
def optimize(job_ids):
    """优化简历"""
    try:
        config = load_config()
        profile = load_user_profile()
        api_key = os.getenv('ANTHROPIC_API_KEY')

        if not api_key:
            console.print("[bold red]✗ 未配置 ANTHROPIC_API_KEY[/bold red]")
            console.print("请在 .env 文件中配置 API Key")
            return

        controller = JobAgentController(config, api_key)

        console.print(f"[bold green]开始优化 {len(job_ids)} 个简历...[/bold green]")

        # 执行优化
        results = controller.optimize_resumes(list(job_ids), profile)

        # 显示结果
        success_count = sum(1 for r in results if r['success'])
        console.print(f"\n[bold green]✓ 优化完成! 成功 {success_count}/{len(results)}[/bold green]")

        for result in results:
            if result['success']:
                console.print(f"  ✓ {result['job_title']}: {result['resume_path']}")
            else:
                console.print(f"  ✗ {result['job_title']}: 失败")

    except Exception as e:
        console.print(f"[bold red]✗ 优化失败: {e}[/bold red]")
    finally:
        controller.close()


@cli.command()
@click.option('--limit', '-l', default=10, help='显示数量')
def history(limit):
    """查看投递历史"""
    try:
        config = load_config()
        controller = JobAgentController(config)

        applications = controller.get_applications(limit=limit)

        if not applications:
            console.print("[yellow]暂无投递记录[/yellow]")
            return

        # 创建表格
        table = Table(title=f"投递历史 (共 {len(applications)} 条)")
        table.add_column("ID", style="cyan")
        table.add_column("岗位", style="green")
        table.add_column("简历路径", style="blue")
        table.add_column("投递时间", style="magenta")
        table.add_column("状态", style="yellow")

        for app in applications:
            job = app.job
            table.add_row(
                str(app.id),
                f"{job.title} - {job.company}",
                app.resume_path[-30:] if app.resume_path else "-",
                app.applied_at.strftime('%Y-%m-%d %H:%M'),
                app.status
            )

        console.print(table)

    except Exception as e:
        console.print(f"[bold red]✗ 获取历史失败: {e}[/bold red]")
    finally:
        controller.close()


@cli.command()
def config():
    """配置用户信息"""
    try:
        profile = load_user_profile()

        console.print("[bold green]当前用户配置:[/bold green]")
        console.print(f"姓名: {profile['basic_info']['name']}")
        console.print(f"学历: {profile['basic_info']['education']}")
        console.print(f"技能: {', '.join(profile['skills'])}")

        console.print("\n[yellow]如需修改,请编辑 config/user_profile.json[/yellow]")

    except Exception as e:
        console.print(f"[bold red]✗ 读取配置失败: {e}[/bold red]")


if __name__ == '__main__':
    cli()
