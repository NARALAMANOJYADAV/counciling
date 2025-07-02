
from django.shortcuts import render, redirect
from .forms import StudentCounselingForm

def counseling_form_view(request):
    if request.method == 'POST':
        form = StudentCounselingForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('success')  # You can create a success.html or message
    else:
        form = StudentCounselingForm()

    return render(request, 'index.html', {'form': form})
def success_view(request):
    return render(request, 'success.html')


