# JS/TS Deep Analysis

## Purpose

增强 JavaScript/TypeScript 仓库的深层分析能力。

## Requirements

### Requirement: ESLint 集成

code_quality 分析器 SHALL 在 JS/TS 仓库上运行 ESLint 检测代码质量问题。

### Requirement: 覆盖率解析

test_coverage 分析器 SHALL 解析 lcov.info 或 coverage-summary.json 获取真实覆盖率。

### Requirement: 循环依赖检测

architecture 分析器 SHALL 使用 madge 检测 JS/TS 仓库的循环依赖。
