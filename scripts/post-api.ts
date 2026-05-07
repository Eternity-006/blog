import type { Plugin } from 'vite'
import fs from 'fs'
import path from 'path'

export function postApi(): Plugin {
  return {
    name: 'post-api',
    configureServer(server) {
      // Save post (create or update)
      server.middlewares.use('/api/save-post', (req, res) => {
        if (req.method !== 'POST') {
          res.statusCode = 405
          res.end(JSON.stringify({ error: 'Method not allowed' }))
          return
        }

        let body = ''
        req.on('data', chunk => { body += chunk })
        req.on('end', () => {
          try {
            const { slug, content } = JSON.parse(body)
            if (!slug || !content) {
              res.statusCode = 400
              res.end(JSON.stringify({ error: 'slug and content are required' }))
              return
            }

            // Security: only allow alphanumeric, hyphens, underscores
            const safeSlug = slug.replace(/[^a-zA-Z0-9\-_]/g, '-')
            const postsDir = path.resolve(process.cwd(), 'posts')
            const filePath = path.join(postsDir, `${safeSlug}.md`)

            fs.writeFileSync(filePath, content, 'utf-8')

            res.setHeader('Content-Type', 'application/json')
            res.end(JSON.stringify({ ok: true, slug: safeSlug }))
          } catch (e) {
            res.statusCode = 500
            res.end(JSON.stringify({ error: String(e) }))
          }
        })
      })

      // List existing slugs (for edit mode)
      server.middlewares.use('/api/list-posts', (_req, res) => {
        try {
          const postsDir = path.resolve(process.cwd(), 'posts')
          const files = fs.readdirSync(postsDir)
            .filter(f => f.endsWith('.md'))

          const posts = files.map(f => {
            const slug = f.replace(/\.md$/, '')
            const raw = fs.readFileSync(path.join(postsDir, f), 'utf-8')
            // extract just the frontmatter title
            const match = raw.match(/^---\s*\ntitle:\s*"(.+?)"/m)
            return { slug, title: match?.[1] || slug }
          })

          res.setHeader('Content-Type', 'application/json')
          res.end(JSON.stringify(posts))
        } catch (e) {
          res.statusCode = 500
          res.end(JSON.stringify({ error: String(e) }))
        }
      })

      // Get a single post's raw markdown
      server.middlewares.use('/api/get-post', (req, res) => {
        const url = new URL(req.url!, `http://${req.headers.host}`)
        const slug = url.searchParams.get('slug')
        if (!slug) {
          res.statusCode = 400
          res.end(JSON.stringify({ error: 'slug required' }))
          return
        }

        try {
          const postsDir = path.resolve(process.cwd(), 'posts')
          const filePath = path.join(postsDir, `${slug}.md`)
          if (!fs.existsSync(filePath)) {
            res.statusCode = 404
            res.end(JSON.stringify({ error: 'Post not found' }))
            return
          }
          const content = fs.readFileSync(filePath, 'utf-8')
          res.setHeader('Content-Type', 'application/json')
          res.end(JSON.stringify({ slug, content }))
        } catch (e) {
          res.statusCode = 500
          res.end(JSON.stringify({ error: String(e) }))
        }
      })
    },
  }
}
