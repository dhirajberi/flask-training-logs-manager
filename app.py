from flask import Flask, render_template, request, session, redirect, url_for, g, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_mail import Mail, Message

class User:
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

users = []
users.append(User(id=1, username='Dhiraj', password='dhiraj'))
users.append(User(id=2, username='Smit', password='smit'))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    post_by = db.Column(db.String(200), nullable = False)
    content = db.Column(db.String(200), nullable = False)
    date_created = db.Column(db.DateTime, default = datetime.utcnow)

app.secret_key = 'dhirajapp'

@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        user = [x for x in users if x.id == session['user_id']][0]
        g.user = user

@app.route("/", methods=['GET', 'POST'])
@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session.pop('user_id', None)

        username = request.form['username']
        password = request.form['password']

        user = [x for x in users if x.username == username][0]
        if user and user.password == password:
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))
        
        flash("Wrong Password...")
        return redirect(url_for('login'))

    return render_template('login.html')

@app.route("/dashboard", methods=['GET', 'POST'])
def dashboard():
    if not g.user:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        task_content = request.form['content']
        task_post_by = g.user.username
        new_task = Todo(content=task_content, post_by=task_post_by)

        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect(url_for('dashboard'))

        except:
            return 'There was in issue in adding task'

    else:
        tasks = Todo.query.order_by(Todo.date_created).filter(Todo.post_by == g.user.username)
        return render_template('dashboard.html', tasks = tasks)

    #return render_template('dashboard.html')

@app.route("/delete/<int:id>")
def delete(id):
    task_to_delete = Todo.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect(url_for('dashboard'))

    except:
        return "Problem"

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'youremail'
app.config['MAIL_PASSWORD'] = 'yourpass'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

@app.route("/send_mail/<int:id>", methods=['GET', 'POST'])
def send_mail(id):
    task = Todo.query.get_or_404(id)
    if request.method == 'POST':
        email = request.form['email']
        msg = Message('Daily Task Report', sender = 'youremail', recipients = [email])
        msg.body = f'Task: {task.content} \nDate: {task.date_created.date()} \n\nSend By {g.user.username}'
        mail.send(msg)
        flash(f"Mail sent successfully to {email}")  
        return redirect(url_for('dashboard'))

@app.route("/logout")
def logout():
    session.pop('user_id', None)
    flash("Logout successfully...")  
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
