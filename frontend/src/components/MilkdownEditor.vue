<template>
  <MilkdownProvider>
    <EditorCore
      :modelValue="modelValue"
      @update:modelValue="(v: string) => emit('update:modelValue', v)"
      @image-uploading="emit('image-uploading')"
      @image-uploaded="(url: string) => emit('image-uploaded', url)"
    />
  </MilkdownProvider>
</template>

<script setup lang="ts">
import { MilkdownProvider } from '@milkdown/vue'
import EditorCore from './MilkdownEditorCore.vue'

defineProps<{ modelValue: string }>()

const emit = defineEmits<{
  'update:modelValue': [value: string]
  'image-uploading': []
  'image-uploaded': [url: string]
}>()
</script>
