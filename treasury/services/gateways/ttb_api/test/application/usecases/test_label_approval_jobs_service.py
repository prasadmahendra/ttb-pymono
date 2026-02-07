import unittest
import uuid
from datetime import datetime
from unittest.mock import Mock, patch

from treasury.services.gateways.ttb_api.main.application.models.domain.entity_descriptor import EntityDescriptor
from treasury.services.gateways.ttb_api.main.application.models.domain.label_approval_job import (
    LabelApprovalJob,
    JobMetadata,
    LabelImage
)
from treasury.services.gateways.ttb_api.main.application.models.domain.label_extraction_data import (
    BrandDataStrict,
    ProductInfoStrict,
    ProductOtherInfo
)
from treasury.services.gateways.ttb_api.main.application.models.domain.user import User
from treasury.services.gateways.ttb_api.main.application.models.gql.label_approvals.create_label_approval_job_request import (
    CreateLabelApprovalJobInput,
    JobMetadataInput,
    CreateLabelApprovalJobResponse
)
from treasury.services.gateways.ttb_api.main.application.models.gql.label_approvals.update_label_approval_job_requests import (
    SetLabelApprovalJobStatusInput,
    SetLabelApprovalJobStatusResponse,
    AddReviewCommentInput,
    AddReviewCommentResponse
)
from treasury.services.gateways.ttb_api.main.application.models.gql.label_approvals.list_label_approval_jobs_request import (
    ListLabelApprovalJobsInput,
    ListLabelApprovalJobsResponse
)
from treasury.services.gateways.ttb_api.main.application.usecases.label_approval_jobs import \
    LabelApprovalJobsService


class TestLabelApprovalJobsServiceValidations(unittest.TestCase):
    """Test validation methods of LabelApprovalJobsService"""

    def test_verify_net_contents_in_milli_litres_valid(self):
        """Test validation with valid net contents"""
        # Should not raise exception
        LabelApprovalJobsService._verify_net_contents_or_raise("355")
        LabelApprovalJobsService._verify_net_contents_or_raise("750.5")
        LabelApprovalJobsService._verify_net_contents_or_raise("1000")

    def test_verify_net_contents_in_milli_litres_none(self):
        """Test validation with None (should be allowed)"""
        # Should not raise exception
        LabelApprovalJobsService._verify_net_contents_or_raise(None)

    def test_verify_net_contents_in_milli_litres_negative(self):
        """Test validation with negative value"""
        with self.assertRaises(ValueError) as context:
            LabelApprovalJobsService._verify_net_contents_or_raise("-100")
        self.assertIn("positive number", str(context.exception))

    def test_verify_net_contents_in_milli_litres_invalid_format(self):
        """Test validation with invalid format"""
        with self.assertRaises(ValueError) as context:
            LabelApprovalJobsService._verify_net_contents_or_raise("abc")
        self.assertIn("valid number", str(context.exception))

    def test_verify_alcohol_content_percentage_valid(self):
        """Test validation with valid alcohol content"""
        # Should not raise exception
        LabelApprovalJobsService._verify_alcohol_content_percentage_or_raise("5%")
        LabelApprovalJobsService._verify_alcohol_content_percentage_or_raise("12.5%")
        LabelApprovalJobsService._verify_alcohol_content_percentage_or_raise("40%")

    def test_verify_alcohol_content_percentage_none(self):
        """Test validation with None (should be allowed)"""
        # Should not raise exception
        LabelApprovalJobsService._verify_alcohol_content_percentage_or_raise(None)

    def test_verify_alcohol_content_percentage_out_of_range(self):
        """Test validation with out of range percentage"""
        with self.assertRaises(ValueError) as context:
            LabelApprovalJobsService._verify_alcohol_content_percentage_or_raise("150%")
        self.assertIn("between 0% and 100%", str(context.exception))

        with self.assertRaises(ValueError) as context:
            LabelApprovalJobsService._verify_alcohol_content_percentage_or_raise("-5%")
        self.assertIn("between 0% and 100%", str(context.exception))

    def test_verify_alcohol_content_percentage_invalid_format(self):
        """Test validation with invalid format"""
        with self.assertRaises(ValueError) as context:
            LabelApprovalJobsService._verify_alcohol_content_percentage_or_raise("abc%")
        self.assertIn("valid number", str(context.exception))

    def test_verify_label_image_valid_jpg(self):
        """Test validation with valid JPG image"""
        valid_jpg = "data:image/jpg;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        # Should not raise exception
        service = LabelApprovalJobsService()
        service._verify_label_image_or_raise(valid_jpg, ["jpg", "png", "gif"])

    def test_verify_label_image_valid_png(self):
        """Test validation with valid PNG image"""
        valid_png = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        # Should not raise exception
        service = LabelApprovalJobsService()
        service._verify_label_image_or_raise(valid_png, ["jpg", "png", "gif"])

    def test_verify_label_image_valid_gif(self):
        """Test validation with valid GIF image"""
        valid_gif = "data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"
        # Should not raise exception
        service = LabelApprovalJobsService()
        service._verify_label_image_or_raise(valid_gif, ["jpg", "png", "gif"])

    def test_verify_label_image_empty(self):
        """Test validation with empty image"""
        service = LabelApprovalJobsService()
        with self.assertRaises(ValueError) as context:
            service._verify_label_image_or_raise("", ["jpg", "png", "gif"])
        self.assertIn("required", str(context.exception))

    def test_verify_label_image_invalid_type(self):
        """Test validation with invalid image type"""
        invalid_image = "data:image/bmp;base64,xyz"
        service = LabelApprovalJobsService()
        with self.assertRaises(ValueError) as context:
            service._verify_label_image_or_raise(invalid_image, ["jpg", "png", "gif"])
        self.assertIn("following types", str(context.exception))

    def test_upload_and_create_label_images_jpg_success(self):
        """Test uploading and creating label images from base64 JPG (blob upload succeeds)"""
        mock_blob_adapter = Mock()
        mock_blob_adapter.upload_image.return_value = "https://blob.vercel-storage.com/label-images/test/label.jpg"

        service = LabelApprovalJobsService(vercel_blob_storage_adapter=mock_blob_adapter)
        jpg_base64 = "data:image/jpg;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        images = service._upload_and_create_label_images(jpg_base64)

        self.assertEqual(len(images), 1)
        self.assertIsInstance(images[0], LabelImage)
        self.assertEqual(images[0].image_content_type, "image/jpg")
        self.assertIsNone(images[0].base64)
        self.assertEqual(images[0].image_url, "https://blob.vercel-storage.com/label-images/test/label.jpg")
        mock_blob_adapter.upload_image.assert_called_once()

    def test_upload_and_create_label_images_png_success(self):
        """Test uploading and creating label images from base64 PNG"""
        mock_blob_adapter = Mock()
        mock_blob_adapter.upload_image.return_value = "https://blob.vercel-storage.com/label-images/test/label.png"

        service = LabelApprovalJobsService(vercel_blob_storage_adapter=mock_blob_adapter)
        png_base64 = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        images = service._upload_and_create_label_images(png_base64)

        self.assertEqual(len(images), 1)
        self.assertIsInstance(images[0], LabelImage)
        self.assertEqual(images[0].image_content_type, "image/png")
        self.assertIsNone(images[0].base64)
        self.assertIsNotNone(images[0].image_url)

    def test_upload_and_create_label_images_gif_success(self):
        """Test uploading and creating label images from base64 GIF"""
        mock_blob_adapter = Mock()
        mock_blob_adapter.upload_image.return_value = "https://blob.vercel-storage.com/label-images/test/label.gif"

        service = LabelApprovalJobsService(vercel_blob_storage_adapter=mock_blob_adapter)
        gif_base64 = "data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"
        images = service._upload_and_create_label_images(gif_base64)

        self.assertEqual(len(images), 1)
        self.assertIsInstance(images[0], LabelImage)
        self.assertEqual(images[0].image_content_type, "image/gif")
        self.assertIsNone(images[0].base64)
        self.assertIsNotNone(images[0].image_url)

    def test_upload_and_create_label_images_empty(self):
        """Test creating label images from empty string"""
        service = LabelApprovalJobsService()
        images = service._upload_and_create_label_images("")

        self.assertEqual(len(images), 0)

    def test_upload_and_create_label_images_fallback_on_upload_failure(self):
        """Test fallback to base64 storage when blob upload fails"""
        mock_blob_adapter = Mock()
        mock_blob_adapter.upload_image.side_effect = RuntimeError("Upload failed")

        service = LabelApprovalJobsService(vercel_blob_storage_adapter=mock_blob_adapter)
        jpg_base64 = "data:image/jpg;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        images = service._upload_and_create_label_images(jpg_base64)

        self.assertEqual(len(images), 1)
        self.assertIsNone(images[0].image_url)
        self.assertEqual(images[0].base64, jpg_base64)
        self.assertEqual(images[0].image_content_type, "image/jpg")


