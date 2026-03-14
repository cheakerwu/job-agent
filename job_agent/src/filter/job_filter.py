"""
岗位筛选器
"""
import re
import json


class JobFilter:
    """岗位筛选器"""

    def __init__(self, config):
        self.config = config

    def filter_by_conditions(self, jobs, cities=None, salary_min=None, salary_max=None,
                            keywords=None, exclude_keywords=None):
        """基于条件筛选岗位"""
        filtered_jobs = []

        for job in jobs:
            # 城市筛选
            if cities and job.city not in cities:
                continue

            # 薪资筛选
            if salary_min or salary_max:
                salary_range = self._parse_salary(job.salary)
                if salary_range:
                    min_sal, max_sal = salary_range
                    if salary_min and max_sal < salary_min:
                        continue
                    if salary_max and min_sal > salary_max:
                        continue

            # 关键词筛选
            if keywords:
                text = f"{job.title} {job.description}".lower()
                if not any(kw.lower() in text for kw in keywords):
                    continue

            # 排除关键词
            if exclude_keywords:
                text = f"{job.title} {job.description}".lower()
                if any(kw.lower() in text for kw in exclude_keywords):
                    continue

            filtered_jobs.append(job)

        return filtered_jobs

    def calculate_match_score(self, job, user_skills, skill_weights=None):
        """计算匹配度得分(0-100)"""
        if not user_skills:
            return 50

        # 提取JD中的技能关键词
        text = f"{job.title} {job.description} {job.requirements}".lower()
        title_text = job.title.lower()

        # 加权匹配
        total_weight = 0
        matched_weight = 0

        for skill in user_skills:
            # 获取技能权重（如果提供）
            weight = skill_weights.get(skill, 1) if skill_weights else 1
            total_weight += weight

            skill_lower = skill.lower()

            # 技能在描述中出现
            if skill_lower in text:
                matched_weight += weight

                # 技能在标题中出现，额外加分
                if skill_lower in title_text:
                    matched_weight += weight * 0.5

        # 计算得分
        if total_weight > 0:
            score = int((matched_weight / total_weight) * 100)
        else:
            score = 0

        return min(score, 100)

    def rank_jobs(self, jobs, user_skills, skill_weights=None):
        """按匹配度排序岗位"""
        # 计算每个岗位的匹配度
        for job in jobs:
            job.match_score = self.calculate_match_score(job, user_skills, skill_weights)

        # 按匹配度降序排列
        return sorted(jobs, key=lambda x: x.match_score or 0, reverse=True)

    def _parse_salary(self, salary_str):
        """解析薪资字符串"""
        if not salary_str:
            return None

        try:
            # 匹配格式: "5-10K", "10-15K·13薪"
            match = re.search(r'(\d+)-(\d+)K', salary_str)
            if match:
                min_sal = int(match.group(1)) * 1000
                max_sal = int(match.group(2)) * 1000
                return (min_sal, max_sal)
        except Exception:
            pass

        return None
