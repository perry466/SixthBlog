<template>
  <div class="milkdown-wrapper">
    <!-- 自定义工具栏 -->
    <div class="milkdown-toolbar">
      <div class="toolbar-group">
        <button @click="exec('ToggleBold')" title="粗体"><b>B</b></button>
        <button @click="exec('ToggleItalic')" title="斜体"><i>I</i></button>
        <button @click="exec('ToggleStrikethrough')" title="删除线"><s>S</s></button>
        <button @click="exec('ToggleInlineCode')" title="行内代码">&lt;/&gt;</button>
      </div>
      <div class="toolbar-divider"></div>
      <div class="toolbar-group">
        <button @click="exec('TurnIntoHeading', 1)" title="标题1">H1</button>
        <button @click="exec('TurnIntoHeading', 2)" title="标题2">H2</button>
        <button @click="exec('TurnIntoHeading', 3)" title="标题3">H3</button>
      </div>
      <div class="toolbar-divider"></div>
      <div class="toolbar-group">
        <button @click="exec('WrapInBlockquote')" title="引用">&ldquo;</button>
        <button @click="exec('WrapInBulletList')" title="无序列表">•≡</button>
        <button @click="exec('WrapInOrderedList')" title="有序列表">1.</button>
        <button @click="exec('CreateCodeBlock')" title="代码块">{ }</button>
        <button @click="exec('InsertHorizontalRule')" title="分割线">—</button>
        <button @click="exec('InsertTable', 3, 3)" title="插入表格">⊞</button>
      </div>
      <div class="toolbar-divider"></div>
      <div class="toolbar-group">
        <button @click="handleLinkClick" title="插入链接">🔗</button>
        <button @click="triggerImageUpload" title="上传图片">🖼</button>
      </div>
    </div>

    <!-- Milkdown 编辑器本体 -->
    <Milkdown />

    <!-- 隐藏的图片上传 input -->
    <input
      ref="imageInputRef"
      type="file"
      accept="image/*"
      hidden
      @change="handleToolbarImageUpload"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { Milkdown, useEditor } from '@milkdown/vue'
import { Editor, defaultValueCtx, rootCtx, commandsCtx, editorViewCtx, editorStateCtx } from '@milkdown/kit/core'
import { commonmark } from '@milkdown/kit/preset/commonmark'
import { gfm } from '@milkdown/kit/preset/gfm'
import { history } from '@milkdown/kit/plugin/history'
import { clipboard } from '@milkdown/kit/plugin/clipboard'
import { cursor } from '@milkdown/kit/plugin/cursor'
import { indent } from '@milkdown/kit/plugin/indent'
import { listener, listenerCtx } from '@milkdown/kit/plugin/listener'
import { prism } from '@milkdown/plugin-prism'
import { nord } from '@milkdown/theme-nord'
import '@milkdown/theme-nord/style.css'
import { replaceAll } from '@milkdown/utils'
import { uploadImage } from '../api/user'

const props = defineProps<{ modelValue: string }>()

const emit = defineEmits<{
  'update:modelValue': [value: string]
  'image-uploading': []
  'image-uploaded': [url: string]
}>()

const imageInputRef = ref<HTMLInputElement | null>(null)

// ===== 创建 Milkdown 编辑器 =====
const { loading, get: getEditor } = useEditor((container: HTMLDivElement) => {
  return Editor.make()
    .config((ctx) => {
      ctx.set(rootCtx, container)
      ctx.set(defaultValueCtx, props.modelValue)
      // 配置 markdown 变更监听
      ctx.get(listenerCtx).markdownUpdated((_ctx: any, markdown: string) => {
        emit('update:modelValue', markdown)
      })
    })
    .use(commonmark)
    .use(gfm)
    .use(history)
    .use(clipboard)
    .use(cursor)
    .use(indent)
    .use(prism)
    .use(nord)
    .use(listener)
    .create()
})

// ===== 命令执行 =====
function exec(command: string, ...args: any[]) {
  const editor = getEditor()
  if (!editor) return
  editor.action((ctx) => {
    const cmds = ctx.get(commandsCtx)
    if (cmds && typeof (cmds as any).call === 'function') {
      ;(cmds as any).call(command, ...args)
    }
  })
}

