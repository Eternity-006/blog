import MarkdownIt from 'markdown-it'
import hljs from 'highlight.js'

const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true,
  highlight(str: string, lang: string): string {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return hljs.highlight(str, { language: lang }).value
      } catch { /* fall through */ }
    }
    return ''
  },
})

export function renderMarkdown(content: string): string {
  return md.render(content)
}

export function extractHeadings(html: string): { id: string; text: string; level: number }[] {
  const headingRegex = /<h([1-3])[^>]*>(.*?)<\/h\1>/gi
  const headings: { id: string; text: string; level: number }[] = []
  let match: RegExpExecArray | null

  while ((match = headingRegex.exec(html)) !== null) {
    const text = match[2].replace(/<[^>]*>/g, '').trim()
    const id = text
      .toLowerCase()
      .replace(/[\s]+/g, '-')
      .replace(/[^a-z0-9一-鿿\-]/g, '')
    headings.push({ id, text, level: parseInt(match[1]) })
  }

  return headings
}

export function extractAllTags(posts: { tags: string[] }[]): string[] {
  const tagSet = new Set<string>()
  posts.forEach(p => p.tags.forEach(t => tagSet.add(t)))
  return [...tagSet].sort()
}

export function extractAllCategories(posts: { category: string }[]): string[] {
  const catSet = new Set<string>()
  posts.forEach(p => catSet.add(p.category))
  return [...catSet].sort()
}

export function estimateReadingTime(text: string): number {
  // Chinese: ~400 chars/min, English: ~200 words/min
  const chineseChars = (text.match(/[一-鿿]/g) || []).length
  const englishWords = (text.replace(/[一-鿿]/g, '').match(/[a-zA-Z]+/g) || []).length
  const minutes = Math.ceil(chineseChars / 400 + englishWords / 200)
  return Math.max(1, minutes)
}
