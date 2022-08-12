import {ref} from "vue";

export const navigation = ref({
    isLeftSideBarOpen: false,
    toggleLeftSideBar() {
        this.isLeftSideBarOpen = !this.isLeftSideBarOpen;
    },
});
