from django.shortcuts import render, get_object_or_404, redirect
from .models import MeetingPoint
from .forms import MeetingPointForm

def add_meeting_point(request):
    if request.method == 'POST':
        form = MeetingPointForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('meeting_point_list')
    else:
        form = MeetingPointForm()
    return render(request, 'orders/add_meeting_point.html', {'form': form})

def meeting_point_list(request):
    meeting_points = MeetingPoint.objects.all()
    return render(request, 'orders/meeting_point_list.html', {'meeting_points': meeting_points})

def meeting_point_detail(request, id):
    meeting_point = get_object_or_404(MeetingPoint, id=id)
    return render(request, 'orders/meeting_point_detail.html', {'meeting_point': meeting_point})

def delete_meeting(request, id):
    meetingPoint = get_object_or_404(MeetingPoint, id=id)
    meetingPoint.delete()
    return redirect('meeting_point_list')  # กลับไปที่หน้ารายการสินค้า