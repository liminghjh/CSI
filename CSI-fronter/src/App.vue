<template>
  <div class="shell">
    <aside class="sidebar">
      <div class="brand">
        <span class="brand-icon">&#x25C8;</span>
        <div>
          <h1>CSI Platform</h1>
          <p>安全测试控制台</p>
        </div>
      </div>

      <nav class="nav">
        <button
          v-for="item in navItems"
          :key="item.name"
          class="nav-item"
          :class="{ active: currentRoute === item.name }"
          type="button"
          @click="goTo(item.name)"
        >
          <span class="nav-icon" v-html="item.icon" />
          <div class="nav-text">
            <strong>{{ item.label }}</strong>
            <span>{{ item.desc }}</span>
          </div>
        </button>
      </nav>

      <div class="side-foot">
        <div class="foot-stat">
          <span>工具</span><strong>{{ toolList.length }}</strong>
        </div>
        <div class="foot-stat">
          <span>模型</span><strong>{{ llmList.length }}</strong>
        </div>
        <div class="foot-stat">
          <span>知识文件</span><strong>{{ knowledgeFileCount }}</strong>
        </div>
      </div>
    </aside>

    <main class="main">
      <header class="topbar">
        <div>
          <span class="topbar-route">{{ activeRouteLabel }}</span>
          <h2>{{ pageTitle }}</h2>
        </div>
        <div class="status" :class="{ err: !!notif.error.value }">
          {{ notif.error.value || notif.message.value || '就绪' }}
        </div>
      </header>

      <OverviewPage
        v-if="currentRoute === 'overview'"
        :tool-count="toolList.length"
        :llm-count="llmList.length"
        :knowledge-files="knowledgeFileCount"
        :knowledge-dirs="knowledgeDirCount"
        @navigate="goTo"
      />

      <TasksPage
        v-else-if="currentRoute === 'tasks'"
        :llm-list="llmList"
        :selected-llm-id="selectedId"
        :url-or-ip="urlOrIp"
        :port="port"
        :system-doc="systemDoc"
        :report="taskReport"
        :loading="taskRunning"
        :error="taskError"
        :log="taskLog"
        @update:selected-llm-id="selectedId = $event"
        @update:url-or-ip="urlOrIp = $event"
        @update:port="port = $event"
        @update:system-doc="systemDoc = $event"
        @run-task="handleRunTask"
        @open-report="reportOpen = true"
        @open-guide="guideOpen = true"
      />

      <KnowledgePage
        v-else-if="currentRoute === 'knowledge'"
        :tree="knowledgeTree"
        :selected-file="selectedFile"
        :loading="knowledgeLoading"
        @refresh="knowledge.refresh()"
        @open-upload="openUploadModal"
        @open-delete="openDeleteModal"
        @select-file="knowledge.selectFile($event)"
      />

      <ToolsPage
        v-else-if="currentRoute === 'tools'"
        :tools="toolList"
        :selected-tool="selectedTool"
        :loading="toolLoading"
        @refresh="tools.refresh()"
        @open-create="toolModalOpen = true"
        @select-tool="tools.select($event)"
        @delete-tool="tools.remove($event)"
      />

      <LlmPage
        v-else
        :llms="llmList"
        :selected-llm="selectedLlm"
        :loading="llmLoading"
        @refresh="llms.refresh()"
        @open-create="llmModalOpen = true"
        @select-llm="llms.select($event)"
        @test-llm="handleTestLlm"
        @delete-llm="llms.remove($event)"
      />
    </main>

    <!-- Guide Modal -->
    <ModalWindow :open="guideOpen" title="使用说明" eyebrow="Guide" @close="guideOpen = false">
      <div class="modal-text">
        <h4>任务页如何工作</h4>
        <p>填写目标地址和端口，选择模型配置和任务类型，后端自动加载知识库与工具集，由 Agent 执行安全测试并返回结果。</p>
        <h4>推荐操作顺序</h4>
        <p>先去模型仓确认 LLM 可用，再到工具台检查工具列表，最后回任务中心发起任务。</p>
      </div>
    </ModalWindow>

    <!-- Report Modal -->
    <ModalWindow :open="reportOpen" title="任务报告" size="large" @close="reportOpen = false">
      <div v-if="taskReport" class="report-wrap">
        <div class="report-actions">
          <button class="btn-primary-sm" @click="downloadReport">&#x2913; 下载 .md</button>
        </div>
        <div class="md-render" v-html="renderMarkdown(taskReport)" />
      </div>
      <p v-else class="report-empty">暂无报告内容</p>
    </ModalWindow>

    <!-- Tool Create Modal -->
    <ModalWindow :open="toolModalOpen" title="新增工具" @close="toolModalOpen = false">
      <form class="modal-form" @submit.prevent="handleCreateTool">
        <label class="mf-field">
          <span>工具名称</span>
          <input v-model.trim="toolForm.tool_name" placeholder="例如 sqlmap" />
        </label>
        <label class="mf-field">
          <span>工具地址</span>
          <input v-model.trim="toolForm.tool_address" placeholder="/usr/bin/sqlmap" />
        </label>
        <label class="mf-field">
          <span>工具描述</span>
          <textarea v-model.trim="toolForm.tool_description" rows="4" placeholder="简单描述用途" />
        </label>
        <div class="mf-actions">
          <button class="btn-primary" type="submit" :disabled="toolSubmitting">
            {{ toolSubmitting ? '提交中...' : '确认' }}
          </button>
          <button class="btn-ghost" type="button" @click="toolModalOpen = false">取消</button>
        </div>
      </form>
    </ModalWindow>

    <!-- LLM Create Modal -->
    <ModalWindow :open="llmModalOpen" title="新增模型配置" @close="llmModalOpen = false">
      <form class="modal-form" @submit.prevent="handleCreateLlm">
        <label class="mf-field">
          <span>配置名称</span>
          <input v-model.trim="llmForm.name" placeholder="例如 NVIDIA 主配置" />
        </label>
        <label class="mf-field">
          <span>提供商</span>
          <input v-model.trim="llmForm.provider" placeholder="openai / ollama" />
        </label>
        <label class="mf-field">
          <span>API Key</span>
          <input v-model.trim="llmForm.key" placeholder="密钥" />
        </label>
        <label class="mf-field">
          <span>接口地址</span>
          <input v-model.trim="llmForm.url" placeholder="http://127.0.0.1:8000/v1" />
        </label>
        <label class="mf-field">
          <span>模型名称</span>
          <input v-model.trim="llmForm.model" placeholder="openai/gpt-oss-120b" />
        </label>
        <div class="mf-actions">
          <button class="btn-primary" type="submit" :disabled="llmSubmitting">
            {{ llmSubmitting ? '提交中...' : '确认' }}
          </button>
          <button class="btn-ghost" type="button" @click="llmModalOpen = false">取消</button>
        </div>
      </form>
    </ModalWindow>

    <!-- LLM Test Modal -->
    <ModalWindow :open="llmTestOpen" title="LLM 连通性测试" :eyebrow="llmTestModelName" @close="llmTestOpen = false">
      <div class="modal-text">
        <div v-if="llmTesting" class="test-status test-pending">正在测试连接，请稍候...</div>
        <div v-else-if="llmTestResult" class="test-result">
          <div class="test-status" :class="llmTestResult.ok ? 'test-ok' : 'test-fail'">
            {{ llmTestResult.ok ? '连接成功' : '连接失败' }}
          </div>
          <p v-if="llmTestResult.message" class="test-detail">{{ llmTestResult.message }}</p>
        </div>
      </div>
    </ModalWindow>

    <!-- Upload Modal -->
    <ModalWindow :open="uploadModalOpen" title="上传知识库文件" @close="uploadModalOpen = false">
      <form class="modal-form" @submit.prevent="handleUpload">
        <label class="mf-field">
          <span>保存目录</span>
          <input v-model.trim="uploadDir" placeholder="/path/to/directory" />
        </label>
        <label class="mf-field">
          <span>选择 md 文件</span>
          <input type="file" accept=".md,text/markdown" @change="onFileChange" />
        </label>
        <p class="file-hint">{{ uploadFile ? uploadFile.name : '未选择文件' }}</p>
        <div class="mf-actions">
          <button class="btn-primary" type="submit" :disabled="knowledgeUploading">
            {{ knowledgeUploading ? '上传中...' : '上传' }}
          </button>
          <button class="btn-ghost" type="button" @click="uploadModalOpen = false">取消</button>
        </div>
      </form>
    </ModalWindow>

    <!-- Delete Knowledge Modal -->
    <ModalWindow :open="deleteModalOpen" title="删除知识库文件" @close="deleteModalOpen = false">
      <div class="modal-text">
        <p v-if="selectedFile">
          确认删除 <strong>{{ selectedFile.fileName }}</strong>？
        </p>
        <p v-else>未选择文件</p>
        <div class="mf-actions">
          <button class="btn-danger" :disabled="!selectedFile" @click="handleDeleteKnowledge">确认删除</button>
          <button class="btn-ghost" type="button" @click="deleteModalOpen = false">取消</button>
        </div>
      </div>
    </ModalWindow>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import { parseAndFormat } from './utils/parse-report'
