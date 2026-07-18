# SixthBlog

一个前后端分离的个人博客系统，前台纯展示，后台 Vue SPA 管理。

## 技术栈

| 层 | 技术 |
|----|------|
| 后端 | Django 6.0 + Django REST Framework + MySQL |
| 前端 | Vue 3 + TypeScript + Vite + Pinia + Vue Router |
| 样式 | CSS Variables 设计系统，亮/暗双主题，Inter 字体 |
| Markdown | marked + highlight.js（GFM + 代码高亮） |
| 部署 | Docker Compose（Nginx + Django + MySQL） |

## 项目结构

```
SixthBlog/
├── backend/                  # Django 后端
│   ├── config/               # 项目配置（settings, urls, wsgi）
│   ├── blog/                 # 博客应用（文章、评论、留言、站点配置）
│   │   ├── models.py
│   │   ├── views.py          # API 视图 + 管理端点
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── admin.py          # Django Admin 配置（已注册所有模型）
│   ├── users/                # 用户应用（登录、注册、角色、资料）
│   ├── templates/admin/      # Django Admin 自定义模板
│   └── static/admin/css/     # Django Admin 自定义样式
│
├── frontend/                 # Vue 3 前端
│   └── src/
│       ├── layouts/
│       │   ├── MainLayout.vue    # 前台布局（极简：Logo + 主题切换）
│       │   └── AdminLayout.vue   # 后台布局（侧边栏导航）
│       ├── views/
│       │   ├── Home.vue          # 首页（Hero + 分类筛选 + 文章卡片 + 统计）
│       │   ├── Articles.vue      # 文章列表（搜索、分类、排序）
│       │   ├── ArticleDetail.vue # 文章详情（Markdown 渲染 + 目录 + 评论 + 前/后篇）
│       │   ├── ArticleEditor.vue # 文章编辑器（Markdown 工具栏 + 预览 + 图片上传）
│       │   ├── ArticleManage.vue # 文章管理（状态筛选、置顶、删除）
│       │   ├── Diaries.vue       # 日记列表
│       │   ├── Archives.vue      # 归档页（按年月展开）
│       │   ├── About.vue         # 关于页
│       │   ├── Guestbook.vue     # 公开留言板
│       │   ├── GuestbookManage.vue # 留言审核
│       │   ├── CommentManage.vue   # 评论管理
│       │   ├── UserManage.vue     # 用户管理
│       │   ├── Profile.vue       # 个人资料
│       │   ├── Login.vue         # 登录
│       │   ├── Register.vue      # 注册
│       │   ├── NotFound.vue      # 404 页面
│       │   └── admin/Dashboard.vue # 后台仪表盘
│       ├── components/
│       │   ├── SplashScreen.vue  # 开屏动画（首次访问首页）
│       │   └── DesktopPet.vue    # 桌宠组件
│       ├── stores/               # Pinia 状态管理
│       ├── api/                  # Axios API 封装
│       ├── router/               # Vue Router 路由
│       ├── utils/request.ts      # Axios 实例（CSRF token 自动注入）
│       └── style.css             # 设计系统变量 + 全局样式
│
├── docker/                  # Docker 部署（docker-compose + Nginx + Dockerfiles）
├── history/                 # 开发历史记录（按序号归档）
├── requirements.txt         # Python 依赖
├── 方案.txt                 # 当前待办事项清单
├── 提示词                   # 给 AI 助手的指令
└── README.md
```

## 功能清单

### 前台（无需登录）
- 首页 — Hero Banner + 分类筛选 + 文章卡片 + 统计数据
- 文章列表 — 搜索 / 分类筛选 / 排序（最新/最热/最早）
- 文章详情 — Markdown 渲染 / 代码高亮 / 目录导航 / 评论 / 前一篇后一篇
- 日记 — 列表 + 详情
- 归档 — 按年月展开，点击查看文章
- 关于页 — Markdown 内容 + 社交链接
- 留言板 — 发表留言（需后台审核后显示）
- 暗色模式 — 手动切换 / 跟随系统
- 开屏动画 — 首次访问首页展示一次（同会话不重复）
- 404 页面

### 后台（`/sixth-admin`，需登录）
- 仪表盘 — 统计卡片 + 快捷操作 + 最近文章
- 文章管理 — 列表 / 搜索 / 状态筛选 / 发布 / 归档 / 草稿 / 置顶 / 删除
- 文章编辑器 — Markdown 工具栏 / 实时预览 / 粘贴图片上传 / 封面图上传
- 评论管理 — 审核通过 / 驳回 / 删除
- 留言审核 — 审核通过 / 驳回 / 删除
- 用户管理 — 创建 / 编辑 / 删除 / 角色分配
- 个人资料 — 头像 / 简介 / 邮箱 / 修改密码

