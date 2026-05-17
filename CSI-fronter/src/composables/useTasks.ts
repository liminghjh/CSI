import { ref } from 'vue'
import { startTaskStream } from '@/api'
import type { SseTaskEvent } from '@/api'
import { useNotification } from './useNotification'

export function useTasks() {
  const urlOrIp = ref('')
  const port = ref<number | null>(null)
  const systemDoc = ref(0)
  const report = ref('')
  const running = ref(false)
  const error = ref('')
  const log = ref<SseTaskEvent[]>([])
  const { success, failure } = useNotification()

  async function run(llmId: number | null) {
    error.value = ''
    log.value = []
    report.value = ''

    if (!urlOrIp.value.trim()) {
      error.value = '请填写目标地址'
      return false
    }
    if (!llmId) {
      error.value = '请选择一个模型配置'
      return false
    }

    running.value = true
    try {
      const stream = startTaskStream({
        url_or_ip: urlOrIp.value.trim(),
        port: port.value,
        LLM_id: llmId,
        system_doc: systemDoc.value,
      })

      for await (const event of stream) {
        log.value.push(event)

        if (event.type === 'report') {
          report.value = event.message
        } else if (event.type === 'error') {
          throw new Error(event.message)
        }
      }

      if (!report.value) {
        throw new Error('任务结束但未收到报告')
      }

      success('任务已完成，报告已生成')
      return true
    } catch (e) {
      const msg = e instanceof Error ? e.message : '任务执行失败'
      error.value = msg
      failure(msg)
      return false
    } finally {
      running.value = false
    }
  }

  return { urlOrIp, port, systemDoc, report, running, error, log, run }
}