import ModalWindow from './components/ModalWindow.vue'
import KnowledgePage from './pages/KnowledgePage.vue'
import LlmPage from './pages/LlmPage.vue'
import OverviewPage from './pages/OverviewPage.vue'
import TasksPage from './pages/TasksPage.vue'
import ToolsPage from './pages/ToolsPage.vue'
import { routes, useHashRoute } from './router'
import { useNotification } from './composables/useNotification'
import { useTools } from './composables/useTools'
import { useLlms } from './composables/useLlms'
import { useKnowledge } from './composables/useKnowledge'
import { testLlm } from './api'
import { useTasks } from './composables/useTasks'

const { currentRoute, goTo } = useHashRoute()
const notif = useNotification()
const tools = useTools()
const llms = useLlms()
const knowledge = useKnowledge()
const tasks = useTasks()

// Destructure for template auto-unwrap
const { list: toolList, loading: toolLoading, selected: selectedTool, submitting: toolSubmitting } = tools
const { list: llmList, loading: llmLoading, selected: selectedLlm, selectedId, submitting: llmSubmitting } = llms
const { tree: knowledgeTree, loading: knowledgeLoading, selectedFile, uploading: knowledgeUploading, uploadDir, uploadFile } = knowledge
const { urlOrIp, port, systemDoc, report: taskReport, running: taskRunning, error: taskError, log: taskLog } = tasks

