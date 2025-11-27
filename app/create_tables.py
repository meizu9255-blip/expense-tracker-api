from .database import engine, Base
# Бұл жерде барлық модельдерді ТІКЕЛЕЙ импорттау маңызды!
from .models import User, Category, Expense, Income, Budget

print("⏳ Кестелерді PostgreSQL-ге жазу басталды...")

# Кестелерді құру командасы
Base.metadata.create_all(bind=engine)

print("✅ ДАЙЫН! Барлық 5 кесте құрылды.")