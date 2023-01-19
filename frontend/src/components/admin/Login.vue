<template>
  <v-card class="mx-auto my-auto mt-16 px-6 py-8" max-width="400">
    <v-form
      ref="form"
      @submit.prevent="onSubmit"
    >
      <v-text-field
        v-model="data.email"
        :readonly="data.loading"
        :rules="[required()]"
        class="mb-2"
        label="Email"
      ></v-text-field>

      <v-text-field
        v-model="data.password"
        :readonly="data.loading"
        :rules="[required()]"
        label="Password"
        placeholder="Enter your password"
        :append-inner-icon="data.showPassword ? 'mdi-eye-off' : 'mdi-eye'"
        @click:append-inner="data.showPassword = !data.showPassword"
        :type="data.showPassword ? 'text' : 'password'"
        :error-messages="data.error"
      ></v-text-field>

      <br>

      <v-btn
        :loading="data.loading"
        block
        color="success"
        size="large"
        type="submit"
        variant="elevated"
      >
        Sign In
      </v-btn>
    </v-form>
  </v-card>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { required } from '@/validation'
import { useRouter } from 'vue-router'
import useURL from '@/composables/useURL'
import axios from 'axios'

const router = useRouter()
const { getParamsFromURL } = useURL()

const form = ref(null as any)
const data = reactive({
  form: false,
  email: '',
  password: '',
  loading: false,
  showPassword: false,
  error: ''
})
const onSubmit = async () => {
  const result = await form.value.validate()
  if (!result.valid) {
    return
  }

  data.loading = true

  const body = new FormData()
  body.append('username', data.email)
  body.append('password', data.password)

  try {
    const res = await axios.post('/user/login', body)
    localStorage.setItem('accesst', res.data.access_token)
    localStorage.setItem('refresht', res.data.refresh_token)

    const redirectPath = (getParamsFromURL().next || '/').toString()
    await router.push({ path: redirectPath })
  } catch (error: any) {
    if (error.response.data.detail) {
      data.error = error.response.data.detail
    } else {
      data.error = 'Something went wrong'
      console.log(error)
    }
  } finally {
    data.loading = false
  }
}
</script>
