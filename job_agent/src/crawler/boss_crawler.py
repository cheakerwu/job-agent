"""
BOSS直聘爬虫
"""
import asyncio
import random
import re
from playwright.async_api import async_playwright
from .base import BaseCrawler


class BossCrawler(BaseCrawler):
    """BOSS直聘爬虫"""

    def __init__(self, config):
        super().__init__(config)
        self.base_url = "https://www.zhipin.com"
        self.playwright = None
        self.browser = None
        self.page = None

    async def init_browser(self):
        """初始化Playwright浏览器"""
        self.playwright = await async_playwright().start()

        # 启动浏览器
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            channel='msedge',   #使用Edge浏览器
            args=['--disable-blink-features=AutomationControlled']
        )

        # 创建上下文
        context = await self.browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
            viewport={'width': 1920, 'height': 1080}
        )

        # 创建页面
        self.page = await context.new_page()

        # 隐藏自动化特征
        await self.page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            })
        """)

    async def search_jobs(self, keyword, city, page_num=1):
        """搜索岗位列表"""
        jobs = []

        try:
            # 构造搜索URL
            search_url = f"{self.base_url}/web/geek/job?query={keyword}&city={city}&page={page_num}"

            # 访问搜索页面
            await self.page.goto(search_url, wait_until='networkidle')

            # 等待岗位列表加载
            await self.page.wait_for_selector('.job-card-wrapper', timeout=10000)

            # 提取岗位列表
            job_cards = await self.page.query_selector_all('.job-card-wrapper')

            for card in job_cards:
                try:
                    # 提取岗位信息
                    title_elem = await card.query_selector('.job-title')
                    title = await title_elem.inner_text() if title_elem else ''

                    company_elem = await card.query_selector('.company-name')
                    company = await company_elem.inner_text() if company_elem else ''

                    salary_elem = await card.query_selector('.salary')
                    salary = await salary_elem.inner_text() if salary_elem else ''

                    link_elem = await card.query_selector('a.job-card-left')
                    job_url = await link_elem.get_attribute('href') if link_elem else ''
                    if job_url:
                        job_url = self.base_url + job_url

                    # 提取岗位ID
                    job_id = ''
                    if job_url:
                        match = re.search(r'job_detail/(\w+)\.html', job_url)
                        if match:
                            job_id = match.group(1)

                    jobs.append({
                        'job_id': job_id,
                        'title': title.strip(),
                        'company': company.strip(),
                        'city': city,
                        'salary': salary.strip(),
                        'url': job_url,
                        'platform': 'boss'
                    })

                except Exception as e:
                    print(f"提取岗位信息失败: {e}")
                    continue

        except Exception as e:
            print(f"搜索岗位失败: {e}")

        return jobs

    async def get_job_detail(self, job_url):
        """获取岗位详情"""
        try:
            # 访问详情页
            await self.page.goto(job_url, wait_until='networkidle')

            # 等待内容加载
            await self.page.wait_for_selector('.job-detail', timeout=10000)

            # 提取岗位描述
            desc_elem = await self.page.query_selector('.job-detail-section')
            description = await desc_elem.inner_text() if desc_elem else ''

            # 提取任职要求
            req_elem = await self.page.query_selector('.job-sec-text')
            requirements = await req_elem.inner_text() if req_elem else ''

            return {
                'description': description.strip(),
                'requirements': requirements.strip()
            }

        except Exception as e:
            print(f"获取岗位详情失败: {e}")
            return {'description': '', 'requirements': ''}

    async def crawl(self, keyword, city, max_pages=5):
        """主爬取流程"""
        all_jobs = []

        try:
            # 初始化浏览器
            await self.init_browser()

            # 遍历页面
            for page_num in range(1, max_pages + 1):
                print(f"正在爬取第 {page_num} 页...")

                # 搜索岗位
                jobs = await self.search_jobs(keyword, city, page_num)
                print(f"找到 {len(jobs)} 个岗位")

                # 获取详情
                for job in jobs:
                    if job['url']:
                        # 随机延迟
                        delay = random.uniform(self.delay_min, self.delay_max)
                        await asyncio.sleep(delay)

                        # 获取详情
                        detail = await self.get_job_detail(job['url'])
                        job.update(detail)

                all_jobs.extend(jobs)

                # 页面间延迟
                await asyncio.sleep(random.uniform(3, 6))

        except Exception as e:
            print(f"爬取失败: {e}")

        finally:
            # 关闭浏览器
            await self.close()

        return all_jobs
