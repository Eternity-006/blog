let runOnce = false

export function useCodeCopy() {
  if (runOnce) return
  runOnce = true

  // Inject styles once
  const style = document.createElement('style')
  style.textContent = `
    .code-block-wrapper { position: relative; }
    .code-block-wrapper .copy-btn {
      position: absolute; top: 8px; right: 8px;
      padding: 4px 8px; font-size: 12px;
      border-radius: 6px; border: none; cursor: pointer;
      background: rgba(255,255,255,0.1); color: #a0aec0;
      opacity: 0; transition: opacity 0.2s;
    }
    .code-block-wrapper:hover .copy-btn { opacity: 1; }
    .code-block-wrapper .copy-btn:hover { background: rgba(255,255,255,0.2); color: #fff; }
    .code-block-wrapper .copy-btn.copied { color: #68d391; }
  `
  document.head.appendChild(style)

  // Add copy buttons to all <pre><code> blocks
  document.querySelectorAll<HTMLElement>('.prose pre').forEach((pre) => {
    if (pre.querySelector('.copy-btn')) return
    const wrapper = document.createElement('div')
    wrapper.className = 'code-block-wrapper'
    pre.parentNode?.insertBefore(wrapper, pre)
    wrapper.appendChild(pre)

    const btn = document.createElement('button')
    btn.className = 'copy-btn'
    btn.textContent = '复制'
    btn.onclick = async () => {
      const code = pre.querySelector('code')?.textContent || ''
      try {
        await navigator.clipboard.writeText(code)
        btn.textContent = '已复制'
        btn.classList.add('copied')
        setTimeout(() => { btn.textContent = '复制'; btn.classList.remove('copied') }, 2000)
      } catch {
        btn.textContent = '复制失败'
        setTimeout(() => { btn.textContent = '复制' }, 2000)
      }
    }
    wrapper.appendChild(btn)
  })
}