const guideOpen = ref(false)
const reportOpen = ref(false)
const toolModalOpen = ref(false)
const llmModalOpen = ref(false)
const uploadModalOpen = ref(false)
const deleteModalOpen = ref(false)
const llmTestOpen = ref(false)
const llmTesting = ref(false)
const llmTestResult = ref<{ ok: boolean; message: string } | null>(null)
const llmTestModelName = ref('')

const toolForm = reactive({ tool_name: '', tool_address: '', tool_description: '' })
const llmForm = reactive({ name: '', provider: '', key: '', url: '', model: '' })

const navItems = [
  { name: 'overview' as const, label: '总览', icon: '&#x25A0;', desc: '控制台仪表盘' },
  { name: 'tasks' as const, label: '任务中心', icon: '&#x25C9;', desc: '发起安全测试' },
  { name: 'knowledge' as const, label: '知识库', icon: '&#x25CB;', desc: '漏洞文档管理' },
  { name: 'tools' as const, label: '工具台', icon: '&#x25C6;', desc: '安全工具列表' },
  { name: 'llm' as const, label: '模型仓', icon: '&#x25B7;', desc: 'LLM 配置管理' },
]

const activeRouteLabel = computed(() => routes.find((r) => r.name === currentRoute.value)?.label ?? '总览')

