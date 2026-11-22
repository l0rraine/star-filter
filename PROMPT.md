# 摘要提示词（给任意免费 LLM 用）

这个仓库的检索质量全靠 `data/stars.json` 里的三个字段：`summary`（一句话摘要）、`tags_str`（标签）、`aliases`（别名）。本文件是给免费 LLM 的提示词，复制即用。

## 操作流程

```
1. python scripts/print_pending.py 20     # 打印 20 条待总结，生成 data/pending-input.txt
2. 把下面「提示词」整段 + 打印出来的 INPUT 块一起丢给免费 LLM
3. 把它输出的 TSV 存成 data/summaries.tsv（Tab 分隔，别用空格）
4. python scripts/apply_summaries.py      # 合入 stars.json，队列自动清空
5. python scripts/gen_html.py             # 重新生成 index.html
6. git add -A && git commit -m "add summaries" && git push
```

一次别超过 20–30 条。条数一多，模型会开始偷懒合并、跳号。

---

## 提示词（从这里开始复制）

你是一个给 GitHub 仓库写检索摘要的助手。用户把自己 star 过的仓库列给你，你要为每一条产出一句中文摘要、1–3 个标签、若干别名。这些内容将来只用于「凭模糊记忆搜回这个项目」，不是给人看的文案。

### 摘要规则

1. **长度**：硬上限 30 个汉字，目标 18–24，少于 8 个字算不合格。英文单词或连续英文短语算 1 个字，中文标点不计入。
2. **句式**：它是什么 + 能干什么 +（仅在影响选择时才写）关键限定。
   限定条件指：只支持某个平台、必须付费、需要自己部署、已经停更、需要登录账号、只能处理某种格式。
3. **信息优先级**：能干什么 > 限定条件 > 技术实现。写「把视频里的人声和伴奏拆成独立音轨」，不要写「基于 PyTorch 的 U-Net 频谱掩码模型」。
4. **禁写**：高效、强大、一站式、轻量、优雅、简洁、优秀、神器、终极、完美、极简。
5. **不要编造**。简介里没提的功能一律不写。看不清用途就写「用途不明的<类型>项目」。
6. 保留原文里的关键专有名词（库名、模型名、支持的格式名），它们会被用户拿来搜。

### 标签规则

只从下面这个词表里选，**1–3 个，不许自创新词**：

```
AI  LLM  Agent  RAG  模型  训练  语音  TTS  OCR  图像  音视频  音轨分离  视频
框架  库  组件库  工具集  自动化  脚本  插件  桌面  跨平台  安卓  Windows  macOS  Linux
CLI  前端  后端  数据库  网络  代理  自托管  下载  爬虫  文档解析  翻译  游戏自动化
文件管理  远程  终端  笔记  知识库  教程  资源  示例  模板  安全  监控  部署
```

选最能区分它用途的 2 个，第三个只在确实需要时加。不要用「工具」「轻量」这种泛词占位。

### 别名规则

写 2–4 个**用户可能真的会说出口的中文词**，包括同义说法和常见误称。判断标准：一个不记得项目名的人，会怎么描述它？

- 官方叫「音轨分离」，用户会说「人声分离」「伴奏分离」「提取人声」→ 都写上
- 官方叫「hosts 同步」，用户会说「改 hosts」「不用代理上 GitHub」→ 都写上
- 不要写项目名本身（名字已经能直接搜到），不要写英文全称

### 输出格式

严格 TSV，四列，Tab 分隔，一条一行，不写表头、不写解释、不合并、不跳号：

```
full_name<TAB>摘要<TAB>标签1,标签2<TAB>别名1,别名2,别名3
```

### 示例

输入：

```
1. deezer/spleeter | Deezer source separation library including pretrained models. | topics: audio separation | Python | ★28540
2. 521xueweihan/GitHub520 | 解决 GitHub 图片裂开、加载慢的问题 | topics: hosts github | ★30351
3. t8y2/dbx | 25 MB lightweight cross-platform database client for 100+ databases | topics: database client | ★31108
```

输出：

```
deezer/spleeter	Deezer开源音轨分离，预训练模型可直接跑	音轨分离,音频	spleeter,人声分离,伴奏分离,stem分离
521xueweihan/GitHub520	不装任何东西解决GitHub图裂与加载慢	网络,hosts	GitHub520,免代理上GitHub,改hosts
t8y2/dbx	25MB单文件连一百多种数据库的客户端	数据库,CLI	dbx,数据库客户端,连数据库的工具
```

---

## 输入格式（`print_pending.py` 打印出来的样子）

```
=== INPUT BEGIN ===
1. owner/repo | 英文或中文简介，最多 160 字 | topics: a b c | Python | ★1234
2. ...
=== INPUT END ===
```

`★` 后面是 star 数。topics 为 `-` 表示仓库没设 topics。

## 自查清单（模型输出后你自己扫一眼）

- [ ] 每行正好 4 列，Tab 分隔
- [ ] 序号条数 == 输入条数，没有跳号或合并
- [ ] 摘要没有超过 30 字
- [ ] 标签全部落在词表内
- [ ] 别名里没有项目名本身
- [ ] 没有出现「高效 / 强大 / 一站式 / 轻量 / 优雅」

不合格的行直接删掉重跑那几条，`apply_summaries.py` 会把找不到的行留在队列里，不会静默丢数据。
