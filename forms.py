from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, FileField, SubmitField
from wtforms.validators import DataRequired, Email

class LoginForm(FlaskForm):
    email = StringField("Email: ", validators=[Email()])
    password = PasswordField("Password: ", validators=[DataRequired()])
    submit = SubmitField("Submit")

class ImageUploadForm(FlaskForm):
    title = StringField('Image title: ', validators=[DataRequired()])
    image_file = FileField('Image file: ', validators=[DataRequired()])
    submit = SubmitField('Upload image')