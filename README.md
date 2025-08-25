# HKIA-SAKA (香港国际机场智能助手)

## 项目简介

HKIA-SAKA 是一个基于 RAG (Retrieval-Augmented Generation) 的机场运营手册智能问答系统，专为香港国际机场工作人员设计。该系统能够基于机场操作手册提供精准的技术指导和操作建议。

### 项目架构图

![alt text](Rag_Framework.png)

### 核心功能

- **智能问答**: 基于机场操作手册提供精准回答
- **多模态检索**: 支持文本和图像内容的综合检索
- **流式响应**: 实时流式输出，提升用户体验
- **双模式回答**: 支持简洁模式和详细模式
- **分析看板**：支持手册查询情况统计分析
- **查询日志**: 记录查询历史便于分析和改进
- **评估系统**: 完整的 RAG 性能评估框架

### 技术架构

- **后端**: LangChain
- **向量数据库**: ChromaDB
- **大语言模型**: Ollama (本地部署)
- **嵌入模型**: BGE-M3
- **检索策略**: 混合检索 (向量检索 + BM25 + 图像检索)
- **API**: RESTful API 支持流式响应



## 项目结构

```
hkia_saka_v2/
├── README.md
├── backend/                      # 后端核心代码
│   ├── app/                     # 应用主目录
│   │   ├── main.py              # Streamlit主应用
│   │   ├── database/            # 数据库相关
│   │   │   └── log_query.py     # 查询日志记录
│   │   ├── embedding/           # 嵌入模型处理
│   │   │   └── embedding.py     # 嵌入模型封装
│   │   ├── llm/                 # 大语言模型
│   │   │   ├── llm.py          # LLM 模型封装
│   │   │   └── rag_query.py    # RAG 查询核心逻辑
│   │   └── retriever/           # 检索器
│   │       └── retriever.py    # 混合检索器实现
│   ├── data/                    # 数据存储
│   │   ├── chroma_langchain_db/ # ChromaDB 向量数据库
│   │   ├── extracted/           # 提取的手册内容
│   │   ├── evaluation/          # 评估数据
│   │   ├── logs/               # 查询日志
│   │   └── manual/             # 原始手册文件
│   ├── evaluation/              # 评估系统
│   │   ├── evaluate_rag.py     # RAG 评估主程序
│   │   ├── generate_eval_questions.py  # 评估问题生成
│   │   └── create_radar_map.py # 雷达图可视化
│   ├── process_pdfs/            # PDF 处理模块
│   │   ├── process_pdfs.py     # PDF 处理主程序
│   │   ├── parsing_pdfs.py     # PDF 解析
│   │   ├── split_md.py         # Markdown 分割
│   │   └── get_images.py       # 图像提取和处理
│   ├── scripts/                 # 实验脚本
│   └── requirements.txt         # Python 依赖
```


## 核心功能详解

### 1. 智能查询重写

系统会自动分析用户查询意图，重写查询以提高检索质量：

```python
# 原始查询: "chemical spill"
# 重写后: "What are the key steps that should be taken in response to a chemical spill involving hazardous materials?"
```

### 2. 混合检索策略

- **文本向量检索**: 基于语义相似度检索相关文本段落
- **图像向量检索**: 检索相关图表和流程图
- **BM25 检索**: 基于关键词的传统检索作为补充
- **权重融合**: 可配置的权重组合策略

### 3. 双模式回答

- **Straightforward 模式**: 为一线工作人员提供简洁明确的操作指导
- **Comprehensive 模式**: 为管理人员提供详细的分析和建议


## 评估系统

项目包含完整的 RAG 评估框架：

### 评估指标

- **Answer Relevancy**: 答案相关性
- **Faithfulness**: 答案忠实度
- **Hit Recall**: 检索命中率
- **Coverage Recall**: 覆盖率

### 运行评估

```bash
cd backend/evaluation
python evaluate_rag.py
```

### 生成评估数据

```bash
# 生成评估问题
python generate_eval_questions.py

# 生成 RAGAS 数据集
python generate_ragas_dataset.py
```

## 数据处理

### PDF 手册处理

```bash
cd backend/process_pdfs
python process_pdfs.py
```

处理流程：
1. PDF 解析为 Markdown
2. Markdown二次清洗（标题重分配、页眉页脚空格清洗）
2. 按标题层次分割文档
3. 提取和描述图像内容
4. 生成向量嵌入
5. 存储到 ChromaDB


## 开发指南

### 添加新的手册

1. 将 PDF 文件放入 `backend/data/manual/raw_manual/` 相应目录
2. 运行 PDF 处理脚本
3. 更新向量数据库

### 自定义检索策略

继承 `EnsembleRetriever` 并实现自定义的权重计算逻辑。

### 扩展评估指标

在 `backend/evaluation/evaluate_rag.py` 中添加新的评估指标。


## 更新日志

### v2.0.0
- 重构 RAG 架构
- 添加图像检索支持
- 优化查询重写逻辑
- 完善评估系统

### v1.0.0
- 初始版本发布
- 基础 RAG 功能
- PDF 处理pipeline