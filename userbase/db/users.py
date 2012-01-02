import colander
import hashlib
import uuid
import datetime
from base import Record, Collection, DateTime
__all__ = ['User', 'Users']

class UserSchema(colander.MappingSchema):
    email = colander.SchemaNode(colander.String(), validator = colander.Email())
    username = colander.SchemaNode(colander.String(), validator = colander.Length(6,35))
    name = colander.SchemaNode(colander.String(), validator = colander.Length(6,200))
    password = colander.SchemaNode(colander.String(), validator = colander.Length(6))
    bio = colander.SchemaNode(colander.String(), missing="")
    state = colander.SchemaNode(colander.String(), missing="initialized")
    validation_code = colander.SchemaNode(colander.String(), missing="")
    pw_code = colander.SchemaNode(colander.String(), missing="")
    validation_code_sent = colander.SchemaNode(DateTime(), missing="")
    pw_code_sent = colander.SchemaNode(DateTime(), missing="")
    last_logged_in = colander.SchemaNode(DateTime(), missing="")

class User(Record):
    """A user record. 

    For validation we use the following workflow:

    initialized
        a new user has been created.
    code_sent
        a verification code has been sent to the user
    active
        a verification code has been validated. The user is full active

   
    Moreover we support a password verification code which is sent in order to set a new password.

    Both codes have a date stored on which they have been sent so we can check for timed validity.
    """
    
    schema = UserSchema()
    create_id = True

    def set_pw(self, pw):
        """store a password"""
        self.d.password = hashlib.new("md5",pw).hexdigest()
        return pw

    def gen_code(self):
        """generate a new validation code"""
        return unicode(uuid.uuid4())[:12]

    def send_validation_code(self, url_for):
        """generate and send a new validation code"""
        if self.d.state not in ("initialized", "code_sent"):
            # TODO: raise something here?
            return
        self.d.validation_code = self.gen_code()
        self.d.validation_code_sent = datetime.datetime.now()
        # TODO: actually sent the code
        self.d.state = "code_sent"
        valcode_link = url_for("validation", code = self.d.validation_code)
        self.collection.config.mail.mailer.mail("%s <%s>" %(self.d.name, self.d.email), "Registration", "welcome.txt",
            valcode = self.d.validation_code,
            valcode_link = valcode_link)

    def save(self):
        """save the object"""
        self.collection.put(self)

class Users(Collection):
    
    data_class = User
    use_objectids = False # does the mongodb collection use object ids?

    def by_email(self, email):
        """return a user by email or None"""
        q = self.query.update(email = email)
        res = q()
        if res.count==0:
            return None
        return res[0]

    def find_by_code(self, code):
        """return a User object by validation code"""
        q = self.query.update(validation_code = code)
        res = q()
        if res.count==0:
            return None
        return res[0]








