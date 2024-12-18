from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from products.models import Product
from django.core.exceptions import ValidationError
import tempfile
from django.core.files.uploadedfile import SimpleUploadedFile
import os
from django.urls import reverse
from .models import Product
from PIL import Image

User = get_user_model()

class ProductModelTest(TestCase):
    def setUp(self):
        """สร้างข้อมูลเริ่มต้นสำหรับการทดสอบ"""
        self.user = User.objects.create_user(username="testuser", password="password")
        self.product = Product.objects.create(
            name="Test Product",
            description="This is a test product",
            price=100.50,
            stock=10,
            user=self.user
        )

    def test_product_creation(self):
        """ทดสอบว่าโมเดล Product ถูกสร้างขึ้นและบันทึกข้อมูลได้อย่างถูกต้อง"""
        self.assertEqual(self.product.name, "Test Product")
        self.assertEqual(self.product.price, 100.50)
        self.assertEqual(self.product.stock, 10)
        self.assertEqual(self.product.user, self.user)

    def test_product_string_representation(self):
        """ทดสอบการแสดงผลในรูปแบบข้อความ (__str__)"""
        self.assertEqual(str(self.product), "Test Product")

    def test_update_stock(self):
        """ทดสอบการปรับปรุงค่า stock"""
        self.product.stock = 20
        self.product.save()
        self.assertEqual(self.product.stock, 20)

    def test_negative_stock_not_allowed(self):
        """ทดสอบว่าการบันทึก stock ที่มีค่าติดลบจะล้มเหลว"""
        self.product.stock = -5
        with self.assertRaises(ValidationError) as context:
            self.product.full_clean()  # ตรวจสอบ validation
        
        # ตรวจสอบว่า ValidationError เกี่ยวข้องกับฟิลด์ stock
        self.assertIn('stock', context.exception.message_dict)
        self.assertEqual(context.exception.message_dict['stock'], ['Ensure this value is greater than or equal to 0.'])



class ProductSignalTest(TestCase):
    def setUp(self):
        """สร้างผู้ใช้และไฟล์ภาพตัวอย่าง"""
        self.user = User.objects.create_user(username="testuser", password="password")
        self.temp_file = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
        self.temp_file.write(b"Test Image Content")
        self.temp_file.close()
        self.product = Product.objects.create(
            name="Test Product",
            price=100.00,
            stock=10,
            user=self.user,
            image=SimpleUploadedFile("test_image.jpg", b"Test Image Content")
        )

    def tearDown(self):
        """ลบไฟล์ที่ถูกสร้างในระหว่างการทดสอบ"""
        if os.path.exists(self.temp_file.name):
            os.remove(self.temp_file.name)

    def test_image_deleted_on_product_delete(self):
        """ทดสอบว่าไฟล์ภาพถูกลบเมื่ออ็อบเจ็กต์ Product ถูกลบ"""
        image_path = self.product.image.path  # เก็บ path ของไฟล์ภาพ
        self.assertTrue(os.path.exists(image_path))  # ยืนยันว่าไฟล์ภาพมีอยู่จริง

        self.product.delete()  # ลบอ็อบเจ็กต์ Product

        # ตรวจสอบว่าไฟล์ภาพถูกลบแล้ว
        self.assertFalse(os.path.exists(image_path))

def get_valid_image_file():
    """สร้างไฟล์ภาพตัวอย่างสำหรับการทดสอบ"""
    image = Image.new('RGB', (100, 100), color='white')
    temp_file = tempfile.NamedTemporaryFile(suffix='.jpg')
    image.save(temp_file, format='JPEG')
    temp_file.seek(0)
    return temp_file


