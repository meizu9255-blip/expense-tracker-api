from app.database import SessionLocal
from app.models import Category, User

db = SessionLocal()

def init_categories():
    # 1. Қолданушыны табу (Ең бірінші тіркелген адамға қосамыз)
    user = db.query(User).first()
    
    if not user:
        print("❌ Қолданушы табылмады! Алдымен сайттан тіркеліңіз.")
        return

    print(f"👤 Қолданушы табылды: {user.email} (ID: {user.id})")
    print("⏳ Санаттарды тексеру және қосу...")

    # Біздің сайттағы тізім (ретімен)
    categories_list = [
        "Тамақ",          # ID 1 болады
        "Көлік",          # ID 2
        "Сатып алу",      # ID 3
        "Ойын-сауық",     # ID 4
        "Коммуналдық",    # ID 5
        "Денсаулық",      # ID 6
        "Білім",          # ID 7
        "Саяхат",         # ID 8
        "Басқа"           # ID 9
    ]

    for cat_name in categories_list:
        # Тексереміз: егер базада жоқ болса ғана қосамыз
        exists = db.query(Category).filter(Category.name == cat_name, Category.user_id == user.id).first()
        if not exists:
            new_cat = Category(name=cat_name, user_id=user.id)
            db.add(new_cat)
            db.commit() # ID ретімен берілуі үшін әрқайсысын жеке сақтаймыз
            print(f"✅ {cat_name} қосылды!")
        else:
            print(f"ℹ️ {cat_name} базада бар.")

    print("\n🎉 БАРЛЫҒЫ ДАЙЫН! Енді сайттан кез келген санатты таңдай аласыз.")

if __name__ == "__main__":
    init_categories()
    db.close()