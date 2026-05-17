<template>
  <section class="tasks">
    <article class="task-main">
      <div class="form-grid">
        <label class="field">
          <span class="field-label">目标地址</span>
          <input
            type="text"
            :value="urlOrIp"
            placeholder="192.168.1.1"
            @input="emit('update:url-or-ip', ($event.target as HTMLInputElement).value)"
          />
        </label>
        <label class="field">
          <span class="field-label">端口（可选）</span>
          <input
            type="number"
            :value="port ?? ''"
            placeholder="80"
            @input="emit('update:port', Number(($event.target as HTMLInputElement).value))"
          />
        </label>
      </div>

      <label class="field">
        <span class="field-label">模型配置</span>
        <select :value="selectedLlmId ?? ''" @change="onSelectLlm">
          <option value="" disabled>选择模型...</option>
          <option v-for="item in llmList" :key="item.id" :value="item.id">
            #{{ item.id }} {{ item.name }} &middot; {{ item.model }}
          </option>
        </select>
      </label>

      <label class="field">
        <span class="field-label">任务类型</span>
        <div class="radio-row">
          <label class="radio-chip" :class="{ active: systemDoc === 0 }">
            <input type="radio" :value="0" :checked="systemDoc === 0" @change="emit('update:system-doc', 0)" />
            <span>
              <strong>生成报告</strong>
              <small>全面安全评估</small>
            </span>
          </label>
          <label class="radio-chip" :class="{ active: systemDoc === 1 }">
            <input type="radio" :value="1" :checked="systemDoc === 1" @change="emit('update:system-doc', 1)" />
            <span>
              <strong>夺取 Flag</strong>
              <small>漏洞利用测试</small>
            </span>
          </label>
        </div>
      </label>

      <div class="action-bar">
        <button class="btn-primary" :disabled="loading" @click="$emit('run-task')">
          {{ loading ? '执行中...' : '执行任务' }}
        </button>
        <button class="btn-ghost" :disabled="!report" data-tooltip="查看报告" @click="$emit('open-report')">
          &#x1F4C4;
        </button>
        <button class="btn-ghost" data-tooltip="使用说明" @click="$emit('open-guide')">
          &#x2139;
        </button>
      </div>

      <p v-if="error" class="task-error">{{ error }}</p>

      <!-- Streaming log -->
      <div v-if="loading || log.length > 0" class="task-stream">
        <div class="stream-header">
          <span>任务执行进度</span>
          <span class="stream-count" v-if="log.length">{{ log.length }} 个事件</span>
        </div>
        <div class="stream-body" ref="streamBody">
          <div v-if="log.length === 0" class="stream-card stream-card--pending">
            <span class="stream-dot stream-dot--pulse"></span>
            <div class="stream-content">
              <span class="stream-title">正在连接后端服务...</span>
            </div>
          </div>
          <div
            v-for="(entry, idx) in log"
            :key="idx"
            class="stream-card"
            :class="cardClass(entry.type)"
          >
            <span class="stream-dot" :class="dotClass(entry.type)"></span>
            <div class="stream-content">
              <span class="stream-title">
                <template v-if="entry.type === 'start'">开始运行任务</template>
                <template v-else-if="entry.type === 'prepare'">完成环境准备</template>
                <template v-else-if="entry.type === 'start_tool'">
                  调用工具 <strong>{{ entry.tool }}</strong>
                </template>
                <template v-else-if="entry.type === 'end_tool'">
                  工具 <strong>{{ entry.tool }}</strong> 执行完毕
                </template>
                <template v-else-if="entry.type === 'report'">报告已生成</template>
                <template v-else-if="entry.type === 'error'">发生错误</template>
              </span>
              <span class="stream-desc" v-if="entry.type === 'start_tool'">
                输入: {{ entry.message }}
              </span>
              <span class="stream-desc" v-else-if="entry.type === 'end_tool'">
                输出: {{ entry.message }}
              </span>
              <span class="stream-desc" v-else-if="entry.type === 'error'">
                {{ entry.message }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </article>

    <aside class="task-aside">
      <div class="aside-card">
        <span class="aside-label">当前模型</span>
        <p class="aside-value">{{ llmSummary }}</p>
      </div>
      <div class="aside-card">
        <span class="aside-label">目标</span>
        <p class="aside-value" v-if="urlOrIp">{{ urlOrIp }}{{ port ? ':' + port : '' }}</p>
        <p class="aside-muted" v-else>未填写</p>
      </div>
      <div class="aside-card">
        <span class="aside-label">报告预览</span>
        <p class="aside-value" v-if="report">{{ reportPreview }}</p>
        <p class="aside-muted" v-else>执行任务后显示</p>
      </div>
    </aside>
  </section>
</template>

<script setup lang="ts">
import { computed, ref, watch, type PropType, nextTick } from 'vue'
import type { LlmItem, SseTaskEvent } from '@/api'

const props = defineProps<{
  llmList: LlmItem[]
  selectedLlmId: number | null
  urlOrIp: string
  port: number | null
  systemDoc: number
  report: string
  loading: boolean
  error: string
  log: SseTaskEvent[]
}>()

const emit = defineEmits<{
  (e: 'update:selected-llm-id' | 'update:port' | 'update:system-doc', value: number): void
  (e: 'update:url-or-ip', value: string): void
  (e: 'run-task' | 'open-report' | 'open-guide'): void
}>()

const streamBody = ref<HTMLElement | null>(null)

watch(
  () => props.log.length,
  () => {
    nextTick(() => {
      if (streamBody.value) {
        streamBody.value.scrollTop = streamBody.value.scrollHeight
      }
    })
  },
)

const llmSummary = computed(() => {
  const m = props.llmList.find((item) => item.id === props.selectedLlmId)
  return m ? `${m.name} / ${m.model}` : '未选择'
})

const reportPreview = computed(() =>
  props.report.length > 200 ? props.report.slice(0, 200) + '...' : props.report,
)

function onSelectLlm(e: Event) {
  const v = Number((e.target as HTMLSelectElement).value)
  if (!Number.isNaN(v)) emit('update:selected-llm-id', v)
}

function cardClass(type: string): string {
  const map: Record<string, string> = {
    start: 'stream-card--start',
    prepare: 'stream-card--prepare',
    start_tool: 'stream-card--tool-start',
    end_tool: 'stream-card--tool-end',
    report: 'stream-card--report',
    error: 'stream-card--error',
  }
  return map[type] ?? ''
}

function dotClass(type: string): string {
  const map: Record<string, string> = {
    start: 'stream-dot--start',
    prepare: 'stream-dot--prepare',
    start_tool: 'stream-dot--tool-start',
    end_tool: 'stream-dot--tool-end',
    report: 'stream-dot--report',
    error: 'stream-dot--error',
  }
  return map[type] ?? ''
}
</script>

<style scoped>
.tasks {
  display: grid;
  grid-template-columns: minmax(0, 1.4fr) 260px;
  gap: 20px;
}

.task-main {
  padding: 24px;
  border: 1px solid #f3f4f6;
  border-radius: 8px;
  background: #fff;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 100px;
  gap: 14px;
  margin-bottom: 4px;
}

.field {
  display: grid;
  gap: 6px;
  margin-bottom: 16px;
}

.field-label {
  font-size: 0.82rem;
  font-weight: 600;
  color: #374151;
}

.field input,
.field select,
.field textarea {
  width: 100%;
  padding: 9px 12px;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  background: #fafbfc;
  color: #111827;
  font-size: 0.9rem;
  transition: border-color 0.15s, box-shadow 0.15s;
}

.field input:focus,
.field select:focus,
.field textarea:focus {
  outline: none;
  border-color: #7c3aed;
  box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.08);
}

