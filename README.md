# PDF 原版式翻译为可编辑 Word

一个用于 Codex 的文档翻译 Skill：将中文 PDF 或扫描报告翻译为英文 Word，按原页面结构重建可编辑表格，并逐页核对版式。

## 适合什么任务

- 批量翻译检验报告、注册技术资料等有固定版式的 PDF。
- 保留原纸张尺寸、分页、表格边界及合并单元格。
- 将表格重建为真正的 Word 表格，允许修改文字和增删行列。
- 保留原照片、标志、手写签名和印章。

这是供 Codex 执行的工作流程与检查工具，**不是独立的一键翻译软件**。仓库中的 Python 脚本只做 DOCX 结构检查，不负责翻译、OCR 或完整的 PDF 转 Word。

## 安装

下载本仓库并解压，将以下文件放到 Codex 的技能目录中：

```text
~/.codex/skills/pdf-layout-translate-word/
├── SKILL.md
├── agents/
│   └── openai.yaml
├── references/
│   └── layout-workflow.md
└── scripts/
    └── audit_docx.py
```

Windows 默认路径为 `%USERPROFILE%\.codex\skills\pdf-layout-translate-word`。如果设置了 `CODEX_HOME`，则使用其下的 `skills/pdf-layout-translate-word`。确保 `SKILL.md` 直接位于该目录内，避免解压后多套一层文件夹。

## 使用示例

在可读取源文件的 Codex 会话中输入：

```text
使用 $pdf-layout-translate-word，
将指定文件夹中的全部中文 PDF 翻译为英文 Word。
保留原分页、表格合并结构、照片和签章位置，表格需要可编辑。
每份 PDF 对应一份 Word，完成后打包交付。
源文件夹：<填写本机文件夹路径>
```

也可以指定其他目标语言；实际执行以用户要求为准。

## 处理流程

1. 清点源文件、页数和页面尺寸，识别扫描件、不同版式及合订关系。
2. 建立术语表，按不同版式先做代表样本，再复用结构批量处理。
3. 提取或 OCR 识别文字，按原图重建表格和定位文字。
4. 翻译并核对报告号、型号、标准、日期、样品编号、数值、单位和判定。
5. 渲染 Word，与原 PDF 逐页比较，修正重叠、截断、跨页和照片比例问题。
6. 输出 DOCX、文件对应表及确实存在的未辨认项说明，可打包为 ZIP。

执行环境需要具备 PDF 读取、扫描件 OCR、Word 生成与渲染能力。具体工具由 Codex 根据环境选择；结构检查脚本本身仅依赖 Python 标准库。

## 排版与翻译边界

- 英文长度与中文不同，部分字号、换行和内边距需要适配，**不能保证像素级完全一致**。
- 增删行列或大幅修改译文后，应重新检查分页和版式。
- 照片、签名和印章保留原图；照片内中文可按报告号及页码提供英文对照。对照文件不代表照片内文字已替换。
- 模糊的手写内容、被遮盖的编号会明确标记，不凭相似报告猜测补全。
- 程序检查不能替代逐页视觉检查，也不能代替必要的专业译文复核。
- 文档默认在本地处理；未经授权不上传第三方翻译或 OCR 服务。

## DOCX 结构检查

```bash
python scripts/audit_docx.py report.docx
```

对于明确采用“一页一节”结构的文件，可额外检查预期分节数：

```bash
python scripts/audit_docx.py report.docx --expected-pages 7
```

脚本检查原生表格、分节尺寸、可编辑文字中的中文残留、批注和可疑占位词，并输出 JSON。退出码 `0` 表示未发现这些结构问题，`1` 表示存在待检查项，`2` 表示读取或解析失败。

**分节数不是实际渲染页数。** 即使脚本通过，仍需渲染并检查页面；照片和印章内的文字不属于该脚本的检测范围。

## 仓库内容

| 文件 | 用途 |
| --- | --- |
| [SKILL.md](SKILL.md) | Skill 入口、工作流程及交付要求 |
| [agents/openai.yaml](agents/openai.yaml) | Skill 显示名称和调用示例 |
| [references/layout-workflow.md](references/layout-workflow.md) | 扫描表格重建与版式核对细节 |
| [scripts/audit_docx.py](scripts/audit_docx.py) | 只读 DOCX 结构检查工具 |

本仓库仅保存 Skill 和通用检查工具，不包含原始报告、客户资料、翻译成品或签章图片。
