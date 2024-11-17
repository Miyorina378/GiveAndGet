from django.test import TestCase
from django.urls import reverse
from products.models import Product
from users_app.models import GGUser  # เพิ่มบรรทัดนี้สำหรับการ import GGUser
from django.core.files.uploadedfile import SimpleUploadedFile

# Create your tests here.

class HomeViewTest(TestCase):
    def setUp(self):
        # สร้างผู้ใช้ใหม่ในตาราง GGUser
        self.user = GGUser.objects.create(username="testuser", email="test@example.com")


        # เตรียมข้อมูลเริ่มต้นสำหรับการทดสอบ
        self.product1 = Product.objects.create(name="Product 1", price=100, stock=10)
        self.product2 = Product.objects.create(name="Product 2", price=200, stock=20)

         # สร้างไฟล์ภาพจำลอง
        image = SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg")

        # สร้างผลิตภัณฑ์พร้อมกับไฟล์ภาพ
        self.product = Product.objects.create(
            name="Test Product",
            price=100,
            stock=10,
            user=self.user,
            image=image  # เพิ่มไฟล์ภาพ
        )

    def test_home_view_status_code(self):
        # ทดสอบว่า home view ส่ง HTTP status 200
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_about_view_status_code(self):
        response = self.client.get(reverse('about'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "About")  # ตรวจสอบว่า "About" มีในหน้า


    def test_home_view_with_products(self):
        # ทดสอบว่า home view แสดงสินค้าที่มีในฐานข้อมูล
        response = self.client.get(reverse('home'))
        self.assertContains(response, "Product 1")
        self.assertContains(response, "10")  # ตรวจสอบว่า stock แสดงผลในหน้าเว็บ
        self.assertContains(response, "Product 2")
        self.assertContains(response, "20")

    def test_product_detail_view(self):
        # ตรวจสอบว่า URL สำหรับ product_detail ทำงานได้
        response = self.client.get(reverse('product_detail', args=[self.product.id]))
        self.assertEqual(response.status_code, 200)

        # ตรวจสอบว่าเนื้อหาของหน้าเพจตรงกับที่คาด
        self.assertContains(response, "Test Product")
        self.assertContains(response, "100")

class TestUrls(TestCase):
    def test_home_url(self):
        # ทดสอบว่า URL 'home' สามารถเข้าถึงได้และแสดงผล HTTP status 200
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_about_url(self):
        # ทดสอบว่า URL 'about' สามารถเข้าถึงได้และแสดงผล HTTP status 200
        response = self.client.get(reverse('about'))
        self.assertEqual(response.status_code, 200)
