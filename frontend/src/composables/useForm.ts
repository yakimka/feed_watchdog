import { computed, Ref, ref } from 'vue'
import { scrollToTop } from '@/utils/pageNavigation'
import Error from '@/types/error'

// eslint-disable-next-line @typescript-eslint/no-empty-function
export default function useForm (errors: Ref<Error[]>, onSubmit: (event: any) => Promise<void> = async () => {}) {
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

  const submit = async (event: any, formRef: any) => {
    if (!await isValid(formRef)) {
      scrollToTop()
      return
    }

    formIsLoading.value = true
    errors.value = []
    await formRef.value.resetValidation()
    await onSubmit(event)
    formIsLoading.value = false
    scrollToTop()
  }

  const isValid = async (formRef: any) => {
    if (formRef.value) {
      const result = await formRef.value.validate()
      return result.valid
    }
    return false
  }

  return {
    formErrors,
    formIsLoading,
    submit
  }
}
