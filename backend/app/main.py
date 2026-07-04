from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from app.api.routes import approvals, categories, dashboard, duplicates, files, health, ollama, operations, watch_folders
from app.core.config import get_settings
from app.core.database import Base, SessionLocal, engine
from app.models.entities import Category

DEFAULT_CATEGORIES = [
    ("CUSTOMER_QUOTATION", "見積書", "取引先/{customer_name}/見積書/{year}"),
    ("INVOICE", "請求書", "経理/請求書/{year}/{month}"),
    ("PURCHASE_ORDER", "注文書", "購買/注文書/{year}/{month}"),
    ("CONTRACT", "契約書", "契約書/{year}"),
    ("MEETING_MINUTES", "議事録", "会議/議事録/{year}/{month}"),
    ("MANUAL", "マニュアル", "技術資料/マニュアル"),
    ("SPECIFICATION", "仕様書", "技術資料/仕様書"),
    ("REPORT", "報告書", "報告書/{year}"),
    ("SPREADSHEET", "表計算資料", "表計算/{year}"),
    ("IMAGE", "画像", "画像/{year}/{month}"),
    ("SOURCE_CODE", "ソースコード", "ソースコード/{year}"),
    ("ARCHIVE", "アーカイブ", "アーカイブ/{year}"),
    ("OTHER", "その他", "保留"),
]


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, version="0.1.0")
    app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
    app.include_router(health.router, prefix="/api")
    app.include_router(ollama.router, prefix="/api")
    app.include_router(watch_folders.router, prefix="/api")
    app.include_router(files.router, prefix="/api")
    app.include_router(categories.router, prefix="/api")
    app.include_router(operations.router, prefix="/api")
    app.include_router(approvals.router, prefix="/api")
    app.include_router(dashboard.router, prefix="/api")
    app.include_router(duplicates.router, prefix="/api")

    @app.on_event("startup")
    def startup() -> None:
        settings.data_dir.mkdir(parents=True, exist_ok=True)
        Base.metadata.create_all(bind=engine)
        with SessionLocal() as db:
            existing = set(db.scalars(select(Category.category_id)))
            for category_id, display_name, template in DEFAULT_CATEGORIES:
                if category_id not in existing:
                    db.add(Category(category_id=category_id, display_name=display_name, destination_template=template))
            db.commit()
    return app


app = create_app()
