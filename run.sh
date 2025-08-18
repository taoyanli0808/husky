#!/bin/bash

# 应用配置
APP_NAME="husky"
PORT=5000
PID_FILE="./logs/${APP_NAME}.pid"
LOG_FILE="./logs/${APP_NAME}.log"

# 函数: 启动应用
start() {
    if [ -f "$PID_FILE" ]; then
        echo "应用已经在运行中 (PID: $(cat $PID_FILE))"
        return 1
    fi

    echo "正在启动${APP_NAME}应用..."
    cd "$(dirname "$0")"
    source .venv/bin/activate

    # 启动应用并记录PID
    nohup python -m flask --app app run --port $PORT --debug > $LOG_FILE 2>&1 &
    echo $! > $PID_FILE
    echo "${APP_NAME}应用已启动 (PID: $(cat $PID_FILE))，日志请查看$LOG_FILE"
}

# 函数: 停止应用
stop() {
    if [ ! -f "$PID_FILE" ]; then
        echo "应用未运行"
        return 1
    fi

    echo "正在停止${APP_NAME}应用..."
    PID=$(cat $PID_FILE)
    kill $PID
    if [ $? -eq 0 ]; then
        rm -f $PID_FILE
        echo "${APP_NAME}应用已停止"
    else
        echo "停止${APP_NAME}应用失败"
        return 1
    fi
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