// ===== 链接 =====
function handleLinkClick() {
  const url = prompt('请输入链接地址:')
  if (!url) return
  const text = prompt('请输入链接文本:', url) || url
  const editor = getEditor()
  if (!editor) return
  editor.action((ctx) => {
    const view = ctx.get(editorViewCtx)
    const state = ctx.get(editorStateCtx)
    if (!view || !state) return
    const { from, to } = state.selection
    const schema = state.schema
    const linkMark = schema.marks.link.create({ href: url })
    if (from !== to) {
      const tr = state.tr.addMark(from, to, linkMark)
      view.dispatch(tr)
    } else {
      const node = schema.text(text, [linkMark])
      const tr = state.tr.insert(from, node)
      view.dispatch(tr)
    }
  })
}

// ===== 图片上传 =====
function triggerImageUpload() {
  imageInputRef.value?.click()
}

async function handleToolbarImageUpload(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file) return

  emit('image-uploading')
  try {
    const res = (await uploadImage(file)) as any
    emit('image-uploaded', res.url)

    const editor = getEditor()
    if (!editor) return
    editor.action((ctx) => {
      const view = ctx.get(editorViewCtx)
      const state = ctx.get(editorStateCtx)
      if (!view || !state) return

      const schema = state.schema
      const imageNode = schema.nodes.image.create({
        src: res.url,
        alt: file.name,
        title: file.name,
      })
      const tr = state.tr.replaceSelectionWith(imageNode)
      view.dispatch(tr)
    })
  } catch {
    // 父组件处理错误
  }

  if (imageInputRef.value) {
    imageInputRef.value.value = ''
  }
}

// ===== 外部内容同步（恢复草稿 / 加载已有文章） =====
let updatingFromParent = false

watch(
  () => props.modelValue,
  (newVal) => {
    if (updatingFromParent) return
    const editor = getEditor()
    if (!editor) return

    let current = ''
    try {
      editor.action((ctx) => {
        const view = ctx.get(editorViewCtx)
        if (view) {
          current = view.state.doc.textContent || ''
        }
      })
    } catch {
      // ignore
    }

    if (newVal !== current && newVal) {
      updatingFromParent = true
      editor.action(replaceAll(newVal))
      setTimeout(() => { updatingFromParent = false }, 50)
    }
  }
)

// ===== 生命周期 =====
let initSyncRan = false

onMounted(() => {
  const unwatch = watch(loading, (isLoading) => {
    if (!isLoading && !initSyncRan) {
      initSyncRan = true
      unwatch()
      setTimeout(() => {
        const editor = getEditor()
        if (editor && props.modelValue) {
          editor.action(replaceAll(props.modelValue))
        }
      }, 100)
    }
  }, { immediate: true })
})
</script>

<style scoped>
/* ===== 外层容器 ===== */
.milkdown-wrapper {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

/* ===== 工具栏 ===== */
.milkdown-toolbar {
  display: flex;
  align-items: center;
  gap: 2px;
  padding: 6px 16px;
  background: var(--bg-subtle);
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
  overflow-x: auto;
  white-space: nowrap;
}

.toolbar-group {
  display: flex;
  align-items: center;
  gap: 2px;
}

.milkdown-toolbar button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 32px;
  height: 30px;
  padding: 0 8px;
  border: none;
  border-radius: 4px;
  background: transparent;
  color: var(--text);
  font-family: var(--heading);
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
  white-space: nowrap;
}

.milkdown-toolbar button:hover {
  background: var(--accent-bg);
  color: var(--accent);
}

.toolbar-divider {
  width: 1px;
  height: 20px;
  background: var(--border);
  margin: 0 6px;
  flex-shrink: 0;
}

/* ===== Milkdown 编辑器区域 ===== */
.milkdown-wrapper :deep(.milkdown) {
  flex: 1;
  overflow-y: auto;
  background: var(--bg-card);
}

