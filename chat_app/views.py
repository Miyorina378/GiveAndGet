from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from .models import Chat
from django.db.models import Q, Count
from django.utils.timezone import now

User = get_user_model()

def get_unread_message_counts(user):
    # คำนวณจำนวนข้อความที่ยังไม่ได้อ่านระหว่างผู้ใช้และผู้ส่ง
    return Chat.objects.filter(receiver=user, is_read=False) \
        .values('sender') \
        .annotate(unread_count=Count('id')) \
        .order_by('sender')

@login_required
def chat_room(request, room_name):
    search_query = request.GET.get('search', '')

    # ดึงข้อมูลผู้ใช้ทั้งหมด ยกเว้นผู้ใช้ที่ล็อกอิน
    users = User.objects.exclude(id=request.user.id)

    # ดึงประวัติการแชทในห้องนี้
    chats = Chat.objects.filter(
        (Q(sender=request.user) & Q(receiver__username=room_name)) |
        (Q(receiver=request.user) & Q(sender__username=room_name))
    )

    # หากมีการค้นหาก็ให้กรองแชทที่ตรงกับข้อความ
    if search_query:
        chats = chats.filter(message__icontains=search_query)

    chats = chats.order_by('timestamp')

    # อัพเดตข้อความที่ยังไม่ได้อ่านเป็นว่าอ่านแล้ว
    unread_messages = chats.filter(receiver=request.user, is_read=False)
    unread_messages.update(is_read=True)

    # ดึงจำนวนข้อความที่ยังไม่ได้อ่านสำหรับแต่ละผู้ส่ง
    unread_message_counts = get_unread_message_counts(request.user)

    # แปลงเป็น dictionary สำหรับการใช้งานในเทมเพลต
    unread_message_counts_dict = {str(item['sender']): item['unread_count'] for item in unread_message_counts}

    # ดึงข้อความล่าสุดจากแต่ละผู้ใช้
    user_last_messages = []
    for user in users:
        last_message = Chat.objects.filter(
            (Q(sender=request.user) & Q(receiver=user)) |
            (Q(receiver=request.user) & Q(sender=user))
        ).order_by('-timestamp').first()

        user_last_messages.append({
            'user': user,
            'last_message': last_message,
            'unread_count': unread_message_counts_dict.get(user.username, 0),
        })

    return render(request, 'chat_app/chat.html', {
        'room_name': room_name,
        'chats': chats,
        'users': users,
        'user_last_messages': user_last_messages,
        'search_query': search_query,
        'unread_message_counts': unread_message_counts_dict,
    })





