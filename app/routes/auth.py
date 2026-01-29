from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from app import db
from app.models import User


auth_bp = Blueprint('auth', __name__)


# Login required decorator
def login_required(f):
    """
    Decorator to protect routes that require authentication.
    Redirects to login page if user is not logged in.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    Handle user registration with validation and error handling.
    """
    # Redirect if user is already logged in
    if 'user_id' in session:
        return redirect(url_for('tasks.view_task'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Input validation
        if not username:
            flash('Username is required', 'danger')
            return redirect(url_for('auth.register'))
        
        if not password:
            flash('Password is required', 'danger')
            return redirect(url_for('auth.register'))
        
        # Username length validation
        if len(username) < 3:
            flash('Username must be at least 3 characters long', 'danger')
            return redirect(url_for('auth.register'))
        
        if len(username) > 50:
            flash('Username must be less than 50 characters', 'danger')
            return redirect(url_for('auth.register'))
        
        # Password strength validation
        if len(password) < 6:
            flash('Password must be at least 6 characters long', 'danger')
            return redirect(url_for('auth.register'))
        
        # Password confirmation (if you have this field in your form)
        if confirm_password and password != confirm_password:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('auth.register'))
        
        # Check if username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists. Please choose a different one.', 'danger')
            return redirect(url_for('auth.register'))
        
        try:
            # Create new user with hashed password
            hashed_password = generate_password_hash(password, method='scrypt')
            new_user = User(username=username, password=hashed_password)
            
            # Add to database
            db.session.add(new_user)
            db.session.commit()
            
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration. Please try again.', 'danger')
            # Log the error for debugging (optional)
            print(f"Registration error: {str(e)}")
            return redirect(url_for('auth.register'))
    
    return render_template('register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handle user login with validation and error handling.
    """
    # Redirect if user is already logged in
    if 'user_id' in session:
        return redirect(url_for('tasks.view_task'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        # Input validation
        if not username or not password:
            flash('Username and password are required', 'danger')
            return redirect(url_for('auth.login'))
        
        try:
            # Query user from database
            user = User.query.filter_by(username=username).first()
            
            # Verify user exists and password is correct
            if user and check_password_hash(user.password, password):
                # Store user ID in session (more secure than username)
                session['user_id'] = user.id
                session['username'] = user.username
                session.permanent = True  # Make session permanent (optional)
                
                flash(f'Welcome back, {user.username}!', 'success')
                
                # Redirect to next page if specified, otherwise to dashboard
                next_page = request.args.get('next')
                if next_page:
                    return redirect(next_page)
                return redirect(url_for('tasks.view_task'))
            else:
                flash('Invalid username or password', 'danger')
                
        except Exception as e:
            flash('An error occurred during login. Please try again.', 'danger')
            # Log the error for debugging (optional)
            print(f"Login error: {str(e)}")
    
    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """
    Handle user logout and clear session.
    """
    username = session.get('username', 'User')
    
    # Clear all session data
    session.clear()
    
    flash(f'Goodbye, {username}! You have been logged out.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/profile')
@login_required
def profile():
    """
    Display user profile page (optional - you can add this if needed).
    """
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    
    if not user:
        flash('User not found', 'danger')
        return redirect(url_for('auth.logout'))
    
    return render_template('profile.html', user=user)


# Optional: Password reset/change functionality
@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """
    Allow logged-in users to change their password.
    """
    if request.method == 'POST':
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Get current user
        user_id = session.get('user_id')
        user = User.query.get(user_id)
        
        if not user:
            flash('User not found', 'danger')
            return redirect(url_for('auth.logout'))
        
        # Validate current password
        if not check_password_hash(user.password, current_password):
            flash('Current password is incorrect', 'danger')
            return redirect(url_for('auth.change_password'))
        
        # Validate new password
        if len(new_password) < 6:
            flash('New password must be at least 6 characters long', 'danger')
            return redirect(url_for('auth.change_password'))
        
        if new_password != confirm_password:
            flash('New passwords do not match', 'danger')
            return redirect(url_for('auth.change_password'))
        
        try:
            # Update password
            user.password = generate_password_hash(new_password, method='scrypt')
            db.session.commit()
            
            flash('Password changed successfully!', 'success')
            return redirect(url_for('tasks.view_task'))
            
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while changing password', 'danger')
            print(f"Password change error: {str(e)}")
            return redirect(url_for('auth.change_password'))
    
    return render_template('change_password.html')

        