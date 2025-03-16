from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Todo
from .forms import TodoForm

# Create your views here.

@login_required
def todo_list(request):
    # Get filter parameters
    goal_type_filter = request.GET.get('goal_type', '')
    
    # Apply filters
    if goal_type_filter and goal_type_filter in ['daily', 'weekly', 'monthly', 'yearly']:
        todos = Todo.objects.filter(goal_type=goal_type_filter, user=request.user)
    else:
        todos = Todo.objects.filter(user=request.user)
    
    form = TodoForm()
    
    # Calculate progress statistics for each goal type
    goal_stats = {
        'daily': {'total': 0, 'completed': 0, 'progress': 0, 'all_completed': False},
        'weekly': {'total': 0, 'completed': 0, 'progress': 0, 'all_completed': False},
        'monthly': {'total': 0, 'completed': 0, 'progress': 0, 'all_completed': False},
        'yearly': {'total': 0, 'completed': 0, 'progress': 0, 'all_completed': False},
    }
    
    # Get all todos for statistics (regardless of filter)
    all_todos = Todo.objects.filter(user=request.user)
    for todo in all_todos:
        goal_type = todo.goal_type
        goal_stats[goal_type]['total'] += 1
        if todo.completed:
            goal_stats[goal_type]['completed'] += 1
    
    # Calculate progress based on completion rate for each goal type
    for goal_type, stats in goal_stats.items():
        if stats['total'] > 0:
            # Calculate progress as percentage of completed tasks
            stats['avg_progress'] = (stats['completed'] / stats['total']) * 100
            stats['completion_rate'] = (stats['completed'] / stats['total']) * 100
            # Check if all tasks are completed
            stats['all_completed'] = stats['completed'] == stats['total'] and stats['total'] > 0
        else:
            stats['avg_progress'] = 0
            stats['completion_rate'] = 0
            stats['all_completed'] = False
    
    # Prepare congratulatory messages
    congrats_messages = {}
    for goal_type, stats in goal_stats.items():
        if stats['all_completed'] and stats['total'] > 0:
            if goal_type == 'daily':
                congrats_messages[goal_type] = "🎉 Congratulations! You've completed all your daily tasks!"
            elif goal_type == 'weekly':
                congrats_messages[goal_type] = "🏆 Amazing job! All your weekly goals are complete!"
            elif goal_type == 'monthly':
                congrats_messages[goal_type] = "🌟 Impressive! You've achieved all your monthly objectives!"
            elif goal_type == 'yearly':
                congrats_messages[goal_type] = "🥇 Outstanding achievement! You've completed all your yearly goals!"
    
    if request.method == 'POST':
        form = TodoForm(request.POST)
        if form.is_valid():
            todo = form.save(commit=False)
            todo.user = request.user
            todo.save()
            messages.success(request, 'Task added successfully!')
            return redirect('todo_list')
    return render(request, 'todo/todo_list.html', {
        'todos': todos, 
        'form': form,
        'goal_stats': goal_stats,
        'current_filter': goal_type_filter,
        'congrats_messages': congrats_messages,
    })

@login_required
def todo_update(request, pk):
    todo = get_object_or_404(Todo, pk=pk, user=request.user)
    if request.method == 'POST':
        form = TodoForm(request.POST, instance=todo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Task updated successfully!')
            return redirect('todo_list')
    else:
        form = TodoForm(instance=todo)
    return render(request, 'todo/todo_update.html', {'form': form})

@login_required
def todo_delete(request, pk):
    todo = get_object_or_404(Todo, pk=pk, user=request.user)
    if request.method == 'POST':
        todo.delete()
        messages.success(request, 'Task deleted successfully!')
        return redirect('todo_list')
    return render(request, 'todo/todo_delete.html', {'todo': todo})

@login_required
def todo_toggle(request, pk):
    todo = get_object_or_404(Todo, pk=pk, user=request.user)
    todo.completed = not todo.completed
    
    # If task is marked as completed, set progress to 100%
    if todo.completed:
        todo.progress = 100
    
    todo.save()
    return redirect('todo_list')

@login_required
def update_progress(request, pk):
    todo = get_object_or_404(Todo, pk=pk, user=request.user)
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
