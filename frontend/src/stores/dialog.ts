import { reactive } from 'vue'

export const dialog = reactive({
  isActive: false,
  title: '',
  text: '',
  close () {
    this.isActive = false
  },
  set (text: string, title = '') {
    this.title = title
    this.text = text
    this.isActive = true
  }
})