const pageTitle = computed(() => {
  switch (currentRoute.value) {
    case 'tasks': return '安全测试任务'
    case 'knowledge': return '漏洞知识库'
    case 'tools': return '安全工具管理'
    case 'llm': return '模型配置管理'
    default: return '控制台总览'
  }
})

function countKnowledge(node: any): { files: number; dirs: number } {
  if (!node) return { files: 0, dirs: 0 }
  let files = node.files.length
  let dirs = node.dirs.length
  for (const c of node.dirs) {
    const r = countKnowledge(c)
    files += r.files
    dirs += r.dirs
  }
  return { files, dirs }
}

const knowledgeFileCount = computed(() => countKnowledge(knowledgeTree.value).files)
const knowledgeDirCount = computed(() => countKnowledge(knowledgeTree.value).dirs)

function resetToolForm() {
  toolForm.tool_name = ''
  toolForm.tool_address = ''
  toolForm.tool_description = ''
}

function resetLlmForm() {
  llmForm.name = ''
  llmForm.provider = ''
  llmForm.key = ''
  llmForm.url = ''
  llmForm.model = ''
}

async function handleCreateTool() {
  const ok = await tools.add({ ...toolForm })
  if (ok) {
    resetToolForm()
    toolModalOpen.value = false
  }
}

async function handleCreateLlm() {
  const ok = await llms.add({ ...llmForm })
  if (ok) {
    resetLlmForm()
    llmModalOpen.value = false
  }
}

function openUploadModal() {
  knowledge.resetUpload()
  uploadModalOpen.value = true
}

function openDeleteModal() {
  if (!selectedFile.value) {
    notif.failure('请先选择一个文件')
    return
  }
  deleteModalOpen.value = true
}

function onFileChange(event: Event) {
  const files = (event.target as HTMLInputElement).files
  knowledge.setUploadFile(files?.item(0) ?? null)
}

async function handleUpload() {
  const ok = await knowledge.upload()
  if (ok) uploadModalOpen.value = false
}

async function handleDeleteKnowledge() {
  const ok = await knowledge.remove()
  if (ok) deleteModalOpen.value = false
}

async function handleRunTask() {
  const ok = await tasks.run(selectedId.value)
  if (ok) reportOpen.value = true
}

async function handleTestLlm(id: number) {
  const llm = llmList.value.find((l) => l.id === id)
  llmTestModelName.value = llm?.name ?? `ID ${id}`
  llmTestResult.value = null
  llmTesting.value = true
  llmTestOpen.value = true
  try {
    const ok = await testLlm(id)
    llmTestResult.value = { ok, message: '' }
  } catch (e) {
    llmTestResult.value = { ok: false, message: e instanceof Error ? e.message : '模型测试失败' }
  } finally {
    llmTesting.value = false
  }
}

function renderMarkdown(text: string): string {
  const md = parseAndFormat(text)
  const html = marked.parse(md) as string
  return DOMPurify.sanitize(html)
}

