import { computed, onMounted, onUnmounted, ref } from 'vue'

export type RouteName = 'overview' | 'tasks' | 'knowledge' | 'tools' | 'llm'

export interface RouteItem {
  name: RouteName
  label: string
  hash: string
  description: string
}

export const routes: RouteItem[] = [
  { name: 'overview', label: '总览', hash: '#/overview', description: '快速进入各功能区' },
  { name: 'tasks', label: '任务中心', hash: '#/tasks', description: '发起安全测试任务并查看报告' },
  { name: 'knowledge', label: '知识库', hash: '#/knowledge', description: '浏览目录、上传与删除漏洞文档' },
  { name: 'tools', label: '工具台', hash: '#/tools', description: '管理安全工具列表' },
  { name: 'llm', label: '模型仓', hash: '#/llm', description: '管理 LLM 配置与连通性' },
]

function resolveRoute(hash: string): RouteName {
  const matched = routes.find((item) => item.hash === hash)
  return matched?.name ?? 'overview'
}

export function useHashRoute() {
  const current = ref<RouteName>(resolveRoute(window.location.hash))

  function syncFromLocation() {
    current.value = resolveRoute(window.location.hash)
  }

  function goTo(routeName: RouteName) {
    const target = routes.find((item) => item.name === routeName)
    if (!target) return
    if (window.location.hash === target.hash) {
      current.value = routeName
      return
    }
    window.location.hash = target.hash
  }

  onMounted(() => {
    if (!window.location.hash) {
      window.location.hash = '#/overview'
    }
    syncFromLocation()
    window.addEventListener('hashchange', syncFromLocation)
  })

  onUnmounted(() => {
    window.removeEventListener('hashchange', syncFromLocation)
  })

  return {
    currentRoute: computed(() => current.value),
    goTo,
  }
}
