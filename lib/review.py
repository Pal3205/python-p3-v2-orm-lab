# lib/review.py
from __init__ import CURSOR, CONN
from department import Department
from employee import Employee

class Review:
    all = {}

    def __init__(self, year, summary, employee_id, id=None):
        self.id = id
        self.year = year
        self.summary = summary
        self.employee_id = employee_id

    def __repr__(self):
        return (
            f"<Review {self.id}: {self.year}, {self.summary}, "
            + f"Employee: {self.employee_id}>"
        )

    @classmethod
    def create_table(cls):
        sql = """
            CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY,
            year INT,
            summary TEXT,
            employee_id INTEGER,
            FOREIGN KEY (employee_id) REFERENCES employees(id))
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        sql = """
            DROP TABLE IF EXISTS reviews;
        """
        CURSOR.execute(sql)
        CONN.commit()

    def save(self):
        if self.id is None:
            CURSOR.execute('''
                INSERT INTO reviews (year, summary, employee_id)
                VALUES (?, ?, ?)
            ''', (self.year, self.summary, self.employee_id))
            self.id = CURSOR.lastrowid
            Review.all[self.id] = self
        else:
            CURSOR.execute('''
                UPDATE reviews SET year = ?, summary = ?, employee_id = ?
                WHERE id = ?
            ''', (self.year, self.summary, self.employee_id, self.id))
        CONN.commit()

    @classmethod
    def create(cls, year, summary, employee_id):
        review = cls(year, summary, employee_id)
        review.save()
        return review

    @classmethod
    def instance_from_db(cls, row):
        id, year, summary, employee_id = row
        if id in cls.all:
            return cls.all[id]
        else:
            review = cls(year, summary, employee_id, id)
            cls.all[id] = review
            return review

    @classmethod
    def find_by_id(cls, id):
        CURSOR.execute('SELECT * FROM reviews WHERE id = ?', (id,))
        row = CURSOR.fetchone()
        if row:
            return cls.instance_from_db(row)
        return None

    def update(self, year=None, summary=None, employee_id=None):
        if year is not None:
            self.year = year
        if summary is not None:
            self.summary = summary
        if employee_id is not None:
            self.employee_id = employee_id
        self.save()

    def delete(self):
        if self.id:
            CURSOR.execute('DELETE FROM reviews WHERE id = ?', (self.id,))
            del Review.all[self.id]
            self.id = None
            CONN.commit()

    @classmethod
    def get_all(cls):
        CURSOR.execute('SELECT * FROM reviews')
        rows = CURSOR.fetchall()
        return [cls.instance_from_db(row) for row in rows]

    @property
    def year(self):
        return self._year

    @year.setter
    def year(self, value):
        if not isinstance(value, int) or value < 2000:
            raise ValueError("Year must be an integer >= 2000")
        self._year = value

    @property
    def summary(self):
        return self._summary

    @summary.setter
    def summary(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Summary must be a non-empty string")
        self._summary = value

    @property
    def employee_id(self):
        return self._employee_id

    @employee_id.setter
    def employee_id(self, value):
        if not isinstance(value, int):
            raise ValueError("Employee ID must be an integer")
        if not Employee.find_by_id(value):
            raise ValueError("Employee ID must reference an existing Employee")
        self._employee_id = value
