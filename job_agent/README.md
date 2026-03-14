# AI Agent 求职助手 - 本地简化版

一个基于 Python 和 Claude API 的智能求职助手工具,帮助求职者自动化岗位采集、智能筛选和简历优化。

## ✨ 功能特性

- 🔍 **岗位采集**: 自动爬取 BOSS直聘等平台的岗位信息
- 🎯 **智能筛选**: 基于城市、薪资、关键词等条件筛选岗位
- 📊 **匹配度计算**: 根据用户技能计算岗位匹配度（支持技能权重）
- ✨ **简历优化**: 使用 Claude API 针对特定岗位优化简历
- 📝 **投递管理**: 记录投递历史,避免重复投递
- 💾 **本地存储**: 使用 SQLite 数据库,无需额外配置
- 🚀 **速率控制**: 自动限制 API 调用频率，避免超限
- 📋 **日志系统**: 完整的操作日志，便于问题排查
- 🌐 **多浏览器支持**: 支持 Edge/Chrome/Chromium

## 技术栈

- Python 3.8+
- Playwright (网页爬取，支持多浏览器)
- SQLite (数据存储)
- Claude API (简历优化)
- Click (CLI 框架)
- Rich (终端美化)

## 🎯 核心优化

### 反爬虫策略
- 随机延迟（2-5秒）
- 完整的浏览器 User-Agent
- 隐藏自动化特征
- 模拟真实用户行为

### 智能匹配
- 技能权重支持
- 标题匹配额外加分
- 多维度匹配度计算

### API 成本控制
- 简历优化结果缓存
- 自动速率限制（默认每分钟10次）
- 每日限额控制
- Prompt 优化

### 稳定性保障
- 完整的日志系统
- 资源自动清理
- 错误重试机制
- 进度实时反馈

## 安装步骤

### 1. 克隆项目

```bash
cd ~/job_agent
```

### 2. 安装依赖

```bash
pip install -r requirements.txt

# 安装浏览器（推荐使用 Edge）
playwright install msedge

# 或使用 Chromium
playwright install chromium
```

### 3. 配置环境变量

创建 `.env` 文件:

```bash
cp .env.example .env
```

编辑 `.env` 文件,添加你的 Claude API Key:

```
ANTHROPIC_API_KEY=your_api_key_here
```

### 4. 配置用户信息

编辑 `config/user_profile.json`,填写你的个人信息、技能和求职偏好。

## 使用指南

### 1. 爬取岗位

```bash
python cli.py crawl --keyword "Python实习" --city "北京" --limit 30
```

参数说明:
- `--keyword, -k`: 搜索关键词(必填)
- `--city, -c`: 城市(默认: 北京)
- `--limit, -l`: 爬取数量(默认: 30)

### 2. 查看岗位列表

```bash
python cli.py list
```

可选参数:
- `--status, -s`: 状态筛选(new/filtered/applied)
- `--limit, -l`: 显示数量(默认: 20)

### 3. 查看岗位详情

```bash
python cli.py detail <job_id>
```

### 4. 筛选岗位

```bash
python cli.py filter --city "北京" --salary-min 6000
```

可选参数:
- `--city, -c`: 城市筛选
- `--salary-min`: 最低薪资(K)
- `--salary-max`: 最高薪资(K)

筛选会根据 `config/user_profile.json` 中的偏好自动应用关键词和技能匹配。

### 5. 优化简历

```bash
python cli.py optimize 1 2 3
```

为指定的岗位 ID 生成优化后的简历,保存在 `data/resumes/` 目录。

### 6. 查看投递历史

```bash
python cli.py history
```

可选参数:
- `--limit, -l`: 显示数量(默认: 10)

### 7. 查看配置

```bash
python cli.py config
```

## 项目结构

```
job_agent/
├── config/
│   ├── config.yaml              # 系统配置
│   └── user_profile.json        # 用户配置
├── src/
│   ├── crawler/                 # 爬虫模块
│   ├── filter/                  # 筛选模块
│   ├── resume/                  # 简历优化模块
│   ├── storage/                 # 数据存储模块
│   ├── controller.py            # 核心控制器
│   └── utils.py                 # 工具函数
├── data/
│   ├── jobs.db                  # SQLite 数据库
│   └── resumes/                 # 生成的简历
├── cli.py                       # CLI 入口
├── requirements.txt             # 依赖列表
└── README.md                    # 项目文档
```

