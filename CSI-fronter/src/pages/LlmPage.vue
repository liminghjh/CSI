<template>
  <section class="llm">
    <article class="l-main">
      <div class="l-header">
        <div>
          <h2>模型配置</h2>
          <p class="l-sub" v-if="llms.length">{{ llms.length }} 个配置</p>
        </div>
        <div class="l-actions">
          <button class="btn-icon" data-tooltip="刷新" @click="$emit('refresh')">&#x21BB;</button>
          <button class="btn-icon" data-tooltip="新增配置" @click="$emit('open-create')">+</button>
        </div>
      </div>

      <div v-if="loading" class="l-empty">加载中...</div>
      <div v-else-if="llms.length === 0" class="l-empty">暂无配置</div>
      <div v-else class="l-table">
        <div class="l-row l-row--head">
          <span class="l-col-id">#</span>
          <span class="l-col-name">名称</span>
          <span class="l-col-prov">提供商</span>
          <span class="l-col-model">模型</span>
          <span class="l-col-act"></span>
        </div>
        <div
          v-for="item in llms"
          :key="item.id"
          class="l-row"
          :class="{ active: selectedLlm?.id === item.id }"
          @click="$emit('select-llm', item)"
        >
          <span class="l-col-id">{{ item.id }}</span>
          <span class="l-col-name">{{ item.name }}</span>
          <span class="l-col-prov">{{ item.provider }}</span>
          <span class="l-col-model">{{ item.model }}</span>
          <span class="l-col-act">
            <button class="btn-del" data-tooltip="删除" @click.stop="$emit('delete-llm', item.id)">&times;</button>
          </span>
        </div>
      </div>
    </article>

    <article class="l-detail">
      <template v-if="selectedLlm">
        <span class="detail-label">配置详情</span>
        <h3>{{ selectedLlm.name }}</h3>
        <dl>
          <dt>Provider</dt>
          <dd>{{ selectedLlm.provider }}</dd>
          <dt>URL</dt>
          <dd>{{ selectedLlm.url }}</dd>
          <dt>Model</dt>
          <dd>{{ selectedLlm.model }}</dd>
          <dt>Key</dt>
          <dd>{{ maskKey(selectedLlm.key) }}</dd>
        </dl>
        <div class="detail-actions">
          <button class="btn-primary-sm" @click="$emit('test-llm', selectedLlm.id)">测试连接</button>
        </div>
      </template>
      <p v-else class="l-empty">选择配置查看详情</p>
    </article>
  </section>
</template>

<script setup lang="ts">
import type { LlmItem } from '@/api'

defineProps<{
  llms: LlmItem[]
  selectedLlm: LlmItem | null
  loading: boolean
}>()

defineEmits<{
  refresh: []
  'open-create': []
  'select-llm': [item: LlmItem]
  'test-llm': [id: number]
  'delete-llm': [id: number]
}>()

function maskKey(key: string | null) {
  if (!key) return '未填写'
  if (key.length <= 10) return key
  return `${key.slice(0, 4)}...${key.slice(-4)}`
}
</script>

<style scoped>
.llm {
  display: grid;
  grid-template-columns: minmax(0, 1.5fr) 280px;
  gap: 20px;
}

.l-main,
.l-detail {
  border: 1px solid #f3f4f6;
  border-radius: 8px;
  background: #fff;
  padding: 20px;
}

.l-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 16px;
}

.l-header h2 { margin: 0; font-size: 1.1rem; font-weight: 600; color: #111827; }
.l-sub { margin: 4px 0 0; font-size: 0.78rem; color: #9ca3af; }

.l-actions { display: flex; gap: 6px; flex-shrink: 0; }

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

.l-table { display: grid; gap: 0; }

.l-row {
  display: grid;
  grid-template-columns: 40px 1fr 120px 1fr 36px;
  gap: 8px;
  align-items: center;
  padding: 10px 12px;
  border-bottom: 1px solid #f9fafb;
  font-size: 0.85rem;
  color: #374151;
  cursor: pointer;
  transition: background 0.1s;
}

.l-row:hover { background: #fafbfc; }
.l-row.active { background: rgba(124, 58, 237, 0.03); }

.l-row--head {
  font-size: 0.72rem;
  font-weight: 600;
  color: #9ca3af;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-bottom: 1px solid #f3f4f6;
  cursor: default;
}

.l-row--head:hover { background: transparent; }

.l-col-id { color: #7c3aed; font-weight: 600; }
.l-col-name { font-weight: 600; }
.l-col-prov,
.l-col-model { color: #6b7280; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

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

.l-detail { align-self: start; }

.detail-label {
  font-size: 0.7rem;
  font-weight: 600;
  color: #9ca3af;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.l-detail h3 { margin: 8px 0 14px; font-size: 0.95rem; font-weight: 600; color: #111827; }

.l-detail dl { display: grid; gap: 12px; }
.l-detail dt { font-size: 0.72rem; font-weight: 600; color: #9ca3af; text-transform: uppercase; margin-bottom: 2px; }
.l-detail dd { margin: 0; font-size: 0.85rem; color: #374151; line-height: 1.5; word-break: break-word; }

.detail-actions { margin-top: 14px; }

.btn-primary-sm {
  padding: 7px 16px;
  border: 0;
  border-radius: 6px;
  background: #7c3aed;
  color: #fff;
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s;
}

.btn-primary-sm:hover { background: #6d28d9; }

.l-empty { padding: 32px 16px; text-align: center; color: #9ca3af; font-size: 0.88rem; }

@media (max-width: 860px) {
  .llm { grid-template-columns: 1fr; }
  .l-row { grid-template-columns: 30px 1fr 36px; }
  .l-col-prov,
  .l-col-model { display: none; }
}
</style>
