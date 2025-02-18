from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Kết nối đến database
def connect_db():
    return sqlite3.connect("transactions.db")

# Khởi tạo database
def init_db():
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                description TEXT,
                transaction_type TEXT NOT NULL
            )
        """)
        conn.commit()

# Trang danh sách giao dịch
@app.route('/')
def index():
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM transactions ORDER BY date DESC")
        transactions = cursor.fetchall()
    return render_template('index.html', transactions=transactions)

# Thêm/Sửa giao dịch
@app.route('/add_edit', methods=['GET', 'POST'])
def add_edit():
    if request.method == 'POST':
        transaction_id = request.form.get('transaction_id', None)
        date = request.form.get('date', '')
        amount = request.form.get('amount', 0)
        category = request.form.get('category', '')
        description = request.form.get('description', '')
        transaction_type = request.form.get('transaction_type', '')

        if not date or not amount or not category or not transaction_type:
            return "Lỗi: Vui lòng điền đầy đủ thông tin.", 400

        with connect_db() as conn:
            cursor = conn.cursor()
            if transaction_id:  # Cập nhật giao dịch
                cursor.execute("""
                    UPDATE transactions 
                    SET date=?, amount=?, category=?, description=?, transaction_type=? 
                    WHERE id=?
                """, (date, amount, category, description, transaction_type, transaction_id))
            else:  # Thêm giao dịch mới
                cursor.execute("""
                    INSERT INTO transactions (date, amount, category, description, transaction_type)
                    VALUES (?, ?, ?, ?, ?)
                """, (date, amount, category, description, transaction_type))
            conn.commit()
        
        return redirect(url_for('index'))

    # Xử lý GET để lấy dữ liệu cập nhật
    transaction_id = request.args.get('id')
    transaction = None
    if transaction_id:
        with connect_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM transactions WHERE id=?", (transaction_id,))
            transaction = cursor.fetchone()
    
    return render_template('add_edit.html', transaction=transaction)

# Xóa giao dịch
@app.route('/delete/<int:transaction_id>')
def delete(transaction_id):
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM transactions WHERE id=?", (transaction_id,))
        conn.commit()
    return redirect(url_for('index'))

# Tìm kiếm giao dịch
@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '')
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM transactions 
            WHERE category LIKE ? OR description LIKE ?
        """, ('%' + query + '%', '%' + query + '%'))
        transactions = cursor.fetchall()
    return render_template('index.html', transactions=transactions)

if __name__ == '__main__':
    init_db()  # Tạo database nếu chưa có
    app.run(debug=True)
