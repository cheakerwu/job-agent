"""
爬虫基类
"""
from abc import ABC, abstractmethod


class BaseCrawler(ABC):
    """爬虫基类"""

    def __init__(self, config):
        self.config = config
        self.delay_min = config.get('delay_min', 2)
        self.delay_max = config.get('delay_max', 5)
        self.headless = config.get('headless', True)

    @abstractmethod
    async def init_browser(self):
        """初始化浏览器"""
        pass

    @abstractmethod
    async def search_jobs(self, keyword, city, page_num=1):
        """搜索岗位列表"""
        pass

    @abstractmethod
    async def get_job_detail(self, job_url):
        """获取岗位详情"""
        pass

    @abstractmethod
    async def crawl(self, keyword, city, max_pages=5):
        """主爬取流程"""
        pass

    async def close(self):
        """关闭浏览器"""
        if hasattr(self, 'browser') and self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright') and self.playwright:
            await self.playwright.stop()
