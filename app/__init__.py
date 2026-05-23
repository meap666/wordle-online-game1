from flask import Flask
# pyrefly: ignore [untyped-import]
from flask_socketio import SocketIO
from app.core.config import AppConfig
from app.models.orm import db

# 準備廣播通訊器
socketio = SocketIO()


def create_app():
    # 1. 建立 Flask 主程式
    app = Flask(__name__)

    # 2. 套用系統設定
    app.config["SECRET_KEY"] = AppConfig.SECRET_KEY
    app.config["SQLALCHEMY_DATABASE_URI"] = AppConfig.SQLALCHEMY_DATABASE_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # 3. 初始化資料庫
    db.init_app(app)

    # 4. 初始化 SocketIO
    # Render 使用 gunicorn -k eventlet 時，這裡建議明確指定 eventlet
    socketio.init_app(
        app,
        cors_allowed_origins="*",
        async_mode="eventlet"
    )  # type: ignore

    # 5. 註冊 Blueprint 路由
    from app.api.routes import main_bp
    app.register_blueprint(main_bp)

    # 6. 確保所有資料表模型都有被載入
    # 如果 Player、GameRecord 等資料表都寫在 app.models.orm 裡，這行可以保險地載入模型
    import app.models.orm  # noqa: F401

    # 7. 建立資料庫資料表
    # Render 第一次部署時，如果沒有資料表，註冊帳號會失敗
    with app.app_context():
        db.create_all()
        print("Database tables created successfully.")

    return app
