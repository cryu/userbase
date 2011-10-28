from starflyer import Application, asjson, ashtml
from werkzeug.routing import Map, Rule, NotFound, RequestRedirect
from framework import Handler
import werkzeug.wsgi
import os
from db import User

import setup

from wtforms import Form, TextField, validators, TextAreaField, PasswordField

class RegistrationForm(Form):
    name        = TextField('Ihr Name', [validators.Length(min=6, max=35)])
    email       = TextField('Ihre Email-Adresse', [validators.Length(min=6, max=35), validators.Email()])
    password    = PasswordField('Passwort', [validators.Length(min=6, max=35)])
    password2   = PasswordField('Passwort Wiederholung', [validators.Length(min=6, max=35)])
    bio         = TextAreaField('Bio (optional)')


class RegistrationView(Handler):
    """an index handler"""

    template = "master/registration.html"

    @ashtml()
    def get(self):
        """show the registration form"""

        # TODO: check if user exists via WTForms
        # TODO: send validation mail
        # TODO: add updated and created and workflow state
        form = RegistrationForm(self.request.form)
        if self.request.method == 'POST' and form.validate():       
            # TODO: check email availability in db model or widget validator?
            if self.settings.db_users.by_email(form.email.data) is not None:
                return ""
            user = User(form.data, settings = settings)
            user.set_pw(form.password.data)
            user = self.settings.db_users.put(user)
            user.send_validation_code()
            user = self.settings.db_users.put(user)
            raise self.redirect(self.url_for('registered'))
        return self.render(form=form)

    post = get


class ValidationView(Handler):
    """validate data from the registration form via AJAX"""

    @asjson()
    def get(self):
        args = self.request.values
        if "email" in args:
            email = args['email']
            if self.settings.db_users.by_email(email) is not None:
                return "Diese E-Mail-Adresse ist schon registriert."
        return True

class RegisteredView(Handler):
    """an index handler"""

    template = "master/registered.html"