class TestLabelApprovalJobsServiceCreateJob(unittest.TestCase):
    """Test create_label_approval_job method of LabelApprovalJobsService"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_org_id = uuid.uuid4()
        self.test_user_id = uuid.uuid4()
        self.test_brand_name = "Test Brand"

        # Create mock dependencies
        self.mock_persistence_adapter = Mock()
        self.mock_user_management_service = Mock()

        # Create service instance with mocked dependencies
        self.service = LabelApprovalJobsService(
            label_approval_jobs_persistence_adapter=self.mock_persistence_adapter,
            user_management_service=self.mock_user_management_service
        )

    def _create_mock_info(self) -> Mock:
        """Helper to create a mock Info object"""
        mock_info = Mock()
        mock_info.context = {
            'security_context': {
                'authenticated_entity': {
                    'entity': 'user',
                    'id': str(self.test_user_id),
                    'org_id': str(self.test_org_id)
                },
            }
        }
        return mock_info

    def _create_mock_user(self) -> User:
        """Helper to create a mock User"""
        user = User(
            id=self.test_user_id,
            email="test@example.com",
            name="Test User",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            created_by_entity="system",
            created_by_entity_id="system",
            created_by_entity_domain="system",
            updated_by_entity="system"
        )
        return user

    def _create_test_input(self, **overrides) -> CreateLabelApprovalJobInput:
        """Helper to create test input with sensible defaults"""
        defaults = {
            'status': 'pending',
            'job_metadata': JobMetadataInput(
                brand_name=self.test_brand_name,
                product_class='beer',
                alcohol_content_abv='5%',
                net_contents='355',
                label_image_base64='data:image/jpg;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=='
            )
        }
        defaults.update(overrides)
        return CreateLabelApprovalJobInput(**defaults)

    def _create_mock_created_job(self) -> LabelApprovalJob:
        """Helper to create a mock created job"""
        # Create product info with all the details
        product_other_info = ProductOtherInfo(
            bottler_info='Test Bottlers',
            manufacturer='Test Brewery',
            warnings='Contains alcohol'
        )
        product_info_strict = ProductInfoStrict(
            name='Test Beer',
            product_class_type='beer',
            alcohol_content_abv='5%',
            net_contents='355 mL',
            other_info=product_other_info
        )
        brand_data_strict = BrandDataStrict(
            brand_name=str(self.test_brand_name),
            products=[product_info_strict]
        )

        job_metadata = JobMetadata(
            reviewer_id=str(self.test_user_id),
            reviewer_name="Test User",
            review_comments=["Review initiated"],
            product_info=brand_data_strict
        )

        job = LabelApprovalJob(
            id=uuid.uuid4(),
            brand_name=self.test_brand_name,
            product_class='beer',
            status='pending',
            job_metadata=job_metadata,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            created_by_entity='user',
            created_by_entity_id=str(self.test_user_id),
            created_by_entity_domain=str(self.test_org_id),
            updated_by_entity='user',
            updated_by_entity_id=str(self.test_user_id),
            updated_by_entity_domain=str(self.test_org_id)
        )
        return job

    @patch('treasury.services.gateways.ttb_api.main.application.usecases.label_approval_jobs.SecurityContext')
    def test_create_label_approval_job_success(self, mock_security_context):
        """Test successful creation of label approval job"""
        # Setup mocks
        mock_info = self._create_mock_info()
        mock_user = self._create_mock_user()
        test_input = self._create_test_input()

        mock_security_ctx_instance = Mock()
        mock_security_context.from_info.return_value = mock_security_ctx_instance
        mock_security_ctx_instance.get_authenticated_entity_from_security_ctx.return_value = EntityDescriptor.of_user(
            id=str(self.test_user_id),
            org_id=self.test_org_id
        )

        # Configure the decorator to call the wrapped function
        def role_permissions_required_decorator(permissions):
            def decorator(func):
                return func

            return decorator

        mock_security_ctx_instance.role_permissions_required = role_permissions_required_decorator

        self.mock_user_management_service.get_user_by_authenticated_entity.return_value = mock_user

        mock_created_job = self._create_mock_created_job()
        self.mock_persistence_adapter.create_approval_job.return_value = mock_created_job

        # Execute
        response = self.service.create_label_approval_job(info=mock_info, input=test_input)

        # Verify
        self.assertIsInstance(response, CreateLabelApprovalJobResponse)
        self.assertTrue(response.success)
        self.assertEqual(response.message, "Label approval job created successfully")
        self.assertIsNotNone(response.job)
        self.assertEqual(response.job.brand_name, self.test_brand_name)
        self.assertEqual(response.job.product_class, 'beer')
        self.assertEqual(response.job.status, 'pending')

        # Verify persistence adapter was called
        self.mock_persistence_adapter.create_approval_job.assert_called_once()
        call_args = self.mock_persistence_adapter.create_approval_job.call_args
        created_job_arg = call_args.kwargs['job']
        self.assertEqual(created_job_arg.brand_name, self.test_brand_name)
        self.assertEqual(created_job_arg.product_class, 'beer')

    @patch('treasury.services.gateways.ttb_api.main.application.usecases.label_approval_jobs.SecurityContext')
    def test_create_label_approval_job_user_not_found(self, mock_security_context):
        """Test creation fails when authenticated user is not found"""
        # Setup mocks
        mock_info = self._create_mock_info()
        test_input = self._create_test_input()

        mock_security_ctx_instance = Mock()
        mock_security_context.from_info.return_value = mock_security_ctx_instance
        mock_security_ctx_instance.get_authenticated_entity_from_security_ctx.return_value = EntityDescriptor.of_user(
            id=str(self.test_user_id),
            org_id=self.test_org_id
        )

        def role_permissions_required_decorator(permissions):
            def decorator(func):
                return func

            return decorator

        mock_security_ctx_instance.role_permissions_required = role_permissions_required_decorator

        # User not found
        self.mock_user_management_service.get_user_by_authenticated_entity.return_value = None

        # Execute
        response = self.service.create_label_approval_job(info=mock_info, input=test_input)

        # Verify
        self.assertFalse(response.success)
        self.assertIn("Authenticated user not found", response.message)
        self.assertIsNone(response.job)

        # Verify persistence adapter was NOT called
        self.mock_persistence_adapter.create_approval_job.assert_not_called()

    @patch('treasury.services.gateways.ttb_api.main.application.usecases.label_approval_jobs.SecurityContext')
    def test_create_label_approval_job_invalid_alcohol_content(self, mock_security_context):
        """Test creation fails with invalid alcohol content percentage"""
        # Setup mocks
        mock_info = self._create_mock_info()
        mock_user = self._create_mock_user()

        # Create input with invalid alcohol content
        job_metadata_input = JobMetadataInput(
            brand_name=self.test_brand_name,
            product_class='beer',
            alcohol_content_abv='150%',  # Invalid - over 100%
            net_contents='355',
            label_image_base64='data:image/jpg;base64,test'
        )
        test_input = self._create_test_input(job_metadata=job_metadata_input)

        mock_security_ctx_instance = Mock()
        mock_security_context.from_info.return_value = mock_security_ctx_instance
        mock_security_ctx_instance.get_authenticated_entity_from_security_ctx.return_value = EntityDescriptor.of_user(
            id=str(self.test_user_id),
            org_id=self.test_org_id
        )

        def role_permissions_required_decorator(permissions):
            def decorator(func):
                return func

            return decorator

        mock_security_ctx_instance.role_permissions_required = role_permissions_required_decorator

        self.mock_user_management_service.get_user_by_authenticated_entity.return_value = mock_user

        # Execute
        response = self.service.create_label_approval_job(info=mock_info, input=test_input)

        # Verify
        self.assertFalse(response.success)
        self.assertIn("Invalid alcohol content percentage", response.message)
        self.assertIsNone(response.job)

        # Verify persistence adapter was NOT called
        self.mock_persistence_adapter.create_approval_job.assert_not_called()

    @patch('treasury.services.gateways.ttb_api.main.application.usecases.label_approval_jobs.SecurityContext')
    def test_create_label_approval_job_invalid_net_contents(self, mock_security_context):
        """Test creation fails with invalid net contents"""
        # Setup mocks
        mock_info = self._create_mock_info()
        mock_user = self._create_mock_user()

        # Create input with invalid net contents
        job_metadata_input = JobMetadataInput(
            brand_name=self.test_brand_name,
            product_class='beer',
            alcohol_content_abv='5%',
            net_contents='invalid',  # Invalid - not a number
            label_image_base64='data:image/jpg;base64,test'
        )
        test_input = self._create_test_input(job_metadata=job_metadata_input)

        mock_security_ctx_instance = Mock()
        mock_security_context.from_info.return_value = mock_security_ctx_instance
        mock_security_ctx_instance.get_authenticated_entity_from_security_ctx.return_value = EntityDescriptor.of_user(
            id=str(self.test_user_id),
            org_id=self.test_org_id
        )

        def role_permissions_required_decorator(permissions):
            def decorator(func):
                return func

            return decorator

        mock_security_ctx_instance.role_permissions_required = role_permissions_required_decorator

        self.mock_user_management_service.get_user_by_authenticated_entity.return_value = mock_user

        # Execute
        response = self.service.create_label_approval_job(info=mock_info, input=test_input)

        # Verify
        self.assertFalse(response.success)
        self.assertIn("Invalid net contents", response.message)
        self.assertIsNone(response.job)

        # Verify persistence adapter was NOT called
        self.mock_persistence_adapter.create_approval_job.assert_not_called()

    @patch('treasury.services.gateways.ttb_api.main.application.usecases.label_approval_jobs.SecurityContext')
    def test_create_label_approval_job_invalid_label_image(self, mock_security_context):
        """Test creation fails with invalid label image"""
        # Setup mocks
        mock_info = self._create_mock_info()
        mock_user = self._create_mock_user()

        # Create input with invalid label image
        job_metadata_input = JobMetadataInput(
            brand_name=self.test_brand_name,
            product_class='beer',
            alcohol_content_abv='5%',
            net_contents='355',
            label_image_base64='data:image/bmp;base64,test'  # Invalid - not jpg/png/gif
        )
        test_input = self._create_test_input(job_metadata=job_metadata_input)

        mock_security_ctx_instance = Mock()
        mock_security_context.from_info.return_value = mock_security_ctx_instance
        mock_security_ctx_instance.get_authenticated_entity_from_security_ctx.return_value = EntityDescriptor.of_user(
            id=str(self.test_user_id),
            org_id=self.test_org_id
        )

        def role_permissions_required_decorator(permissions):
            def decorator(func):
                return func

            return decorator

        mock_security_ctx_instance.role_permissions_required = role_permissions_required_decorator

        self.mock_user_management_service.get_user_by_authenticated_entity.return_value = mock_user

        # Execute
        response = self.service.create_label_approval_job(info=mock_info, input=test_input)

        # Verify
        self.assertFalse(response.success)
        self.assertIn("Invalid label image", response.message)
        self.assertIsNone(response.job)

        # Verify persistence adapter was NOT called
        self.mock_persistence_adapter.create_approval_job.assert_not_called()

    @patch('treasury.services.gateways.ttb_api.main.application.usecases.label_approval_jobs.SecurityContext')
    def test_create_label_approval_job_persistence_failure(self, mock_security_context):
        """Test creation fails when persistence adapter returns None"""
        # Setup mocks
        mock_info = self._create_mock_info()
        mock_user = self._create_mock_user()
        test_input = self._create_test_input()

        mock_security_ctx_instance = Mock()
        mock_security_context.from_info.return_value = mock_security_ctx_instance
        mock_security_ctx_instance.get_authenticated_entity_from_security_ctx.return_value = EntityDescriptor.of_user(
            id=str(self.test_user_id),
            org_id=self.test_org_id
        )

        def role_permissions_required_decorator(permissions):
            def decorator(func):
                return func

            return decorator

        mock_security_ctx_instance.role_permissions_required = role_permissions_required_decorator

        self.mock_user_management_service.get_user_by_authenticated_entity.return_value = mock_user

        # Persistence fails
        self.mock_persistence_adapter.create_approval_job.return_value = None

        # Execute
        response = self.service.create_label_approval_job(info=mock_info, input=test_input)

        # Verify
        self.assertFalse(response.success)
        self.assertIn("Failed to create label approval job", response.message)
        self.assertIsNone(response.job)

    @patch('treasury.services.gateways.ttb_api.main.application.usecases.label_approval_jobs.SecurityContext')
    def test_create_label_approval_job_exception_handling(self, mock_security_context):
        """Test that exceptions are properly caught and handled"""
        # Setup mocks
        mock_info = self._create_mock_info()
        test_input = self._create_test_input()

        mock_security_ctx_instance = Mock()
        mock_security_context.from_info.return_value = mock_security_ctx_instance
        mock_security_ctx_instance.get_authenticated_entity_from_security_ctx.return_value = EntityDescriptor.of_user(
            id=str(self.test_user_id),
            org_id=self.test_org_id
        )

        def role_permissions_required_decorator(permissions):
            def decorator(func):
                return func

            return decorator

        mock_security_ctx_instance.role_permissions_required = role_permissions_required_decorator

        # Raise an exception
        self.mock_user_management_service.get_user_by_authenticated_entity.side_effect = Exception(
            "Database connection error")

        # Execute
        response = self.service.create_label_approval_job(info=mock_info, input=test_input)

        # Verify
        self.assertFalse(response.success)
        self.assertIn("Error creating label approval job", response.message)
        self.assertIn("Database connection error", response.message)
        self.assertIsNone(response.job)

    @patch('treasury.services.gateways.ttb_api.main.application.usecases.label_approval_jobs.SecurityContext')
    def test_create_label_approval_job_with_optional_fields(self, mock_security_context):
        """Test creation with optional fields in metadata"""
        # Setup mocks
        mock_info = self._create_mock_info()
        mock_user = self._create_mock_user()

        # Create input with minimal metadata
        job_metadata_input = JobMetadataInput(
            brand_name=self.test_brand_name,
            product_class='beer',
            alcohol_content_abv='5%',
            net_contents='355',
            label_image_base64='data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=='
        )
        test_input = self._create_test_input(job_metadata=job_metadata_input)

        mock_security_ctx_instance = Mock()
        mock_security_context.from_info.return_value = mock_security_ctx_instance
        mock_security_ctx_instance.get_authenticated_entity_from_security_ctx.return_value = EntityDescriptor.of_user(
            id=str(self.test_user_id),
            org_id=self.test_org_id
        )

        def role_permissions_required_decorator(permissions):
            def decorator(func):
                return func

            return decorator

        mock_security_ctx_instance.role_permissions_required = role_permissions_required_decorator

        self.mock_user_management_service.get_user_by_authenticated_entity.return_value = mock_user

        mock_created_job = self._create_mock_created_job()
        self.mock_persistence_adapter.create_approval_job.return_value = mock_created_job

        # Execute
        response = self.service.create_label_approval_job(info=mock_info, input=test_input)

        # Verify
        self.assertTrue(response.success)
        self.assertIsNotNone(response.job)

        # Verify persistence adapter was called
        self.mock_persistence_adapter.create_approval_job.assert_called_once()


class TestLabelApprovalJobsServiceSingleton(unittest.TestCase):
    """Test singleton pattern of LabelApprovalJobsService"""

    def test_get_singleton_instance(self):
        """Test that get_singleton_instance_of returns an instance"""
        instance = LabelApprovalJobsService.get_singleton_instance_of()
        self.assertIsInstance(instance, LabelApprovalJobsService)

    def test_lazy_initialization_of_persistence_adapter(self):
        """Test that persistence adapter is lazily initialized"""
        service = LabelApprovalJobsService()

        # Initially should be None
        self.assertIsNone(service._label_approval_jobs_persistence_adapter_lazy)

        # Access the property should trigger initialization
        adapter = service._label_approval_jobs_persistence_adapter
        self.assertIsNotNone(adapter)

        # Second access should return the same instance
        adapter2 = service._label_approval_jobs_persistence_adapter
        self.assertIs(adapter, adapter2)

    def test_lazy_initialization_of_user_management_service(self):
        """Test that user management service is lazily initialized"""
        service = LabelApprovalJobsService()

        # Initially should be None
        self.assertIsNone(service._user_management_service_lazy)

        # Access the property should trigger initialization
        user_service = service._user_management_service
        self.assertIsNotNone(user_service)

        # Second access should return the same instance
        user_service2 = service._user_management_service
        self.assertIs(user_service, user_service2)


class TestLabelApprovalJobsServiceSetStatus(unittest.TestCase):
    """Test set_label_approval_job_status method of LabelApprovalJobsService"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_org_id = uuid.uuid4()
        self.test_user_id = uuid.uuid4()
        self.test_job_id = uuid.uuid4()
        self.test_brand_name = uuid.uuid4()

        # Create mock dependencies
        self.mock_persistence_adapter = Mock()
        self.mock_user_management_service = Mock()

        # Create service instance with mocked dependencies
        self.service = LabelApprovalJobsService(
            label_approval_jobs_persistence_adapter=self.mock_persistence_adapter,
            user_management_service=self.mock_user_management_service
        )

    def _create_mock_info(self) -> Mock:
        """Helper to create a mock Info object"""
        mock_info = Mock()
        mock_info.context = {
            'security_context': {
                'authenticated_entity': {
                    'entity': 'user',
                    'id': str(self.test_user_id),
                    'org_id': str(self.test_org_id)
                },
            }
        }
        return mock_info

    def _create_mock_user(self) -> User:
        """Helper to create a mock User"""
        user = User(
            id=self.test_user_id,
            email="test@example.com",
            name="Test User",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            created_by_entity="system",
            created_by_entity_id="system",
            created_by_entity_domain="system",
            updated_by_entity="system"
        )
        return user

    def _create_mock_existing_job(self) -> LabelApprovalJob:
        """Helper to create a mock existing job"""
        job_metadata = JobMetadata(
            reviewer_id=str(self.test_user_id),
            reviewer_name="Test User",
            review_comments=["Initial review"],
            alcohol_content_percentage='5%',
            net_contents_in_milli_litres='355'
        )

        job = LabelApprovalJob(
            id=self.test_job_id,
            brand_name=self.test_brand_name,
            product_class='beer',
            status='pending',
            job_metadata=job_metadata,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            created_by_entity='user',
            created_by_entity_id=str(self.test_user_id),
            created_by_entity_domain=str(self.test_org_id),
            updated_by_entity='user',
            updated_by_entity_id=str(self.test_user_id),
            updated_by_entity_domain=str(self.test_org_id)
        )
        return job

    @patch('treasury.services.gateways.ttb_api.main.application.usecases.label_approval_jobs.SecurityContext')
    def test_set_label_approval_job_status_success(self, mock_security_context):
        """Test successfully setting job status"""
        # Setup mocks
        mock_info = self._create_mock_info()
        mock_user = self._create_mock_user()
        test_input = SetLabelApprovalJobStatusInput(
            job_id=self.test_job_id,
            status='approved',
            review_comment='Looks good!'
        )

        mock_security_ctx_instance = Mock()
        mock_security_context.from_info.return_value = mock_security_ctx_instance
        mock_security_ctx_instance.get_authenticated_entity_from_security_ctx.return_value = EntityDescriptor.of_user(
            id=str(self.test_user_id),
            org_id=self.test_org_id
        )

        def role_permissions_required_decorator(permissions):
            def decorator(func):
                return func

            return decorator

        mock_security_ctx_instance.role_permissions_required = role_permissions_required_decorator

        self.mock_user_management_service.get_user_by_authenticated_entity.return_value = mock_user

        mock_existing_job = self._create_mock_existing_job()
        self.mock_persistence_adapter.get_approval_job_by_id.return_value = mock_existing_job

        # Mock the updated job after status change
        mock_updated_job = self._create_mock_existing_job()
        mock_updated_job.status = 'approved'
        mock_updated_job.job_metadata = JobMetadata(
            reviewer_id=str(self.test_user_id),
            reviewer_name="Test User",
            review_comments=["Initial review", "Looks good!"],
            alcohol_content_percentage='5%',
            net_contents_in_milli_litres='355'
        )
        self.mock_persistence_adapter.set_job_status.return_value = mock_updated_job
        self.mock_persistence_adapter.set_job_metadata.return_value = mock_updated_job

        # Execute
        response = self.service.set_label_approval_job_status(info=mock_info, input=test_input)

        # Verify
        self.assertIsInstance(response, SetLabelApprovalJobStatusResponse)
        self.assertTrue(response.success)
        self.assertEqual(response.message, "Label approval job status updated successfully")
        self.assertIsNotNone(response.job)

        # Verify persistence adapter was called
        self.mock_persistence_adapter.get_approval_job_by_id.assert_called_once_with(job_id=self.test_job_id)
        self.mock_persistence_adapter.set_job_status.assert_called_once()
        self.mock_persistence_adapter.set_job_metadata.assert_called_once()

    @patch('treasury.services.gateways.ttb_api.main.application.usecases.label_approval_jobs.SecurityContext')
    def test_set_label_approval_job_status_job_not_found(self, mock_security_context):
        """Test setting status when job doesn't exist"""
        # Setup mocks
        mock_info = self._create_mock_info()
        mock_user = self._create_mock_user()
        test_input = SetLabelApprovalJobStatusInput(
            job_id=self.test_job_id,
            status='approved'
        )

        mock_security_ctx_instance = Mock()
        mock_security_context.from_info.return_value = mock_security_ctx_instance
        mock_security_ctx_instance.get_authenticated_entity_from_security_ctx.return_value = EntityDescriptor.of_user(
            id=str(self.test_user_id),
            org_id=self.test_org_id
        )

        def role_permissions_required_decorator(permissions):
            def decorator(func):
                return func

            return decorator

        mock_security_ctx_instance.role_permissions_required = role_permissions_required_decorator

        self.mock_user_management_service.get_user_by_authenticated_entity.return_value = mock_user

        # Job not found
        self.mock_persistence_adapter.get_approval_job_by_id.return_value = None

        # Execute
        response = self.service.set_label_approval_job_status(info=mock_info, input=test_input)

        # Verify
        self.assertFalse(response.success)
        self.assertIn("not found", response.message)
        self.assertIsNone(response.job)

    @patch('treasury.services.gateways.ttb_api.main.application.usecases.label_approval_jobs.SecurityContext')
    def test_set_label_approval_job_status_without_comment(self, mock_security_context):
        """Test setting status without review comment"""
        # Setup mocks
        mock_info = self._create_mock_info()
        mock_user = self._create_mock_user()
        test_input = SetLabelApprovalJobStatusInput(
            job_id=self.test_job_id,
            status='rejected'
        )

        mock_security_ctx_instance = Mock()
        mock_security_context.from_info.return_value = mock_security_ctx_instance
        mock_security_ctx_instance.get_authenticated_entity_from_security_ctx.return_value = EntityDescriptor.of_user(
            id=str(self.test_user_id),
            org_id=self.test_org_id
        )

        def role_permissions_required_decorator(permissions):
            def decorator(func):
                return func

            return decorator

        mock_security_ctx_instance.role_permissions_required = role_permissions_required_decorator

        self.mock_user_management_service.get_user_by_authenticated_entity.return_value = mock_user

        mock_existing_job = self._create_mock_existing_job()
        self.mock_persistence_adapter.get_approval_job_by_id.return_value = mock_existing_job

        mock_updated_job = self._create_mock_existing_job()
        mock_updated_job.status = 'rejected'
        self.mock_persistence_adapter.set_job_status.return_value = mock_updated_job

        # Execute
        response = self.service.set_label_approval_job_status(info=mock_info, input=test_input)

        # Verify
        self.assertTrue(response.success)
        self.assertIsNotNone(response.job)

        # Verify metadata was NOT updated (no comment provided)
        self.mock_persistence_adapter.set_job_metadata.assert_not_called()


