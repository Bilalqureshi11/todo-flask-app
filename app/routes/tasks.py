from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app import db
from app.models import Task
from app.routes.auth import login_required

task_bp = Blueprint('tasks', __name__)


@task_bp.route('/')
@login_required
def view_task():
    """
    Display all tasks for the currently logged-in user.
    """
    user_id = session.get('user_id')
    
    # Get only the current user's tasks
    tasks = Task.query.filter_by(user_id=user_id).order_by(Task.created_at.desc()).all()
    
    # Calculate task statistics
    total_tasks = len(tasks)
    pending_tasks = sum(1 for task in tasks if task.status == 'Pending')
    working_tasks = sum(1 for task in tasks if task.status == 'Working')
    completed_tasks = sum(1 for task in tasks if task.status == 'Done')
    
    return render_template('tasks.html', 
                         tasks=tasks,
                         total_tasks=total_tasks,
                         pending_tasks=pending_tasks,
                         working_tasks=working_tasks,
                         completed_tasks=completed_tasks)


@task_bp.route('/add', methods=['POST'])
@login_required
def add_task():
    """
    Add a new task for the current user with validation.
    """
    user_id = session.get('user_id')
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    
    # Validation
    if not title:
        flash('Task title is required', 'danger')
        return redirect(url_for('tasks.view_task'))
    
    if len(title) > 200:
        flash('Task title must be less than 200 characters', 'danger')
        return redirect(url_for('tasks.view_task'))
    
    try:
        # Create new task
        new_task = Task(
            title=title,
            description=description if description else None,
            status='Pending',
            user_id=user_id
        )
        
        db.session.add(new_task)
        db.session.commit()
        flash('Task added successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('Error adding task. Please try again.', 'danger')
        print(f"Add task error: {str(e)}")
    
    return redirect(url_for('tasks.view_task'))


@task_bp.route('/edit/<int:task_id>', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    """
    Edit an existing task (only if it belongs to the current user).
    """
    user_id = session.get('user_id')
    task = Task.query.filter_by(id=task_id, user_id=user_id).first()
    
    if not task:
        flash('Task not found or you do not have permission to edit it', 'danger')
        return redirect(url_for('tasks.view_task'))
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        
        # Validation
        if not title:
            flash('Task title is required', 'danger')
            return redirect(url_for('tasks.edit_task', task_id=task_id))
        
        if len(title) > 200:
            flash('Task title must be less than 200 characters', 'danger')
            return redirect(url_for('tasks.edit_task', task_id=task_id))
        
        try:
            task.title = title
            task.description = description if description else None
            db.session.commit()
            flash('Task updated successfully!', 'success')
            return redirect(url_for('tasks.view_task'))
            
        except Exception as e:
            db.session.rollback()
            flash('Error updating task. Please try again.', 'danger')
            print(f"Edit task error: {str(e)}")
            return redirect(url_for('tasks.edit_task', task_id=task_id))
    
    return render_template('edit_task.html', task=task)


@task_bp.route('/toggle/<int:task_id>', methods=['POST'])
@login_required
def toggle_status(task_id):
    """
    Toggle task status: Pending -> Working -> Done -> Pending
    Only allows users to toggle their own tasks.
    """
    user_id = session.get('user_id')
    task = Task.query.filter_by(id=task_id, user_id=user_id).first()
    
    if not task:
        flash('Task not found or you do not have permission to modify it', 'danger')
        return redirect(url_for('tasks.view_task'))
    
    try:
        # Cycle through statuses
        if task.status == 'Pending':
            task.status = 'Working'
            flash(f'Task "{task.title}" is now in progress', 'info')
        elif task.status == 'Working':
            task.status = 'Done'
            flash(f'Task "{task.title}" completed!', 'success')
        else:  # Done
            task.status = 'Pending'
            flash(f'Task "{task.title}" reopened', 'info')
        
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
        flash('Error updating task status', 'danger')
        print(f"Toggle status error: {str(e)}")
    
    return redirect(url_for('tasks.view_task'))


@task_bp.route('/delete/<int:task_id>', methods=['POST'])
@login_required
def delete_task(task_id):
    """
    Delete a specific task (only if it belongs to the current user).
    """
    user_id = session.get('user_id')
    task = Task.query.filter_by(id=task_id, user_id=user_id).first()
    
    if not task:
        flash('Task not found or you do not have permission to delete it', 'danger')
        return redirect(url_for('tasks.view_task'))
    
    try:
        task_title = task.title
        db.session.delete(task)
        db.session.commit()
        flash(f'Task "{task_title}" deleted successfully', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('Error deleting task. Please try again.', 'danger')
        print(f"Delete task error: {str(e)}")
    
    return redirect(url_for('tasks.view_task'))


@task_bp.route('/clear', methods=['POST'])
@login_required
def clear_tasks():
    """
    Delete all tasks for the current user.
    """
    user_id = session.get('user_id')
    
    try:
        # Delete only the current user's tasks
        tasks_to_delete = Task.query.filter_by(user_id=user_id).all()
        task_count = len(tasks_to_delete)
        
        if task_count == 0:
            flash('No tasks to clear', 'info')
            return redirect(url_for('tasks.view_task'))
        
        Task.query.filter_by(user_id=user_id).delete()
        db.session.commit()
        flash(f'{task_count} task(s) cleared successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('Error clearing tasks. Please try again.', 'danger')
        print(f"Clear tasks error: {str(e)}")
    
    return redirect(url_for('tasks.view_task'))


@task_bp.route('/clear-completed', methods=['POST'])
@login_required
def clear_completed():
    """
    Delete all completed tasks for the current user.
    """
    user_id = session.get('user_id')
    
    try:
        # Delete only completed tasks for current user
        completed_tasks = Task.query.filter_by(user_id=user_id, status='Done').all()
        task_count = len(completed_tasks)
        
        if task_count == 0:
            flash('No completed tasks to clear', 'info')
            return redirect(url_for('tasks.view_task'))
        
        Task.query.filter_by(user_id=user_id, status='Done').delete()
        db.session.commit()
        flash(f'{task_count} completed task(s) cleared!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('Error clearing completed tasks. Please try again.', 'danger')
        print(f"Clear completed tasks error: {str(e)}")
    
    return redirect(url_for('tasks.view_task'))


@task_bp.route('/filter/<status>')
@login_required
def filter_tasks(status):
    """
    Filter tasks by status (Pending, Working, Done).
    """
    user_id = session.get('user_id')
    
    valid_statuses = ['Pending', 'Working', 'Done', 'All']
    
    if status not in valid_statuses:
        flash('Invalid filter option', 'danger')
        return redirect(url_for('tasks.view_task'))
    
    if status == 'All':
        tasks = Task.query.filter_by(user_id=user_id).order_by(Task.created_at.desc()).all()
    else:
        tasks = Task.query.filter_by(user_id=user_id, status=status).order_by(Task.created_at.desc()).all()
    
    # Calculate task statistics
    all_tasks = Task.query.filter_by(user_id=user_id).all()
    total_tasks = len(all_tasks)
    pending_tasks = sum(1 for task in all_tasks if task.status == 'Pending')
    working_tasks = sum(1 for task in all_tasks if task.status == 'Working')
    completed_tasks = sum(1 for task in all_tasks if task.status == 'Done')
    
    return render_template('tasks.html', 
                         tasks=tasks,
                         total_tasks=total_tasks,
                         pending_tasks=pending_tasks,
                         working_tasks=working_tasks,
                         completed_tasks=completed_tasks,
                         current_filter=status)
