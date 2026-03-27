# ai-collab-blackbox

[🇺🇸 English Version](README.md)

> A1 Coder 团队的 AI 协作黑匣子协议。
>
> 这个仓库现在是两层结构：
> - 一层是项目内正常可读的 skill 目录
> - 一层是可选的全局命令，用来把 skill 部署到任意项目，并直接调用内置程序能力

`ai-collab-blackbox` 不只是文档，它还自带实际可执行程序，能够校验 AI 给出的 JSON，并把记录安全写入项目日志文件。

---

## 它是什么

当多个 AI 在同一个代码库里协作时，每轮工作结束都应该留下一个干净、可检索、可交接的记录。

这个项目提供的就是这套能力：
- 追加式历史记录
- 按 AI 分组的日志
- 全局时间轴
- 项目内可读的正常 skill
- 可执行脚本层，负责真正把记录写进文件

---

## 部署模型

### 1. 项目内正常 skill

真正给 AI 在项目里读和使用的 skill 目录仍然是：

```text
<project>/.agents/skills/ai-collab-blackbox/
```

里面包含：
- `SKILL.md`
- `SKILL_zh.md`
- `references/`
- `scripts/`

这部分就是 AI 在项目里实际读取的 skill。

### 2. 可选的全局命令

如果你全局安装这个包，就会得到：

```bash
ai-blackbox
```

这个命令可以：
- 把 skill 部署到任意目标项目
- 输出内置 skill 文本
- 直接调用程序能力：
  - `write`
  - `validate`
  - `render`

所以最终结构是：
- 项目内 skill
- 全局辅助命令

---

## 安装方式

### 方案 A：只把它当正常 skill 使用

直接把整个目录复制到目标项目：

```bash
cp -r ai-collab-blackbox/. <project>/.agents/skills/ai-collab-blackbox/
```

### 方案 B：安装全局辅助命令

从源码安装：

```bash
pip install .
```

或安装打包后的 zip / wheel：

```bash
pip install ai-collab-blackbox.zip
```

---

## 全局命令用法

### 把 skill 部署到任意项目

```bash
ai-blackbox init --project-root /path/to/project
```

它会建立：

```text
/path/to/project/.agents/skills/ai-collab-blackbox/
```

### 查询 skill 将部署到哪里

```bash
ai-blackbox where --project-root /path/to/project
```

### 查看命令信息

```bash
ai-blackbox info
```

### 查看内置 skill 内容

```bash
ai-blackbox show-skill --lang zh
ai-blackbox show-skill --lang en
```

---

## 程序能力

这个仓库里有真正的程序逻辑，不只是 skill 文档。

### 写入工作日志

```bash
ai-blackbox write --project-root /path/to/project --file record.json
```

### 校验 JSON / JSONL

```bash
ai-blackbox validate record.jsonl
```

### 渲染可读日志块

```bash
ai-blackbox render .ai/claude_opus_4/worklog.jsonl
```

---

## 会写出的文件

每个 AI 最终会写出：

```text
.ai/
├── <AI_ID>/
│   ├── worklog.md
│   └── worklog.jsonl
└── all_time.jsonl
```

---

## 为什么这样设计

只有普通 skill：AI 能读，但它不能自己全局部署。
只有 CLI：能跑命令，但它不是项目内正常 skill。

所以这个仓库现在同时保留：
- 项目内 skill 目录
- 全局 CLI 部署与执行层

这是兼顾两种工作流最干净的结构。

---

## 非目标

这个项目不负责：
- 自动解析 IDE 历史
- 自动生成 git diff
- 替代 git
- 自己编造 AI 身份

---

## 许可证

MIT-0

---

## 作者

[@icestomr012002](https://github.com/icestorm012002)
