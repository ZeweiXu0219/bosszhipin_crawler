# BossZhipin 职位爬虫

[English](README_EN.md)

一个专为爬取 [zhipin.com](https://www.zhipin.com/)（BOSS直聘）职位信息设计的网络爬虫。


## 功能特点

- 根据特定条件搜索职位（职位名称、地点等）
- 按职位类型、工作经验、薪资、学历、公司规模和融资阶段筛选结果
- 浏览多页搜索结果
- 提取详细的职位信息，包括：
  - 职位名称
  - 公司信息（名称、行业、融资阶段、规模）
  - 工作地点
  - 薪资范围
  - 经验要求
  - 学历要求
  - 联系信息
- 自动处理登录弹窗
- 实现重试逻辑，确保爬取稳定性
- 通过随机延迟模拟人类浏览行为

## 系统要求

- Python 3.6+
- Chrome 浏览器
- `requirements.txt` 中列出的依赖项：
  - selenium
  - webdriver-manager
  - tqdm

## 安装

1. 克隆此仓库：
   ```
   git clone https://github.com/ZeweiXu0219/bosszhipin_crawler.git
   cd bosszhipin_crawler
   ```

2. 安装所需的包：
   ```
   pip install -r requirements.txt
   ```

3. 确保您的系统上已安装 Chrome 浏览器。

## 使用方法

### 基本用法

```python
from scripts.JobListingCrawler import JobListingCrawler

# 初始化爬虫
crawler = JobListingCrawler(headless=False)  # 设置为 True 启用无头模式

# 搜索职位
job_listings = crawler.search_jobs(
    url="https://www.zhipin.com/web/geek/job?query=",
    query="NLP算法",  # 职位名称/关键词
    location="北京"   # 地点
)

# 打印找到的职位列表
print(f"找到 {len(job_listings)} 个职位列表。")

# 浏览多个页面
for i in range(4):
    crawler.click_page()  # 前往下一页
    new_jobs = crawler.scan_page()
    print(f"在第 {i+2} 页找到 {len(new_jobs)} 个更多职位。")

# 完成后务必关闭爬虫
crawler.close()
```

### 高级筛选

爬虫支持使用 `select_menu.json` 配置进行高级筛选：

```python
# 定义筛选选项
options = {
    "求职类型": ["全职"],           # 职位类型：全职
    "工作经验": ["3-5年"],          # 经验：3-5年
    "薪资待遇": ["20-50K"],         # 薪资：20-50K
    "学历要求": ["本科"],           # 学历：本科
    "公司规模": ["10000人以上"],    # 公司规模：10000人以上
    "融资阶段": ["已上市"]          # 融资阶段：已上市公司
}

# 获取应用筛选条件的URL
filtered_url = crawler.get_full_select_url(base_url, "data/select_menu.json", options)
crawler.navigate_to_url(filtered_url)
```

## 项目结构

- `main.py`：演示爬虫使用方法的示例脚本
- `requirements.txt`：所需的Python包列表
- `scripts/`：
  - `WebCrawler.py`：具有通用网络爬取功能的基础爬虫类
  - `JobListingCrawler.py`：专门用于职位列表的爬虫
  - `PopupMonitor.py`：处理登录弹窗的工具
- `data/`：
  - `select_menu.json`：筛选选项的配置

## 功能详解

### WebCrawler 类

基础 `WebCrawler` 类提供：

- 可配置选项的浏览器初始化（无头模式、用户代理、代理）
- 带重试逻辑的导航
- 带等待和重试逻辑的元素查找
- 安全的元素交互（点击、文本提取）
- 模拟人类行为的随机延迟

### JobListingCrawler 类

扩展基础爬虫，增加职位特定功能：

- 带地点和关键词筛选的职位搜索
- 使用 select_menu.json 配置的高级筛选
- 从搜索结果中提取职位列表
- 搜索结果的分页浏览
- 控制滚动以加载动态内容

### PopupMonitor 类 (未调试)

处理爬取过程中可能出现的登录弹窗：

- 多种监控策略（循环、WebDriverWait、MutationObserver）
- 自动关闭登录对话框
- 资源清理

## 注意事项

- 该爬虫设计适用于开发时的 zhipin.com 网站结构。网站变更可能需要更新选择器。
- 请负责任地使用，并遵守网站的服务条款和 robots.txt 文件。
- 考虑在请求之间添加延迟，以避免对目标网站造成过载。

## 许可证

本项目采用 MIT 许可证 - 详情请参阅 [LICENSE](LICENSE) 文件。