## 配置说明

### config.yaml

系统配置文件,包含爬虫、筛选、简历优化等模块的配置:

```yaml
crawler:
  platform: boss
  delay_min: 2          # 最小延迟（秒）
  delay_max: 5          # 最大延迟（秒）
  max_pages: 5          # 最大爬取页数
  headless: true        # 无头模式
  browser: msedge       # 浏览器选择（msedge/chromium）
  timeout: 30000        # 超时时间（毫秒）
  retry_times: 3        # 重试次数

resume:
  api_provider: claude
  model: claude-3-5-sonnet-20241022
  max_tokens: 2000
  cache_enabled: true
  daily_limit: 10       # 每日限额
  rate_limit: 10        # 每分钟限制

storage:
  db_path: "data/jobs.db"
  resume_dir: "data/resumes"
  log_dir: "logs"       # 日志目录
```

### user_profile.json

用户配置文件,包含:
- `basic_info`: 基本信息(姓名、学历、联系方式)
- `skills`: 技能列表（支持权重，标题匹配会额外加分）
- `experiences`: 项目经历
- `filter_preferences`: 筛选偏好

示例:
```json
{
  "skills": ["Python", "Django", "MySQL"],
  "filter_preferences": {
    "cities": ["北京", "上海"],
    "salary_min": 5000,
    "keywords": ["Python", "后端"]
  }
}
```

## 成本说明

- **Claude API**: 每个简历优化约 $0.01-0.05
- **速率限制**: 默认每分钟最多10次调用，自动等待
- **每日限额**: 默认最多优化 10 个简历
- **月度成本**: 约 $5-10

## 📋 日志系统

所有操作都会记录到日志文件：
- 位置：`logs/job_agent_YYYYMMDD.log`
- 格式：时间戳 + 日志级别 + 消息
- 用途：问题排查、操作审计

查看日志：
```bash
# 查看今天的日志
cat logs/job_agent_$(date +%Y%m%d).log

# 实时监控日志
tail -f logs/job_agent_$(date +%Y%m%d).log
```

## 注意事项

1. **反爬虫**: 爬虫已配置随机延迟和反自动化检测,但仍需谨慎使用
2. **API Key**: 请妥善保管 Claude API Key,不要提交到版本控制
3. **简历真实性**: AI 优化的简历仍需人工审核,确保内容真实
4. **法律合规**: 仅用于个人求职,不得用于商业用途
5. **速率限制**: 系统自动控制 API 调用频率，避免超限
6. **日志隐私**: 日志文件可能包含敏感信息，注意保护
7. **浏览器选择**: 默认使用 Edge，可在配置中切换

## 常见问题

### Q: 爬虫被封怎么办?

A: 增加延迟时间(修改 `config.yaml` 中的 `delay_min` 和 `delay_max`),减少爬取数量。

### Q: Claude API 调用失败?

A: 检查 API Key 是否正确,网络连接是否正常。查看日志文件了解详细错误。

### Q: 简历优化质量不好?

A: 优化 `user_profile.json` 中的基础信息,提供更详细的项目经历。

### Q: 如何切换浏览器?

A: 编辑 `config/config.yaml`，修改 `crawler.browser` 为 `msedge` 或 `chromium`。

### Q: 速率限制如何调整?

A: 编辑 `config/config.yaml`，修改 `resume.rate_limit` 值（每分钟调用次数）。

### Q: 日志文件在哪里?

A: 日志保存在 `logs/` 目录，按日期命名，如 `job_agent_20240314.log`。

## 后续优化

- [ ] 支持更多招聘平台(智联、拉勾等)
- [ ] 添加 Web UI 界面
- [ ] 实现自动投递功能
- [ ] 添加数据分析和可视化
- [ ] 支持简历模板系统
- [ ] 持久化缓存系统
- [ ] 并发爬取优化
- [ ] 更智能的匹配算法

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request!

## 联系方式

如有问题,请提交 Issue。
