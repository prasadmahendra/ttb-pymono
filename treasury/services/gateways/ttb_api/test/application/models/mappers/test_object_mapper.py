"""Unit tests for ObjectMapper"""
import unittest
import uuid
from datetime import datetime

from treasury.services.gateways.ttb_api.main.application.models.domain.label_approval_job import (
    LabelApprovalJob,
    JobMetadata,
    LabelImage,
    LabelImageAnalysisResult
)
from treasury.services.gateways.ttb_api.main.application.models.domain.label_extraction_data import (
    BrandDataStrict,
    ProductInfoStrict,
    ProductOtherInfo
)
from treasury.services.gateways.ttb_api.main.application.models.dto.label_approval_job_dto import (
    LabelApprovalJobDTO,
    JobMetadataDTO
)
from treasury.services.gateways.ttb_api.main.application.models.dto.label_extraction_dto import (
    BrandDataStrictDTO,
    ProductInfoStrictDTO,
    ProductOtherInfoDTO
)
from treasury.services.gateways.ttb_api.main.application.models.dto.label_image_dto import (
    LabelImageDTO,
    LabelImageAnalysisResultDTO
)
from treasury.services.gateways.ttb_api.main.application.models.mappers.object_mapper import ObjectMapper


class TestObjectMapperLabelApprovalJob(unittest.TestCase):
    """Test ObjectMapper for LabelApprovalJob to LabelApprovalJobDTO mapping"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_job_id = uuid.uuid4()
        self.test_brand_name = "Test Brand"
        self.test_org_id = uuid.uuid4()
        self.test_reviewer_id = str(uuid.uuid4())
        self.current_time = datetime.now()

    def test_map_label_approval_job_with_full_metadata(self):
        """Test mapping LabelApprovalJob with complete nested metadata to DTO"""
        # Create nested structures
        product_other_info = ProductOtherInfo(
            bottler_info="Test Bottlers Inc.",
            manufacturer="Test Brewery",
            warnings="Contains alcohol"
        )

        product_info_strict = ProductInfoStrict(
            name=self.test_brand_name,
            product_class_type="beer",
            alcohol_content_abv="5%",
            net_contents="355 mL",
            other_info=product_other_info
        )

        brand_data_strict = BrandDataStrict(
            brand_name=self.test_brand_name,
            products=[product_info_strict]
        )

        analysis_result = LabelImageAnalysisResult(
            brand_name_found=True,
            brand_name_found_results_reasoning="Brand name clearly visible",
            product_class_found=True,
            product_class_found_results_reasoning="Product class stated as beer",
            alcohol_content_found=True,
            alcohol_content_found_results_reasoning="5% ABV found on label",
            net_contents_found=True,
            net_contents_found_results_reasoning="355 mL stated on label",
            health_warning_found=True,
            health_warning_found_results_reasoning="Government warning present"
        )

        label_image = LabelImage(
            image_url="https://example.com/label.jpg",
            image_content_type="image/jpg",
            base64="data:image/jpg;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
            upload_date=self.current_time,
            approved=True,
            approved_date=self.current_time,
            rejected=False,
            rejected_date=None,
            analysis_result=analysis_result
        )

        job_metadata = JobMetadata(
            reviewer_id=self.test_reviewer_id,
            reviewer_name="John Doe",
            review_comments=["Initial review", "Looks good", "Approved"],
            product_info=brand_data_strict,
            label_images=[label_image]
        )

        # Create LabelApprovalJob
        label_approval_job = LabelApprovalJob(
            id=self.test_job_id,
            brand_name=self.test_brand_name,
            product_class="beer",
            status="approved",
            job_metadata=job_metadata,
            created_at=self.current_time,
            updated_at=self.current_time,
            created_by_entity="user",
            created_by_entity_id="user-123",
            created_by_entity_domain=str(self.test_org_id),
            updated_by_entity="user",
            updated_by_entity_id="user-123",
            updated_by_entity_domain=str(self.test_org_id)
        )

        # Map to DTO
        job_dto = ObjectMapper.map(label_approval_job, LabelApprovalJobDTO)

        # Verify basic fields
        self.assertEqual(job_dto.id, self.test_job_id)
        self.assertEqual(job_dto.brand_name, self.test_brand_name)
        self.assertEqual(job_dto.product_class, "beer")
        self.assertEqual(job_dto.status, "approved")
        self.assertEqual(job_dto.created_by_entity, "user")
        self.assertEqual(job_dto.created_by_entity_id, "user-123")

        # Verify job_metadata is not None
        self.assertIsNotNone(job_dto.job_metadata, "job_metadata should not be None")

        # Verify job_metadata fields
        self.assertEqual(job_dto.job_metadata.reviewer_id, self.test_reviewer_id)
        self.assertEqual(job_dto.job_metadata.reviewer_name, "John Doe")
        self.assertEqual(len(job_dto.job_metadata.review_comments), 3)
        self.assertIn("Initial review", job_dto.job_metadata.review_comments)
        self.assertIn("Looks good", job_dto.job_metadata.review_comments)
        self.assertIn("Approved", job_dto.job_metadata.review_comments)

        # Verify product_info is not None
        self.assertIsNotNone(job_dto.job_metadata.product_info, "product_info should not be None")
        self.assertEqual(job_dto.job_metadata.product_info.brand_name, self.test_brand_name)

        # Verify products list
        self.assertIsNotNone(job_dto.job_metadata.product_info.products)
        self.assertEqual(len(job_dto.job_metadata.product_info.products), 1)

        product = job_dto.job_metadata.product_info.products[0]
        self.assertEqual(product.name, self.test_brand_name)
        self.assertEqual(product.product_class_type, "beer")
        self.assertEqual(product.alcohol_content_abv, "5%")
        self.assertEqual(product.net_contents, "355 mL")

        # Verify product other_info
        self.assertIsNotNone(product.other_info)
        self.assertEqual(product.other_info.bottler_info, "Test Bottlers Inc.")
        self.assertEqual(product.other_info.manufacturer, "Test Brewery")
        self.assertEqual(product.other_info.warnings, "Contains alcohol")

        # Verify label_images is not None
        self.assertIsNotNone(job_dto.job_metadata.label_images, "label_images should not be None")
        self.assertEqual(len(job_dto.job_metadata.label_images), 1)

        label_image_dto = job_dto.job_metadata.label_images[0]
        self.assertEqual(label_image_dto.image_url, "https://example.com/label.jpg")
        self.assertEqual(label_image_dto.image_content_type, "image/jpg")
        self.assertEqual(label_image_dto.approved, True)
        self.assertEqual(label_image_dto.rejected, False)

        # Verify analysis_result
        self.assertIsNotNone(label_image_dto.analysis_result)
        self.assertTrue(label_image_dto.analysis_result.brand_name_found)
        self.assertEqual(label_image_dto.analysis_result.brand_name_found_results_reasoning, "Brand name clearly visible")
        self.assertTrue(label_image_dto.analysis_result.product_class_found)
        self.assertTrue(label_image_dto.analysis_result.alcohol_content_found)
        self.assertTrue(label_image_dto.analysis_result.net_contents_found)
        self.assertTrue(label_image_dto.analysis_result.health_warning_found)

    def test_map_label_approval_job_with_minimal_metadata(self):
        """Test mapping LabelApprovalJob with minimal metadata"""
        job_metadata = JobMetadata(
            reviewer_id=self.test_reviewer_id,
            reviewer_name=None,
            review_comments=None,
            product_info=None,
            label_images=None
        )

        label_approval_job = LabelApprovalJob(
            id=self.test_job_id,
            brand_name=self.test_brand_name,
            product_class="spirits",
            status="pending",
            job_metadata=job_metadata,
            created_at=self.current_time,
            updated_at=self.current_time,
            created_by_entity="user",
            created_by_entity_id="user-456",
            created_by_entity_domain=str(self.test_org_id),
            updated_by_entity="user",
            updated_by_entity_id="user-456",
            updated_by_entity_domain=str(self.test_org_id)
        )

        # Map to DTO
        job_dto = ObjectMapper.map(label_approval_job, LabelApprovalJobDTO)

        # Verify basic fields
        self.assertEqual(job_dto.id, self.test_job_id)
        self.assertEqual(job_dto.brand_name, self.test_brand_name)
        self.assertEqual(job_dto.product_class, "spirits")
        self.assertEqual(job_dto.status, "pending")

        # Verify job_metadata is not None even with minimal data
        self.assertIsNotNone(job_dto.job_metadata, "job_metadata should not be None")
        self.assertEqual(job_dto.job_metadata.reviewer_id, self.test_reviewer_id)
        self.assertIsNone(job_dto.job_metadata.reviewer_name)
        self.assertIsNone(job_dto.job_metadata.review_comments)
        self.assertIsNone(job_dto.job_metadata.product_info)
        self.assertIsNone(job_dto.job_metadata.label_images)

    def test_map_label_approval_job_with_empty_review_comments(self):
        """Test mapping LabelApprovalJob with empty review comments list"""
        job_metadata = JobMetadata(
            reviewer_id=self.test_reviewer_id,
            reviewer_name="Jane Smith",
            review_comments=[],  # Empty list
            product_info=None,
            label_images=None
        )

        label_approval_job = LabelApprovalJob(
            id=self.test_job_id,
            brand_name=self.test_brand_name,
            product_class="wine",
            status="rejected",
            job_metadata=job_metadata,
            created_at=self.current_time,
            updated_at=self.current_time,
            created_by_entity="user",
            created_by_entity_id="user-789",
            created_by_entity_domain=str(self.test_org_id),
            updated_by_entity="user",
            updated_by_entity_id="user-789",
            updated_by_entity_domain=str(self.test_org_id)
        )

        # Map to DTO
        job_dto = ObjectMapper.map(label_approval_job, LabelApprovalJobDTO)

        # Verify job_metadata
        self.assertIsNotNone(job_dto.job_metadata)
        self.assertEqual(job_dto.job_metadata.reviewer_id, self.test_reviewer_id)
        self.assertEqual(job_dto.job_metadata.reviewer_name, "Jane Smith")
        self.assertEqual(job_dto.job_metadata.review_comments, [])

    def test_map_label_approval_job_with_multiple_label_images(self):
        """Test mapping LabelApprovalJob with multiple label images"""
        label_image1 = LabelImage(
            image_url="https://example.com/label1.jpg",
            image_content_type="image/jpg",
            base64="data:image/jpg;base64,test1",
            upload_date=self.current_time,
            approved=True,
            approved_date=self.current_time
        )

        label_image2 = LabelImage(
            image_url="https://example.com/label2.png",
            image_content_type="image/png",
            base64="data:image/png;base64,test2",
            upload_date=self.current_time,
            approved=False,
            rejected=True,
            rejected_date=self.current_time
        )

        job_metadata = JobMetadata(
            reviewer_id=self.test_reviewer_id,
            reviewer_name="Test Reviewer",
            review_comments=["Multiple images uploaded"],
            product_info=None,
            label_images=[label_image1, label_image2]
        )

        label_approval_job = LabelApprovalJob(
            id=self.test_job_id,
            brand_name=self.test_brand_name,
            product_class="beer",
            status="pending",
            job_metadata=job_metadata,
            created_at=self.current_time,
            updated_at=self.current_time,
            created_by_entity="user",
            created_by_entity_id="user-123",
            created_by_entity_domain=str(self.test_org_id),
            updated_by_entity="user",
            updated_by_entity_id="user-123",
            updated_by_entity_domain=str(self.test_org_id)
        )

        # Map to DTO
        job_dto = ObjectMapper.map(label_approval_job, LabelApprovalJobDTO)

        # Verify label_images
        self.assertIsNotNone(job_dto.job_metadata.label_images)
        self.assertEqual(len(job_dto.job_metadata.label_images), 2)

        # Verify first image
        self.assertEqual(job_dto.job_metadata.label_images[0].image_url, "https://example.com/label1.jpg")
        self.assertEqual(job_dto.job_metadata.label_images[0].image_content_type, "image/jpg")
        self.assertTrue(job_dto.job_metadata.label_images[0].approved)

        # Verify second image
        self.assertEqual(job_dto.job_metadata.label_images[1].image_url, "https://example.com/label2.png")
        self.assertEqual(job_dto.job_metadata.label_images[1].image_content_type, "image/png")
        self.assertFalse(job_dto.job_metadata.label_images[1].approved)
        self.assertTrue(job_dto.job_metadata.label_images[1].rejected)

    def test_map_list_of_label_approval_jobs(self):
        """Test mapping a list of LabelApprovalJobs to DTOs"""
        jobs = []
        for i in range(3):
            job_metadata = JobMetadata(
                reviewer_id=f"reviewer-{i}",
                reviewer_name=f"Reviewer {i}",
                review_comments=[f"Comment {i}"]
            )

            job = LabelApprovalJob(
                id=uuid.uuid4(),
                brand_name=f"Brand {i}",
                product_class="beer",
                status="pending",
                job_metadata=job_metadata,
                created_at=self.current_time,
                updated_at=self.current_time,
                created_by_entity="user",
                created_by_entity_id=f"user-{i}",
                created_by_entity_domain=str(self.test_org_id),
                updated_by_entity="user",
                updated_by_entity_id=f"user-{i}",
                updated_by_entity_domain=str(self.test_org_id)
            )
            jobs.append(job)

        # Map list to DTOs
        job_dtos = ObjectMapper.map_list(jobs, LabelApprovalJobDTO)

        # Verify
        self.assertEqual(len(job_dtos), 3)
        for i, job_dto in enumerate(job_dtos):
            self.assertEqual(job_dto.brand_name, f"Brand {i}")
            self.assertIsNotNone(job_dto.job_metadata)
            self.assertEqual(job_dto.job_metadata.reviewer_id, f"reviewer-{i}")
            self.assertEqual(job_dto.job_metadata.reviewer_name, f"Reviewer {i}")


class TestLabelApprovalJobDeserialization(unittest.TestCase):
    """Test that LabelApprovalJob properly deserializes job_metadata from dict"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_job_id = uuid.uuid4()
        self.test_brand_name = "Test Brand"
        self.test_org_id = uuid.uuid4()
        self.current_time = datetime.now()

    def test_job_metadata_deserialization_from_dict(self):
        """Test that job_metadata is automatically converted from dict to JobMetadata"""
        # Simulate what SQLAlchemy does when loading from database
        # The job_metadata comes back as a dict from the JSON column
        job_metadata_dict = {
            "reviewer_id": "reviewer-123",
            "reviewer_name": "John Doe",
            "review_comments": ["Comment 1", "Comment 2"],
            "product_info": {
                "brand_name": "Test Brand",
                "products": [
                    {
                        "name": "Test Product",
                        "product_class_type": "beer",
                        "alcohol_content_abv": "5%",
                        "net_contents": "355 mL",
                        "other_info": {
                            "bottler_info": "Test Bottlers",
                            "manufacturer": "Test Brewery",
                            "warnings": "Contains alcohol"
                        }
                    }
                ]
            },
            "label_images": [
                {
                    "image_url": "https://example.com/label.jpg",
                    "image_content_type": "image/jpg",
                    "base64": "data:image/jpg;base64,test",
                    "upload_date": self.current_time.isoformat(),
                    "approved": True
                }
            ]
        }

        # Create LabelApprovalJob with job_metadata as dict (simulating database load)
        job = LabelApprovalJob(
            id=self.test_job_id,
            brand_name=self.test_brand_name,
            product_class="beer",
            status="pending",
            job_metadata=job_metadata_dict,  # Pass as dict
            created_at=self.current_time,
            updated_at=self.current_time,
            created_by_entity="user",
            created_by_entity_id="user-123",
            created_by_entity_domain=str(self.test_org_id),
            updated_by_entity="user",
            updated_by_entity_id="user-123",
            updated_by_entity_domain=str(self.test_org_id)
        )

        # Verify that job_metadata is now a JobMetadata object, not a dict
        self.assertIsInstance(job.job_metadata, JobMetadata,
                            "job_metadata should be JobMetadata object, not dict")
        self.assertNotIsInstance(job.job_metadata, dict,
                                "job_metadata should not be a dict")

        # Verify nested data is properly deserialized
        self.assertEqual(job.job_metadata.reviewer_id, "reviewer-123")
        self.assertEqual(job.job_metadata.reviewer_name, "John Doe")
        self.assertEqual(len(job.job_metadata.review_comments), 2)

        # Verify product_info is a BrandDataStrict object
        self.assertIsNotNone(job.job_metadata.product_info)
        self.assertIsInstance(job.job_metadata.product_info, BrandDataStrict)
        self.assertEqual(job.job_metadata.product_info.brand_name, "Test Brand")

        # Verify products
        self.assertEqual(len(job.job_metadata.product_info.products), 1)
        product = job.job_metadata.product_info.products[0]
        self.assertIsInstance(product, ProductInfoStrict)
        self.assertEqual(product.name, "Test Product")
        self.assertEqual(product.alcohol_content_abv, "5%")

        # Verify label_images
        self.assertIsNotNone(job.job_metadata.label_images)
        self.assertEqual(len(job.job_metadata.label_images), 1)
        label_image = job.job_metadata.label_images[0]
        self.assertIsInstance(label_image, LabelImage)
        self.assertEqual(label_image.image_url, "https://example.com/label.jpg")

    def test_job_metadata_remains_as_object_when_already_object(self):
        """Test that job_metadata remains as JobMetadata when already an object"""
        # Create JobMetadata object
        job_metadata = JobMetadata(
            reviewer_id="reviewer-456",
            reviewer_name="Jane Smith",
            review_comments=["Review completed"]
        )

        # Create LabelApprovalJob with job_metadata as object
        job = LabelApprovalJob(
            id=self.test_job_id,
            brand_name=self.test_brand_name,
            product_class="wine",
            status="approved",
            job_metadata=job_metadata,  # Pass as JobMetadata object
            created_at=self.current_time,
            updated_at=self.current_time,
            created_by_entity="user",
            created_by_entity_id="user-456",
            created_by_entity_domain=str(self.test_org_id),
            updated_by_entity="user",
            updated_by_entity_id="user-456",
            updated_by_entity_domain=str(self.test_org_id)
        )

        # Verify it remains a JobMetadata object
        self.assertIsInstance(job.job_metadata, JobMetadata)
        self.assertEqual(job.job_metadata.reviewer_id, "reviewer-456")
        self.assertEqual(job.job_metadata.reviewer_name, "Jane Smith")


if __name__ == '__main__':
    unittest.main()