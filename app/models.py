from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    """
    User model for authentication and task ownership.
    """
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship: One user can have many tasks
    tasks = db.relationship('Task', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def set_password(self, password):
        """Hash and set the user's password."""
        self.password = generate_password_hash(password, method='scrypt')
    
    def check_password(self, password):
        """Check if the provided password matches the hashed password."""
        return check_password_hash(self.password, password)
    
    def get_task_count(self):
        """Get the total number of tasks for this user."""
        return len(self.tasks)
    
    def get_completed_task_count(self):
        """Get the number of completed tasks for this user."""
        return sum(1 for task in self.tasks if task.status == 'Done')


class Task(db.Model):
    """
    Task model for todo items.
    """
    __tablename__ = 'task'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='Pending', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Foreign key to link task to user
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    
    def __repr__(self):
        return f'<Task {self.title} - {self.status}>'
    
    def is_pending(self):
        """Check if the task is pending."""
        return self.status == 'Pending'
    
    def is_working(self):
        """Check if the task is in progress."""
        return self.status == 'Working'
    
    def is_done(self):
        """Check if the task is completed."""
        return self.status == 'Done'
    
    def mark_as_pending(self):
        """Mark the task as pending."""
        self.status = 'Pending'
    
    def mark_as_working(self):
        """Mark the task as in progress."""
        self.status = 'Working'
    
    def mark_as_done(self):
        """Mark the task as completed."""
        self.status = 'Done'
    
    def toggle_status(self):
        """Toggle task status: Pending -> Working -> Done -> Pending."""
        if self.status == 'Pending':
            self.status = 'Working'
        elif self.status == 'Working':
            self.status = 'Done'
        else:
            self.status = 'Pending'
        return self.status
