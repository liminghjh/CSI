import { ref } from 'vue'
import type { KnowledgeTreeNode } from '@/api'
import { fetchKnowledgeTree, uploadKnowledgeFile, deleteKnowledgeFile } from '@/api'
import { useNotification } from './useNotification'

export function useKnowledge() {
  const tree = ref<KnowledgeTreeNode | null>(null)
  const loading = ref(false)
  const uploading = ref(false)
  const selectedFile = ref<{ directory: string; fileName: string } | null>(null)
  const uploadDir = ref('')
  const uploadFile = ref<File | null>(null)
  const { success, failure } = useNotification()

  async function refresh() {
    loading.value = true
    try {
      tree.value = await fetchKnowledgeTree()
    } catch (e) {
      failure(e instanceof Error ? e.message : '知识库加载失败')
    } finally {
      loading.value = false
    }
  }

  async function upload() {
    if (!uploadDir.value || !uploadFile.value) {
      failure('请填写目录并选择文件')
      return false
    }
    uploading.value = true
    try {
      const result = await uploadKnowledgeFile({ file_addr: uploadDir.value, file: uploadFile.value })
      await refresh()
      success(`${result.message}，新增 ${result.ids.length} 个向量片段`)
      return true
    } catch (e) {
      failure(e instanceof Error ? e.message : '上传失败')
      return false
    } finally {
      uploading.value = false
    }
  }

  async function remove() {
    if (!selectedFile.value) {
      failure('请先选择一个文件')
      return false
    }
    try {
      const result = await deleteKnowledgeFile({
        file_addr: selectedFile.value.directory,
        file_name: selectedFile.value.fileName,
      })
      selectedFile.value = null
      await refresh()
      success(result.message)
      return true
    } catch (e) {
      failure(e instanceof Error ? e.message : '删除失败')
      return false
    }
  }

  function selectFile(payload: { directory: string; fileName: string }) {
    selectedFile.value = payload
    uploadDir.value = payload.directory
  }

  function resetUpload() {
    uploadDir.value = selectedFile.value?.directory ?? ''
    uploadFile.value = null
  }

  function setUploadFile(file: File | null) {
    uploadFile.value = file
  }

  return { tree, loading, uploading, selectedFile, uploadDir, uploadFile, refresh, upload, remove, selectFile, resetUpload, setUploadFile }
}
