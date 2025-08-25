import matplotlib.pyplot as plt
import numpy as np
import os

# 数据定义
data = {
    "answer_relevancy": 0.736581350139128,
    "faithfulness": 0.7290300353917019,
    "text_hit_recall": 0.8059701492537313,
    "img_hit_recall": 0.5588235294117647,
    "full_hit_recall": 0.8656716417910447,
    "coverage_recall": 0.6753731343283582,
}

# 提取标签和值
labels = list(data.keys())
values = list(data.values())

# 闭合图形
values += values[:1]
angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
angles += angles[:1]

# 创建图形
fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))

# 绘制雷达图
ax.plot(angles, values, linewidth=2, linestyle='solid')
ax.fill(angles, values, alpha=0.25)

# 设置角度标签
ax.set_thetagrids(np.degrees(angles[:-1]), labels)
ax.set_ylim(0, 1)
ax.set_title("RAG Evaluation Radar Chart", size=16)

# 在每个点上添加值
for i, (angle, value) in enumerate(zip(angles, values)):
    if i < len(labels):  # 不标注闭合的第一个点
        ax.text(angle, value + 0.05, f"{value:.2f}", ha='center', va='center', fontsize=10, color='black')

# 保存图片
output_path = "backend/evaluation/radar_chart.png"
os.makedirs(os.path.dirname(output_path), exist_ok=True)
plt.tight_layout()
plt.savefig(output_path)
plt.close()

print(f"雷达图已保存至: {output_path}")