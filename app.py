import os
from datetime import datetime

from flask import Flask, render_template, flash, redirect, url_for, request
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_uploads import configure_uploads, IMAGES, UploadSet
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from forms import LoginForm, ImageUploadForm
from api import FaceDetector

app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'secretkeyforthisappneedstobeprovidedhere'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:dk@PSG20@localhost:5432/face_app_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOADED_IMAGES_DEST'] = 'static/user_images'

db = SQLAlchemy(app)

manager = Manager(app)
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)

upload_set = UploadSet('images', IMAGES)
configure_uploads(app, upload_set)


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer(), primary_key=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    patronymic = db.Column(db.String(100))
    email = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(100), nullable=False)
    images_count = db.Column(db.Integer(), default=0)

    def __str__(self):
        return f'id: {self.id}. Email: {self.email}'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Image(db.Model):
    __tablename__ = 'images'
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    created_on = db.Column(db.DateTime(), default=datetime.utcnow)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))

    def __str__(self):
        return f'user id: {self.user_id}. {self.title} ({self.filename})'

    def get_upload_date(self):
        return self.created_on.strftime('%d.%m.%Y %H:%M')


class Detection(db.Model):
    __tablename__ = 'detections'
    id = db.Column(db.Integer(), primary_key=True)
    topleft_x = db.Column(db.Integer())
    topleft_y = db.Column(db.Integer())
    height = db.Column(db.Integer())
    width = db.Column(db.Integer())
    image_id = db.Column(db.Integer(), db.ForeignKey('images.id', ondelete='CASCADE'))

    def __str__(self):
        return f'image id: {self.image_id}, x: {self.topleft_x}, y: {self.topleft_y}, width: {self.width}, ' \
               f'height: {self.height}'


login_manager = LoginManager(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).get(user_id)


# views
@app.route('/login', methods=['post', 'get'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=True)
            flash('You have successfully logged in!', 'success')
            return redirect(url_for('home'))

        flash('Invalid username or password!', 'error')
        return redirect(url_for('login'))
    return render_template('login.html', form=form, title='Login page')


@app.route('/')
@login_required
def home():
    images = db.session.query(Image).filter(Image.user_id == current_user.id)
    images = images if images else []
    context = {
        'images': images,
        'upload_dir': app.config['UPLOADED_IMAGES_DEST'],
        'title': 'Home page',
    }
    return render_template('home.html', **context)


@app.route('/upload', methods=['post', 'get'])
@login_required
def upload():
    form = ImageUploadForm()
    if form.validate_on_submit():
        # save file
        safe_filename = secure_filename(form.image_file.data.filename)
        final_filename = f'{current_user.id}_{str(current_user.images_count + 1)}_{safe_filename}'
        upload_set.save(form.image_file.data, name=final_filename)

        # add image row in db
        image = Image()
        image.title = form.title.data
        image.filename = final_filename
        image.user_id = current_user.id
        db.session.add(image)
        db.session.commit()

        # update user uploaded images count
        current_user.images_count += 1

        # detect faces for current image and save data in db
        detector = FaceDetector(final_filename)
        result = detector.get_detections()
        data = result.get('data')
        if data:
            image_id = image.id
            detections_to_commit = []
            for item in data:
                detection = Detection()
                detection.topleft_x = item['x']
                detection.topleft_y = item['y']
                detection.width = item['width']
                detection.height = item['height']
                detection.image_id = image_id
                detections_to_commit.append(detection)

            if detections_to_commit:
                db.session.add_all(detections_to_commit)
                db.session.commit()

        flash(f'File {safe_filename} has been uploaded successfully!', 'success')
        return redirect(url_for('home'))
    return render_template('upload.html', form=form, title='Image upload page')


@app.route('/view/<int:image_id>', methods=['post', 'get'])
@login_required
def view(image_id):
    image = db.session.query(Image).get(image_id)
    if not image:
        flash('Image not found!', 'error')
        return redirect(url_for('home'))

    if request.method == 'POST':
        # delete existing rows for current image
        existing_detections = db.session.query(Detection).filter(Detection.image_id == image_id)
        for row in existing_detections:
            db.session.delete(row)

        # add new rows for current image
        image_data_to_save = request.json
        if image_data_to_save:
            detections_to_commit = []

            for item in image_data_to_save:
                detection = Detection()
                detection.topleft_x = item['x']
                detection.topleft_y = item['y']
                detection.width = item['width']
                detection.height = item['height']
                detection.image_id = image_id
                detections_to_commit.append(detection)

            if detections_to_commit:
                db.session.add_all(detections_to_commit)

        db.session.commit()

        flash('Image data has been successfully updated!', 'success')
        # return redirect(url_for('view', image_id=image_id))

    detections = db.session.query(Detection).filter(Detection.image_id == image.id)
    detections = detections if len(tuple(detections)) else None
    context = {
        'image': image,
        'upload_dir': app.config['UPLOADED_IMAGES_DEST'],
        'title': f'{image.title} (image view page)',
    }
    if detections:
        context['detections'] = detections

    return render_template('view.html', **context)


@app.route('/delete/<int:image_id>')
@login_required
def delete(image_id):
    image = db.session.query(Image).get(image_id)
    if not image:
        flash('Image not found!', 'error')
    else:
        image_filename = image.filename
        db.session.delete(image)
        db.session.commit()

        file_dir = app.config['UPLOADED_IMAGES_DEST']
        file_full_path = os.path.normpath(os.path.join(file_dir, image_filename))
        try:
            os.remove(file_full_path)
        except (FileNotFoundError, FileExistsError) as e:
            pass

        flash(f'Image {image_filename} has been deleted successfully!', 'success')

    return redirect(url_for('home'))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have logged out!', 'success')
    return redirect(url_for('login'))


if __name__ == '__main__':
    # manager.run()
    app.run()
