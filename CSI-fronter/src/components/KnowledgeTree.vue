<template>
  <div class="tree-node">
    <div class="tree-folder">
      <button class="folder-header" type="button" @click="expanded = !expanded">
        <span class="folder-icon">{{ expanded ? '&#9660;' : '&#9654;' }}</span>
        <div class="folder-info">
          <span class="folder-path">{{ displayPath(node.path_name) }}</span>
          <span class="folder-meta">{{ node.dirs.length }} dirs &middot; {{ node.files.length }} files</span>
        </div>
      </button>

      <div v-if="expanded" class="folder-body">
        <div v-if="node.files.length" class="file-list">
          <button
            v-for="file in node.files"
            :key="file"
            class="file-chip"
            :class="{ active: isActive(node.path_name, file) }"
            type="button"
            @click="$emit('select-file', { directory: node.path_name, fileName: file })"
          >
            <span class="file-icon">&#x1F4C4;</span>
            <span class="file-name">{{ file }}</span>
          </button>
        </div>

        <div v-if="node.dirs.length" class="child-tree">
          <KnowledgeTree
            v-for="child in node.dirs"
            :key="child.path_name"
            :node="child"
            :selected-dir="selectedDir"
            :selected-file="selectedFile"
            @select-file="$emit('select-file', $event)"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { KnowledgeTreeNode } from '@/api'

const props = defineProps<{
  node: KnowledgeTreeNode
  selectedDir?: string
  selectedFile?: string
}>()

defineEmits<{
  'select-file': [{ directory: string; fileName: string }]
}>()

const expanded = ref(true)

function displayPath(fullPath: string): string {
  const idx = fullPath.indexOf('/CSI/')
  if (idx !== -1) return fullPath.slice(idx + 1)
  if (fullPath.startsWith('CSI/') || fullPath === 'CSI') return fullPath
  return fullPath
}

function isActive(dir: string, file: string) {
  return props.selectedDir === dir && props.selectedFile === file
}
</script>

<style scoped>
.tree-node {
  padding-left: 0;
}

.tree-folder {
  border: 1px solid #f3f4f6;
  border-radius: 8px;
  background: #fff;
  margin-bottom: 6px;
  transition: border-color 0.15s;
}

.tree-folder:hover {
  border-color: #e5e7eb;
}

.folder-header {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  border: 0;
  background: transparent;
  text-align: left;
  cursor: pointer;
  border-radius: 8px;
}

.folder-header:hover {
  background: #fafbfc;
}

.folder-icon {
  color: #7c3aed;
  font-size: 0.6rem;
  flex-shrink: 0;
  width: 14px;
  text-align: center;
  transition: transform 0.15s;
}

.folder-info {
  min-width: 0;
}

.folder-path {
  display: block;
  font-weight: 600;
  font-size: 0.9rem;
  color: #111827;
  word-break: break-all;
}

.folder-meta {
  display: block;
  margin-top: 2px;
  font-size: 0.75rem;
  color: #9ca3af;
}

.folder-body {
  padding: 0 14px 12px;
}

.file-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 10px;
}

.file-chip {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 5px 10px;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  background: #fafbfc;
  color: #374151;
  font-size: 0.82rem;
  cursor: pointer;
  transition: all 0.15s;
}

.file-chip:hover {
  border-color: #c4b5fd;
  background: #f5f3ff;
  color: #6d28d9;
}

.file-chip.active {
  border-color: #7c3aed;
  background: rgba(124, 58, 237, 0.06);
  color: #7c3aed;
}

.file-icon {
  font-size: 0.8rem;
}

.file-name {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.child-tree {
  padding-left: 16px;
}
</style>
