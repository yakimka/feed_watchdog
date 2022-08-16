import { ref } from 'vue'

export const navigation = ref({
  isLeftSideBarOpen: true,
  toggleLeftSideBar () {
    this.isLeftSideBarOpen = !this.isLeftSideBarOpen
  }
})
