from django.test import TestCase, Client
from django.urls import reverse
from products.models import Product
from users_app.models import GGUser  # Import GGUser model
from django.core.files.uploadedfile import SimpleUploadedFile

# Create your tests here.



class TestUrls(TestCase):
    def test_home_url(self):
        # ทดสอบว่า URL 'home' สามารถเข้าถึงได้และแสดงผล HTTP status 200
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_about_url(self):
        # ทดสอบว่า URL 'about' สามารถเข้าถึงได้และแสดงผล HTTP status 200
        response = self.client.get(reverse('about'))
        self.assertEqual(response.status_code, 200)

class CompleteViewsTest(TestCase):
    def setUp(self):
        # สร้างผู้ใช้และล็อกอิน
        self.user = GGUser.objects.create(username="testuser", email="test@example.com")
        self.client = Client()

        # สร้างสินค้าพร้อมข้อมูลจำลอง
        self.product1 = Product.objects.create(name="Product 1", price=100, stock=10)
        self.product2 = Product.objects.create(name="Product 2", price=200, stock=5)

    def test_home_view_without_filters(self):
        """ทดสอบ home view โดยไม่มีการกรองข้อมูล"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Product 1")
        self.assertContains(response, "Product 2")

    def test_home_view_with_search(self):
        """ทดสอบ home view โดยใช้การค้นหาสินค้า"""
        response = self.client.get(reverse('home'), {'search': 'Product 1'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Product 1")
        self.assertNotContains(response, "Product 2")

    def test_home_view_with_category_filter(self):
        """ทดสอบ home view โดยใช้การกรองตาม category"""
        self.product1.category = "electronics"
        self.product1.save()
        response = self.client.get(reverse('home'), {'category': 'electronics'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Product 1")
        self.assertNotContains(response, "Product 2")

    def test_home_view_with_sorting(self):
        """ทดสอบ home view โดยใช้การเรียงลำดับ"""
        response = self.client.get(reverse('home'), {'sort': 'price'})
        self.assertEqual(response.status_code, 200)
        products = response.context['products']
        self.assertEqual(products[0].name, "Product 1")  # ราคาน้อยสุดมาก่อน

    def test_about_view(self):
        """ทดสอบ about view"""
        response = self.client.get(reverse('about'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main_app/about.html')

    def test_home_view_invalid_sorting(self):
        """ทดสอบ home view โดยส่งค่าการเรียงลำดับที่ไม่ถูกต้อง"""
        response = self.client.get(reverse('home'), {'sort': 'invalid_field'})
        self.assertEqual(response.status_code, 200)  # ไม่เกิด error
        products = response.context['products']
        self.assertEqual(len(products), 2)  # ผลลัพธ์ยังมีสินค้าทั้งหมด

    def test_home_view_empty_result(self):
        """ทดสอบ home view เมื่อไม่มีสินค้าตรงตามเงื่อนไข"""
        response = self.client.get(reverse('home'), {'search': 'Nonexistent Product'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No products found")  # ข้อความแสดงเมื่อไม่มีสินค้า

