export interface PostMeta {
  slug: string
  title: string
  date: string
  category: string
  tags: string[]
  excerpt: string
  cover_image?: string
  pinned?: boolean
  author?: string
  user_id?: number
  status?: string
  is_favorited?: boolean
  favorite_count?: number
}

export interface Post extends PostMeta {
  html: string
  content?: string
  views?: number
}

export interface PaginatedResponse<T> {
  posts: T[]
  total: number
  page: number
  per_page: number
  total_pages: number
}
