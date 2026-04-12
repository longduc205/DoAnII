"""
Task routes - Task management page
"""

from datetime import datetime, timezone
from flask import Blueprint, render_template, request, jsonify

from app import db
from app.models.task import Task

tasks_bp = Blueprint('tasks', __name__)


@tasks_bp.route('/')
def task_list():
    """Render the task management page."""
    tasks = Task.query.order_by(Task.phase, Task.day).all()
    return render_template('tasks.html', tasks=tasks)


@tasks_bp.route('/api/tasks', methods=['GET'])
def get_tasks():
    """API: Get all tasks as JSON."""
    tasks = Task.query.order_by(Task.phase, Task.day).all()
    return jsonify([task.to_dict() for task in tasks])


@tasks_bp.route('/api/tasks', methods=['POST'])
def create_tasks():
    """API: Create or seed tasks from TASKS.md data."""
    data = request.get_json()
    Task.query.delete()
    if isinstance(data, list):
        for item in data:
            task = Task(
                phase=item.get('phase', ''),
                day=item.get('day', ''),
                title=item.get('title', ''),
                description=item.get('description', ''),
                status=item.get('status', 'pending')
            )
            db.session.add(task)
    else:
        task = Task(
            phase=data.get('phase', ''),
            day=data.get('day', ''),
            title=data.get('title', ''),
            description=data.get('description', ''),
            status=data.get('status', 'pending')
        )
        db.session.add(task)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Tasks created'}), 201


@tasks_bp.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    """API: Update task status."""
    task = Task.query.get_or_404(task_id)
    data = request.get_json()

    task.status = data.get('status', task.status)
    if task.status == 'done':
        task.completed_at = datetime.now(timezone.utc)
    elif task.status != 'done' and task.completed_at:
        task.completed_at = None

    db.session.commit()
    return jsonify({'success': True, 'task': task.to_dict()})


@tasks_bp.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """API: Delete a task."""
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return jsonify({'success': True})


@tasks_bp.route('/api/tasks/reset', methods=['POST'])
def reset_tasks():
    """API: Reset all tasks to pending."""
    Task.query.update({'status': 'pending', 'completed_at': None})
    db.session.commit()
    return jsonify({'success': True, 'message': 'All tasks reset'})