function downloadReport() {
  const text = taskReport.value
  if (!text) return
  const md = parseAndFormat(text)
  const blob = new Blob([md], { type: 'text/markdown' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `report_${Date.now()}.md`
  a.click()
  URL.revokeObjectURL(url)
}

onMounted(async () => {
  await Promise.all([tools.refresh(), llms.refresh(), knowledge.refresh()])
})
</script>

<style>
*,
*::before,
*::after {
  box-sizing: border-box;
}

body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
  font-size: 15px;
  color: #111827;
  background: #f8f9fc;
  -webkit-font-smoothing: antialiased;
}

button,
input,
textarea,
select {
  font: inherit;
}

button {
  cursor: pointer;
}

/* ---- Markdown rendered content (non-scoped for v-html) ---- */
.md-render { padding: 16px; border-radius: 6px; background: #fafbfc; font-size: 0.88rem; line-height: 1.8; color: #1f2937; max-height: 60vh; overflow-y: auto; word-break: break-word; }
.md-render h1 { font-size: 1.4rem; margin: 20px 0 12px; padding-bottom: 8px; border-bottom: 1px solid #e5e7eb; color: #111827; }
.md-render h2 { font-size: 1.2rem; margin: 18px 0 10px; color: #111827; }
.md-render h3 { font-size: 1.05rem; margin: 14px 0 8px; color: #111827; }
.md-render h4 { font-size: 0.95rem; margin: 12px 0 6px; color: #111827; }
.md-render p { margin: 8px 0; }
.md-render strong { color: #111827; }
.md-render code { padding: 2px 6px; border-radius: 3px; background: #f3f4f6; font-size: 0.84rem; color: #7c3aed; }
.md-render pre { padding: 14px; border-radius: 6px; background: #1e293b; color: #e2e8f0; overflow-x: auto; margin: 10px 0; }
.md-render pre code { padding: 0; background: transparent; color: inherit; font-size: 0.82rem; }
.md-render ul, .md-render ol { padding-left: 22px; margin: 8px 0; }
.md-render li { margin: 4px 0; }
.md-render table { width: 100%; border-collapse: collapse; margin: 12px 0; font-size: 0.85rem; }
.md-render th, .md-render td { padding: 8px 12px; border: 1px solid #e5e7eb; text-align: left; }
.md-render th { background: #f3f4f6; font-weight: 600; color: #374151; }
.md-render blockquote { margin: 10px 0; padding: 8px 16px; border-left: 3px solid #7c3aed; background: rgba(124,58,237,0.04); color: #6b7280; }
.md-render a { color: #7c3aed; text-decoration: underline; }
.md-render hr { border: 0; border-top: 1px solid #e5e7eb; margin: 16px 0; }
.md-render img { max-width: 100%; border-radius: 4px; }
</style>

<style scoped>
.shell {
  min-height: 100vh;
  display: grid;
  grid-template-columns: 240px minmax(0, 1fr);
}

/* ---- Sidebar ---- */
.sidebar {
  position: sticky;
  top: 0;
  height: 100vh;
  display: grid;
  align-content: start;
  gap: 0;
  padding: 20px 16px;
  background: #fff;
  border-right: 1px solid #f3f4f6;
  overflow-y: auto;
}

.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 0 6px 20px;
  margin-bottom: 8px;
  border-bottom: 1px solid #f3f4f6;
}

.brand-icon {
  width: 34px;
  height: 34px;
  display: grid;
  place-items: center;
  border-radius: 8px;
  background: #7c3aed;
  color: #fff;
  font-size: 0.9rem;
  flex-shrink: 0;
}

.brand h1 {
  margin: 0;
  font-size: 0.95rem;
  font-weight: 700;
  color: #111827;
  line-height: 1.2;
}

.brand p {
  margin: 2px 0 0;
  font-size: 0.72rem;
  color: #9ca3af;
}

.nav {
  display: grid;
  gap: 2px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 10px;
  border: 0;
  border-radius: 6px;
  background: transparent;
  color: #6b7280;
  text-align: left;
  transition: all 0.15s;
}

.nav-item:hover {
  background: #f5f3ff;
  color: #7c3aed;
}

.nav-item.active {
  background: rgba(124, 58, 237, 0.07);
  color: #7c3aed;
}

.nav-icon {
  width: 20px;
  font-size: 0.7rem;
  text-align: center;
  flex-shrink: 0;
}

.nav-text strong {
  display: block;
  font-size: 0.85rem;
  font-weight: 600;
}

.nav-text span {
  display: block;
  font-size: 0.72rem;
  opacity: 0.65;
  margin-top: 1px;
}

.side-foot {
  margin-top: auto;
  padding: 16px 6px 0;
  border-top: 1px solid #f3f4f6;
  display: grid;
  gap: 8px;
}

.foot-stat {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.78rem;
}

.foot-stat span {
  color: #9ca3af;
}

.foot-stat strong {
  color: #7c3aed;
  font-size: 0.9rem;
}

/* ---- Main ---- */
.main {
  padding: 20px 24px;
  min-width: 0;
}

.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 20px;
}

.topbar-route {
  font-size: 0.72rem;
  font-weight: 600;
  color: #7c3aed;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.topbar h2 {
  margin: 2px 0 0;
  font-size: 1.3rem;
  font-weight: 700;
  color: #111827;
}

.status {
  padding: 6px 14px;
  border-radius: 999px;
  background: rgba(124, 58, 237, 0.06);
  color: #7c3aed;
  font-size: 0.8rem;
  white-space: nowrap;
}

.status.err {
  background: #fef2f2;
  color: #ef4444;
}

/* ---- Modal shared ---- */
.modal-form {
  display: grid;
  gap: 14px;
}

.mf-field {
  display: grid;
  gap: 5px;
}

.mf-field span {
  font-size: 0.82rem;
  font-weight: 600;
  color: #374151;
}

.mf-field input,
.mf-field textarea {
  width: 100%;
  padding: 9px 12px;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  background: #fafbfc;
  color: #111827;
  font-size: 0.9rem;
  transition: border-color 0.15s, box-shadow 0.15s;
}

.mf-field input:focus,
.mf-field textarea:focus {
  outline: none;
  border-color: #7c3aed;
  box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.08);
}

.mf-field textarea {
  resize: vertical;
}

.file-hint {
  padding: 10px 14px;
  border-radius: 6px;
  background: #f9fafb;
  color: #9ca3af;
  font-size: 0.85rem;
}

.mf-actions {
  display: flex;
  gap: 8px;
  margin-top: 4px;
}

.modal-text {
  color: #374151;
  line-height: 1.6;
}

.modal-text h4 {
  margin: 14px 0 6px;
  font-size: 0.9rem;
  color: #111827;
}

.modal-text h4:first-child { margin-top: 0; }

.modal-text p { margin: 0 0 10px; font-size: 0.88rem; }

.test-status {
  padding: 12px 16px;
  border-radius: 8px;
  font-size: 0.95rem;
  font-weight: 600;
  text-align: center;
}

.test-pending {
  background: #f5f3ff;
  color: #7c3aed;
}

.test-ok {
  background: #ecfdf5;
  color: #059669;
}

.test-fail {
  background: #fef2f2;
  color: #ef4444;
}

.test-detail {
  margin-top: 12px;
  color: #6b7280;
  font-size: 0.86rem;
  text-align: center;
}

.test-result { display: grid; gap: 4px; }

.report-wrap {
  display: grid;
  gap: 12px;
}

.report-actions {
  display: flex;
  justify-content: flex-end;
}

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

.report-empty {
  text-align: center;
  color: #9ca3af;
  padding: 24px;
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
  padding: 9px 16px;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  background: #fff;
  color: #374151;
  font-size: 0.88rem;
  cursor: pointer;
  transition: all 0.15s;
}

.btn-ghost:hover { border-color: #c4b5fd; background: #faf9fe; }

.btn-danger {
  padding: 9px 20px;
  border: 0;
  border-radius: 6px;
  background: #ef4444;
  color: #fff;
  font-size: 0.88rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s;
}

.btn-danger:hover:not(:disabled) { background: #dc2626; }
.btn-danger:disabled { opacity: 0.5; cursor: not-allowed; }

@media (max-width: 900px) {
  .shell { grid-template-columns: 1fr; }
  .sidebar {
    position: static;
    height: auto;
    border-right: 0;
    border-bottom: 1px solid #f3f4f6;
  }
  .topbar { flex-direction: column; align-items: stretch; }
}
</style>
