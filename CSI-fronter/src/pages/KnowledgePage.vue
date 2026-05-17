<template>
  <section class="knowledge">
    <article class="k-main">
      <div class="k-header">
        <div>
          <h2>漏洞知识库</h2>
          <p class="k-sub" v-if="tree">{{ fileCount }} 个文件 &middot; {{ dirCount }} 个目录</p>
        </div>
        <div class="k-actions">
          <button class="btn-icon" data-tooltip="刷新" @click="$emit('refresh')">&#x21BB;</button>
          <button class="btn-icon" data-tooltip="上传文件" @click="$emit('open-upload')">+</button>
        </div>
      </div>

      <div v-if="loading" class="k-empty">加载中...</div>
      <div v-else-if="tree" class="k-tree">
        <KnowledgeTree
          :node="tree"
          :selected-dir="selectedFile?.directory"
          :selected-file="selectedFile?.fileName"
          @select-file="$emit('select-file', $event)"
        />
      </div>
      <div v-else class="k-empty">暂无知识库数据</div>
    </article>

    <article class="k-detail">
      <template v-if="selectedFile">
        <span class="detail-label">已选文件</span>
        <h3 class="detail-name">{{ selectedFile.fileName }}</h3>
        <p class="detail-path">{{ displayPath(selectedFile.directory) }}</p>
        <button class="btn-danger" data-tooltip="删除此文件" @click="$emit('open-delete')">&times;</button>
      </template>
      <div v-else class="k-empty">
        <p>点击左侧文件查看详情</p>
      </div>
    </article>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { KnowledgeTreeNode } from '@/api'
import KnowledgeTree from '@/components/KnowledgeTree.vue'

const props = defineProps<{
  tree: KnowledgeTreeNode | null
  selectedFile: { directory: string; fileName: string } | null
  loading: boolean
}>()

defineEmits<{
  refresh: []
  'open-upload': []
  'open-delete': []
  'select-file': [{ directory: string; fileName: string }]
}>()

function displayPath(fullPath: string): string {
  const idx = fullPath.indexOf('/CSI/')
  if (idx !== -1) return fullPath.slice(idx + 1)
  if (fullPath.startsWith('CSI/') || fullPath === 'CSI') return fullPath
  return fullPath
}

function count(node: KnowledgeTreeNode | null): { files: number; dirs: number } {
  if (!node) return { files: 0, dirs: 0 }
  let files = node.files.length
  let dirs = node.dirs.length
  for (const c of node.dirs) {
    const r = count(c)
    files += r.files
    dirs += r.dirs
  }
  return { files, dirs }
}

const fileCount = computed(() => count(props.tree).files)
const dirCount = computed(() => count(props.tree).dirs)
</script>

<style scoped>
.knowledge {
  display: grid;
  grid-template-columns: minmax(0, 1.5fr) 280px;
  gap: 20px;
}

.k-main,
.k-detail {
  border: 1px solid #f3f4f6;
  border-radius: 8px;
  background: #fff;
  padding: 20px;
}

.k-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 16px;
}

.k-header h2 {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 600;
  color: #111827;
}

.k-sub {
  margin: 4px 0 0;
  font-size: 0.78rem;
  color: #9ca3af;
}

.k-actions {
  display: flex;
  gap: 6px;
  flex-shrink: 0;
}

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

.btn-icon:hover {
  border-color: #7c3aed;
  color: #7c3aed;
  background: #faf9fe;
}

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

.k-tree {
  max-height: calc(100vh - 280px);
  overflow-y: auto;
}

.k-empty {
  padding: 32px 16px;
  text-align: center;
  color: #9ca3af;
  font-size: 0.88rem;
}

.k-detail {
  align-self: start;
}

.detail-label {
  font-size: 0.7rem;
  font-weight: 600;
  color: #9ca3af;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.detail-name {
  margin: 8px 0 4px;
  font-size: 0.95rem;
  font-weight: 600;
  color: #111827;
  word-break: break-all;
}

.detail-path {
  margin: 0 0 16px;
  font-size: 0.78rem;
  color: #9ca3af;
  word-break: break-all;
  line-height: 1.5;
}

.btn-danger {
  width: 32px;
  height: 32px;
  display: grid;
  place-items: center;
  border: 0;
  border-radius: 6px;
  background: #fef2f2;
  color: #ef4444;
  font-size: 1.2rem;
  cursor: pointer;
  transition: all 0.15s;
  position: relative;
}

.btn-danger:hover { background: #fee2e2; }

.btn-danger::after {
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

.btn-danger:hover::after { opacity: 1; }

@media (max-width: 860px) {
  .knowledge { grid-template-columns: 1fr; }
}
</style>
