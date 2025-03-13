from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Todo
from .forms import TodoForm

# Create your views here.

def todo_list(request):
    # Get filter parameters
    goal_type_filter = request.GET.get('goal_type', '')
    
    # Apply filters
    if goal_type_filter and goal_type_filter in ['daily', 'weekly', 'monthly', 'yearly']:
        todos = Todo.objects.filter(goal_type=goal_type_filter)
    else:
        todos = Todo.objects.all()
    
    form = TodoForm()
    
    # Calculate progress statistics for each goal type
    goal_stats = {
        'daily': {'total': 0, 'completed': 0, 'progress': 0},
        'weekly': {'total': 0, 'completed': 0, 'progress': 0},
        'monthly': {'total': 0, 'completed': 0, 'progress': 0},
        'yearly': {'total': 0, 'completed': 0, 'progress': 0},
    }
    
    # Get all todos for statistics (regardless of filter)
    all_todos = Todo.objects.all()
    for todo in all_todos:
        goal_type = todo.goal_type
        goal_stats[goal_type]['total'] += 1
        if todo.completed:
            goal_stats[goal_type]['completed'] += 1
        goal_stats[goal_type]['progress'] += todo.progress
    
    # Calculate average progress for each goal type
    for goal_type, stats in goal_stats.items():
        if stats['total'] > 0:
            stats['avg_progress'] = stats['progress'] / stats['total']
            stats['completion_rate'] = (stats['completed'] / stats['total']) * 100
        else:
            stats['avg_progress'] = 0
            stats['completion_rate'] = 0
    
    if request.method == 'POST':
        form = TodoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Task added successfully!')
            return redirect('todo_list')
    return render(request, 'todo/todo_list.html', {
        'todos': todos, 
        'form': form,
        'goal_stats': goal_stats,
        'current_filter': goal_type_filter,
    })

def todo_update(request, pk):
    todo = get_object_or_404(Todo, pk=pk)
    if request.method == 'POST':
        form = TodoForm(request.POST, instance=todo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Task updated successfully!')
            return redirect('todo_list')
    else:
        form = TodoForm(instance=todo)
    return render(request, 'todo/todo_update.html', {'form': form})

def todo_delete(request, pk):
    todo = get_object_or_404(Todo, pk=pk)
    if request.method == 'POST':
        todo.delete()
        messages.success(request, 'Task deleted successfully!')
        return redirect('todo_list')
    return render(request, 'todo/todo_delete.html', {'todo': todo})

def todo_toggle(request, pk):
    todo = get_object_or_404(Todo, pk=pk)
    todo.completed = not todo.completed
    todo.save()
    return redirect('todo_list')

def update_progress(request, pk):
    todo = get_object_or_404(Todo, pk=pk)
    if request.method == 'POST':
        progress = request.POST.get('progress')
        try:
            progress = int(progress)
            if 0 <= progress <= 100:
                todo.progress = progress
                # Automatically mark as completed if progress is 100%
                if progress == 100 and not todo.completed:
                    todo.completed = True
                    messages.success(request, f'Task "{todo.title}" marked as completed!')
                # If progress is less than 100% and task is marked as completed, update it
                elif progress < 100 and todo.completed:
                    todo.completed = False
                    messages.info(request, f'Task "{todo.title}" marked as in progress.')
                todo.save()
                messages.success(request, f'Progress for "{todo.title}" updated to {progress}%!')
            else:
                messages.error(request, 'Progress must be between 0 and 100.')
        except ValueError:
            messages.error(request, 'Invalid progress value.')
    return redirect('todo_list')
