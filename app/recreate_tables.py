from .database import engine, Base
from .models import User, Category, Expense, Income, Budget

print("⏳ Базаны тазалап, қайта құрудамын...")

# 1. Ескі кестелерді өшіру (Егер бар болса)
Base.metadata.drop_all(bind=engine)
print("🗑️ Ескі кестелер өшірілді.")

# 2. Жаңа кестелерді құру
Base.metadata.create_all(bind=engine)
print("✅ Жаңа кестелер (5 дана) сәтті құрылды!")