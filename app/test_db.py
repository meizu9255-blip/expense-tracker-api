import psycopg2

try:
    # МЫНА ЖЕРГЕ ПАРОЛЬДІ ЖАЗЫҢЫЗ:
    connection = psycopg2.connect(
        dbname="expense_db",
        user="postgres",
        password="1234",  # <--- Осы жерге pgAdmin паролін жазыңыз
        host="localhost",
        port="5432"
    )
    print("✅ КЕРЕМЕТ! PostgreSQL-ге сәтті қосылдық!")
    connection.close()

except Exception as e:
    print("❌ ҚАТЕ ШЫҚТЫ:")
    print(e)