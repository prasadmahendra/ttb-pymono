import uuid
from datetime import datetime
from unittest.mock import MagicMock

from treasury.services.gateways.ttb_api.main.adapter.inp.gql.mutations.common import MutationsCommon
from treasury.services.gateways.ttb_api.main.application.config.api_service_config import ApiServiceConfig
from treasury.services.gateways.ttb_api.main.application.models.dto.label_approval_job_dto import (
    LabelApprovalJobDTO,
    JobMetadataDTO
)
from treasury.services.gateways.ttb_api.main.application.models.gql.label_approvals.create_label_approval_job_request import (
    CreateLabelApprovalJobResponse
)
from treasury.services.gateways.ttb_api.main.application.models.gql.label_approvals.update_label_approval_job_requests import (
    SetLabelApprovalJobStatusResponse,
    AddReviewCommentResponse
)
from treasury.services.gateways.ttb_api.main.application.usecases.label_approval_jobs_service import \
    LabelApprovalJobsService
from treasury.services.gateways.ttb_api.test.testing.base_api_service_test_case import BaseApiServiceTestCase


class TestMutationsLabelApprovalJobsRelated(BaseApiServiceTestCase):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(
            *args,
            api_service_config_base=ApiServiceConfig(),
            **kwargs
        )

    def setUp(self):
        super().setUp()
        MutationsCommon._label_approval_jobs_service = MagicMock(spec=LabelApprovalJobsService)

        # Test data
        self._test_job_id: uuid.UUID = uuid.uuid4()
        self._test_brand_name: uuid.UUID = uuid.uuid4()
        self._test_org_id: uuid.UUID = uuid.uuid4()
        self._current_time = datetime.now()

        # Sample job metadata DTO
        self._test_job_metadata_dto = JobMetadataDTO(
            reviewer_id="reviewer_123",
            reviewer_name="John Doe",
            review_comments=["Looks good", "Approved"],
            alcohol_content="40%",
            net_contents="750ml",
            bottler_info="XYZ Bottlers",
            manufacturer="ABC Distillery",
            warnings="Contains sulfites"
        )

        # Sample label approval job DTO
        self._test_job_dto = LabelApprovalJobDTO(
            id=self._test_job_id,
            brand_name=self._test_brand_name,
            product_class="spirits",
            status="pending",
            job_metadata=self._test_job_metadata_dto,
            created_at=self._current_time,
            updated_at=self._current_time,
            created_by_entity="user",
            created_by_entity_id="user-123",
            created_by_entity_domain=str(self._test_org_id),
            updated_by_entity="user",
            updated_by_entity_id="user-123",
            updated_by_entity_domain=str(self._test_org_id)
        )

    def test_create_label_approval_job_success(self) -> None:
        """Test successful creation of label approval job"""
        # Mock the service response
        MutationsCommon._label_approval_jobs_service.create_label_approval_job.return_value = CreateLabelApprovalJobResponse(
            job=self._test_job_dto,
            success=True,
            message="Label approval job created successfully"
        )

        mutation = """
        mutation CreateLabelApprovalJob($input: CreateLabelApprovalJobInput!) {
            createLabelApprovalJob(input: $input) {
                success
                message
                job {
                    id
                    brandName
                    productClass
                    status
                    jobMetadata {
                        reviewerId
                        reviewerName
                        reviewComments
                        alcoholContent
                        netContents
                        bottlerInfo
                        manufacturer
                        warnings
                    }
                    createdAt
                    updatedAt
                    createdByEntity
                    createdByEntityId
                    createdByEntityDomain
                }
            }
        }
        """

        variables = {
            "input": {
                "brandName": str(self._test_brand_name),
                "productClass": "spirits",
                "status": "pending",
                "jobMetadata": {
                    "reviewerId": "reviewer_123",
                    "reviewerName": "John Doe",
                    "reviewComments": ["Looks good", "Approved"],
                    "alcoholContentPercentage": "40%",
                    "netContentsInMilliLitres": "750ml",
                    "bottlerInfo": "XYZ Bottlers",
                    "manufacturer": "ABC Distillery",
                    "warnings": "Contains sulfites"
                }
            }
        }

        # Execute GraphQL mutation
        response = self.post(
            "/graphql",
            json={"query": mutation, "variables": variables}
        )

        # Verify response
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertIn("data", result)
        data = result["data"]

        create_job_response = data["createLabelApprovalJob"]
        self.assertIsNotNone(create_job_response)
        self.assertTrue(create_job_response.get("success"))
        self.assertEqual(create_job_response.get("message"), "Label approval job created successfully")

        job = create_job_response.get("job")
        self.assertIsNotNone(job)
        self.assertEqual(job.get("brandName"), str(self._test_brand_name))
        self.assertEqual(job.get("productClass"), "spirits")
        self.assertEqual(job.get("status"), "pending")

        # Verify job metadata
        job_metadata = job.get("jobMetadata")
        self.assertIsNotNone(job_metadata)
        self.assertEqual(job_metadata.get("reviewerId"), "reviewer_123")
        self.assertEqual(job_metadata.get("reviewerName"), "John Doe")
        self.assertEqual(job_metadata.get("alcoholContent"), "40%")
        self.assertEqual(job_metadata.get("netContents"), "750ml")

        # Verify service was called
        MutationsCommon._label_approval_jobs_service.create_label_approval_job.assert_called_once()

    def test_create_label_approval_job_minimal_metadata(self) -> None:
        """Test creation of label approval job with minimal metadata"""
        # Create DTO with minimal metadata
        minimal_metadata_dto = JobMetadataDTO(
            reviewer_id="reviewer_456"
        )

        minimal_job_dto = LabelApprovalJobDTO(
            id=self._test_job_id,
            brand_name=self._test_brand_name,
            product_class="beer",
            status="pending",
            job_metadata=minimal_metadata_dto,
            created_at=self._current_time,
            updated_at=self._current_time,
            created_by_entity="user",
            created_by_entity_id="user-123",
            created_by_entity_domain=str(self._test_org_id),
            updated_by_entity="user",
            updated_by_entity_id="user-123",
            updated_by_entity_domain=str(self._test_org_id)
        )

        # Mock the service response
        MutationsCommon._label_approval_jobs_service.create_label_approval_job.return_value = CreateLabelApprovalJobResponse(
            job=minimal_job_dto,
            success=True,
            message="Label approval job created successfully"
        )

        mutation = """
        mutation CreateLabelApprovalJob($input: CreateLabelApprovalJobInput!) {
            createLabelApprovalJob(input: $input) {
                success
                message
                job {
                    id
                    brandName
                    productClass
                    status
                    jobMetadata {
                        reviewerId
                    }
                }
            }
        }
        """

        variables = {
            "input": {
                "brandName": str(self._test_brand_name),
                "productClass": "beer",
                "status": "pending",
                "jobMetadata": {
                    "reviewerId": "reviewer_456"
                }
            }
        }

        # Execute GraphQL mutation
        response = self.post(
            "/graphql",
            json={"query": mutation, "variables": variables}
        )

        # Verify response
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertIn("data", result)
        data = result["data"]

        create_job_response = data["createLabelApprovalJob"]
        self.assertIsNotNone(create_job_response)
        self.assertTrue(create_job_response.get("success"))

        job = create_job_response.get("job")
        self.assertIsNotNone(job)
        self.assertEqual(job.get("productClass"), "beer")

        job_metadata = job.get("jobMetadata")
        self.assertIsNotNone(job_metadata)
        self.assertEqual(job_metadata.get("reviewerId"), "reviewer_456")

        # Verify service was called
        MutationsCommon._label_approval_jobs_service.create_label_approval_job.assert_called_once()

    def test_create_label_approval_job_without_metadata(self) -> None:
        """Test creation of label approval job without metadata"""
        # Create DTO with empty metadata
        empty_metadata_dto = JobMetadataDTO()

        empty_job_dto = LabelApprovalJobDTO(
            id=self._test_job_id,
            brand_name=self._test_brand_name,
            product_class="wine",
            status="pending",
            job_metadata=empty_metadata_dto,
            created_at=self._current_time,
            updated_at=self._current_time,
            created_by_entity="user",
            created_by_entity_id="user-123",
            created_by_entity_domain=str(self._test_org_id),
            updated_by_entity="user",
            updated_by_entity_id="user-123",
            updated_by_entity_domain=str(self._test_org_id)
        )

        # Mock the service response
        MutationsCommon._label_approval_jobs_service.create_label_approval_job.return_value = CreateLabelApprovalJobResponse(
            job=empty_job_dto,
            success=True,
            message="Label approval job created successfully"
        )

        mutation = """
        mutation CreateLabelApprovalJob($input: CreateLabelApprovalJobInput!) {
            createLabelApprovalJob(input: $input) {
                success
                message
                job {
                    id
                    brandName
                    productClass
                    status
                }
            }
        }
        """

        variables = {
            "input": {
                "brandName": str(self._test_brand_name),
                "productClass": "wine",
                "status": "pending"
            }
        }

        # Execute GraphQL mutation
        response = self.post(
            "/graphql",
            json={"query": mutation, "variables": variables}
        )

        # Verify response
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertIn("data", result)
        data = result["data"]

        create_job_response = data["createLabelApprovalJob"]
        self.assertIsNotNone(create_job_response)
        self.assertTrue(create_job_response.get("success"))

        job = create_job_response.get("job")
        self.assertIsNotNone(job)
        self.assertEqual(job.get("productClass"), "wine")

        # Verify service was called
        MutationsCommon._label_approval_jobs_service.create_label_approval_job.assert_called_once()

    def test_create_label_approval_job_failure(self) -> None:
        """Test label approval job creation failure"""
        # Mock the service response with failure
        MutationsCommon._label_approval_jobs_service.create_label_approval_job.return_value = CreateLabelApprovalJobResponse(
            job=None,
            success=False,
            message="Failed to create label approval job"
        )

        mutation = """
        mutation CreateLabelApprovalJob($input: CreateLabelApprovalJobInput!) {
            createLabelApprovalJob(input: $input) {
                success
                message
                job {
                    id
                }
            }
        }
        """

        variables = {
            "input": {
                "brandName": str(self._test_brand_name),
                "productClass": "spirits",
                "status": "pending"
            }
        }

        # Execute GraphQL mutation
        response = self.post(
            "/graphql",
            json={"query": mutation, "variables": variables}
        )

        # Verify response
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertIn("data", result)
        data = result["data"]

        create_job_response = data["createLabelApprovalJob"]
        self.assertIsNotNone(create_job_response)
        self.assertFalse(create_job_response.get("success"))
        self.assertEqual(create_job_response.get("message"), "Failed to create label approval job")
        self.assertIsNone(create_job_response.get("job"))

        # Verify service was called
        MutationsCommon._label_approval_jobs_service.create_label_approval_job.assert_called_once()

    def test_create_label_approval_job_different_product_classes(self) -> None:
        """Test creation of label approval jobs with different product classes"""
        product_classes = ["beer", "wine", "spirits"]

        for product_class in product_classes:
            with self.subTest(product_class=product_class):
                # Reset mock for each subtest
                MutationsCommon._label_approval_jobs_service.create_label_approval_job.reset_mock()

                # Create DTO for this product class
                job_dto = LabelApprovalJobDTO(
                    id=uuid.uuid4(),
                    brand_name=self._test_brand_name,
                    product_class=product_class,
                    status="pending",
                    job_metadata=JobMetadataDTO(reviewer_id="reviewer_123"),
                    created_at=self._current_time,
                    updated_at=self._current_time,
                    created_by_entity="user",
                    created_by_entity_id="user-123",
                    created_by_entity_domain=str(self._test_org_id),
                    updated_by_entity="user",
                    updated_by_entity_id="user-123",
                    updated_by_entity_domain=str(self._test_org_id)
                )

                # Mock the service response
                MutationsCommon._label_approval_jobs_service.create_label_approval_job.return_value = CreateLabelApprovalJobResponse(
                    job=job_dto,
                    success=True,
                    message=f"Label approval job for {product_class} created successfully"
                )

                mutation = """
                mutation CreateLabelApprovalJob($input: CreateLabelApprovalJobInput!) {
                    createLabelApprovalJob(input: $input) {
                        success
                        message
                        job {
                            productClass
                        }
                    }
                }
                """

                variables = {
                    "input": {
                        "brandName": str(self._test_brand_name),
                        "productClass": product_class,
                        "status": "pending",
                        "jobMetadata": {
                            "reviewerId": "reviewer_123"
                        }
                    }
                }

                # Execute GraphQL mutation
                response = self.post(
                    "/graphql",
                    json={"query": mutation, "variables": variables}
                )

                # Verify response
                self.assertEqual(response.status_code, 200)
                result = response.json()
                self.assertIn("data", result)
                data = result["data"]

                create_job_response = data["createLabelApprovalJob"]
                self.assertTrue(create_job_response.get("success"))

                job = create_job_response.get("job")
                self.assertIsNotNone(job)
                self.assertEqual(job.get("productClass"), product_class)

                # Verify service was called
                MutationsCommon._label_approval_jobs_service.create_label_approval_job.assert_called_once()

    def test_create_label_approval_job_with_review_comments(self) -> None:
        """Test creation with review comments"""
        # Create DTO with review comments
        metadata_with_comments = JobMetadataDTO(
            reviewer_id="reviewer_789",
            reviewer_name="Jane Smith",
            review_comments=["Comment 1", "Comment 2", "Comment 3"]
        )

        job_with_comments = LabelApprovalJobDTO(
            id=self._test_job_id,
            brand_name=self._test_brand_name,
            product_class="beer",
            status="pending",
            job_metadata=metadata_with_comments,
            created_at=self._current_time,
            updated_at=self._current_time,
            created_by_entity="user",
            created_by_entity_id="user-123",
            created_by_entity_domain=str(self._test_org_id),
            updated_by_entity="user",
            updated_by_entity_id="user-123",
            updated_by_entity_domain=str(self._test_org_id)
        )

        # Mock the service response
        MutationsCommon._label_approval_jobs_service.create_label_approval_job.return_value = CreateLabelApprovalJobResponse(
            job=job_with_comments,
            success=True,
            message="Label approval job created successfully"
        )

        mutation = """
        mutation CreateLabelApprovalJob($input: CreateLabelApprovalJobInput!) {
            createLabelApprovalJob(input: $input) {
                success
                job {
                    jobMetadata {
                        reviewerId
                        reviewerName
                        reviewComments
                    }
                }
            }
        }
        """

        variables = {
            "input": {
                "brandName": str(self._test_brand_name),
                "productClass": "beer",
                "status": "pending",
                "jobMetadata": {
                    "reviewerId": "reviewer_789",
                    "reviewerName": "Jane Smith",
                    "reviewComments": ["Comment 1", "Comment 2", "Comment 3"]
                }
            }
        }

        # Execute GraphQL mutation
        response = self.post(
            "/graphql",
            json={"query": mutation, "variables": variables}
        )

        # Verify response
        self.assertEqual(response.status_code, 200)
        result = response.json()
        data = result["data"]

        create_job_response = data["createLabelApprovalJob"]
        self.assertTrue(create_job_response.get("success"))

        job = create_job_response.get("job")
        job_metadata = job.get("jobMetadata")
        self.assertEqual(job_metadata.get("reviewComments"), ["Comment 1", "Comment 2", "Comment 3"])

        # Verify service was called
        MutationsCommon._label_approval_jobs_service.create_label_approval_job.assert_called_once()
    def test_set_label_approval_job_status_success(self) -> None:
        """Test successfully setting label approval job status"""
        # Create updated job DTO with new status
        updated_metadata_dto = JobMetadataDTO(
            reviewer_id="reviewer_123",
            reviewer_name="John Doe",
            review_comments=["Initial review", "Approved after review"],
            alcohol_content="40%",
            net_contents="750ml"
        )

        updated_job_dto = LabelApprovalJobDTO(
            id=self._test_job_id,
            brand_name=self._test_brand_name,
            product_class="spirits",
            status="approved",
            job_metadata=updated_metadata_dto,
            created_at=self._current_time,
            updated_at=self._current_time,
            created_by_entity="user",
            created_by_entity_id="user-123",
            created_by_entity_domain=str(self._test_org_id),
            updated_by_entity="user",
            updated_by_entity_id="user-123",
            updated_by_entity_domain=str(self._test_org_id)
        )

        # Mock the service response
        MutationsCommon._label_approval_jobs_service.set_label_approval_job_status.return_value = SetLabelApprovalJobStatusResponse(
            job=updated_job_dto,
            success=True,
            message="Label approval job status updated successfully"
        )

        mutation = """
        mutation SetLabelApprovalJobStatus($input: SetLabelApprovalJobStatusInput!) {
            setLabelApprovalJobStatus(input: $input) {
                success
                message
                job {
                    id
                    status
                    jobMetadata {
                        reviewComments
                    }
                }
            }
        }
        """

        variables = {
            "input": {
                "jobId": str(self._test_job_id),
                "status": "approved",
                "reviewComment": "Approved after review"
            }
        }

        # Execute GraphQL mutation
        response = self.post(
            "/graphql",
            json={"query": mutation, "variables": variables}
        )

        # Verify response
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertIn("data", result)
        data = result["data"]

        set_status_response = data["setLabelApprovalJobStatus"]
        self.assertIsNotNone(set_status_response)
        self.assertTrue(set_status_response.get("success"))
        self.assertEqual(set_status_response.get("message"), "Label approval job status updated successfully")

        job = set_status_response.get("job")
        self.assertIsNotNone(job)
        self.assertEqual(job.get("status"), "approved")

        # Verify review comments were updated
        job_metadata = job.get("jobMetadata")
        self.assertIsNotNone(job_metadata)
        review_comments = job_metadata.get("reviewComments")
        self.assertIn("Approved after review", review_comments)

        # Verify service was called
        MutationsCommon._label_approval_jobs_service.set_label_approval_job_status.assert_called_once()

    def test_set_label_approval_job_status_without_comment(self) -> None:
        """Test setting job status without review comment"""
        # Create updated job DTO
        updated_job_dto = LabelApprovalJobDTO(
            id=self._test_job_id,
            brand_name=self._test_brand_name,
            product_class="spirits",
            status="rejected",
            job_metadata=self._test_job_metadata_dto,
            created_at=self._current_time,
            updated_at=self._current_time,
            created_by_entity="user",
            created_by_entity_id="user-123",
            created_by_entity_domain=str(self._test_org_id),
            updated_by_entity="user",
            updated_by_entity_id="user-123",
            updated_by_entity_domain=str(self._test_org_id)
        )

        # Mock the service response
        MutationsCommon._label_approval_jobs_service.set_label_approval_job_status.return_value = SetLabelApprovalJobStatusResponse(
            job=updated_job_dto,
            success=True,
            message="Label approval job status updated successfully"
        )

        mutation = """
        mutation SetLabelApprovalJobStatus($input: SetLabelApprovalJobStatusInput!) {
            setLabelApprovalJobStatus(input: $input) {
                success
                message
                job {
                    id
                    status
                }
            }
        }
        """

        variables = {
            "input": {
                "jobId": str(self._test_job_id),
                "status": "rejected"
            }
        }

        # Execute GraphQL mutation
        response = self.post(
            "/graphql",
            json={"query": mutation, "variables": variables}
        )

        # Verify response
        self.assertEqual(response.status_code, 200)
        result = response.json()
        data = result["data"]

        set_status_response = data["setLabelApprovalJobStatus"]
        self.assertTrue(set_status_response.get("success"))
        self.assertEqual(set_status_response.get("job").get("status"), "rejected")

        # Verify service was called
        MutationsCommon._label_approval_jobs_service.set_label_approval_job_status.assert_called_once()

    def test_set_label_approval_job_status_job_not_found(self) -> None:
        """Test setting status for non-existent job"""
        # Mock the service response with failure
        MutationsCommon._label_approval_jobs_service.set_label_approval_job_status.return_value = SetLabelApprovalJobStatusResponse(
            job=None,
            success=False,
            message=f"Label approval job with id {self._test_job_id} not found"
        )

        mutation = """
        mutation SetLabelApprovalJobStatus($input: SetLabelApprovalJobStatusInput!) {
            setLabelApprovalJobStatus(input: $input) {
                success
                message
                job {
                    id
                }
            }
        }
        """

        variables = {
            "input": {
                "jobId": str(self._test_job_id),
                "status": "approved"
            }
        }

        # Execute GraphQL mutation
        response = self.post(
            "/graphql",
            json={"query": mutation, "variables": variables}
        )

        # Verify response
        self.assertEqual(response.status_code, 200)
        result = response.json()
        data = result["data"]

        set_status_response = data["setLabelApprovalJobStatus"]
        self.assertIsNotNone(set_status_response)
        self.assertFalse(set_status_response.get("success"))
        self.assertIn("not found", set_status_response.get("message"))
        self.assertIsNone(set_status_response.get("job"))

        # Verify service was called
        MutationsCommon._label_approval_jobs_service.set_label_approval_job_status.assert_called_once()

    def test_add_review_comment_success(self) -> None:
        """Test successfully adding a review comment"""
        # Create updated job DTO with new comment
        updated_metadata_dto = JobMetadataDTO(
            reviewer_id="reviewer_123",
            reviewer_name="John Doe",
            review_comments=["Initial review", "Additional feedback"],
            alcohol_content="40%",
            net_contents="750ml"
        )

        updated_job_dto = LabelApprovalJobDTO(
            id=self._test_job_id,
            brand_name=self._test_brand_name,
            product_class="spirits",
            status="pending",
            job_metadata=updated_metadata_dto,
            created_at=self._current_time,
            updated_at=self._current_time,
            created_by_entity="user",
            created_by_entity_id="user-123",
            created_by_entity_domain=str(self._test_org_id),
            updated_by_entity="user",
            updated_by_entity_id="user-123",
            updated_by_entity_domain=str(self._test_org_id)
        )

        # Mock the service response
        MutationsCommon._label_approval_jobs_service.add_review_comment.return_value = AddReviewCommentResponse(
            job=updated_job_dto,
            success=True,
            message="Review comment added successfully"
        )

        mutation = """
        mutation AddReviewComment($input: AddReviewCommentInput!) {
            addReviewComment(input: $input) {
                success
                message
                job {
                    id
                    jobMetadata {
                        reviewComments
                    }
                }
            }
        }
        """

        variables = {
            "input": {
                "jobId": str(self._test_job_id),
                "reviewComment": "Additional feedback"
            }
        }

        # Execute GraphQL mutation
        response = self.post(
            "/graphql",
            json={"query": mutation, "variables": variables}
        )

        # Verify response
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertIn("data", result)
        data = result["data"]

        add_comment_response = data["addReviewComment"]
        self.assertIsNotNone(add_comment_response)
        self.assertTrue(add_comment_response.get("success"))
        self.assertEqual(add_comment_response.get("message"), "Review comment added successfully")

        job = add_comment_response.get("job")
        self.assertIsNotNone(job)

        # Verify review comments were updated
        job_metadata = job.get("jobMetadata")
        self.assertIsNotNone(job_metadata)
        review_comments = job_metadata.get("reviewComments")
        self.assertIn("Additional feedback", review_comments)
        self.assertEqual(len(review_comments), 2)

        # Verify service was called
        MutationsCommon._label_approval_jobs_service.add_review_comment.assert_called_once()

    def test_add_review_comment_job_not_found(self) -> None:
        """Test adding comment to non-existent job"""
        # Mock the service response with failure
        MutationsCommon._label_approval_jobs_service.add_review_comment.return_value = AddReviewCommentResponse(
            job=None,
            success=False,
            message=f"Label approval job with id {self._test_job_id} not found"
        )

        mutation = """
        mutation AddReviewComment($input: AddReviewCommentInput!) {
            addReviewComment(input: $input) {
                success
                message
                job {
                    id
                }
            }
        }
        """

        variables = {
            "input": {
                "jobId": str(self._test_job_id),
                "reviewComment": "This should fail"
            }
        }

        # Execute GraphQL mutation
        response = self.post(
            "/graphql",
            json={"query": mutation, "variables": variables}
        )

        # Verify response
        self.assertEqual(response.status_code, 200)
        result = response.json()
        data = result["data"]

        add_comment_response = data["addReviewComment"]
        self.assertIsNotNone(add_comment_response)
        self.assertFalse(add_comment_response.get("success"))
        self.assertIn("not found", add_comment_response.get("message"))
        self.assertIsNone(add_comment_response.get("job"))

        # Verify service was called
        MutationsCommon._label_approval_jobs_service.add_review_comment.assert_called_once()
