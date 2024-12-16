# forms.py: เก็บฟอร์มทั้งหมดที่ใช้ในแอป
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, ValidationError

# Register Form
class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=50)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Register')

    def validate_password(self, password):
        if self.password.data != self.confirm_password.data:
            raise ValidationError('Passwords must match.')

# Login Form
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

# Create Form
class CreateForm(FlaskForm):
    create_date = StringField("Create Date", validators=[DataRequired()])
    work_order = StringField("Work Order", validators=[DataRequired()])
    equipment = StringField("Equipment", validators=[DataRequired()])
    description = TextAreaField("Description", validators=[DataRequired()])
    location = StringField("Location", validators=[DataRequired()])
    report_by = StringField("Report By", validators=[DataRequired()])
    status = SelectField("Status", choices=[("Open", "Open"), ("Closed", "Closed")], validators=[DataRequired()])
    action = TextAreaField("Action", validators=[DataRequired()])
    link = StringField("Link", validators=[DataRequired()])
    submit = SubmitField("Submit")

# Edit Form
class EditForm(FlaskForm):
    create_date = StringField("Create Date", validators=[DataRequired()])
    work_order = StringField("Work Order", validators=[DataRequired()])
    equipment = StringField("Equipment", validators=[DataRequired()])
    description = TextAreaField("Description", validators=[DataRequired()])
    location = StringField("Location", validators=[DataRequired()])
    report_by = StringField("Report By", validators=[DataRequired()])
    status = SelectField("Status", choices=[("Open", "Open"), ("Closed", "Closed")], validators=[DataRequired()])
    action = TextAreaField("Action", validators=[DataRequired()])
    link = StringField("Link", validators=[DataRequired()])
    submit = SubmitField("Submit")
