<template>
  <section class="tools">
    <article class="t-main">
      <div class="t-header">
        <div>
          <h2>安全工具</h2>
          <p class="t-sub" v-if="tools.length">{{ tools.length }} 个工具</p>
        </div>
        <div class="t-actions">
          <button class="btn-icon" data-tooltip="刷新" @click="$emit('refresh')">&#x21BB;</button>
          <button class="btn-icon" data-tooltip="新增工具" @click="$emit('open-create')">+</button>
        </div>
      </div>

      <div v-if="loading" class="t-empty">加载中...</div>
      <div v-else-if="tools.length === 0" class="t-empty">暂无工具</div>
      <div v-else class="t-table">
        <div class="t-row t-row--head">
          <span class="t-col-id">#</span>
          <span class="t-col-name">名称</span>
          <span class="t-col-addr">地址</span>
          <span class="t-col-desc">描述</span>
          <span class="t-col-act"></span>
        </div>
        <div
          v-for="tool in tools"
          :key="tool.id"
          class="t-row"
          :class="{ active: selectedTool?.id === tool.id }"
          @click="$emit('select-tool', tool)"
        >
          <span class="t-col-id">{{ tool.id }}</span>
          <span class="t-col-name">{{ tool.name }}</span>
          <span class="t-col-addr">{{ tool.address || '&mdash;' }}</span>
          <span class="t-col-desc">{{ tool.description || '&mdash;' }}</span>
          <span class="t-col-act">
            <button class="btn-del" data-tooltip="删除" @click.stop="$emit('delete-tool', tool.id)">&times;</button>
          </span>
        </div>
      </div>
    </article>

    <article class="t-detail">
      <template v-if="selectedTool">
        <span class="detail-label">工具详情</span>
        <h3>{{ selectedTool.name }}</h3>
        <dl>
          <dt>ID</dt>
          <dd>#{{ selectedTool.id }}</dd>
          <dt>地址</dt>
          <dd>{{ selectedTool.address || '未填写' }}</dd>
          <dt>描述</dt>
          <dd>{{ selectedTool.description || '未填写' }}</dd>
        </dl>
      </template>
      <p v-else class="t-empty">选择工具查看详情</p>
    </article>
  </section>
</template>

<script setup lang="ts">
import type { ToolItem } from '@/api'

defineProps<{
  tools: ToolItem[]
  selectedTool: ToolItem | null
  loading: boolean
}>()

defineEmits<{
  refresh: []
  'open-create': []
  'select-tool': [tool: ToolItem]
  'delete-tool': [id: number]
}>()
</script>

<style scoped>
.tools {
  display: grid;
  grid-template-columns: minmax(0, 1.5fr) 280px;
  gap: 20px;
}

.t-main,
.t-detail {
  border: 1px solid #f3f4f6;
  border-radius: 8px;
  background: #fff;
  padding: 20px;
}

.t-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 16px;
}

.t-header h2 { margin: 0; font-size: 1.1rem; font-weight: 600; color: #111827; }
.t-sub { margin: 4px 0 0; font-size: 0.78rem; color: #9ca3af; }

.t-actions { display: flex; gap: 6px; flex-shrink: 0; }

.btn-icon {
  width: 32px;
  height: 32px;
  display: grid;
  place-items: center;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  background: #fff;
  color: #374151;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.15s;
  position: relative;
}

.btn-icon:hover { border-color: #7c3aed; color: #7c3aed; background: #faf9fe; }

.btn-icon::after {
  content: attr(data-tooltip);
  position: absolute;
  bottom: calc(100% + 6px);
  left: 50%;
  transform: translateX(-50%);
  padding: 3px 8px;
  border-radius: 4px;
  background: #1f2937;
  color: #fff;
  font-size: 0.68rem;
  white-space: nowrap;
  pointer-events: none;
  opacity: 0;
  transition: opacity 0.15s;
}

.btn-icon:hover::after { opacity: 1; }

.t-table { display: grid; gap: 0; }

.t-row {
  display: grid;
  grid-template-columns: 40px 1fr 1fr 1.5fr 36px;
  gap: 8px;
  align-items: center;
  padding: 10px 12px;
  border-bottom: 1px solid #f9fafb;
  font-size: 0.85rem;
  color: #374151;
  cursor: pointer;
  transition: background 0.1s;
}

.t-row:hover { background: #fafbfc; }
.t-row.active { background: rgba(124, 58, 237, 0.03); }

.t-row--head {
  font-size: 0.72rem;
  font-weight: 600;
  color: #9ca3af;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-bottom: 1px solid #f3f4f6;
  cursor: default;
}

.t-row--head:hover { background: transparent; }

.t-col-id { color: #7c3aed; font-weight: 600; }
.t-col-name { font-weight: 600; }
.t-col-addr,
.t-col-desc { color: #6b7280; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

.btn-del {
  width: 26px;
  height: 26px;
  display: grid;
  place-items: center;
  border: 0;
  border-radius: 4px;
  background: transparent;
  color: #9ca3af;
  font-size: 1.1rem;
  cursor: pointer;
  transition: all 0.15s;
  position: relative;
}

.btn-del:hover { background: #fef2f2; color: #ef4444; }

.btn-del::after {
  content: attr(data-tooltip);
  position: absolute;
  bottom: calc(100% + 6px);
  left: 50%;
  transform: translateX(-50%);
  padding: 3px 8px;
  border-radius: 4px;
  background: #1f2937;
  color: #fff;
  font-size: 0.68rem;
  white-space: nowrap;
  pointer-events: none;
  opacity: 0;
  transition: opacity 0.15s;
}

.btn-del:hover::after { opacity: 1; }

.t-detail { align-self: start; }

.detail-label {
  font-size: 0.7rem;
  font-weight: 600;
  color: #9ca3af;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.t-detail h3 { margin: 8px 0 14px; font-size: 0.95rem; font-weight: 600; color: #111827; }

.t-detail dl { display: grid; gap: 12px; }
.t-detail dt { font-size: 0.72rem; font-weight: 600; color: #9ca3af; text-transform: uppercase; margin-bottom: 2px; }
.t-detail dd { margin: 0; font-size: 0.85rem; color: #374151; line-height: 1.5; word-break: break-word; }

.t-empty { padding: 32px 16px; text-align: center; color: #9ca3af; font-size: 0.88rem; }

@media (max-width: 860px) {
  .tools { grid-template-columns: 1fr; }
  .t-row { grid-template-columns: 30px 1fr 36px; }
  .t-col-addr,
  .t-col-desc { display: none; }
}
</style>
