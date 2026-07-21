import { createRouter, createWebHistory } from "vue-router";
import { getSetupStatus } from "../api/setup";

const router = createRouter({
    history: createWebHistory(),

    routes: [
        // ===== 安装向导 =====
        {
            path: "/setup",
            name: "Setup",
            component: () => import("../views/Setup.vue"),
        },

        // ===== 前台路由 =====
        { path: "/", redirect: "/home" },
        {
            path: "/home",
            name: "Home",
            component: () => import("../views/Home.vue"),
        },
        {
            path: "/articles",
            name: "Articles",
            component: () => import("../views/Articles.vue"),
        },
        {
            path: "/article/:id",
            name: "ArticleDetail",
            component: () => import("../views/ArticleDetail.vue"),
        },
        {
            path: "/about",
            name: "About",
            component: () => import("../views/About.vue"),
        },
        {
            path: "/guestbook",
            name: "Guestbook",
            component: () => import("../views/Guestbook.vue"),
        },
        {
            path: "/diaries",
            name: "Diaries",
            component: () => import("../views/Diaries.vue"),
        },
        {
            path: "/diary/:id",
            name: "DiaryDetail",
            component: () => import("../views/ArticleDetail.vue"),
        },
        {
            path: "/archives",
            name: "Archives",
            component: () => import("../views/Archives.vue"),
        },
        {
            path: "/login",
            name: "Login",
            component: () => import("../views/Login.vue"),
        },
        {
            path: "/register",
            name: "Register",
            component: () => import("../views/Register.vue"),
        },
        {
            path: "/profile",
            name: "Profile",
            component: () => import("../views/Profile.vue"),
        },

        // ===== 后台管理路由 =====
        {
            path: "/sixth-admin",
            component: () => import("../layouts/AdminLayout.vue"),
            children: [
                {
                    path: "",
                    name: "AdminDashboard",
                    component: () => import("../views/admin/Dashboard.vue"),
                },
                {
                    path: "articles",
                    name: "AdminArticles",
                    component: () => import("../views/ArticleManage.vue"),
                },
                {
                    path: "articles/new",
                    name: "AdminArticleNew",
                    component: () => import("../views/ArticleEditor.vue"),
                },
                {
                    path: "articles/:id/edit",
                    name: "AdminArticleEdit",
                    component: () => import("../views/ArticleEditor.vue"),
                },
                {
                    path: "comments",
                    name: "AdminComments",
                    component: () => import("../views/CommentManage.vue"),
                },
                {
                    path: "guestbook",
                    name: "AdminGuestbook",
                    component: () => import("../views/GuestbookManage.vue"),
                },
                {
                    path: "categories",
                    name: "AdminCategories",
                    component: () => import("../views/CategoryManage.vue"),
                },
                {
                    path: "menus",
                    name: "AdminMenus",
                    component: () => import("../views/MenuManage.vue"),
                },
                {
                    path: "media",
                    name: "AdminMedia",
                    component: () => import("../views/admin/MediaManage.vue"),
                },
                {
                    path: "settings",
                    name: "AdminSettings",
                    component: () => import("../views/SiteSettings.vue"),
                },
                {
                    path: "users",
                    name: "AdminUsers",
                    component: () => import("../views/UserManage.vue"),
                },
            ],
        },

        // ===== 404（必须放在最后）=====
        {
            path: "/:pathMatch(.*)*",
            name: "NotFound",
            component: () => import("../views/NotFound.vue"),
        },
    ],
});

// 全局路由守卫：检查系统初始化状态
let setupChecked = false;
let isInitialized = false;

router.beforeEach(async (to, _from, next) => {
  // Setup 页面始终可访问
  if (to.path === '/setup') {
    return next();
  }

  // 仅在首次访问时检查初始化状态
  if (!setupChecked) {
    let retries = 1;
    while (retries >= 0) {
      try {
        const res = await getSetupStatus() as any;
        isInitialized = res.initialized;
        break;
      } catch (e) {
        console.error('初始化检查失败:', e)
        if (retries > 0) {
          retries--;
          // 等一小段时间再重试
          await new Promise(r => setTimeout(r, 500));
          continue;
        }
        isInitialized = false;
      }
    }
    setupChecked = true;
  }

  if (!isInitialized) {
    return next('/setup');
  }

  next();
});

export default router;
