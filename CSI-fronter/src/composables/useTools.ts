import { ref } from 'vue'
import { fetchTools, createTool, removeTool, type ToolItem, type ToolForm } from '@/api'
import { useNotification } from './useNotification'

export function useTools() {
  const list = ref<ToolItem[]>([])
  const loading = ref(false)
  const submitting = ref(false)
  const selected = ref<ToolItem | null>(null)
  const { success, failure } = useNotification()

  async function refresh() {
    loading.value = true
    try {
      list.value = await fetchTools()
      if (selected.value) {
        selected.value = list.value.find((item) => item.id === selected.value?.id) ?? null
      }
    } catch (e) {
      failure(e instanceof Error ? e.message : '工具列表加载失败')
    } finally {
      loading.value = false
    }
  }

  async function add(form: ToolForm) {
    if (!form.tool_name) {
      failure('工具名称不能为空')
      return false
    }
    submitting.value = true
    try {
      await createTool(form)
      await refresh()
      success('工具新增成功')
      return true
    } catch (e) {
      failure(e instanceof Error ? e.message : '工具新增失败')
      return false
    } finally {
      submitting.value = false
    }
  }

  async function remove(id: number) {
    try {
      await removeTool(id)
      if (selected.value?.id === id) selected.value = null
      await refresh()
      success('工具已删除')
    } catch (e) {
      failure(e instanceof Error ? e.message : '工具删除失败')
    }
  }

  function select(tool: ToolItem) {
    selected.value = tool
  }

  return { list, loading, submitting, selected, refresh, add, remove, select }
}
