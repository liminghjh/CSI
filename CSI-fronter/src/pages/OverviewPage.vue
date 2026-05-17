<template>
  <section class="overview">
    <div class="stat-grid">
      <article v-for="stat in stats" :key="stat.label" class="stat-card">
        <span class="stat-value">{{ stat.value }}</span>
        <span class="stat-label">{{ stat.label }}</span>
      </article>
    </div>

    <div class="quick-grid">
      <article
        v-for="item in entries"
        :key="item.route"
        class="quick-card"
        @click="$emit('navigate', item.route)"
      >
        <div class="quick-icon">{{ item.icon }}</div>
        <div class="quick-text">
          <h3>{{ item.title }}</h3>
          <p>{{ item.description }}</p>
        </div>
        <span class="quick-arrow">&rarr;</span>
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { RouteName } from '@/router'

const props = defineProps<{
  toolCount: number
  llmCount: number
  knowledgeFiles: number
  knowledgeDirs: number
}>()

defineEmits<{ navigate: [route: RouteName] }>()

const stats = computed(() => [
  { label: '安全工具', value: props.toolCount },
  { label: '模型配置', value: props.llmCount },
  { label: '知识文件', value: props.knowledgeFiles },
  { label: '目录层级', value: props.knowledgeDirs },
])

const entries = [
  { icon: '\u{1F3AF}', title: '任务中心', description: '发起安全测试任务，选择模型与工具生成报告', route: 'tasks' as RouteName },
  { icon: '\u{1F4DA}', title: '知识库', description: '浏览漏洞目录树，上传与管理知识文档', route: 'knowledge' as RouteName },
  { icon: '\u{1F6E0}', title: '工具台', description: '管理安全工具列表，保持工具集最新', route: 'tools' as RouteName },
  { icon: '\u{1F9E0}', title: '模型仓', description: '维护 LLM 配置与测试连通性', route: 'llm' as RouteName },
]
</script>

<style scoped>
.overview {
  display: grid;
  gap: 24px;
}

.stat-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
}

.stat-card {
  padding: 20px;
  border: 1px solid #f3f4f6;
  border-radius: 8px;
  background: #fff;
}

.stat-value {
  display: block;
  font-size: 2rem;
  font-weight: 700;
  color: #111827;
  line-height: 1;
}

.stat-label {
  display: block;
  margin-top: 8px;
  font-size: 0.82rem;
  color: #9ca3af;
}

.quick-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 14px;
}

.quick-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  border: 1px solid #f3f4f6;
  border-radius: 8px;
  background: #fff;
  cursor: pointer;
  transition: all 0.2s;
}

.quick-card:hover {
  border-color: #c4b5fd;
  background: #faf9fe;
  box-shadow: 0 2px 12px rgba(124, 58, 237, 0.06);
}

.quick-card:hover .quick-arrow {
  color: #7c3aed;
  transform: translateX(2px);
}

.quick-icon {
  font-size: 1.4rem;
  flex-shrink: 0;
}

.quick-text {
  flex: 1;
  min-width: 0;
}

.quick-text h3 {
  margin: 0;
  font-size: 0.95rem;
  font-weight: 600;
  color: #111827;
}

.quick-text p {
  margin: 4px 0 0;
  font-size: 0.8rem;
  color: #9ca3af;
  line-height: 1.5;
}

.quick-arrow {
  color: #d1d5db;
  font-size: 1.1rem;
  transition: all 0.2s;
  flex-shrink: 0;
}

@media (max-width: 800px) {
  .stat-grid { grid-template-columns: repeat(2, 1fr); }
  .quick-grid { grid-template-columns: 1fr; }
}
</style>
