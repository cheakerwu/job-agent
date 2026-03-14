# 快速开始指南

## 第一步: 安装依赖

```bash
cd ~/job_agent
pip install -r requirements.txt

# 安装浏览器（支持 Edge/Chrome/Chromium）
playwright install msedge    # 推荐：使用 Edge
# 或者
playwright install chromium  # 使用 Chromium
```

## 第二步: 配置环境

1. 复制环境变量模板:
```bash
cp .env.example .env
```

2. 编辑 `.env` 文件,添加你的 Claude API Key:
```
ANTHROPIC_API_KEY=sk-ant-xxxxx
```

获取 API Key: https://console.anthropic.com/

## 第三步: 配置用户信息

编辑 `config/user_profile.json`,填写:
- 基本信息(姓名、学历、联系方式)
- 技能列表（支持技能权重，标题中出现的技能会额外加分）
- 项目经历
- 求职偏好(城市、薪资、关键词)

## 第四步: 配置系统参数（可选）

编辑 `config/config.yaml` 可调整:
- 爬虫延迟时间（防止被封）
- 浏览器选择（msedge/chromium）
- API 速率限制（默认每分钟10次）
- 日志级别和存储路径

## 第五步: 测试系统

```bash
python test_setup.py
```

确保所有测试通过。

## 第六步: 开始使用

### 1. 爬取岗位

```bash
python cli.py crawl -k "Python实习" -c "北京" -l 30
```

### 2. 查看岗位

```bash
python cli.py list
```

### 3. 筛选岗位

```bash
python cli.py filter
```

### 4. 查看详情

```bash
python cli.py detail 1
```

### 5. 优化简历

```bash
python cli.py optimize 1 2 3
```

### 6. 查看历史

```bash
python cli.py history
```

## 完整工作流程

```bash
# 1. 爬取岗位
python cli.py crawl -k "Python后端实习" -c "北京" -l 50

# 2. 筛选匹配岗位
python cli.py filter

# 3. 查看筛选结果
python cli.py list -s filtered -l 10

# 4. 查看感兴趣的岗位详情
python cli.py detail 1
python cli.py detail 5
python cli.py detail 8

# 5. 为选中的岗位优化简历
python cli.py optimize 1 5 8

# 6. 查看生成的简历
ls data/resumes/

# 7. 人工审核简历后,手动投递

# 8. 查看投递历史
python cli.py history
```

## 注意事项

1. **首次使用**: 建议先爬取少量岗位(10-20个)测试
2. **API 成本**: 每次优化简历会调用 Claude API,注意成本控制
3. **速率限制**: 系统自动限制 API 调用频率（默认每分钟10次）
4. **简历审核**: AI 生成的简历需要人工审核,确保真实性
5. **爬虫频率**: 不要过于频繁爬取,避免被封 IP
6. **日志查看**: 所有操作日志保存在 `logs/` 目录，便于问题排查
7. **浏览器选择**: 默认使用 Edge 浏览器，可在配置文件中修改

## 常用命令速查

| 命令 | 说明 | 示例 |
|------|------|------|
| `crawl` | 爬取岗位 | `python cli.py crawl -k "Python" -c "北京"` |
| `list` | 列出岗位 | `python cli.py list -s new -l 20` |
| `detail` | 查看详情 | `python cli.py detail 1` |
| `filter` | 筛选岗位 | `python cli.py filter --salary-min 6000` |
| `optimize` | 优化简历 | `python cli.py optimize 1 2 3` |
| `history` | 投递历史 | `python cli.py history -l 10` |
| `config` | 查看配置 | `python cli.py config` |

## 获取帮助

```bash
python cli.py --help
python cli.py crawl --help
```

## 问题排查

### 问题1: 导入错误

```bash
# 重新安装依赖
pip install -r requirements.txt --force-reinstall
```

### 问题2: Playwright 错误

```bash
# 重新安装浏览器（Edge）
playwright install msedge

# 或使用 Chromium
playwright install chromium
```

### 问题3: 浏览器选择

如果想切换浏览器，编辑 `config/config.yaml`:
```yaml
crawler:
  browser: msedge  # 或 chromium
```

### 问题4: API Key 错误

检查 `.env` 文件中的 `ANTHROPIC_API_KEY` 是否正确。

### 问题5: 爬虫失败

- 检查网络连接
- 增加延迟时间(修改 `config/config.yaml`)
- 减少爬取数量
- 查看日志文件 `logs/job_agent_YYYYMMDD.log` 了解详细错误

### 问题6: 速率限制

如果遇到 API 速率限制，系统会自动等待。可在 `config/config.yaml` 中调整:
```yaml
resume:
  rate_limit: 10  # 每分钟最多调用次数
```

## 下一步

- 探索更多筛选条件
- 优化用户配置以提高匹配度
- 定期爬取新岗位
- 分析投递数据

祝求职顺利! 🎉