## 快速开始

### 环境要求
- Python 3.12+
- Node.js 20+
- MySQL 8.0+

### 1. 克隆并配置数据库

```bash
git clone <repo-url>
cd SixthBlog
```

创建 MySQL 数据库：
```sql
CREATE DATABASE sixth_db CHARACTER SET utf8mb4;
CREATE USER 'Sixth_user'@'localhost' IDENTIFIED BY 'perry139140@';
GRANT ALL ON sixth_db.* TO 'Sixth_user'@'localhost';
```

> 数据库配置在 `backend/config/settings.py` 的 `DATABASES` 中。

### 2. 后端

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r ../requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

后端运行在 `http://localhost:8000`。

### 3. 前端

```bash
cd frontend
npm install
npm run dev
```

前端运行在 `http://localhost:5173`。

### 4. 访问

| 地址 | 说明 |
|------|------|
| `http://localhost:5173` | 博客前台 |
| `http://localhost:5173/sixth-admin` | 管理后台 |
| `http://localhost:8000/sixth-admin/` | Django Admin（备用） |

### Docker 部署

```bash
cd docker
docker-compose up -d
```

访问 `http://localhost` 即可。

## 设计系统

项目使用统一的 CSS 变量，前后台共享相同的设计语言：

```css
--accent: #6366f1;              /* Indigo 主色 */
--gradient-primary: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
--bg: #f1f5f9;                  /* 页面背景 */
--bg-card: #ffffff;             /* 卡片背景 */
--border: #e2e8f0;              /* 边框 */
--text: #475569;                /* 正文 */
--text-h: #0f172a;              /* 标题 */
--radius: 8px; --radius-lg: 12px; --radius-xl: 16px;
--shadow-md: 0 10px 15px -3px rgba(0,0,0,0.06);
```

暗色模式通过 `[data-theme="dark"]` 或系统 `prefers-color-scheme` 自动切换。

## API 概览

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/blog/articles/` | GET | 文章列表（支持 search/ordering/status/category/scope） |
| `/api/blog/articles/` | POST | 创建文章（需登录） |
| `/api/blog/articles/:id/` | GET/PATCH/DELETE | 文章详情/更新/删除 |
| `/api/blog/articles/:id/comments/` | GET/POST | 文章评论 |
| `/api/blog/categories/` | GET | 分类列表 |
| `/api/blog/tags/` | GET | 标签列表 |
| `/api/blog/guestbook/` | GET/POST | 公开留言板 |
| `/api/blog/diaries/` | GET | 日记列表 |
| `/api/blog/site-config/` | GET | 站点配置 |
| `/api/blog/menu-items/` | GET | 菜单项 |
| `/api/blog/upload-image/` | POST | 图片上传 |
| `/api/blog/admin/guestbook/` | GET/PATCH/DELETE | 留言管理（需登录） |
| `/api/blog/admin/comments/` | GET/PATCH/DELETE | 评论管理（需登录） |
| `/api/users/auth/login/` | POST | 登录 |
| `/api/users/auth/logout/` | POST | 登出 |
| `/api/users/auth/register/` | POST | 注册 |
| `/api/users/auth/user/` | GET | 当前用户信息 |
| `/api/users/auth/profile/` | PUT | 更新个人资料 |
| `/api/users/admin/users/` | GET/POST | 用户列表/创建（管理员） |
| `/api/users/admin/users/:id/` | GET/PUT/DELETE | 用户详情/更新/删除（管理员） |

## 配置项

### 环境变量
| 变量 | 说明 | 默认值 |
|------|------|--------|
| `DJANGO_SECRET_KEY` | Django 密钥 | 开发默认值（仅本地） |
| `DEBUG` | 调试模式 | `True` |

### 站点配置（数据库）
通过 Django Admin 或直接修改 `SiteConfig` 表：
- 网站标题/描述/Logo/Favicon
- 博客背景图
- 社交链接（JSON）
- 开屏动画文字/背景色/主题
- 随机问候语列表
- 每页文章数

## 开发说明

### 文章类型
- `article` — 博客文章（在前台展示）
- `diary` — 日记（在日记页展示）
- `about` — 关于页面内容

### 用户角色
- `admin` — 管理员（全部权限）
- `editor` — 编辑（管理文章、评论、留言）
- `author` — 作者（管理自己的文章）
- `subscriber` — 订阅者（仅前台功能）

### 注意事项
1. 文章编辑 API 使用 PATCH 进行局部更新，不要用 PUT
2. 请求默认带 `withCredentials: true`，CSRF token 由 axios 拦截器自动处理
3. 登录/注册接口已 `csrf_exempt`
4. 后台路由在 `/sixth-admin` 下，由 Vue Router 管理
5. 修改项目后请同步更新本 README 和 `方案.txt`
