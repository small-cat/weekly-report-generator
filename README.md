# 每周技术周刊自动生成器

自动化从 RSS 订阅源获取本周技术文章，通过 Claude Code 生成中文摘要，并推送到 GitHub。

## 功能特性

- RSS 订阅源解析（支持 OPML 格式）
- 自动获取本周新文章
- 文章去重
- Claude Code 生成中文摘要
- 模板渲染生成 Markdown 周报
- 自动推送到 GitHub

## 目录结构

```
weekly-reports/
├── config/
│   └── config.yaml          # 配置文件
├── src/
│   ├── config.py            # 配置管理
│   ├── logger.py            # 日志模块
│   ├── rss_parser.py       # RSS 解析
│   ├── deduplicator.py     # 去重
│   ├── claude_client.py    # Claude CLI 调用
│   ├── template_renderer.py # 模板渲染
│   ├── git_publisher.py    # Git 推送
│   └── main.py             # 主程序
├── output/                  # 周报输出目录
├── download/                # 下载缓存目录
├── logs/                    # 日志目录
├── template.md              # 周报模板
├── ReadSource.opml          # RSS 订阅源
├── requirements.txt         # Python 依赖
└── run.sh                   # 启动脚本
```

## 配置

编辑 `config/config.yaml`：

```yaml
claude:
  command: "claude-sonnet"   # 或 "claude-kimi"
  model: "claude-sonnet-4-6"

github:
  repo_url: "git@github.com:EuGeneWu/weekly-reports.git"
  branch: "main"

rss:
  opml_path: "./ReadSource.opml"
  start_date: "this_week"   # 或具体日期 "2026-01-01"

output:
  output_dir: "./output"
  download_dir: "./download"
  log_dir: "./logs"
```

## 使用方法

### 首次运行

1. 确保已安装依赖：
```bash
conda create --name weekly -c conda-forge python=3.11 -y
conda activate weekly
pip install -r requirements.txt
```

2. 配置 GitHub SSH 密钥（如果没有）

3. 运行程序：
```bash
./run.sh
```

### 命令行选项

```bash
./run.sh [选项]

选项:
  --config PATH       配置文件路径 (默认: ./config/config.yaml)
  --template PATH    模板路径 (默认: ./template.md)
  --skip-git         跳过 Git 推送
  --week-number N    指定周报期数
  --start-date DATE  开始日期 (格式: YYYY-MM-DD)
```

### 示例

```bash
# 跳过 Git 推送，仅生成周报
./run.sh --skip-git

# 指定特定周报期数
./run.sh --week-number 25

# 指定开始日期
./run.sh --start-date 2026-03-01
```

## 输出

- 周报保存在 `output/` 目录，文件名格式：`weekly-report-YYYY-MM-DD-Www.md`
- 日志保存在 `logs/` 目录，文件名格式：`YYYY-MM-DD.log`

## 依赖

- Python 3.8+
- feedparser
- PyYAML
- python-dateutil
- Claude Code CLI

## 注意事项

- 确保 Claude Code CLI 已安装并配置
- 确保 GitHub SSH 密钥已配置
- 首次运行建议使用 `--skip-git` 测试
