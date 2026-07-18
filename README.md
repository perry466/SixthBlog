# SixthBlog

前后端分离的个人博客系统。Vue 3 前台 + Django REST 后端 + MySQL。

## 技术栈

| 层 | 技术 |
|----|------|
| 后端 | Django 6.0 + Django REST Framework + MySQL |
| 前端 | Vue 3 + TypeScript + Vite + Pinia + Vue Router |
| 样式 | CSS Variables + 亮/暗双主题 |
| Markdown | marked |
| 部署 | Docker Compose（Nginx + Django + MySQL） |

## 项目结构

```
SixthBlog/
├── backend/
│   ├── config/           # Django 配置
│   ├── blog/             # 博客应用（文章/分类/标签/评论/留言/菜单/站点配置）
│   ├── users/            # 用户应用（登录/注册/角色/资料）
│   ├── templates/admin/  # Django Admin 模板覆盖
│   └── static/admin/css/ # Django Admin 样式覆盖
├── frontend/
│   └── src/
│       ├── layouts/      # MainLayout（前台）/ AdminLayout（后台）
│       ├── views/        # 页面组件
│       │   └── admin/    # 后台仪表盘
│       ├── components/   # 公共组件（开屏动画/桌宠）
│       ├── stores/       # Pinia 状态
│       ├── api/          # Axios 请求封装
│       ├── router/       # 路由
│       └── utils/        # 工具函数（Axios 实例/CSRF）
├── docker/               # Docker 部署配置
└── requirements.txt
```

## 功能

### 前台
- 文章列表：分类筛选、搜索、排序、分页
- 文章详情：Markdown 渲染、目录、评论、上/下篇
- 日记列表与详情
- 归档页：按年月分组
- 关于页：Markdown 内容 + 社交链接
- 留言板：提交留言（审核后显示）
- 导航栏：下拉菜单，支持多分类子菜单
- 暗色模式（手动/跟随系统）
- 开屏动画

### 后台（`/sixth-admin`）
- 仪表盘：统计概览
- 文章管理：列表/搜索/筛选/置顶/删除，Markdown 编辑器 + 预览
- 评论管理：审核/删除
- 留言审核：审核/删除
- 分类管理：CRUD + 层级结构
- 菜单管理：树形结构，关联分类自动生成下拉子菜单
- 站点设置：标题/Logo/Favicon/背景/社交链接/问候语/开屏动画/关于内容
- 用户管理：CRUD + 角色分配
- 个人资料：修改密码/信息

## 快速开始

### 环境要求
- Python 3.12+
- Node.js 20+
- MySQL 8.0+

### 1. 数据库

```sql
CREATE DATABASE sixth_db CHARACTER SET utf8mb4;
CREATE USER 'Sixth_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL ON sixth_db.* TO 'Sixth_user'@'localhost';
```

### 2. 环境变量

在 `backend/` 目录创建 `.env` 文件：

```env
DJANGO_SECRET_KEY=your-secret-key
DB_NAME=sixth_db
DB_USER=Sixth_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306
```

### 3. 后端

```bash
cd backend
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r ../requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

后端运行在 `http://localhost:8000`。

### 4. 前端

```bash
cd frontend
npm install
npm run dev
```

前端运行在 `http://localhost:5173`。

### 5. Docker 部署

```bash
cd docker
docker-compose up -d
```

## API

### 公开接口

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/blog/articles/` | GET | 文章列表（`?search=&category_slug=&ordering=`） |
| `/api/blog/articles/:id/` | GET | 文章详情 |
| `/api/blog/articles/:id/comments/` | GET/POST | 文章评论 |
| `/api/blog/articles/archives/` | GET | 归档 |
| `/api/blog/articles/stats/` | GET | 统计 |
| `/api/blog/categories/` | GET | 分类列表 |
| `/api/blog/tags/` | GET | 标签列表 |
| `/api/blog/menu-items/` | GET | 菜单（含层级） |
| `/api/blog/guestbook/` | GET/POST | 留言板 |
| `/api/blog/diaries/` | GET | 日记列表 |
| `/api/blog/about/` | GET | 关于页面 |
| `/api/blog/site-config/` | GET | 站点配置 |
| `/api/users/auth/login/` | POST | 登录 |
| `/api/users/auth/logout/` | POST | 登出 |
| `/api/users/auth/register/` | POST | 注册 |

### 管理接口（需登录）

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/blog/articles/` | POST | 创建文章 |
| `/api/blog/articles/:id/` | PATCH/DELETE | 更新/删除文章 |
| `/api/blog/upload-image/` | POST | 上传图片 |
| `/api/blog/admin/categories/` | GET/POST | 分类管理 |
| `/api/blog/admin/categories/:id/` | PATCH/DELETE | 更新/删除分类 |
| `/api/blog/admin/menu-items/` | GET/POST | 菜单管理 |
| `/api/blog/admin/menu-items/:id/` | PATCH/DELETE | 更新/删除菜单 |
| `/api/blog/admin/guestbook/` | GET | 留言列表 |
| `/api/blog/admin/guestbook/:id/` | PATCH/DELETE | 审核/删除留言 |
| `/api/blog/admin/comments/` | GET | 评论列表 |
| `/api/blog/admin/comments/:id/` | PATCH/DELETE | 审核/删除评论 |
| `/api/blog/admin/site-config/` | GET/PATCH | 站点配置读写 |
| `/api/users/auth/user/` | GET | 当前用户信息 |
| `/api/users/auth/profile/` | PUT | 更新个人资料 |
| `/api/users/admin/users/` | GET/POST | 用户管理 |
| `/api/users/admin/users/:id/` | PUT/DELETE | 更新/删除用户 |

## 用户角色

| 角色 | 权限 |
|------|------|
| admin | 全部权限 |
| editor | 文章/评论/留言管理 |
| author | 管理自己的文章 |
| subscriber | 仅前台 |

## 文章类型

| 类型 | 说明 |
|------|------|
| article | 博客文章（文章列表页展示） |
| diary | 日记（日记页展示） |
| about | 关于页面（全站唯一） |

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `DJANGO_SECRET_KEY` | Django 密钥 | 开发默认值 |
| `DB_ENGINE` | 数据库引擎 | `django.db.backends.mysql` |
| `DB_NAME` | 数据库名 | `sixth_db` |
| `DB_USER` | 数据库用户 | `Sixth_user` |
| `DB_PASSWORD` | 数据库密码 | （空） |
| `DB_HOST` | 数据库地址 | `localhost` |
| `DB_PORT` | 数据库端口 | `3306` |
