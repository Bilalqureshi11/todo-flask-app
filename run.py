from app import create_app, db
from app.models import Task, User

app = create_app()

# Create database tables if they don't exist
with app.app_context():
    db.create_all()
    print("✅ Database tables created/verified successfully!")


# Optional: Flask CLI commands for database management
@app.cli.command()
def init_db():
    """Initialize the database."""
    db.create_all()
    print("✅ Database initialized!")


@app.cli.command()
def drop_db():
    """Drop all database tables."""
    if input("Are you sure you want to drop all tables? (yes/no): ").lower() == 'yes':
        db.drop_all()
        print("✅ All tables dropped!")
    else:
        print("❌ Operation cancelled.")


@app.cli.command()
def reset_db():
    """Drop and recreate all database tables."""
    if input("Are you sure you want to reset the database? (yes/no): ").lower() == 'yes':
        db.drop_all()
        db.create_all()
        print("✅ Database reset successfully!")
    else:
        print("❌ Operation cancelled.")


@app.cli.command()
def create_test_user():
    """Create a test user for development."""
    from werkzeug.security import generate_password_hash
    
    username = input("Enter username (default: testuser): ") or "testuser"
    password = input("Enter password (default: password123): ") or "password123"
    
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        print(f"❌ User '{username}' already exists!")
        return
    
    user = User(
        username=username,
        password=generate_password_hash(password, method='scrypt')
    )
    db.session.add(user)
    db.session.commit()
    
    print(f"✅ Test user created!")
    print(f"   Username: {username}")
    print(f"   Password: {password}")


@app.cli.command()
def list_users():
    """List all users in the database."""
    users = User.query.all()
    if not users:
        print("No users found in database.")
        return
    
    print(f"\n{'ID':<5} {'Username':<20} {'Tasks':<10} {'Created At'}")
    print("-" * 60)
    for user in users:
        task_count = len(user.tasks)
        created = user.created_at.strftime('%Y-%m-%d %H:%M') if hasattr(user, 'created_at') and user.created_at else 'N/A'
        print(f"{user.id:<5} {user.username:<20} {task_count:<10} {created}")


@app.cli.command()
def list_tasks():
    """List all tasks in the database."""
    tasks = Task.query.all()
    if not tasks:
        print("No tasks found in database.")
        return
    
    print(f"\n{'ID':<5} {'Title':<30} {'Status':<12} {'User':<15}")
    print("-" * 70)
    for task in tasks:
        title = task.title[:27] + '...' if len(task.title) > 30 else task.title
        username = task.user.username if hasattr(task, 'user') and task.user else 'N/A'
        print(f"{task.id:<5} {title:<30} {task.status:<12} {username:<15}")


@app.cli.command()
def seed_db():
    """Seed the database with sample data."""
    from werkzeug.security import generate_password_hash
    from datetime import datetime, timedelta
    
    print("Seeding database with sample data...")
    
    # Create test users
    users_data = [
        {'username': 'john', 'password': 'password123'},
        {'username': 'jane', 'password': 'password123'},
    ]
    
    users = []
    for user_data in users_data:
        existing = User.query.filter_by(username=user_data['username']).first()
        if not existing:
            user = User(
                username=user_data['username'],
                password=generate_password_hash(user_data['password'], method='scrypt')
            )
            db.session.add(user)
            users.append(user)
            print(f"   ✓ Created user: {user_data['username']}")
        else:
            users.append(existing)
            print(f"   - User already exists: {user_data['username']}")
    
    db.session.commit()
    
    # Create sample tasks
    sample_tasks = [
        {'title': 'Complete project documentation', 'description': 'Write comprehensive docs', 'status': 'Working'},
        {'title': 'Review pull requests', 'description': 'Check team PRs', 'status': 'Pending'},
        {'title': 'Setup CI/CD pipeline', 'description': 'Configure GitHub Actions', 'status': 'Done'},
        {'title': 'Update dependencies', 'description': 'Update npm packages', 'status': 'Pending'},
        {'title': 'Fix bug in login', 'description': 'Session timeout issue', 'status': 'Working'},
    ]
    
    for i, task_data in enumerate(sample_tasks):
        user = users[i % len(users)]
        task = Task(
            title=task_data['title'],
            description=task_data.get('description'),
            status=task_data['status'],
            user_id=user.id
        )
        db.session.add(task)
        print(f"   ✓ Created task: {task_data['title']} (for {user.username})")
    
    db.session.commit()
    print("\n✅ Database seeded successfully!")
    print("\nTest credentials:")
    print("   Username: john / Password: password123")
    print("   Username: jane / Password: password123")


# Shell context for easier debugging
@app.shell_context_processor
def make_shell_context():
    """Make database objects available in Flask shell."""
    return {
        'db': db,
        'User': User,
        'Task': Task
    }


if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Starting Flask Todo App")
    print("=" * 60)
    print(f"📍 Server running at: http://127.0.0.1:5000")
    print(f"📍 Login page: http://127.0.0.1:5000/auth/login")
    print(f"📍 Register page: http://127.0.0.1:5000/auth/register")
    print("=" * 60)
    print("\n💡 Tip: Press CTRL+C to stop the server\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)