import { shallowMount } from '@vue/test-utils'
import JsonField from '@/components/JsonField.vue'

describe('JsonField.vue', () => {
  it('renders field name', () => {
    const wrapper = shallowMount(JsonField, {
      props: { name: 'MyName' }
    })
    expect(wrapper.text()).toMatch('MyName')
  })
})
