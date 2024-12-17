from django.test import TestCase
from datetime import date, time
from .models import MeetingPoint

class MeetingPointTest(TestCase):

    def setUp(self):
        # สร้าง object ของ MeetingPoint สำหรับการทดสอบ
        self.meeting_point = MeetingPoint.objects.create(
            product_name='Test Product',
            payment_method='Cash',
            pickup_location='Test Location',
            meeting_date=date(2024, 12, 18),
            meeting_time=time(14, 30),
            seller_name='John Doe'
        )

    def test_meeting_point_creation(self):
        # ทดสอบว่า meeting_point ถูกสร้างขึ้นมาอย่างถูกต้องหรือไม่
        meeting_point = self.meeting_point
        self.assertEqual(meeting_point.product_name, 'Test Product')
        self.assertEqual(meeting_point.payment_method, 'Cash')
        self.assertEqual(meeting_point.pickup_location, 'Test Location')
        self.assertEqual(meeting_point.meeting_date, date(2024, 12, 18))
        self.assertEqual(meeting_point.meeting_time, time(14, 30))
        self.assertEqual(meeting_point.seller_name, 'John Doe')

    def test_str_method(self):
        # ทดสอบว่า method __str__ คืนค่าได้ถูกต้องหรือไม่
        self.assertEqual(str(self.meeting_point), 'Test Product')

    def test_default_seller_name(self):
        # ทดสอบว่า default value ของ seller_name ถูกตั้งค่าเป็นค่าว่างหรือไม่
        meeting_point = MeetingPoint.objects.create(
            product_name='Another Product',
            payment_method='Credit',
            pickup_location='Another Location',
            meeting_date=date(2024, 12, 19),
            meeting_time=time(10, 0)
        )
        self.assertEqual(meeting_point.seller_name, '')  # ค่าปริยายควรเป็นค่าว่าง

from django.test import TestCase
from django.urls import reverse
from .models import MeetingPoint
from datetime import date, time

class MeetingPointViewsTest(TestCase):

    def setUp(self):
        # สร้าง MeetingPoint สำหรับการทดสอบ
        self.meeting_point = MeetingPoint.objects.create(
            product_name='Test Product',
            payment_method='Cash',
            pickup_location='Test Location',
            meeting_date=date(2024, 12, 18),
            meeting_time=time(14, 30),
            seller_name='John Doe'
        )
        self.meeting_point_url = reverse('meeting_point_detail', args=[self.meeting_point.id])
        self.add_meeting_point_url = reverse('add_meeting_point')
        self.meeting_point_list_url = reverse('meeting_point_list')

    def test_meeting_point_list_view(self):
        # ทดสอบการแสดงรายการ MeetingPoint
        response = self.client.get(self.meeting_point_list_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'orders/meeting_point_list.html')
        self.assertContains(response, 'Test Product')
        self.assertContains(response, 'Test Location')

    def test_meeting_point_detail_view(self):
        # ทดสอบการแสดงรายละเอียดของ MeetingPoint
        response = self.client.get(self.meeting_point_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'orders/meeting_point_detail.html')
        self.assertContains(response, 'Test Product')
        self.assertContains(response, 'John Doe')

    def test_add_meeting_point_view_get(self):
        # ทดสอบการแสดงฟอร์มการเพิ่ม MeetingPoint (GET)
        response = self.client.get(self.add_meeting_point_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'orders/add_meeting_point.html')
        self.assertContains(response, 'form')

    def test_add_meeting_point_view_post(self):
        # ทดสอบการส่งข้อมูลผ่านฟอร์ม (POST)
        data = {
            'product_name': 'New Product',
            'payment_method': 'Credit',
            'pickup_location': 'New Location',
            'meeting_date': '2024-12-19',
            'meeting_time': '10:00:00',
            'seller_name': 'Jane Doe'
        }
        response = self.client.post(self.add_meeting_point_url, data)
        self.assertEqual(response.status_code, 302)  # คาดว่าจะถูก redirect หลังจากบันทึกข้อมูล
        self.assertRedirects(response, self.meeting_point_list_url)
        self.assertTrue(MeetingPoint.objects.filter(product_name='New Product').exists())

    def test_delete_meeting_view(self):
        # ทดสอบการลบ MeetingPoint
        response = self.client.post(reverse('delete_meeting', args=[self.meeting_point.id]))
        self.assertEqual(response.status_code, 302)  # คาดว่าจะถูก redirect หลังจากลบ
        self.assertRedirects(response, self.meeting_point_list_url)
        self.assertFalse(MeetingPoint.objects.filter(id=self.meeting_point.id).exists())
