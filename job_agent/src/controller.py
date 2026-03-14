"""
核心控制器
"""
import asyncio
from .storage import DatabaseManager
from .crawler import BossCrawler
from .filter import JobFilter
from .resume import ResumeOptimizer
from .utils import setup_logger


class JobAgentController:
    """AI Agent 求职助手控制器"""

    def __init__(self, config, api_key=None):
        self.config = config
        self.logger = setup_logger('job_agent', config['storage']['log_dir'])
        self.db = DatabaseManager(config['storage']['db_path'])
        self.filter = JobFilter(config['filter'])

        # 初始化爬虫
        self.crawler = BossCrawler(config['crawler'])

        # 初始化简历优化器
        if api_key:
            self.resume_optimizer = ResumeOptimizer(api_key, config['resume'])
        else:
            self.resume_optimizer = None

    async def crawl_jobs(self, keyword, city, max_pages=5):
        """爬取岗位"""
        self.logger.info(f"开始爬取岗位: {keyword} @ {city}")
        print(f"开始爬取岗位: {keyword} @ {city}")

        # 爬取岗位
        jobs = await self.crawler.crawl(keyword, city, max_pages)

        # 保存到数据库
        saved_count = 0
        for job_data in jobs:
            # 检查是否已存在
            existing = self.db.get_job_by_platform_id(job_data['job_id'])
            if not existing:
                self.db.add_job(job_data)
                saved_count += 1

        message = f"爬取完成! 共找到 {len(jobs)} 个岗位, 新增 {saved_count} 个"
        self.logger.info(message)
        print(message)
        return saved_count

    def list_jobs(self, status=None, limit=None):
        """列出岗位"""
        jobs = self.db.get_all_jobs(status=status, limit=limit)
        return jobs

    def get_job_detail(self, job_id):
        """获取岗位详情"""
        job = self.db.get_job_by_id(job_id)
        return job

    def filter_jobs(self, cities=None, salary_min=None, salary_max=None,
                   keywords=None, exclude_keywords=None, user_skills=None):
        """筛选岗位"""
        # 获取所有岗位
        all_jobs = self.db.get_all_jobs(status='new')

        # 应用筛选条件
        filtered = self.filter.filter_by_conditions(
            all_jobs, cities, salary_min, salary_max, keywords, exclude_keywords
        )

        # 计算匹配度并排序
        if user_skills:
            ranked = self.filter.rank_jobs(filtered, user_skills)
        else:
            ranked = filtered

        # 更新数据库中的匹配度
        for job in ranked:
            if job.match_score:
                self.db.update_job(job.id, match_score=job.match_score, status='filtered')

        return ranked

    def optimize_resumes(self, job_ids, base_resume):
        """优化简历"""
        if not self.resume_optimizer:
            error_msg = "错误: 未配置API Key"
            self.logger.error(error_msg)
            print(error_msg)
            return []

        # 获取岗位
        jobs = [self.db.get_job_by_id(jid) for jid in job_ids]
        jobs = [j for j in jobs if j]  # 过滤None

        if not jobs:
            warning_msg = "未找到岗位"
            self.logger.warning(warning_msg)
            print(warning_msg)
            return []

        self.logger.info(f"开始优化 {len(jobs)} 个简历")

        # 批量优化
        results = self.resume_optimizer.batch_optimize(base_resume, jobs)

        # 记录投递
        success_count = 0
        for result in results:
            if result['success']:
                self.db.add_application(
                    result['job_id'],
                    result['resume_path'],
                    notes='简历已优化'
                )
                success_count += 1

        self.logger.info(f"简历优化完成: 成功 {success_count}/{len(jobs)}")
        return results

    def get_applications(self, limit=None):
        """获取投递记录"""
        return self.db.get_applications(limit=limit)

    def close(self):
        """关闭资源"""
        self.db.close()
