"""
数据模型定义
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Job(Base):
    """岗位表"""
    __tablename__ = 'jobs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(String(100), unique=True, nullable=False)  # 平台岗位ID
    title = Column(String(200), nullable=False)  # 职位名称
    company = Column(String(200), nullable=False)  # 公司名称
    city = Column(String(50))  # 城市
    salary = Column(String(100))  # 薪资范围
    description = Column(Text)  # 岗位描述
    requirements = Column(Text)  # 任职要求(JSON)
    platform = Column(String(20), default='boss')  # 来源平台
    url = Column(String(500))  # 岗位链接
    status = Column(String(20), default='new')  # 状态(new/filtered/applied)
    match_score = Column(Integer)  # 匹配度得分(0-100)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # 关系
    applications = relationship("Application", back_populates="job")

    def __repr__(self):
        return f"<Job(id={self.id}, title='{self.title}', company='{self.company}')>"


class Application(Base):
    """投递记录表"""
    __tablename__ = 'applications'

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(Integer, ForeignKey('jobs.id'), nullable=False)
    resume_path = Column(String(500))  # 简历文件路径
    applied_at = Column(DateTime, default=datetime.now)
    status = Column(String(20), default='pending')  # pending/success/failed
    notes = Column(Text)  # 备注

    # 关系
    job = relationship("Job", back_populates="applications")

    def __repr__(self):
        return f"<Application(id={self.id}, job_id={self.job_id}, status='{self.status}')>"
