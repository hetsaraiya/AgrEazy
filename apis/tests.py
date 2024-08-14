from django.test import TestCase
from django.test import TestCase
from django.core.exceptions import ValidationError
from .models import User, Product, Contract, VerificationDocs

# Create your tests here.

class UserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            name="Test User",
            phone_number="+1234567890",
            email="testuser@example.com",
            password="password123",
            user_type=User.FARMER
        )

    def test_user_creation(self):
        self.assertEqual(self.user.name, "Test User")
        self.assertEqual(self.user.phone_number, "+1234567890")
        self.assertEqual(self.user.email, "testuser@example.com")
        self.assertEqual(self.user.user_type, User.FARMER)

class ProductModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            name="Test Farmer",
            phone_number="+1234567890",
            email="testfarmer@example.com",
            password="password123",
            user_type=User.FARMER
        )
        self.product = Product.objects.create(
            name="Product1",
            description="Test Product",
            price=10.0,
            quantity=100,
            user=self.user,
            remaining_quantity=100
        )

    def test_product_creation(self):
        self.assertEqual(self.product.name, "Product1")
        self.assertEqual(self.product.description, "Test Product")
        self.assertEqual(self.product.price, 10.0)
        self.assertEqual(self.product.quantity, 100)
        self.assertEqual(self.product.remaining_quantity, 100)
        self.assertEqual(self.product.user, self.user)

    def test_product_save_validation(self):
        self.product.quantity = -10
        with self.assertRaises(ValidationError):
            self.product.save()

class ContractModelTest(TestCase):
    def setUp(self):
        self.farmer = User.objects.create(
            name="Test Farmer",
            phone_number="+1234567890",
            email="testfarmer@example.com",
            password="password123",
            user_type=User.FARMER
        )
        self.consumer = User.objects.create(
            name="Test Consumer",
            phone_number="+0987654321",
            email="testconsumer@example.com",
            password="password123",
            user_type=User.CONSUMER
        )
        self.product = Product.objects.create(
            name="Product1",
            description="Test Product",
            price=10.0,
            quantity=100,
            user=self.farmer,
            remaining_quantity=100
        )
        self.contract = Contract.objects.create(
            farmer=self.farmer,
            consumer=self.consumer,
            product=self.product,
            quantity=10
        )

    def test_contract_creation(self):
        self.assertEqual(self.contract.farmer, self.farmer)
        self.assertEqual(self.contract.consumer, self.consumer)
        self.assertEqual(self.contract.product, self.product)
        self.assertEqual(self.contract.quantity, 10)

    def test_contract_save_validation(self):
        self.contract.quantity = 200
        with self.assertRaises(ValidationError):
            self.contract.save()

class VerificationDocsModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            name="Test User",
            phone_number="+1234567890",
            email="testuser@example.com",
            password="password123",
            user_type=User.CONSUMER
        )
        self.verification_docs = VerificationDocs.objects.create(
            user=self.user,
            addhar_card="path/to/addhar",
            pan_card="path/to/pan"
        )

    def test_verification_docs_creation(self):
        self.assertEqual(self.verification_docs.user, self.user)
        self.assertEqual(self.verification_docs.addhar_card, "path/to/addhar")
        self.assertEqual(self.verification_docs.pan_card, "path/to/pan")