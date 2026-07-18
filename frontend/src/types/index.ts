// 分类
export interface Category {
  id: number
  name: string
  slug: string
  description: string
  parent: number | null
  order: number
  article_count: number
  children: Category[]
}

// 标签
export interface Tag {
  id: number
  name: string
  slug: string
}

// 文章列表项
export interface ArticleList {
  id: number
  title: string
  slug: string
  summary: string
  cover_image: string | null
  category: number | null
  category_name: string
  tags: Tag[]
  view_count: number
  word_count: number
  status: string
  article_type: string
  is_featured: boolean
  created_at: string
  updated_at: string
  published_at: string
  comment_count: number
}

// 文章详情
export interface ArticleDetail extends ArticleList {
  content: string
  seo_title: string
  seo_description: string
  author_name: string
  comments: Comment[]
  table_of_contents: TocItem[]
}

// 目录项
export interface TocItem {
  level: number
  text: string
  id: string
}

// 评论
export interface Comment {
  id: number
  article: number
  nickname: string
  email: string
  content: string
  parent: number | null
  replies: Comment[]
  created_at: string
}

// 站点配置
export interface SiteConfig {
  id: number
  site_title: string
  site_description: string
  site_logo: string | null
  site_favicon: string | null
  blog_background: string | null
  about_content: string
  social_links: Record<string, string>
  welcome_messages: string[]
  splash_animation_text: string
  splash_animation_bg: string
  splash_animation_theme: string
  articles_per_page: number
  show_article_stats: boolean
}

// 菜单项
export interface MenuItem {
  id: number
  name: string
  url: string
  icon: string
  order: number
  is_active: boolean
  parent: number | null
  children: MenuItem[]
}

// 留言板
export interface Guestbook {
  id: number
  nickname: string
  email: string
  content: string
  created_at: string
}

// 用户
export interface User {
  id: number
  username: string
  email: string
  is_staff: boolean
  is_superuser: boolean
  role: string
  date_joined: string
}

// 分页响应
export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}
