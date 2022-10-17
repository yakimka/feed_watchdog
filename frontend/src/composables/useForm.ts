import { computed, Ref, ref } from 'vue'
import { scrollToTop } from '@/utils/pageNavigation'
import Error from '@/types/error'

// eslint-disable-next-line @typescript-eslint/no-empty-function
export default function useForm (errors: Ref<Error[]>, onSubmit: (event: any) => Promise<void> = async () => {}) {
  const form = ref(null as any)
  const formIsLoading = ref(true)

  const formErrors = computed(() => {
    const result: { [key: string ]: string} = {}
    for (const error of errors.value) {
      if (!error.field) {
        result.nonFieldError = error.message
      } else {
        result[error.field] = error.message
      }
    }
    return result
  })

  const submit = async (event: any) => {
    if (!await isValid()) {
      scrollToTop()
      return
    }

    formIsLoading.value = true
    errors.value = []
    await form.value.resetValidation()
    await onSubmit(event)
    formIsLoading.value = false
    scrollToTop()
  }

  const isValid = async () => {
    if (form.value) {
      const result = await form.value.validate()
      return result.valid
    }
    return false
  }

  return {
    form,
    formErrors,
    formIsLoading,
    submit
  }
}
