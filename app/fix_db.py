from app.database import engine, Base, SessionLocal
from app.models import User, Category, Expense, Income
from app.utils import get_password_hash
from datetime import datetime

# 1. Базаны тазалау және қайта құру
print("⏳ Базаны тазалап жатырмын...")
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
print("✅ Кестелер құрылды!")

# 2. Деректерді толтыру
db = SessionLocal()

# Қолданушы
user = User(username="admin", email="admin@test.kz", hashed_password=get_password_hash("123"))
db.add(user)
db.commit()
db.refresh(user)
print("👤 Admin қосылды (admin@test.kz / 123)")

# Санаттар
cats = ["Тамақ", "Көлік", "Сатып алу", "Денсаулық", "Білім"]
cat_objs = []
for c in cats:
    cat = Category(name=c, user_id=user.id)
    db.add(cat)
    db.commit()
    db.refresh(cat)
    cat_objs.append(cat)
print("📂 Санаттар қосылды.")

# Кіріс (100 000)
inc = Income(amount=100000, description="Айлық", date=datetime.now(), user_id=user.id)
db.add(inc)

# Шығындар (График үшін)
exp1 = Expense(amount=5000, description="KFC", category_id=cat_objs[0].id, date=datetime.now(), user_id=user.id) # Тамақ
exp2 = Expense(amount=2000, description="Такси", category_id=cat_objs[1].id, date=datetime.now(), user_id=user.id) # Көлік

db.add(exp1)
db.add(exp2)
db.commit()
print("💰 Кіріс пен Шығыстар қосылды!")

db.close()