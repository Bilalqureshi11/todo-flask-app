"""
Database Migration Script for Todo Flask App
"""

from app import create_app, db
from app.models import User, Task
from datetime import datetime

def migrate_database():
    """Migrate the database schema to add new columns."""
    app = create_app()
    
    with app.app_context():
        print("Starting database migration...")
        
        try:
            # Try to inspect existing columns
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            
            # Check Task table columns
            task_columns = [col['name'] for col in inspector.get_columns('task')]
            print(f"Current Task columns: {task_columns}")
            
            # Add missing columns
            with db.engine.connect() as conn:
                if 'description' not in task_columns:
                    print("Adding 'description' column...")
                    conn.execute(db.text('ALTER TABLE task ADD COLUMN description TEXT'))
                    conn.commit()
                
                if 'created_at' not in task_columns:
                    print("Adding 'created_at' column...")
                    conn.execute(db.text(f"ALTER TABLE task ADD COLUMN created_at DATETIME DEFAULT '{datetime.utcnow()}'"))
                    conn.commit()
                
                if 'updated_at' not in task_columns:
                    print("Adding 'updated_at' column...")
                    conn.execute(db.text(f"ALTER TABLE task ADD COLUMN updated_at DATETIME DEFAULT '{datetime.utcnow()}'"))
                    conn.commit()
                
                if 'user_id' not in task_columns:
                    print("Adding 'user_id' column...")
                    conn.execute(db.text('ALTER TABLE task ADD COLUMN user_id INTEGER'))
                    conn.commit()
                    
                    # Assign existing tasks to first user
                    first_user = User.query.first()
                    if first_user:
                        print(f"Assigning tasks to user: {first_user.username}")
                        conn.execute(db.text(f'UPDATE task SET user_id = {first_user.id} WHERE user_id IS NULL'))
                        conn.commit()
            
            # Check User table
            user_columns = [col['name'] for col in inspector.get_columns('user')]
            print(f"Current User columns: {user_columns}")
            
            with db.engine.connect() as conn:
                if 'created_at' not in user_columns:
                    print("Adding 'created_at' column to User table...")
                    conn.execute(db.text(f"ALTER TABLE user ADD COLUMN created_at DATETIME DEFAULT '{datetime.utcnow()}'"))
                    conn.commit()
            
            print("\n✅ Migration completed successfully!")
            
        except Exception as e:
            print(f"\n❌ Migration failed: {str(e)}")
            raise


def fresh_database():
    """Create a fresh database (deletes all data!)."""
    app = create_app()
    
    with app.app_context():
        print("⚠️  WARNING: This will delete all existing data!")
        confirm = input("Type 'YES' to continue: ")
        
        if confirm == 'YES':
            print("Dropping all tables...")
            db.drop_all()
            
            print("Creating new tables...")
            db.create_all()
            
            print("✅ Fresh database created successfully!")
        else:
            print("❌ Operation cancelled.")


if __name__ == '__main__':
    print("=" * 60)
    print("Todo Flask App - Database Migration")
    print("=" * 60)
    print("\nOptions:")
    print("1. Migrate existing database (preserves data)")
    print("2. Create fresh database (DELETES all data)")
    print("3. Cancel")
    
    choice = input("\nEnter your choice (1/2/3): ")
    
    if choice == '1':
        migrate_database()
    elif choice == '2':
        fresh_database()
    else:
        print("Operation cancelled.")