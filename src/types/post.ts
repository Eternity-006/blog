export interface PostMeta {
  slug: string
  title: string
  date: string
  category: string
  tags: string[]
  excerpt: string
  author?: string
  user_id?: number
  status?: string
}

export interface Post extends PostMeta {
  html: string
  content?: string
  views?: number
}
