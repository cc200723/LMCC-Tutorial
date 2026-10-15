# LMCC 大模型能力认证教材 青少年组 + 成人组（全等级覆盖）

本书面向准备参加LMCC 大模型能力认证的学生与成人学习者。青少年组考生适用年龄大致在 8–18 岁，成人组考生无年龄限制。全书覆盖 CCF 大模型能力认证大纲全部 12 个模块、3 个难度等级的知识点：【1】级（基础级）和【2】级（进阶级）为青少年组与成人组共考内容，【3】级（高级）为成人组专属——正文中对成人组专属内容会以醒目方式标注，青少年组考生可按需选读。我们假设你此前没有系统学习过人工智能或深度学习，因此每一章都从最基础的概念讲起，遇到公式和代码会先解释"它到底在算什么"，再给出可运行、可检查的示例。

本书的创作合理运用了AI Agent工具，主要使用Workbuddy+Dumate .

## 引用本书

若在论文、报告或课程材料中引用本教材或配套工程，请采用以下格式（APA 7th 与 BibTeX）。作者 ORCID：0009-0001-2763-8317。

**教材（Zenodo 归档版，推荐）**

Cheng, C. (2026, October 15). *LMCC人工智能与大模型能力认证教材*. Zenodo. https://doi.org/10.5281/zenodo.23384442

```bibtex
@misc{Cheng2026LMCC,
  author       = {Cheng, Chi},
  title        = {{LMCC} 人工智能与大模型能力认证教材},
  year         = {2026},
  month        = {10},
  day          = {15},
  howpublished = {Zenodo},
  doi          = {10.5281/zenodo.23384442},
  url          = {https://doi.org/10.5281/zenodo.23384442}
}
```

**配套工程与题库（GitHub 仓库）**

Cheng, C. (2026). *LMCC-Tutorial* [Source code]. GitHub. https://github.com/cc200723/LMCC-Tutorial

```bibtex
@misc{Cheng2026LMCCGitHub,
  author       = {Cheng, Chi},
  title        = {{LMCC-Tutorial}: {LMCC} 大模型能力认证教材配套工程与题库},
  year         = {2026},
  howpublished = {GitHub repository},
  publisher    = {GitHub},
  url          = {https://github.com/cc200723/LMCC-Tutorial}
}
```

### 参考资源
- LMCC IDE 使用教程：https://jy.hpe.cn/jhkx/jsxx/706058.htm
- LMCC IDE 学习仓库（Gitee）：https://gitee.com/lmcc-ide/learn
- CCF 中小学大模型教育提纲：https://lmcc.ccf.org.cn/101/1010/10261.html
- CCF 大模型能力认证大纲：https://lmcc.ccf.org.cn/101/1002/10080.html
- 2026年敬业中学同济大学暑期夏令营选拔活动LMCC大模型能力操作细则：https://jy.hpe.cn/jhkx/jsxx/706058.htm
- 首次LMCC青少年组交流活动试题分析：https://lmcc.ccf.org.cn/101/1002/10248.html
- 首次LMCC试题解析及第二轮代码下载:https://lmcc.ccf.org.cn/101/1002/10195.html
- 2026 LMCC青少年组第一轮认证试题分析  https://lmcc.ccf.org.cn/101/1018/10344.html
- 2026 LMCC第二轮认证例题 https://lmcc.ccf.org.cn/101/1002/10346.html

## 仓库内容

| 路径 | 说明 |
| --- | --- |
| `LMCC青少年组教材-增强版.html` | 最新增强版教材（单文件 HTML，含 KaTeX 公式与内嵌 SVG 图） |
| `LMCC青少年组教材-增强版.pdf` | 由 HTML 渲染生成的教材 PDF（含完整答案版附录） |
| `lmcc/` | LMCC 认证各题位评测工程：`T0_CSP`、`T0_LMCC`、`T1`、`T2`、`T3`、`T3_real_demo` |
| `.review/work/work/` | 教材构建与修订管线脚本（见下节） |
| `.review/reports/` | 代码评审与审计过程的输出报告 |

`lmcc/` 采用统一布局：每道题一个目录，内含 `README.md`（题目说明）、`evaluate.py`（评测脚本）、`submission.py`（考生模板）与 `submission.ans.py`（参考答案）。公共依赖 `result_store.py` 负责把各题得分写入统一结果文件。

## 运行评测的信任边界说明

评测脚本在加载通义千问（Qwen）系列模型与 tokenizer 时使用了 `trust_remote_code=True`（见 `T0_LMCC/evaluate.py`、`T1/evaluate.py`、`T2/evaluate.py`、`T3_real_demo/run_real_qwen_diversed.py`）。原因与边界：

1. **必要性**：Qwen 系列在 HuggingFace Hub 上发布的自定义 tokenizer 与模型代码需要该开关才能加载；关闭后无法解析其远程代码配置。
2. **风险**：`trust_remote_code=True` 会执行模型仓库内的自定义 Python 代码，属于"远程代码即执行"的信任扩展。
3. **安全约定**：只应从**官方组织**（`Qwen` / `QwenLM`）或本地可信模型目录加载模型；不要随意加载来源不明、被篡改的模型仓库。生产环境建议将模型下载到本地后，关闭网络并从本地路径加载。
4. **评测数据边界**：评测脚本只读取 `lmcc/data/` 下随仓库发布的用例文件，不读取任意外部数据。

## 从源码复现增强版教材

构建管线按以下顺序执行（均为 `work/` 下的 Python 脚本）。除特别说明外，脚本以 `work/` 同级目录中的教材 HTML 为输入，直接原地修改：

1. `gen_figures.py`：生成教材用矢量图（SVG/PNG 素材）
2. `build_book.py`：读取 `chapters/` 下的章节 HTML，组装出基础版单文件教材 `LMCC青少年组教材.html`；首次进入增强管线时先将其复制为 `LMCC青少年组教材-增强版.html`
3. `gen_terminals.py`：注入终端窗口样式与代码块配色
4. `fix_structure.py`：修正章节结构与排版层级
5. `add_figures.py`：注入 12 幅代码绘制矢量图
6. `expand_trends.py`：补充 2026 前沿趋势与实战案例
7. `revise_book.py`：整体文字修订
8. 图形修复三件套（按需）：`fix_figures.py`、`redraw_figs.py`、`redraw_figs2.py`
9. `update_roc_and_status.py`：重绘 ROC 图并更新 1.4.3 节最新进展
10. `add_lmcc_ide_section.py`：新增 LMCC IDE 实战附录
11. `add_project_report.py`：新增项目报告附录
12. `convert_formulas.py`：把文本公式转换为 KaTeX 渲染块（依赖 `katex/` 本地 KaTeX 资源）
13. `render_enhanced.py`：用 Playwright 将增强版 HTML 渲染为 A4 PDF

**运行依赖**：Python 3.10+；`matplotlib`（出图）、`playwright`（PDF 渲染，需 `playwright install chromium`）、KaTeX 本地资源（`work/katex/`）。因 `build_book.py` 输出路径为 `LMCC青少年组教材.html`，而复现增强管线统一操作 `LMCC青少年组教材-增强版.html`，首次复现请先执行一次复制再进入第 3 步。


