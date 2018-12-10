import click
from corvidae import app, bcrypt, db
from flask.cli import AppGroup
import corvidae.models as cmodels


user_cli = AppGroup('user')

@user_cli.command('hash')
@click.password_option()
def gen_pw_hash(password):
    hash = bcrypt.generate_password_hash(password, 10)
    print(hash.decode('utf-8'))


@user_cli.command('add')
@click.argument('email')
@click.argument('pw_hash')
@click.option('--flags', default='', help="comma-separated list of flags for the account")
@click.option('--make-handle', 'handle', default=False, help="Create a new handle for the newly created user")
def add_user(email, pw_hash, flags, handle):

    # Check that the email is not already used.
    maybe_user = cmodels.User.query.filter_by(email=email).one_or_none()
    if(maybe_user != None):
        print(f"There is already a user, {maybe_user.id} with email {email}!")
        import sys
        sys.exit(-1)
    
    # okay, at this point, we should be able to create a user. 
    # flags is comma-separated, so we should break that out. 
    split_flags = flags.split(',')

    user = cmodels.User()
    user.email = email
    user.db_flags = split_flags
    user.password = pw_hash
    
    db.session.add(user)

    # now, we add our handle 
    # Check that the handle doesn't already exist
    if(handle != False):
        
        maybe_handle = cmodels.Handle.query.filter_by(name=handle).one_or_none()
        if(maybe_handle != None):
            print(f"Handle {handle} already exists, cannot create duplicate!")
            import sys
            sys.exit(-1)
        else:
            handle = cmodels.Handle()
            handle.display_name = handle
            handle.name = handle
            handle.user = user

            db.session.add(handle)
    db.session.commit()
    
app.cli.add_command(user_cli)