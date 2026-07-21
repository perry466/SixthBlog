#!/bin/bash
set -e

# ============================================================
#  SixthBlog 首次部署配置向导
# ============================================================

clear
echo ""
echo "  ╔══════════════════════════════════════╗"
echo "  ║     SixthBlog 首次部署配置向导       ║"
echo "  ╚══════════════════════════════════════╝"
echo ""
echo "  按提示输入数据库配置，密码不会显示在屏幕上。"
echo ""

# ---- 数据库名称 ----
echo -n "  数据库名称 [sixth_db]: "
read DB_NAME
DB_NAME=${DB_NAME:-sixth_db}

# ---- 数据库用户名 ----
echo -n "  数据库用户名 [Sixth_user]: "
read DB_USER
DB_USER=${DB_USER:-Sixth_user}

# ---- Root 密码（必须输入）----
while true; do
    echo -n "  MySQL Root 密码 (必须输入): "
    read -s MYSQL_ROOT_PASSWORD
    echo ""
    if [ -z "$MYSQL_ROOT_PASSWORD" ]; then
        echo "  ⚠ 密码不能为空，请重新输入。"
        echo ""
    else
        break
    fi
done

# ---- 用户密码（必须输入）----
while true; do
    echo -n "  数据库用户密码 (必须输入): "
    read -s DB_PASSWORD
    echo ""
    if [ -z "$DB_PASSWORD" ]; then
        echo "  ⚠ 密码不能为空，请重新输入。"
        echo ""
    else
        break
    fi
done

# ---- 配置预览 ----
echo ""
echo "  ══════════════════════════════════════════════"
echo "  即将使用以下配置创建数据库："
echo ""
echo "    数据库名:         $DB_NAME"
echo "    数据库用户名:     $DB_USER"
echo "    数据库用户密码:   $DB_PASSWORD"
echo "    Root 密码:        $MYSQL_ROOT_PASSWORD"
echo ""
echo "  ══════════════════════════════════════════════"
echo ""

read -p "  确认写入 docker/.env 并启动? [Y/n]: " CONFIRM
CONFIRM=${CONFIRM:-Y}

if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
    echo "  已取消。"
    exit 0
fi

# ---- 写入 .env ----
ENV_DIR="$(cd "$(dirname "$0")" && pwd)/docker"
mkdir -p "$ENV_DIR"

cat > "$ENV_DIR/.env" <<EOF
# SixthBlog 数据库配置（由 setup.sh 自动生成）
MYSQL_ROOT_PASSWORD=$MYSQL_ROOT_PASSWORD
DB_NAME=$DB_NAME
DB_USER=$DB_USER
DB_PASSWORD=$DB_PASSWORD
EOF

echo ""
echo "  ✅ 配置已写入 docker/.env"
echo ""

# ---- 启动 Docker Compose ----
read -p "  是否立即启动 Docker Compose? [Y/n]: " START
START=${START:-Y}

if [[ "$START" =~ ^[Yy]$ ]]; then
    echo ""
    echo "  正在启动容器..."
    cd "$ENV_DIR"
    docker compose up -d
    echo ""
    echo "  ╔══════════════════════════════════════════════════╗"
    echo "  ║     SixthBlog 已启动！                          ║"
    echo "  ╠══════════════════════════════════════════════════╣"
    echo "  ║  访问地址:    http://localhost                  ║"
    echo "  ║                                                ║"
    echo "  ║  MySQL Root 密码:  $MYSQL_ROOT_PASSWORD"
    echo "  ║  数据库名:         $DB_NAME"
    echo "  ║  数据库用户:       $DB_USER"
    echo "  ║  数据库用户密码:   $DB_PASSWORD"
    echo "  ║                                                ║"
    echo "  ║  配置已保存至: docker/.env                      ║"
    echo "  ╚══════════════════════════════════════════════════╝"
    echo ""
else
    echo ""
    echo "  ╔══════════════════════════════════════════════════╗"
    echo "  ║  配置已保存至 docker/.env，以下为创建的内容：   ║"
    echo "  ╠══════════════════════════════════════════════════╣"
    echo "  ║  MySQL Root 密码:  $MYSQL_ROOT_PASSWORD"
    echo "  ║  数据库名:         $DB_NAME"
    echo "  ║  数据库用户:       $DB_USER"
    echo "  ║  数据库用户密码:   $DB_PASSWORD"
    echo "  ╚══════════════════════════════════════════════════╝"
    echo ""
    echo "  之后可手动启动: cd docker && docker compose up -d"
fi