class TestLabelApprovalJobsServiceAddComment(unittest.TestCase):
    """Test add_review_comment method of LabelApprovalJobsService"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_org_id = uuid.uuid4()
        self.test_user_id = uuid.uuid4()
        self.test_job_id = uuid.uuid4()
        self.test_brand_name = uuid.uuid4()

        # Create mock dependencies
        self.mock_persistence_adapter = Mock()
        self.mock_user_management_service = Mock()

        # Create service instance with mocked dependencies
        self.service = LabelApprovalJobsService(
            label_approval_jobs_persistence_adapter=self.mock_persistence_adapter,
            user_management_service=self.mock_user_management_service
        )

    def _create_mock_info(self) -> Mock:
        """Helper to create a mock Info object"""
        mock_info = Mock()
        mock_info.context = {
            'security_context': {
                'authenticated_entity': {
                    'entity': 'user',
                    'id': str(self.test_user_id),
                    'org_id': str(self.test_org_id)
                },
            }
        }
        return mock_info

    def _create_mock_user(self) -> User:
        """Helper to create a mock User"""
        user = User(
            id=self.test_user_id,
            email="test@example.com",
            name="Test User",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            created_by_entity="system",
            created_by_entity_id="system",
            created_by_entity_domain="system",
            updated_by_entity="system"
        )
        return user

    def _create_mock_existing_job(self) -> LabelApprovalJob:
        """Helper to create a mock existing job"""
        job_metadata = JobMetadata(
            reviewer_id=str(self.test_user_id),
            reviewer_name="Test User",
            review_comments=["Initial review"],
            alcohol_content_percentage='5%',
            net_contents_in_milli_litres='355'
        )

        job = LabelApprovalJob(
            id=self.test_job_id,
            brand_name=self.test_brand_name,
            product_class='beer',
            status='pending',
            job_metadata=job_metadata,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            created_by_entity='user',
            created_by_entity_id=str(self.test_user_id),
            created_by_entity_domain=str(self.test_org_id),
            updated_by_entity='user',
            updated_by_entity_id=str(self.test_user_id),
            updated_by_entity_domain=str(self.test_org_id)
        )
        return job

    @patch('treasury.services.gateways.ttb_api.main.application.usecases.label_approval_jobs.SecurityContext')
    def test_add_review_comment_success(self, mock_security_context):
        """Test successfully adding a review comment"""
        # Setup mocks
        mock_info = self._create_mock_info()
        mock_user = self._create_mock_user()
        test_input = AddReviewCommentInput(
            job_id=self.test_job_id,
            review_comment='Additional feedback added'
        )

        mock_security_ctx_instance = Mock()
        mock_security_context.from_info.return_value = mock_security_ctx_instance
        mock_security_ctx_instance.get_authenticated_entity_from_security_ctx.return_value = EntityDescriptor.of_user(
            id=str(self.test_user_id),
            org_id=self.test_org_id
        )

        def role_permissions_required_decorator(permissions):
            def decorator(func):
                return func

            return decorator

        mock_security_ctx_instance.role_permissions_required = role_permissions_required_decorator

        self.mock_user_management_service.get_user_by_authenticated_entity.return_value = mock_user

        mock_existing_job = self._create_mock_existing_job()
        self.mock_persistence_adapter.get_approval_job_by_id.return_value = mock_existing_job

        # Mock the updated job with new comment
        mock_updated_job = self._create_mock_existing_job()
        mock_updated_job.job_metadata = JobMetadata(
            reviewer_id=str(self.test_user_id),
            reviewer_name="Test User",
            review_comments=["Initial review", "Additional feedback added"],
            alcohol_content_percentage='5%',
            net_contents_in_milli_litres='355'
        )
        self.mock_persistence_adapter.set_job_metadata.return_value = mock_updated_job

        # Execute
        response = self.service.add_review_comment(info=mock_info, input=test_input)

        # Verify
        self.assertIsInstance(response, AddReviewCommentResponse)
        self.assertTrue(response.success)
        self.assertEqual(response.message, "Review comment added successfully")
        self.assertIsNotNone(response.job)

        # Verify persistence adapter was called
        self.mock_persistence_adapter.get_approval_job_by_id.assert_called_once_with(job_id=self.test_job_id)
        self.mock_persistence_adapter.set_job_metadata.assert_called_once()

    @patch('treasury.services.gateways.ttb_api.main.application.usecases.label_approval_jobs.SecurityContext')
    def test_add_review_comment_job_not_found(self, mock_security_context):
        """Test adding comment when job doesn't exist"""
        # Setup mocks
        mock_info = self._create_mock_info()
        mock_user = self._create_mock_user()
        test_input = AddReviewCommentInput(
            job_id=self.test_job_id,
            review_comment='Comment for non-existent job'
        )

        mock_security_ctx_instance = Mock()
        mock_security_context.from_info.return_value = mock_security_ctx_instance
        mock_security_ctx_instance.get_authenticated_entity_from_security_ctx.return_value = EntityDescriptor.of_user(
            id=str(self.test_user_id),
            org_id=self.test_org_id
        )

        def role_permissions_required_decorator(permissions):
            def decorator(func):
                return func

            return decorator

        mock_security_ctx_instance.role_permissions_required = role_permissions_required_decorator

        self.mock_user_management_service.get_user_by_authenticated_entity.return_value = mock_user

        # Job not found
        self.mock_persistence_adapter.get_approval_job_by_id.return_value = None

        # Execute
        response = self.service.add_review_comment(info=mock_info, input=test_input)

        # Verify
        self.assertFalse(response.success)
        self.assertIn("not found", response.message)
        self.assertIsNone(response.job)

    @patch('treasury.services.gateways.ttb_api.main.application.usecases.label_approval_jobs.SecurityContext')
    def test_add_review_comment_with_empty_comments_list(self, mock_security_context):
        """Test adding comment when review_comments is initially None"""
        # Setup mocks
        mock_info = self._create_mock_info()
        mock_user = self._create_mock_user()
        test_input = AddReviewCommentInput(
            job_id=self.test_job_id,
            review_comment='First comment'
        )

        mock_security_ctx_instance = Mock()
        mock_security_context.from_info.return_value = mock_security_ctx_instance
        mock_security_ctx_instance.get_authenticated_entity_from_security_ctx.return_value = EntityDescriptor.of_user(
            id=str(self.test_user_id),
            org_id=self.test_org_id
        )

        def role_permissions_required_decorator(permissions):
            def decorator(func):
                return func

            return decorator

        mock_security_ctx_instance.role_permissions_required = role_permissions_required_decorator

        self.mock_user_management_service.get_user_by_authenticated_entity.return_value = mock_user

        # Create job with None review_comments
        mock_existing_job = self._create_mock_existing_job()
        mock_existing_job.job_metadata = JobMetadata(
            reviewer_id=str(self.test_user_id),
            reviewer_name="Test User",
            review_comments=None,  # Initially None
            alcohol_content_percentage='5%',
            net_contents_in_milli_litres='355'
        )
        self.mock_persistence_adapter.get_approval_job_by_id.return_value = mock_existing_job

        mock_updated_job = self._create_mock_existing_job()
        mock_updated_job.job_metadata = JobMetadata(
            reviewer_id=str(self.test_user_id),
            reviewer_name="Test User",
            review_comments=["First comment"],
            alcohol_content_percentage='5%',
            net_contents_in_milli_litres='355'
        )
        self.mock_persistence_adapter.set_job_metadata.return_value = mock_updated_job

        # Execute
        response = self.service.add_review_comment(info=mock_info, input=test_input)

        # Verify
        self.assertTrue(response.success)
        self.assertIsNotNone(response.job)


