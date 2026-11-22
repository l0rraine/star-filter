# star-filter

把我 star 过的 GitHub 仓库变成一个**能凭模糊记忆搜回来的单文件页面**。

不用后端、不用数据库、不用向量模型：全部数据内嵌在一个 `index.html` 里，双击就打开，检索在浏览器里算完。中文按两字滑窗切分 + BM25 打分，命中摘要 / 标签 / 别名 / 简介 / 仓库名。

在线版：<https://l0rraine.github.io/star-filter/>

## 目录

```
index.html              生成出来的检索页面（唯一需要打开的产物）
data/stars.json         全部条目（摘要 / 标签 / 别名 / star 数 / 状态）
data/pending.tsv        未总结清单（自动生成，给 LLM 用）
data/summaries.tsv      待合入的总结结果（手动粘贴进来）
scripts/fetch_stars.py     从 GitHub 拉取 star 列表并合并
scripts/apply_summaries.py 把 summaries.tsv 合进 stars.json
scripts/gen_html.py        重建 index.html
scripts/print_pending.py   打印待总结条目（LLM 输入格式）
scripts/template.html      页面模板（改样式改这个）
scripts/import_local.py    一次性导入旧的 stars.json
PROMPT.md               给免费 LLM 的提示词
```

## 日常怎么用

**只查不改**：双击 `index.html`，或直接开在线版。

**有新 star 要更新**：

```bash
export STARS_TOKEN=<你的 PAT>      # PowerShell: $env:STARS_TOKEN="..."
python scripts/fetch_stars.py      # 拉取，新条目标 pending
python scripts/print_pending.py 20 # 打印待总结
# 丢给免费 LLM，把结果存成 data/summaries.tsv
python scripts/apply_summaries.py
python scripts/gen_html.py
git add -A && git commit -m "refresh" && git push
```

**自动更新**：`.github/workflows/refresh.yml` 每周一 06:00（UTC+8）跑一次，用完即弃的 runner 上执行同样流程，只在有变化时 commit。手动触发走 Actions 页面上的 *Run workflow*。

## 一次性设置

1. **加 secret**（必需）：仓库 Settings → Secrets and variables → Actions → New repository secret，名字 `STARS_TOKEN`，值是 classic PAT（`ghp_...`，勾 `repo` 就够）。
   > 为什么不用内置的 `GITHUB_TOKEN`：它是仓库级安装令牌，读不到 `/user/starred`（会 403）。只有你自己的 PAT 能读你的 star 列表。没配 secret 时 workflow 会跳过拉取、只用现有数据重建页面，不会报红。
2. **开 Pages**：Settings → Pages → Source 选 `Deploy from a branch`，Branch 选 `main` / `(root)`。页面入口是 `index.html`。

## 设计取舍

- **不要向量检索**。1034 个条目的量级下，BM25 + 别名已经够用，省掉 2GB 依赖和一次索引构建。别名是性价比最高的「语义扩展」——每次搜不到就补一条，比装模型实在。
- **不调 LLM API**。摘要靠人工搭免费 LLM 批量做，提示词在 `PROMPT.md`。仓库里没有任何需要付费的东西。
- **纯前端**。`index.html` 是唯一交付物，换机器、发朋友、放 U 盘都能用，不存在服务挂了打不开的情况。

## 已知边界

- 长句场景描述（「能把视频里的人声和配乐分开」）会掉分：中文滑窗会让「视频」「频里」两个重叠片段重复计分，把框架词抬得比内容词还高。**短词准得多**，3–6 个字最好。
- 只索引摘要/标签/别名/简介，不含 README 全文。
- 库里没有的东西搜不出来（这不是算法问题）。比如「重命名」这个词在整个库里出现 0 次。
