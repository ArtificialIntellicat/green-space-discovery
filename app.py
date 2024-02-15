from flask import Flask, render_template, request, redirect, flash, url_for
from urllib.parse import urlparse, urljoin
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
import os
import time
from sqlalchemy.sql import func
from datetime import datetime
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from forms import RegistrationForm, LoginForm, ChangeLoginForm, AddSpaceForm, RatingForm
from db_models import User, Space, db, Rating
from config import Config

# App and Database Setup
app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

def create_database(app):
    with app.app_context():
        db.create_all()
login_manager = LoginManager(app)
login_manager.login_view = 'login'
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

@app.context_processor
def inject_login_form():
    form = LoginForm()
    return dict(form=form)

# INDEX
from sqlalchemy.sql import func

@app.route('/', methods=['GET', 'POST'])
def index():
    spaces = Space.query.order_by(Space.date_created.desc()).all()
    #ratings = Rating.query.with_entities(
    #    Rating.space_id,
    #    func.avg((Rating.cleanliness + Rating.facilities + Rating.accessibility + Rating.natural_diversity + Rating.eco_friendly_practices + Rating.safety_security + Rating.recreational_opportunities + Rating.community_engagement + Rating.educational_value + Rating.scenic_beauty)/10).label('average_rating'),
    #    Rating.text
    #).group_by(Rating.space_id).all()

    # Prepare rating data for display
    #rating_info = {r.space_id: {'text': r.text[:50], 'average_rating': round(r.average_rating)} for r in ratings}
    rating_info = 0

    return render_template('index.html', spaces=spaces, rating_info=rating_info)

# USER LOGIN
def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            next_page = form.next.data
            if next_page and is_safe_url(next_page):
                print("next")
                return redirect(next_page)
            print("Index")
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password', 'error')

    return render_template('login.html', form=form)

# USER LOGOUT
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

# USER ACTIONS
@app.route('/user_profile')
@login_required  # This decorator ensures that the route is accessible only when the user is logged in
def user_profile():
    return render_template('user.html', user=current_user)

@app.route('/change_login_data', methods=['GET', 'POST'])
@login_required
def change_login_data():
    form = ChangeLoginForm()
    user = current_user
    if form.validate_on_submit():
        change_made = False

        # Check and update username
        if form.username.data and form.username.data != user.username:
            existing_user = User.query.filter_by(username=form.username.data).first()
            if existing_user:
                print("Username already taken.")
                flash('Username already taken.', 'error')
            else:
                user.username = form.username.data
                print(form.username.data)
                change_made = True

        # Check and update email
        if form.email.data and form.email.data != user.email:
            existing_user = User.query.filter_by(email=form.email.data).first()
            if existing_user:
                flash('Email already taken.', 'error')
            else:
                user.email = form.email.data
                change_made = True

        # Update password
        if form.password.data:
            user.set_password(form.password.data)
            change_made = True

        # Commit changes to database and redirect
        if change_made:
            db.session.commit()
            flash('Your login data has been updated.', 'success')
            return redirect(url_for('user_profile'))
        else:
            flash('No changes were made.', 'info')
    else:
        print("Form errors:", form.errors)  # Print detailed form errors

    return render_template('change_login_data.html', form=form, user=current_user)


# USER REGISTRATION
@app.route('/registration', methods=['GET', 'POST'])
def registration():
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = User.query.filter(
            (User.username == form.username.data) | (User.email == form.email.data)).first()
        if existing_user:
            flash('Username or email already exists. Please choose a different one.', 'error')
            return render_template('registration.html', form=form)

        # hashed_password = generate_password_hash(form.password.data)
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        # Handle profile picture upload
        if form.profile_pic.data:
            ext = form.profile_pic.data.filename.rsplit('.', 1)[1]
            filename = f"{form.username.data}_{int(time.time())}.{ext}"
            form.profile_pic.data.save(os.path.join(app.config['UPLOAD_FOLDER'], 'user_profile_pics', filename))
            user.profile_pic = filename

        try:
            db.session.add(user)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash('Error: Unable to create user.')
            app.logger.error(f'Error creating user: {e}')

        return render_template('user.html', user=user)

    else:
        for fieldName, errorMessages in form.errors.items():
            for err in errorMessages:
                flash(f"{fieldName}: {err}", 'error')
    return render_template('registration.html', form=form)

# ADD SPACE
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

