import psycopg2


class DataBase:
    def __init__(self, cursor):
        self.cursor = cursor

    @staticmethod
    def create_db(cursor):
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Customers(
            id SERIAL PRIMARY KEY,
            f_name VARCHAR(20) NOT NULL,
            l_name VARCHAR(30) NOT NULL,
            email VARCHAR(50) UNIQUE
            );
         """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Phone(
            id SERIAL PRIMARY KEY,
            phone_number VARCHAR(12),
            customer_id INTEGER NOT NULL references Customers(id)
            );
         """)

    def add_phone_number(self, customer_id, phone_number):
        self.cursor.execute("INSERT INTO Phone(customer_id, phone_number) VALUES(%s,%s);", (customer_id, phone_number))

    def del_phone_number(self, customer_id):
        self.cursor.execute(" DELETE FROM Phone WHERE id=%s; ", (customer_id,))

    def add_customer(self, name, lastname, email=None, phone_number=None):
        self.cursor.execute("INSERT INTO Customers(f_name, l_name, email) VALUES(%s,%s,%s) RETURNING id;",
                            (name, lastname, email))
        id_ = self.cursor.fetchone()
        if phone_number:
            self.add_phone_number(phone_number=phone_number, customer_id=id_)

    def del_customer(self, customer_id):
        self.cursor.execute(" DELETE FROM Customers WHERE id=%s; ", (customer_id,))

    def update_customer(self, customer_id, name, lastname, email=None, phone_number=None):
        self.cursor.execute("UPDATE Customers SET f_name=%s,l_name =%s, email =%s WHERE id=%s RETURNING id; ",
                            (name, lastname, email, customer_id))
        id_ = self.cursor.fetchone()
        if phone_number:
            self.del_phone_number(id_)
            self.add_phone_number(phone_number=phone_number, customer_id=id_)

    def find_customer(self, name=None, lastname=None, email=None, phone_number=None):
        """Обязательно указать один из критериев поиска(name=, lastname=, email=, phone_number=).
         Например name='Пушкин'"""
        self.cursor.execute("SELECT * FROM Customers WHERE f_name=%s or l_name =%s or email =%s; ",
                            (name, lastname, email))
        if phone_number:
            self.cursor.execute("""SELECT * FROM (
            SELECT f_name, l_name, email,phone_number  FROM Customers c
            JOIN Phone p ON p.customer_id = c.id) res
            WHERE res.phone_number=%s; """, (phone_number,))
        print(self.cursor.fetchone())


def main():
    database = input('Введите название вашей базы данных: ')
    user = input('Введите имя пользователя вашей базы данных: ')
    password = input('Введите пароль вашей базы данных: ')
    with psycopg2.connect(database=database, user=user, password=password) as conn:
        with conn.cursor() as cur:
            db = DataBase(cursor=cur)
            # # разкоментировать для теста
            # cur.execute("""
            #     DROP TABLE Phone;
            #     DROP TABLE Customers;
            #     """)

            db.create_db(cur)
            db.add_customer(name='Джоэл', lastname='Миллер')
            db.add_phone_number(1, '+79851112233')
            db.add_customer(name='name', lastname='lname', email='example@tlou.com', phone_number='+79254444787')
            db.update_customer(2, 'Элли', 'Уильямс', 'example@tlou.com', '+79651472536')
            db.add_customer('Эбби', 'Андерсон')
            db.del_customer(3)
            conn.commit()
            cur.execute("SELECT * FROM Customers;")
            print('Customers_tbl', cur.fetchall())
            cur.execute("SELECT * FROM Phone;")
            print('Phone_tbl', cur.fetchall())
            db.find_customer(phone_number='+79651472536')

    conn.close()


if __name__ == '__main__':
    # перед запуском создать БД в терминале.
    main()