.field textarea {
  resize: vertical;
}

.radio-row {
  display: flex;
  gap: 10px;
}

.radio-chip {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 14px;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  background: #fafbfc;
  cursor: pointer;
  transition: all 0.15s;
}

.radio-chip:hover {
  border-color: #c4b5fd;
  background: #faf9fe;
}

.radio-chip.active {
  border-color: #7c3aed;
  background: rgba(124, 58, 237, 0.04);
}

.radio-chip input[type="radio"] { display: none; }
.radio-chip strong { display: block; font-size: 0.88rem; color: #111827; }
.radio-chip small { display: block; font-size: 0.75rem; color: #9ca3af; margin-top: 2px; }

.action-bar {
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-primary {
  padding: 9px 20px;
  border: 0;
  border-radius: 6px;
  background: #7c3aed;
  color: #fff;
  font-size: 0.88rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s;
}

.btn-primary:hover:not(:disabled) { background: #6d28d9; }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }

.btn-ghost {
  width: 36px;
  height: 36px;
  display: grid;
  place-items: center;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  background: #fff;
  cursor: pointer;
  font-size: 0.95rem;
  transition: all 0.15s;
  position: relative;
}

.btn-ghost:hover:not(:disabled) { border-color: #c4b5fd; background: #faf9fe; }
.btn-ghost:disabled { opacity: 0.4; cursor: not-allowed; }

.btn-ghost::after {
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

.btn-ghost:hover::after { opacity: 1; }

.task-error {
  margin: 14px 0 0;
  color: #ef4444;
  font-size: 0.85rem;
}

/* ---- Streaming log ---- */
.task-stream {
  margin-top: 16px;
  border: 1px solid #f3f4f6;
  border-radius: 8px;
  background: #fff;
  overflow: hidden;
}

.stream-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 16px;
  font-size: 0.75rem;
  font-weight: 600;
  color: #9ca3af;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-bottom: 1px solid #f3f4f6;
  background: #fafbfc;
}

.stream-count {
  font-size: 0.7rem;
  font-weight: 500;
  color: #c4b5fd;
}

.stream-body {
  padding: 8px;
  max-height: 320px;
  overflow-y: auto;
  display: grid;
  gap: 6px;
}

.stream-card {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 10px 14px;
  border: 1px solid #f3f4f6;
  border-radius: 6px;
  background: #fff;
  border-left: 3px solid #e5e7eb;
  transition: border-color 0.2s, background 0.2s;
}

.stream-card--start       { border-left-color: #7c3aed; background: rgba(124,58,237,0.02); }
.stream-card--prepare     { border-left-color: #059669; background: rgba(5,150,105,0.02); }
.stream-card--tool-start  { border-left-color: #d97706; background: rgba(217,119,6,0.02); }
.stream-card--tool-end    { border-left-color: #059669; background: rgba(5,150,105,0.02); }
.stream-card--report      { border-left-color: #7c3aed; background: rgba(124,58,237,0.03); }
.stream-card--error       { border-left-color: #ef4444; background: rgba(239,68,68,0.03); }
.stream-card--pending     { border-left-color: #7c3aed; }

.stream-dot {
  flex-shrink: 0;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-top: 5px;
  background: #d1d5db;
}

.stream-dot--start       { background: #7c3aed; }
.stream-dot--prepare     { background: #059669; }
.stream-dot--tool-start  { background: #d97706; }
.stream-dot--tool-end    { background: #059669; }
.stream-dot--report      { background: #7c3aed; }
.stream-dot--error       { background: #ef4444; }

.stream-dot--pulse {
  background: #7c3aed;
  animation: stream-pulse 1.2s ease-in-out infinite;
}

@keyframes stream-pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.35; }
}

.stream-content {
  min-width: 0;
  display: grid;
  gap: 3px;
}

.stream-title {
  font-size: 0.84rem;
  color: #374151;
  line-height: 1.5;
}

.stream-title strong {
  color: #111827;
  font-weight: 600;
}

.stream-desc {
  font-size: 0.76rem;
  color: #9ca3af;
  line-height: 1.5;
  word-break: break-all;
  max-height: 80px;
  overflow-y: auto;
}

.task-aside {
  display: grid;
  gap: 12px;
  align-content: start;
}

.aside-card {
  padding: 16px;
  border: 1px solid #f3f4f6;
  border-radius: 8px;
  background: #fff;
}

.aside-label {
  display: block;
  font-size: 0.7rem;
  font-weight: 600;
  color: #9ca3af;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  margin-bottom: 6px;
}

.aside-value {
  margin: 0;
  font-size: 0.85rem;
  color: #111827;
  line-height: 1.5;
  word-break: break-all;
}

.aside-muted { margin: 0; font-size: 0.82rem; color: #d1d5db; }

@media (max-width: 860px) {
  .tasks { grid-template-columns: 1fr; }
  .form-grid { grid-template-columns: 1fr; }
  .radio-row { flex-direction: column; }
}
</style>
