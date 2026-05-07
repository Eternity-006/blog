import fs from 'fs'
import path from 'path'
import matter from 'gray-matter'
import MarkdownIt from 'markdown-it'
import hljs from 'highlight.js'
import { fileURLToPath } from 'url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const postsDir = path.resolve(__dirname, '../posts')
const outputFile = path.resolve(__dirname, '../public/posts-index.json')

const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true,
  highlight(str: string, lang: string): string {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return hljs.highlight(str, { language: lang }).value
      } catch {
        // fall through
      }
    }
    return ''
  },
})

interface PostEntry {
  slug: string
  title: string
  date: string
  category: string
  tags: string[]
  excerpt: string
  html: string
}

const files = fs.readdirSync(postsDir).filter(f => f.endsWith('.md'))

const posts: PostEntry[] = files.map(file => {
  const raw = fs.readFileSync(path.join(postsDir, file), 'utf-8')
  const { data, content } = matter(raw)
  const slug = file.replace(/\.md$/, '')
  const html = md.render(content)

  return {
    slug,
    title: data.title || slug,
    date: data.date || '1970-01-01',
    category: data.category || 'Uncategorized',
    tags: data.tags || [],
    excerpt: data.excerpt || '',
    html,
  }
})

posts.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())

fs.writeFileSync(outputFile, JSON.stringify(posts, null, 2))
console.log(`Generated posts-index.json with ${posts.length} posts.`)

// Generate RSS
const SITE_URL = 'https://yourblog.vercel.app'
const rssFile = path.resolve(__dirname, '../public/rss.xml')

const rssItems = posts.map(p => `
    <item>
      <title><![CDATA[${p.title}]]></title>
      <link>${SITE_URL}/post/${p.slug}</link>
      <guid>${SITE_URL}/post/${p.slug}</guid>
      <pubDate>${new Date(p.date).toUTCString()}</pubDate>
      <category>${p.category}</category>
      <description><![CDATA[${p.excerpt}]]></description>
    </item>`).join('')

const rssXml = `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>我的博客</title>
    <link>${SITE_URL}</link>
    <description>记录前端开发与技术探索</description>
    <language>zh-CN</language>
    <atom:link href="${SITE_URL}/rss.xml" rel="self" type="application/rss+xml"/>
    ${rssItems}
  </channel>
</rss>`

fs.writeFileSync(rssFile, rssXml)
console.log(`Generated rss.xml.`)
