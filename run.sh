#!/bin/bash

# 应用配置
APP_NAME="husky"
BACKEND_PORT=5000
FRONTEND_PORT=3000
BACKEND_PID_FILE="./logs/${APP_NAME}_backend.pid"
FRONTEND_PID_FILE="./logs/${APP_NAME}_frontend.pid"
BACKEND_LOG_FILE="./logs/${APP_NAME}_backend.log"
FRONTEND_LOG_FILE="./logs/${APP_NAME}_frontend.log"

# 函数: 启动后端应用
start_backend() {
    if [ -f "$BACKEND_PID_FILE" ]; then
        echo "后端应用已经在运行中 (PID: $(cat $BACKEND_PID_FILE))"
        return 1
    fi

    echo "正在启动${APP_NAME}后端应用..."
    cd "$(dirname "$0")"
    
    # 检查是否有虚拟环境，如果有则激活
    if [ -d ".venv" ]; then
        source .venv/bin/activate
    fi

    # 启动后端应用并记录PID
    nohup python app.py > $BACKEND_LOG_FILE 2>&1 &
    echo $! > $BACKEND_PID_FILE
    echo "${APP_NAME}后端应用已启动 (PID: $(cat $BACKEND_PID_FILE))，日志请查看$BACKEND_LOG_FILE"
}

# 函数: 启动前端应用
start_frontend() {
    if [ -f "$FRONTEND_PID_FILE" ]; then
        echo "前端应用已经在运行中 (PID: $(cat $FRONTEND_PID_FILE))"
        return 1
    fi

    echo "正在启动${APP_NAME}前端应用..."
    cd "$(dirname "$0")"

    # 启动前端应用并记录PID
    nohup npm run start > $FRONTEND_LOG_FILE 2>&1 &
    echo $! > $FRONTEND_PID_FILE
    echo "${APP_NAME}前端应用已启动 (PID: $(cat $FRONTEND_PID_FILE))，日志请查看$FRONTEND_LOG_FILE"
}

# 函数: 启动应用
start() {
    start_backend
    start_frontend
    echo "${APP_NAME}应用已全部启动完毕"
    echo "后端服务运行在 http://localhost:$BACKEND_PORT"
    echo "前端服务运行在 http://localhost:$FRONTEND_PORT"
}

# 函数: 停止后端应用
stop_backend() {
    if [ ! -f "$BACKEND_PID_FILE" ]; then
        echo "后端应用未运行"
        return 1
    fi

    echo "正在停止${APP_NAME}后端应用..."
    PID=$(cat $BACKEND_PID_FILE)
    kill $PID
    if [ $? -eq 0 ]; then
        rm -f $BACKEND_PID_FILE
        echo "${APP_NAME}后端应用已停止"
    else
        echo "停止${APP_NAME}后端应用失败"
        return 1
    fi
}

# 函数: 停止前端应用
stop_frontend() {
    if [ ! -f "$FRONTEND_PID_FILE" ]; then
        echo "前端应用未运行"
        return 1
    fi

    echo "正在停止${APP_NAME}前端应用..."
    PID=$(cat $FRONTEND_PID_FILE)
    kill $PID
    if [ $? -eq 0 ]; then
        rm -f $FRONTEND_PID_FILE
        echo "${APP_NAME}前端应用已停止"
    else
        echo "停止${APP_NAME}前端应用失败"
        return 1
    fi
}

# 函数: 停止应用
stop() {
    stop_backend
    stop_frontend
    echo "${APP_NAME}应用已全部停止"
}

# 函数: 重启应用
restart() {
    echo "正在重启${APP_NAME}应用..."
    stop
    start
}

# 主程序
case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    *)
        echo "用法: $0 {start|stop|restart}"
        exit 1
        ;;
esac

exit 0