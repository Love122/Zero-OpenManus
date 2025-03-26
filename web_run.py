import argparse
import os
import sys
import subprocess
import time
import signal
import threading
import platform
import logging
from pathlib import Path
import io

import uvicorn


# LMStudio服务器进程
lmstudio_process = None


# 获取LMStudio可执行文件路径列表
def get_lmstudio_paths():
    system = platform.system()
    if system == "Windows":
        return [
            r"C:\Program Files\LM Studio\LM Studio.exe",
            r"C:\Program Files (x86)\LM Studio\LM Studio.exe",
            os.path.expanduser(r"~\AppData\Local\Programs\LM Studio\LM Studio.exe"),
        ]
    elif system == "Darwin":  # macOS
        return [
            "/Applications/LM Studio.app/Contents/MacOS/LM Studio",
            os.path.expanduser("~/Applications/LM Studio.app/Contents/MacOS/LM Studio"),
        ]
    elif system == "Linux":
        return [
            "/usr/bin/lmstudio",
            "/usr/local/bin/lmstudio",
            os.path.expanduser("~/lmstudio/LM Studio"),
        ]
    return []


# 启动LMStudio服务器
def start_lmstudio_server(lm_port=1234, no_gui=True):
    global lmstudio_process

    print(f"🔍 正在查找LMStudio服务器可执行文件...")

    # 查找可执行文件
    lmstudio_executable = None
    for path in get_lmstudio_paths():
        if os.path.exists(path):
            lmstudio_executable = path
            break

    if not lmstudio_executable:
        print("⚠️ 未找到LMStudio可执行文件，请手动启动")
        print(f"   请开启LMStudio并启用端口 {lm_port} 的API服务器")
        return False

    try:
        # 构建命令行参数
        cmd = [lmstudio_executable, "--api-port", str(lm_port), "--max-listeners", "20"]
        if no_gui:
            cmd.append("--no-gui")

        # 启动子进程
        print(f"🚀 正在启动LMStudio API服务器(端口: {lm_port})...")
        lmstudio_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=False,  # 二进制模式获取输出
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if platform.system() == "Windows" else 0
        )

        # 等待启动确认
        time.sleep(2)

        if lmstudio_process.poll() is None:
            print(f"✅ LMStudio服务器成功启动 (端口: {lm_port})")

            # 异步读取输出函数
            def read_output(pipe, prefix):
                text_stream = io.TextIOWrapper(pipe, encoding='utf-8', errors='replace')
                for line in text_stream:
                    if line:
                        # 过滤特定错误信息
                        if "MaxListenersExceededWarning" not in line and "lib-bad" not in line:
                            print(f"{prefix}: {line.strip()}")

            # 启动输出读取线程
            threading.Thread(target=read_output, args=(lmstudio_process.stdout, "LMStudio"), daemon=True).start()
            threading.Thread(target=read_output, args=(lmstudio_process.stderr, "LMStudio Error"), daemon=True).start()

            return True
        else:
            print(f"⚠️ LMStudio服务器启动失败")
            return False

    except Exception as e:
        print(f"⚠️ 启动LMStudio服务器时发生错误: {str(e)}")
        return False


# 清理LMStudio进程
def cleanup_lmstudio():
    global lmstudio_process
    if lmstudio_process:
        print("🛑 正在停止LMStudio服务器...")
        try:
            if platform.system() == "Windows":
                lmstudio_process.terminate()
                # Windows需要终止进程树
                subprocess.call(['taskkill', '/F', '/T', '/PID', str(lmstudio_process.pid)])
            else:
                # Unix系统处理
                lmstudio_process.terminate()
                lmstudio_process.wait(timeout=5)
        except Exception as e:
            print(f"停止LMStudio时发生错误: {str(e)}")
            if platform.system() != "Windows":
                try:
                    lmstudio_process.kill()
                except:
                    pass


# 检查WebSocket依赖
def check_websocket_dependencies():
    pass
    return True


# 确保目录结构
def ensure_directories():
    # 创建模板目录
    templates_dir = Path("app/web/templates")
    templates_dir.mkdir(parents=True, exist_ok=True)

    # 创建静态资源目录
    static_dir = Path("app/web/static")
    static_dir.mkdir(parents=True, exist_ok=True)

    # 检查初始化文件
    init_file = Path("app/web/__init__.py")
    if not init_file.exists():
        init_file.touch()


# 配置uvicorn日志
def configure_uvicorn_logging(log_level="warning"):
    log_level = log_level.lower()
    level_map = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL
    }

    level = level_map.get(log_level, logging.WARNING)

    # 设置所有相关日志器
    loggers = [
        "uvicorn",
        "uvicorn.access",
        "uvicorn.error",
        "websockets",
        "websockets.protocol"
    ]

    for logger_name in loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(level)

    # 配置基础日志
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


if __name__ == "__main__":
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="OpenManus Web应用服务器")
    parser.add_argument("--no-browser", action="store_true", help="不自动打开浏览器")
    parser.add_argument("--port", type=int, default=8000, help="服务器监听端口 (默认: 8000)")
    parser.add_argument("--lmstudio", action="store_true", help="同时启动LMStudio服务器")
    parser.add_argument("--lm-port", type=int, default=1234, help="LMStudio服务器端口 (默认: 1234)")
    parser.add_argument("--lm-gui", action="store_true", help="使用GUI模式启动LMStudio")
    parser.add_argument("--log-level", type=str, default="warning",
                      choices=["debug", "info", "warning", "error", "critical"],
                      help="日志级别 (默认: warning)")

    args = parser.parse_args()

    # 配置日志系统
    configure_uvicorn_logging(args.log_level)

    ensure_directories()

    if not check_websocket_dependencies():
        print("缺少必要依赖，请安装所需包后重试")
        sys.exit(1)

    if args.lmstudio:
        start_lmstudio_server(lm_port=args.lm_port, no_gui=not args.lm_gui)

    if args.no_browser:
        os.environ["AUTO_OPEN_BROWSER"] = "0"
    else:
        os.environ["AUTO_OPEN_BROWSER"] = "1"

    port = args.port

    print(f"🚀 正在启动OpenManus Web应用...")
    print(f"http://localhost:{port} 准备就绪")

    def signal_handler(sig, frame):
        print("\n⏹️ 正在停止服务...")
        cleanup_lmstudio()
        sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        uvicorn.run(
            "app.web.app:app",
            host="0.0.0.0",
            port=port,
            reload=True,
            log_level=args.log_level
        )
    finally:
        cleanup_lmstudio()