import { ref } from 'vue'
import { fetchLlms, createLlm, removeLlm, testLlm, type LlmItem, type LlmForm } from '@/api'
import { useNotification } from './useNotification'

export function useLlms() {
  const list = ref<LlmItem[]>([])
  const loading = ref(false)
  const submitting = ref(false)
  const selected = ref<LlmItem | null>(null)
  const selectedId = ref<number | null>(null)
  const { success, failure } = useNotification()

  async function refresh() {
    loading.value = true
    try {
      list.value = await fetchLlms()
      if (selected.value) {
        selected.value = list.value.find((item) => item.id === selected.value?.id) ?? null
      }
      const first = list.value[0]
      if (first) {
        if (!selectedId.value) selectedId.value = first.id
        if (!selected.value) selected.value = first
      }
    } catch (e) {
      failure(e instanceof Error ? e.message : '模型列表加载失败')
    } finally {
      loading.value = false
    }
  }

  async function add(form: LlmForm) {
    if (!form.name || !form.provider || !form.url || !form.model) {
      failure('名称、提供商、地址、模型名称不能为空')
      return false
    }
    submitting.value = true
    try {
      await createLlm(form)
      await refresh()
      success('模型配置新增成功')
      return true
    } catch (e) {
      failure(e instanceof Error ? e.message : '模型配置新增失败')
      return false
    } finally {
      submitting.value = false
    }
  }

  async function remove(id: number) {
    try {
      await removeLlm(id)
      if (selected.value?.id === id) selected.value = null
      if (selectedId.value === id) selectedId.value = null
      await refresh()
      success('模型配置已删除')
    } catch (e) {
      failure(e instanceof Error ? e.message : '模型配置删除失败')
    }
  }

  async function test(id: number) {
    try {
      const ok = await testLlm(id)
      success(ok ? '连接成功' : '连接失败')
    } catch (e) {
      failure(e instanceof Error ? e.message : '模型测试失败')
    }
  }

  function select(item: LlmItem) {
    selected.value = item
  }

  return { list, loading, submitting, selected, selectedId, refresh, add, remove, test, select }
}
