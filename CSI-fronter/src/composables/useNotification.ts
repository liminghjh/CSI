import { ref } from 'vue'

const message = ref('')
const error = ref('')
let timer: ReturnType<typeof setTimeout> | null = null

export function useNotification() {
  function success(msg: string) {
    error.value = ''
    message.value = msg
    resetTimer()
  }

  function failure(msg: string) {
    message.value = ''
    error.value = msg
    resetTimer()
  }

  function clear() {
    message.value = ''
    error.value = ''
  }

  function resetTimer() {
    if (timer) clearTimeout(timer)
    timer = setTimeout(clear, 6000)
  }

  return { message, error, success, failure, clear }
}
