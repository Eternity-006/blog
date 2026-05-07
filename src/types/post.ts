export interface PostMeta {
  slug: string
  title: string
  date: string
  category: string
  tags: string[]
  excerpt: string
}

export interface Post extends PostMeta {
  html: string
}
