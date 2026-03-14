"""
数据库管理器
"""
import os
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from .models import Base, Job, Application


class DatabaseManager:
    """数据库管理器"""

    def __init__(self, db_path='data/jobs.db'):
        """初始化数据库连接"""
        # 确保数据目录存在
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        # 创建数据库引擎
        self.engine = create_engine(f'sqlite:///{db_path}', echo=False)

        # 创建表
        Base.metadata.create_all(self.engine)

        # 创建会话工厂
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def add_job(self, job_data):
        """添加岗位"""
        try:
            job = Job(**job_data)
            self.session.add(job)
            self.session.commit()
            return job
        except Exception as e:
            self.session.rollback()
            print(f"添加岗位失败: {e}")
            return None

    def get_job_by_id(self, job_id):
        """根据ID获取岗位"""
        return self.session.query(Job).filter(Job.id == job_id).first()

    def get_job_by_platform_id(self, platform_id):
        """根据平台ID获取岗位"""
        return self.session.query(Job).filter(Job.job_id == platform_id).first()

    def get_all_jobs(self, status=None, limit=None):
        """获取所有岗位"""
        query = self.session.query(Job)

        if status:
            query = query.filter(Job.status == status)

        query = query.order_by(desc(Job.created_at))

        if limit:
            query = query.limit(limit)

        return query.all()

    def update_job(self, job_id, **kwargs):
        """更新岗位信息"""
        try:
            job = self.get_job_by_id(job_id)
            if job:
                for key, value in kwargs.items():
                    setattr(job, key, value)
                self.session.commit()
                return job
            return None
        except Exception as e:
            self.session.rollback()
            print(f"更新岗位失败: {e}")
            return None

    def filter_jobs(self, city=None, salary_min=None, salary_max=None, keywords=None):
        """筛选岗位"""
        query = self.session.query(Job)

        if city:
            query = query.filter(Job.city == city)

        if keywords:
            for keyword in keywords:
                query = query.filter(
                    (Job.title.contains(keyword)) | (Job.description.contains(keyword))
                )

        return query.order_by(desc(Job.match_score)).all()

    def add_application(self, job_id, resume_path, notes=None):
        """添加投递记录"""
        try:
            application = Application(
                job_id=job_id,
                resume_path=resume_path,
                notes=notes
            )
            self.session.add(application)

            # 更新岗位状态
            job = self.get_job_by_id(job_id)
            if job:
                job.status = 'applied'

            self.session.commit()
            return application
        except Exception as e:
            self.session.rollback()
            print(f"添加投递记录失败: {e}")
            return None

    def get_applications(self, limit=None):
        """获取投递记录"""
        query = self.session.query(Application).order_by(desc(Application.applied_at))

        if limit:
            query = query.limit(limit)

        return query.all()

    def close(self):
        """关闭数据库连接"""
        self.session.close()