class ProductViewsTest(TestCase):
    def setUp(self):
        # สร้างผู้ใช้
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client = Client()
        self.client.login(username='testuser', password='password')

        # สร้างสินค้าตัวอย่างพร้อมฟิลด์ stock และ image
        valid_image = get_valid_image_file()
        self.product = Product.objects.create(
            name="Test Product",
            price=100.0,
            stock=10,
            user=self.user,
            image=SimpleUploadedFile(
                name=valid_image.name,
                content=valid_image.read(),
                content_type='image/jpeg'
            ),
        )
    
    def test_product_list_view_with_category_filter(self):
        # ทดสอบการกรองสินค้าตาม category_filter
        category = 'electronics'  # ตัวอย่าง category
        category_product = Product.objects.create(
            name="Category Product",
            price=150.0,
            stock=5,
            user=self.user,
            category=category,
            image=SimpleUploadedFile(
                name='test_image.jpg',
                content=b'fake_image_data',
                content_type='image/jpeg'
            ),
        )

        # สร้างสินค้าที่ไม่มี category ตรงกับ filter
        other_product = Product.objects.create(
            name="Other Product",
            price=200.0,
            stock=3,
            user=self.user,
            image=SimpleUploadedFile(
                name='test_image2.jpg',
                content=b'fake_image_data',
                content_type='image/jpeg'
            ),
        )

        # ส่ง request โดยใช้ category filter
        url = reverse('product_list') + f'?category={category}'
        response = self.client.get(url)

        # ตรวจสอบผลลัพธ์
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'products/product_list.html')

        # ตรวจสอบว่าเฉพาะสินค้าที่ตรงกับ category ที่กรองมาแสดงในหน้า
        self.assertContains(response, "Category Product")
        self.assertNotContains(response, "Other Product")

    


    def test_product_list_view(self):
        # ทดสอบการเข้าถึง product_list
        url = reverse('product_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'products/product_list.html')
        self.assertContains(response, "Test Product")

    def test_add_product_view_get(self):
        # ทดสอบการแสดงฟอร์มเมื่อส่งคำขอ GET
        url = reverse('add_product')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'products/add_product.html')
        self.assertIn('form', response.context)

    def test_add_product_view_post_valid(self):
        # ทดสอบการเพิ่มสินค้าใหม่
        url = reverse('add_product')
        valid_image = get_valid_image_file()
        data = {
            'name': 'New Product',
            'price': 200.0,
            'stock': 5,
            'image': SimpleUploadedFile(
                name=valid_image.name,
                content=valid_image.read(),
                content_type='image/jpeg'
            ),
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertTrue(Product.objects.filter(name='New Product').exists())

    def test_add_product_view_post_invalid(self):
        # ทดสอบการแสดงฟอร์มใหม่เมื่อฟอร์มไม่ valid
        url = reverse('add_product')
        data = {
            'name': '',  # ข้อมูลไม่ครบ
            'price': '',  # ข้อมูลไม่ครบ
            'stock': '',  # ข้อมูลไม่ครบ
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)  # แสดงฟอร์มเดิม
        self.assertTemplateUsed(response, 'products/add_product.html')
        self.assertIn('form', response.context)
        self.assertTrue(response.context['form'].errors)

    def test_product_detail_view(self):
        # ทดสอบหน้ารายละเอียดสินค้า
        url = reverse('product_detail', args=[self.product.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'products/product_detail.html')
        self.assertContains(response, "Test Product")

    def test_delete_product_view(self):
        # ทดสอบการลบสินค้า
        url = reverse('delete_product', args=[self.product.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertFalse(Product.objects.filter(id=self.product.id).exists())

    def test_product_detail_view_invalid_id(self):
        # ทดสอบการเข้าถึงสินค้าที่ไม่มีอยู่
        url = reverse('product_detail', args=[9999])  # ID ที่ไม่มีในระบบ
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_delete_product_invalid_id(self):
        # ทดสอบการลบสินค้าที่ไม่มีอยู่
        url = reverse('delete_product', args=[9999])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

    def test_product_list_view_unauthenticated(self):
        # ทดสอบการเข้าถึง product_list โดยไม่ล็อกอิน
        self.client.logout()
        url = reverse('product_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # Redirect ไปที่หน้า login

class ProductEditViewTest(TestCase):
    def setUp(self):
        # สร้างผู้ใช้และเข้าสู่ระบบ
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client = Client()
        self.client.login(username='testuser', password='password')

        # สร้างสินค้าตัวอย่าง
        valid_image = get_valid_image_file()
        self.product = Product.objects.create(
            name="Original Product",
            price=100.0,
            stock=10,
            user=self.user,
            image=SimpleUploadedFile(
                name=valid_image.name,
                content=valid_image.read(),
                content_type='image/jpeg'
            ),
        )

    def test_edit_product_view_get(self):
        """ทดสอบการแสดงฟอร์มแก้ไขสินค้า"""
        url = reverse('edit_product', args=[self.product.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'products/add_product.html')
        self.assertIn('form', response.context)
        self.assertEqual(response.context['form'].instance, self.product)

    def test_edit_product_view_post_valid(self):
        """ทดสอบการแก้ไขสินค้าเมื่อข้อมูลถูกต้อง"""
        url = reverse('edit_product', args=[self.product.id])
        valid_image = get_valid_image_file()
        data = {
            'name': 'Updated Product',
            'price': 150.0,
            'stock': 20,
            'image': SimpleUploadedFile(
                name=valid_image.name,
                content=valid_image.read(),
                content_type='image/jpeg'
            ),
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)  # Redirect หลังจากบันทึกสำเร็จ
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, 'Updated Product')
        self.assertEqual(self.product.price, 150.0)
        self.assertEqual(self.product.stock, 20)

    def test_edit_product_view_post_invalid(self):
        """ทดสอบการแก้ไขสินค้าเมื่อข้อมูลไม่สมบูรณ์"""
        url = reverse('edit_product', args=[self.product.id])
        data = {
            'name': '',  # ชื่อสินค้าเป็นค่าว่าง
            'price': '',  # ราคาเป็นค่าว่าง
            'stock': '',  # Stock เป็นค่าว่าง
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)  # แสดงฟอร์มเดิมอีกครั้ง
        self.assertTemplateUsed(response, 'products/add_product.html')
        self.assertIn('form', response.context)
        self.assertTrue(response.context['form'].errors)
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from users_app.models import Report

User = get_user_model()

class AddReportViewTest(TestCase):
    def setUp(self):
        # สร้างผู้ใช้ที่ใช้ทดสอบ
        self.reporter = User.objects.create_user(username='reporter', password='password')
        self.reported_user = User.objects.create_user(username='reported_user', password='password')





        # ตรวจสอบว่า redirect ไปยังหน้าที่ต้องการหรือไม่

    def test_add_report_user_does_not_exist(self):
        # เข้าสู่ระบบในฐานะผู้รายงาน
        self.client.login(username='reporter', password='password')

        # ส่ง POST request โดยใช้ username ของผู้ใช้ที่ไม่อยู่ในระบบ
        data = {
            'reported_user_username': 'non_existent_user',
            'reason': 'Violation of terms',
            'description': 'The user was abusive in chat.',
        }

        response = self.client.post(reverse('add_report'), data)

        # ตรวจสอบว่าแสดงข้อความผิดพลาดหรือไม่
        self.assertContains(response, "ERROR: Reported user with username 'non_existent_user' does not exist.")



   

