import os
import sys
import traceback

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

try:
    print("正在启动应用程序...")
    from app import create_app
    import config
    
    # 获取配置
    config_obj = config.config['default']()
    print(f"使用配置: {config_obj.__class__.__name__}")
    print(f"主机: {config_obj.HOST}")
    print(f"端口: {config_obj.PORT_FLASK}")
    
    # 创建Flask应用实例
    app = create_app()
    print("Flask应用实例创建成功")
    
    # 启动应用
    print("正在启动服务器...")
    app.run(
        debug=config_obj.DEBUG,
        host=config_obj.HOST,
        port=config_obj.PORT_FLASK
    )
    
except Exception as e:
    print("启动应用程序时发生错误:")
    print(f"错误类型: {type(e).__name__}")
    print(f"错误信息: {str(e)}")
    print("详细错误堆栈:")
    traceback.print_exc()
    sys.exit(1)