class TestLabelApprovalJobsServiceListJobs(unittest.TestCase):
    """Test list_label_approval_jobs method of LabelApprovalJobsService"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_org_id = uuid.uuid4()
        self.test_user_id = uuid.uuid4()

        # Create mock dependencies
        self.mock_persistence_adapter = Mock()
        self.mock_user_management_service = Mock()

        # Create service instance with mocked dependencies
        self.service = LabelApprovalJobsService(
            label_approval_jobs_persistence_adapter=self.mock_persistence_adapter,
            user_management_service=self.mock_user_management_service
        )

    def _create_mock_info(self) -> Mock:
        """Helper to create a mock Info object"""
        mock_info = Mock()
        mock_info.context = {
            'security_context': {
                'authenticated_entity': {
                    'entity': 'user',
                    'id': str(self.test_user_id),
                    'org_id': str(self.test_org_id)
                },
            }
        }
        return mock_info

    def _create_mock_jobs_list(self, count: int = 3) -> list[LabelApprovalJob]:
        """Helper to create a list of mock jobs"""
        jobs = []
        for i in range(count):
            job_metadata = JobMetadata(
                reviewer_id=str(self.test_user_id),
                reviewer_name="Test User",
                review_comments=["Initial review"],
                alcohol_content_percentage='5%',
                net_contents_in_milli_litres='355'
            )

            job = LabelApprovalJob(
                id=uuid.uuid4(),
                brand_name=f"Brand_{i}",
                product_class='beer',
                status='pending' if i % 2 == 0 else 'approved',
                job_metadata=job_metadata,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                created_by_entity='user',
                created_by_entity_id=str(self.test_user_id),
                created_by_entity_domain=str(self.test_org_id),
                updated_by_entity='user',
                updated_by_entity_id=str(self.test_user_id),
                updated_by_entity_domain=str(self.test_org_id)
            )
            jobs.append(job)
        return jobs

    @patch('treasury.services.gateways.ttb_api.main.application.usecases.label_approval_jobs.SecurityContext')
    def test_list_label_approval_jobs_success(self, mock_security_context):
        """Test successfully listing label approval jobs"""
        # Setup mocks
        mock_info = self._create_mock_info()
        test_input = ListLabelApprovalJobsInput(
            brand_name_like=None,
            status=None,
            offset=0,
            limit=100
        )

        mock_security_ctx_instance = Mock()
        mock_security_context.from_info.return_value = mock_security_ctx_instance

        def role_permissions_required_decorator(permissions):
            def decorator(func):
                return func

            return decorator

        mock_security_ctx_instance.role_permissions_required = role_permissions_required_decorator

        # Mock persistence adapter to return jobs
        mock_jobs = self._create_mock_jobs_list(count=3)
        self.mock_persistence_adapter.list_approval_jobs.return_value = (mock_jobs, 3)

        # Execute
        response = self.service.list_label_approval_jobs(info=mock_info, input=test_input)

        # Verify
        self.assertIsInstance(response, ListLabelApprovalJobsResponse)
        self.assertTrue(response.success)
        self.assertEqual(len(response.jobs), 3)
        self.assertEqual(response.total_count, 3)
        self.assertEqual(response.offset, 0)
        self.assertEqual(response.limit, 100)
        self.assertIn("Found 3 jobs", response.message)

        # Verify persistence adapter was called
        self.mock_persistence_adapter.list_approval_jobs.assert_called_once_with(
            brand_name_like=None,
            status=None,
            offset=0,
            limit=100
        )

    @patch('treasury.services.gateways.ttb_api.main.application.usecases.label_approval_jobs.SecurityContext')
    def test_list_label_approval_jobs_with_brand_filter(self, mock_security_context):
        """Test listing jobs with brand_name_like filter"""
        # Setup mocks
        mock_info = self._create_mock_info()
        test_input = ListLabelApprovalJobsInput(
            brand_name_like="Bud",
            status=None,
            offset=0,
            limit=100
        )

        mock_security_ctx_instance = Mock()
        mock_security_context.from_info.return_value = mock_security_ctx_instance

        def role_permissions_required_decorator(permissions):
            def decorator(func):
                return func

            return decorator

        mock_security_ctx_instance.role_permissions_required = role_permissions_required_decorator

        # Mock persistence adapter to return filtered jobs
        mock_jobs = self._create_mock_jobs_list(count=2)
        self.mock_persistence_adapter.list_approval_jobs.return_value = (mock_jobs, 2)

        # Execute
        response = self.service.list_label_approval_jobs(info=mock_info, input=test_input)

        # Verify
        self.assertTrue(response.success)
        self.assertEqual(len(response.jobs), 2)
        self.assertEqual(response.total_count, 2)

        # Verify persistence adapter was called with filter
        self.mock_persistence_adapter.list_approval_jobs.assert_called_once_with(
            brand_name_like="Bud",
            status=None,
            offset=0,
            limit=100
        )

    @patch('treasury.services.gateways.ttb_api.main.application.usecases.label_approval_jobs.SecurityContext')
    def test_list_label_approval_jobs_with_status_filter(self, mock_security_context):
        """Test listing jobs with status filter"""
        # Setup mocks
        mock_info = self._create_mock_info()
        test_input = ListLabelApprovalJobsInput(
            brand_name_like=None,
            status="pending",
            offset=0,
            limit=100
        )

        mock_security_ctx_instance = Mock()
        mock_security_context.from_info.return_value = mock_security_ctx_instance

        def role_permissions_required_decorator(permissions):
            def decorator(func):
                return func

            return decorator

        mock_security_ctx_instance.role_permissions_required = role_permissions_required_decorator

        # Mock persistence adapter to return filtered jobs
        mock_jobs = self._create_mock_jobs_list(count=2)
        self.mock_persistence_adapter.list_approval_jobs.return_value = (mock_jobs, 2)

        # Execute
        response = self.service.list_label_approval_jobs(info=mock_info, input=test_input)

        # Verify
        self.assertTrue(response.success)
        self.assertEqual(len(response.jobs), 2)
        self.assertEqual(response.total_count, 2)

        # Verify persistence adapter was called with filter
        self.mock_persistence_adapter.list_approval_jobs.assert_called_once_with(
            brand_name_like=None,
            status="pending",
            offset=0,
            limit=100
        )

    @patch('treasury.services.gateways.ttb_api.main.application.usecases.label_approval_jobs.SecurityContext')
    def test_list_label_approval_jobs_with_pagination(self, mock_security_context):
        """Test listing jobs with pagination parameters"""
        # Setup mocks
        mock_info = self._create_mock_info()
        test_input = ListLabelApprovalJobsInput(
            brand_name_like=None,
            status=None,
            offset=10,
            limit=20
        )

        mock_security_ctx_instance = Mock()
        mock_security_context.from_info.return_value = mock_security_ctx_instance

        def role_permissions_required_decorator(permissions):
            def decorator(func):
                return func

            return decorator

        mock_security_ctx_instance.role_permissions_required = role_permissions_required_decorator

        # Mock persistence adapter to return jobs
        mock_jobs = self._create_mock_jobs_list(count=20)
        self.mock_persistence_adapter.list_approval_jobs.return_value = (mock_jobs, 100)

        # Execute
        response = self.service.list_label_approval_jobs(info=mock_info, input=test_input)

        # Verify
        self.assertTrue(response.success)
        self.assertEqual(len(response.jobs), 20)
        self.assertEqual(response.total_count, 100)
        self.assertEqual(response.offset, 10)
        self.assertEqual(response.limit, 20)

        # Verify persistence adapter was called with pagination
        self.mock_persistence_adapter.list_approval_jobs.assert_called_once_with(
            brand_name_like=None,
            status=None,
            offset=10,
            limit=20
        )

    @patch('treasury.services.gateways.ttb_api.main.application.usecases.label_approval_jobs.SecurityContext')
    def test_list_label_approval_jobs_empty_result(self, mock_security_context):
        """Test listing jobs when no jobs match the criteria"""
        # Setup mocks
        mock_info = self._create_mock_info()
        test_input = ListLabelApprovalJobsInput(
            brand_name_like="NonExistent",
            status=None,
            offset=0,
            limit=100
        )

        mock_security_ctx_instance = Mock()
        mock_security_context.from_info.return_value = mock_security_ctx_instance

        def role_permissions_required_decorator(permissions):
            def decorator(func):
                return func

            return decorator

        mock_security_ctx_instance.role_permissions_required = role_permissions_required_decorator

        # Mock persistence adapter to return empty list
        self.mock_persistence_adapter.list_approval_jobs.return_value = ([], 0)

        # Execute
        response = self.service.list_label_approval_jobs(info=mock_info, input=test_input)

        # Verify
        self.assertTrue(response.success)
        self.assertEqual(len(response.jobs), 0)
        self.assertEqual(response.total_count, 0)
        self.assertIn("Found 0 jobs", response.message)

    @patch('treasury.services.gateways.ttb_api.main.application.usecases.label_approval_jobs.SecurityContext')
    def test_list_label_approval_jobs_exception_handling(self, mock_security_context):
        """Test that exceptions are properly caught and handled"""
        # Setup mocks
        mock_info = self._create_mock_info()
        test_input = ListLabelApprovalJobsInput()

        mock_security_ctx_instance = Mock()
        mock_security_context.from_info.return_value = mock_security_ctx_instance

        def role_permissions_required_decorator(permissions):
            def decorator(func):
                return func

            return decorator

        mock_security_ctx_instance.role_permissions_required = role_permissions_required_decorator

        # Raise an exception
        self.mock_persistence_adapter.list_approval_jobs.side_effect = Exception("Database connection error")

        # Execute
        response = self.service.list_label_approval_jobs(info=mock_info, input=test_input)

        # Verify
        self.assertFalse(response.success)
        self.assertIn("Error listing label approval jobs", response.message)
        self.assertIn("Database connection error", response.message)
        self.assertEqual(len(response.jobs), 0)
        self.assertEqual(response.total_count, 0)

    def test_verify_label_image_or_raise_corrupted_image(self) -> None:
        """Test that corrupted/truncated images are rejected"""
        # This is a truncated JPEG image that should fail validation
        corrupted_image = "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/wAALCAABAAEBAREA/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9/9oACAEBAAA/APvV/9k="
        with self.assertRaises(ValueError) as context:
            self.service._verify_label_image_or_raise(
                label_image_base64=corrupted_image,
                permitted_types=["jpg", "png", "gif", "jpeg"]
            )
        self.assertIn("Invalid or corrupted image", str(context.exception))


if __name__ == '__main__':
    unittest.main()
