import os
import json
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, render_template, jsonify, request, redirect, url_for, flash, Response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from forms import ReviewForm, ContactForm
from flask import Flask
from flask import redirect, url_for
app = Flask(__name__, static_folder="static", template_folder="templates", static_url_path="/static")


app = Flask(__name__)
os.makedirs(app.instance_path, exist_ok=True)

app.config['SECRET_KEY'] = os.environ.get("SESSION_SECRET", "your_secret_key_here")
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(app.instance_path, "site.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'fittwithpriya@gmail.com'
app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PASSWORD', 'your_app_password_here')

if os.environ.get('FLASK_ENV') == 'production':
    app.config['DEBUG'] = False
else:
    app.config['DEBUG'] = True

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'rating': self.rating,
            'comment': self.comment,
            'date': self.date_posted.strftime('%B %d, %Y')
        }

class Visit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    page = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(50), nullable=True)
    user_agent = db.Column(db.String(500), nullable=True)
    session_id = db.Column(db.String(100), nullable=True)

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    date_submitted = db.Column(db.DateTime, default=datetime.utcnow)

def send_contact_email(contact_data):
    try:
        msg = MIMEMultipart()
        msg['From'] = app.config['MAIL_USERNAME']
        msg['To'] = 'fittwithpriya@gmail.com'
        msg['Subject'] = f'New Contact Form Submission from {contact_data.name}'
        
        # Email body
        body = f"""
New contact form submission received:

Name: {contact_data.name}
Email: {contact_data.email}
Date: {contact_data.date_submitted.strftime('%B %d, %Y at %I:%M %p')}

Message:
{contact_data.message}

---
This message was sent from your Fit with Priya website contact form.
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        server = smtplib.SMTP(app.config['MAIL_SERVER'], app.config['MAIL_PORT'])
        server.starttls()
        server.login(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        text = msg.as_string()
        server.sendmail(app.config['MAIL_USERNAME'], 'fittwithpriya@gmail.com', text)
        server.quit()
        
        return True
    except Exception as e:
        print(f"Email sending failed: {e}")
        return False

class AdminUser(UserMixin):
    def __init__(self, id):
        self.id = id
        self.username = "admin"

@login_manager.user_loader
def load_user(user_id):
    return AdminUser(user_id)

with app.app_context():
    db.create_all()

def record_visit(page):
    session_id = request.cookies.get('session_id')
    visit = Visit(
        page=page,
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent'),
        session_id=session_id
    )
    db.session.add(visit)
    db.session.commit()

@app.route("/favicon.ico")
def favicon():
    return redirect(url_for("static", filename="images/logo.png"))

@app.route('/')
def index():
    record_visit('home')
    review_form = ReviewForm()
    contact_form = ContactForm()
    reviews = Review.query.order_by(Review.date_posted.desc()).all()
    return render_template('index.html', review_form=review_form, contact_form=contact_form, reviews=reviews)

@app.route('/reviews', methods=['GET'])
def get_reviews():
    record_visit('reviews_api')
    reviews = Review.query.order_by(Review.date_posted.desc()).all()
    return jsonify({
        'success': True,
        'reviews': [r.to_dict() for r in reviews]
    })

@app.route('/reviews', methods=['POST'])
def add_review():
    record_visit('review_submission')
    form = ReviewForm()
    if form.validate_on_submit():
        # Prevent duplicates
        existing = Review.query.filter_by(
            name=form.name.data.strip(),
            comment=form.comment.data.strip()
        ).first()
        if not existing:
            new_review = Review(
                name=form.name.data.strip(),
                rating=form.rating.data,
                comment=form.comment.data.strip()
            )
            db.session.add(new_review)
            db.session.commit()
            return jsonify({'success': True, 'review': new_review.to_dict()})
        else:
            return jsonify({'success': False, 'errors': {'duplicate': 'You already submitted this review.'}})
    return jsonify({'success': False, 'errors': form.errors})

@app.route('/contact', methods=['POST'])
def contact():
    record_visit('contact_submission')
    form = ContactForm()
    if form.validate_on_submit():
        new_contact = Contact(
            name=form.name.data,
            email=form.email.data,
            message=form.message.data
        )
        db.session.add(new_contact)
        db.session.commit()
        
        # Send email notification
        email_sent = send_contact_email(new_contact)
        
        return jsonify({
            'success': True, 
            'message': 'Thank you for your message! We\'ll get back to you soon.',
            'email_sent': email_sent
        })
    return jsonify({'success': False, 'errors': form.errors})

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('username') == 'admin' and request.form.get('password') == 'priyafit123':
            login_user(AdminUser(id=1))
            flash('Logged in successfully.', 'success')
            return redirect(url_for('stats'))
        else:
            flash('Invalid credentials.', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/admin/stats')
@login_required
def stats():
    total_visits = Visit.query.count()
    unique_visitors = db.session.query(Visit.session_id).distinct().count()
    total_reviews = Review.query.count()
    total_contacts = Contact.query.count()
    review_conversion = (total_reviews / total_visits * 100) if total_visits > 0 else 0
    contact_conversion = (total_contacts / total_visits * 100) if total_visits > 0 else 0

    # Chart data
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    daily_visits = db.session.query(
        func.date(Visit.timestamp).label('date'),
        func.count(Visit.id).label('count')
    ).filter(Visit.timestamp >= seven_days_ago)\
     .group_by(func.date(Visit.timestamp))\
     .order_by(func.date(Visit.timestamp)).all()
    
    dates = [str(row.date) for row in daily_visits]
    visit_counts = [row.count for row in daily_visits]

    page_stats = db.session.query(
        Visit.page,
        func.count(Visit.id)
    ).group_by(Visit.page).order_by(func.count(Visit.id).desc()).all()
    
    page_names = [row[0] for row in page_stats]
    page_counts = [row[1] for row in page_stats]

    avg_rating = db.session.query(func.avg(Review.rating)).scalar() or 0

    return render_template('stats.html',
                           total_visits=total_visits,
                           unique_visitors=unique_visitors,
                           total_reviews=total_reviews,
                           total_contacts=total_contacts,
                           review_conversion=round(review_conversion, 2),
                           contact_conversion=round(contact_conversion, 2),
                           dates=json.dumps(dates),
                           visit_counts=json.dumps(visit_counts),
                           page_names=json.dumps(page_names),
                           page_counts=json.dumps(page_counts),
                           avg_rating=round(avg_rating, 1))

@app.route('/sitemap.xml')
def sitemap():
    sitemap_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>''' + request.url_root + '''</loc>
    <lastmod>''' + datetime.utcnow().strftime('%Y-%m-%d') + '''</lastmod>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>''' + request.url_root + '''#services</loc>
    <lastmod>''' + datetime.utcnow().strftime('%Y-%m-%d') + '''</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
  <url>
    <loc>''' + request.url_root + '''#reviews</loc>
    <lastmod>''' + datetime.utcnow().strftime('%Y-%m-%d') + '''</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.7</priority>
  </url>
  <url>
    <loc>''' + request.url_root + '''#contact</loc>
    <lastmod>''' + datetime.utcnow().strftime('%Y-%m-%d') + '''</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.6</priority>
  </url>
</urlset>'''
    return Response(sitemap_xml, mimetype='application/xml')

@app.route('/robots.txt')
def robots_txt():
    robots_txt = '''User-agent: *
Allow: /

Sitemap: ''' + request.url_root + '''sitemap.xml'''
    return Response(robots_txt, mimetype='text/plain')

if __name__ == '__main__':
    app.run(debug=True)