.milkdown-wrapper :deep(.editor) {
  padding: 20px 24px;
  font-size: 0.875rem;
  line-height: 1.75;
  color: var(--text-h);
  outline: none;
  min-height: 100%;
  font-family: var(--sans);
}

.milkdown-wrapper :deep(.ProseMirror) {
  outline: none;
  min-height: 300px;
  caret-color: var(--text-h);
}

.milkdown-wrapper :deep(.ProseMirror:focus) {
  outline: none;
}

.milkdown-wrapper :deep(.ProseMirror) > * + * {
  margin-top: 0.5em;
}

/* 标题 */
.milkdown-wrapper :deep(h1) {
  font-size: 1.6rem;
  font-weight: 700;
  color: var(--text-h);
  margin: 1.2em 0 0.5em;
}
.milkdown-wrapper :deep(h2) {
  font-size: 1.35rem;
  font-weight: 650;
  color: var(--text-h);
  margin: 1em 0 0.4em;
}
.milkdown-wrapper :deep(h3) {
  font-size: 1.15rem;
  font-weight: 600;
  color: var(--text-h);
  margin: 0.8em 0 0.3em;
}

/* 段落 */
.milkdown-wrapper :deep(p) {
  margin: 0.5em 0;
  color: var(--text);
}

/* 粗体/斜体/删除线 */
.milkdown-wrapper :deep(strong) { font-weight: 700; color: var(--text-h); }
.milkdown-wrapper :deep(em) { font-style: italic; }
.milkdown-wrapper :deep(s) { text-decoration: line-through; color: var(--text-muted); }

/* 链接 */
.milkdown-wrapper :deep(a) {
  color: var(--accent);
  text-decoration: underline;
}

/* 引用 */
.milkdown-wrapper :deep(blockquote) {
  border-left: 3px solid var(--accent);
  padding: 6px 16px;
  margin: 0.75em 0;
  color: var(--text-muted);
  background: var(--bg-subtle);
  border-radius: 0 var(--radius) var(--radius) 0;
}

/* 列表 */
.milkdown-wrapper :deep(ul),
.milkdown-wrapper :deep(ol) {
  padding-left: 1.5em;
  margin: 0.4em 0;
}

.milkdown-wrapper :deep(li) {
  margin: 0.2em 0;
}

/* 代码 */
.milkdown-wrapper :deep(code) {
  background: var(--code-bg);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: var(--mono);
  font-size: 0.82rem;
}

.milkdown-wrapper :deep(pre) {
  background: var(--code-bg);
  padding: 12px 16px;
  border-radius: var(--radius);
  overflow-x: auto;
  margin: 0.75em 0;
}

.milkdown-wrapper :deep(pre code) {
  background: none;
  padding: 0;
  border-radius: 0;
  font-size: 0.82rem;
  line-height: 1.6;
}

/* 表格 */
.milkdown-wrapper :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin: 0.75em 0;
  font-size: 0.85rem;
}

.milkdown-wrapper :deep(th),
.milkdown-wrapper :deep(td) {
  border: 1px solid var(--border);
  padding: 8px 12px;
  text-align: left;
}

.milkdown-wrapper :deep(th) {
  background: var(--bg-subtle);
  font-weight: 650;
  color: var(--text-h);
}

/* 图片 */
.milkdown-wrapper :deep(img) {
  max-width: 100%;
  height: auto;
  border-radius: var(--radius);
  margin: 0.5em 0;
}

/* 分割线 */
.milkdown-wrapper :deep(hr) {
  border: none;
  border-top: 1px solid var(--border);
  margin: 1.5em 0;
}

/* 任务列表 */
.milkdown-wrapper :deep(input[type="checkbox"]) {
  margin-right: 6px;
  accent-color: var(--accent);
}

/* ===== 暗色模式适配 ===== */
[data-theme="dark"] .milkdown-wrapper :deep(blockquote) {
  background: rgba(255, 255, 255, 0.03);
}

/* ===== 响应式 ===== */
@media (max-width: 768px) {
  .milkdown-toolbar {
    padding: 6px 10px;
  }

  .milkdown-wrapper :deep(.editor) {
    padding: 14px 16px;
    font-size: 0.85rem;
  }
}
</style>
