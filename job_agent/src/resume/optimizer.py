"""
简历优化器
"""
import os
import json
import time
from datetime import datetime
from anthropic import Anthropic


class ResumeOptimizer:
    """简历优化器"""

    def __init__(self, api_key, config):
        self.client = Anthropic(api_key=api_key)
        self.config = config
        self.model = config.get('model', 'claude-3-5-sonnet-20241022')
        self.max_tokens = config.get('max_tokens', 2000)
        self.cache = {}
        self.rate_limit = config.get('rate_limit', 10)  # 每分钟限制
        self.call_times = []  # 记录调用时间

    def _check_rate_limit(self):
        """检查速率限制"""
        now = time.time()
        # 清理60秒前的记录
        self.call_times = [t for t in self.call_times if now - t < 60]

        if len(self.call_times) >= self.rate_limit:
            sleep_time = 60 - (now - self.call_times[0])
            if sleep_time > 0:
                print(f"达到速率限制，等待 {sleep_time:.1f} 秒...")
                time.sleep(sleep_time)
                self.call_times = []

        self.call_times.append(now)

    def optimize_resume(self, base_resume, job_description, job_title):
        """优化简历"""
        # 检查缓存
        cache_key = f"{job_title}_{hash(job_description)}"
        if cache_key in self.cache:
            print("使用缓存的优化结果")
            return self.cache[cache_key]

        # 检查速率限制
        self._check_rate_limit()

        # 构造Prompt
        prompt = self.build_prompt(base_resume, job_description, job_title)

        try:
            # 调用Claude API
            message = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            # 提取结果
            optimized_resume = message.content[0].text

            # 保存到缓存
            self.cache[cache_key] = optimized_resume

            return optimized_resume

        except Exception as e:
            print(f"简历优化失败: {e}")
            return None

    def build_prompt(self, base_resume, jd, job_title):
        """构造优化Prompt"""
        prompt = f"""你是一位专业的简历优化顾问。请根据以下岗位描述(JD)优化用户的简历。

**重要原则**:
1. 保持真实性 - 不要编造经历或技能
2. 突出相关性 - 强调与岗位要求匹配的经验和技能
3. 关键词匹配 - 适当使用JD中的关键词
4. 量化成果 - 用数据说话
5. 简洁明了 - 控制在1页以内

**岗位信息**:
职位: {job_title}

岗位描述:
{jd}

**用户基础简历**:
{json.dumps(base_resume, ensure_ascii=False, indent=2)}

**请输出优化后的简历** (Markdown格式):
"""
        return prompt

    def save_resume(self, resume_content, job_id, resume_dir='data/resumes'):
        """保存简历文件"""
        try:
            # 确保目录存在
            os.makedirs(resume_dir, exist_ok=True)

            # 生成文件名
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"resume_job{job_id}_{timestamp}.md"
            filepath = os.path.join(resume_dir, filename)

            # 保存文件
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(resume_content)

            print(f"简历已保存: {filepath}")
            return filepath

        except Exception as e:
            print(f"保存简历失败: {e}")
            return None

    def batch_optimize(self, base_resume, jobs, max_count=None):
        """批量优化简历"""
        results = []

        if max_count:
            jobs = jobs[:max_count]

        for i, job in enumerate(jobs, 1):
            print(f"\n正在优化第 {i}/{len(jobs)} 个简历...")
            print(f"岗位: {job.title} - {job.company}")

            # 优化简历
            jd = f"{job.description}\n\n{job.requirements}"
            optimized = self.optimize_resume(base_resume, jd, job.title)

            if optimized:
                # 保存简历
                filepath = self.save_resume(optimized, job.id)
                results.append({
                    'job_id': job.id,
                    'job_title': job.title,
                    'resume_path': filepath,
                    'success': True
                })
            else:
                results.append({
                    'job_id': job.id,
                    'job_title': job.title,
                    'success': False
                })

        return results
