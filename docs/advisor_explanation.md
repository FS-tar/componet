# Advisor Explanation Notes

本文件用于整理给导师汇报时的简明讲解。

## 一句话概括

CompoNet 是一种持续强化学习中的可增长策略网络：每来一个新任务就新增一个模块，冻结旧模块，并让新模块通过 attention 动态组合旧策略输出和自己的 internal policy，从而减少遗忘和负迁移。

## 当前复核结论

- 论文发表于 ICML 2024；本地 PDF 共 29 页，文本抽取显示 arXiv 版本日期为 2025-06-04。
- 实验包括 Meta-World 20 任务序列、SpaceInvaders 10 mode 序列、Freeway 序列。
- Freeway 任务数需要特别说明：正文/附录 D.3 描述到 mode 0-6，但附录成功阈值表和代码使用 0-7。
- 第一阶段复现不应直接跑完整实验，应先完成环境检查和短 smoke test。