@app.route('/add_space', methods=['GET', 'POST'])
@login_required
def add_space():
    form = AddSpaceForm()
    if form.validate_on_submit():
        base_folder_name = secure_filename(form.name.data.replace(" ", "_")).lower()
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        space_folder_name = f"{base_folder_name}_{timestamp}"
        space_folder_path = os.path.join(app.config['UPLOAD_FOLDER'], 'spaces', space_folder_name)
        os.makedirs(space_folder_path, exist_ok=True)

        filenames = []
        for file in request.files.getlist('photos'):
            if file and allowed_file(file.filename):
                ext = file.filename.rsplit('.', 1)[1].lower()
                photo_timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
                filename = f"{base_folder_name}_{photo_timestamp}.{ext}"
                file.save(os.path.join(space_folder_path, filename))
                web_path = f"uploads/spaces/{space_folder_name}/{filename}"
                filenames.append(web_path)

        new_space = Space(
            name=form.name.data,
            address=form.address.data,
            description=form.description.data,
            photos=','.join(filenames),
            user_id=current_user.id,
            user_name=current_user.username
        )

        try:
            db.session.add(new_space)
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue adding the space.'
    return render_template('add_space.html', form=form)

# DELETE SPACE
@app.route('/delete_space/<int:space_id>', methods=['POST'])
@login_required
def delete_space(space_id):
    space = Space.query.get_or_404(space_id)
    if space.user_id != current_user.id:
        flash('You do not have permission to delete this space.', 'error')
        return redirect(url_for('index'))

    try:
        # Delete associated ratings
        ratings = Rating.query.filter_by(space_id=space_id).all()
        for rating in ratings:
            db.session.delete(rating)

        # Delete associated files (photos)
        if space.photos:
            for photo in space.photos.split(','):
                photo_path = os.path.join(app.static_folder, photo)
                if os.path.exists(photo_path):
                    os.remove(photo_path)
            # Remove the folder if empty
            folder_path = os.path.dirname(os.path.join(app.static_folder, space.photos.split(',')[0]))
            if os.path.exists(folder_path) and not os.listdir(folder_path):
                os.rmdir(folder_path)

        # Finally, delete the space
        db.session.delete(space)
        db.session.commit()
        flash('Space and associated ratings deleted successfully.', 'success')
    except Exception as e:
        flash('Error occurred while deleting space and associated ratings.', 'error')
        app.logger.error(f"Error deleting space and ratings: {e}")

    return redirect(url_for('index'))

# SPACE DETAILS
@app.route('/space_details/<int:space_id>', methods=['GET', 'POST'])
def space_details(space_id):
    space = Space.query.get_or_404(space_id)
    ratings = Rating.query.filter_by(space_id=space_id).all()
    ratingform = RatingForm()
    return render_template('space_details.html', space=space, ratings=ratings, ratingform=ratingform)

# RATE SPACE
@app.route('/add_rating/<int:space_id>', methods=['GET', 'POST'])
@login_required
def add_rating(space_id):
    form = RatingForm()
    if form.validate_on_submit():
        new_rating = Rating(
            cleanliness=form.cleanliness.data,
            facilities=form.facilities.data,
            accessibility=form.accessibility.data,
            natural_diversity=form.natural_diversity.data,
            eco_friendly_practices=form.eco_friendly_practices.data,
            safety_security=form.safety_security.data,
            recreational_opportunities=form.recreational_opportunities.data,
            community_engagement=form.community_engagement.data,
            educational_value=form.educational_value.data,
            scenic_beauty=form.scenic_beauty.data,
            text=form.text.data,
            space_id=space_id,
            user_id=current_user.id,
            user_name=current_user.username
        )
        try:
            db.session.add(new_rating)
            db.session.commit()
            flash('Your rating was added successfully.', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Error occurred while adding rating.', 'error')
            app.logger.error(f"Error addind space: {e}")
        return redirect(url_for('space_details', space_id=space_id))
    form.space_id.data = space_id
    return render_template(url_for('space_details', space_id=space_id), ratingform=form)

# DELETE RATING
@app.route('/delete_rating/<int:rating_id>', methods=['GET', 'POST'])
@login_required
def delete_rating(rating_id):
    rating = Rating.query.get_or_404(rating_id)
    if rating.user_id != current_user.id:
        flash('You do not have permission to delete this space.', 'error')
        return redirect(url_for('index'))

    try:
        db.session.delete(rating)
        db.session.commit()
        flash('Your rating was deleted successfully.', 'success')
    except Exception as e:
        flash('Error occurred while deleting rating.', 'error')
        app.logger.error(f"Error deleting space: {e}")

    return redirect(url_for('index'))

if __name__ == '__main__':
    create_database(app)
    app.run(debug=True)
