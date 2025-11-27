from .database import SessionLocal, engine, Base
from .models import Category, User
from .utils import get_password_hash

# Базамен байланыс
db = SessionLocal()

def init_data():
    print("⏳ Деректерді енгізу басталды...")

    # 1. Егер база бос болса, кестелерді құру
    Base.metadata.create_all(bind=engine)

    # 2. Админ қолданушыны тексеру/құру
    admin = db.query(User).filter(User.email == "admin@test.kz").first()
    if not admin:
        admin = User(
            username="Admin",
            email="admin@test.kz",
            hashed_password=get_password_hash("123")
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        print("✅ Админ қолданушы құрылды (email: admin@test.kz, pass: 123)")
    else:
        print("ℹ️ Админ қолданушы бар.")

    # 3. Санаттарды қосу
    categories = [
        "Тамақ",          # ID 1
        "Көлік",          # ID 2
        "Сатып алу",      # ID 3
        "Ойын-сауық",     # ID 4
        "Коммуналдық",    # ID 5
        "Денсаулық",      # ID 6
        "Білім",          # ID 7
        "Саяхат",         # ID 8
        "Басқа"           # ID 9
    ]

    for cat_name in categories:
        # Тексеру: бұндай санат бар ма?
        exists = db.query(Category).filter(Category.name == cat_name, Category.user_id == admin.id).first()
        if not exists:
            new_cat = Category(name=cat_name, user_id=admin.id)
            db.add(new_cat)
            print(f"✅ Санат қосылды: {cat_name}")
    
    db.commit()
    print("🎉 Барлық санаттар сәтті енгізілді!")
    db.close()

if __name__ == "__main__":
    init_data()