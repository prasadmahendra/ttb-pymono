import uuid
from datetime import datetime, timedelta
from unittest.mock import MagicMock, ANY

from treasury.services.gateways.ttb_api.main.adapter.inp.gql.queries.common import QueriesCommon
from treasury.services.gateways.ttb_api.main.application.config.api_service_config import ApiServiceConfig
from treasury.services.gateways.ttb_api.main.application.models.dto.label_approval_job_dto import LabelApprovalJobDTO, JobMetadataDTO
from treasury.services.gateways.ttb_api.main.application.models.gql.label_approvals.list_label_approval_jobs_request import (
    ListLabelApprovalJobsResponse
)
from treasury.services.gateways.ttb_api.main.application.usecases.label_approval_jobs_service import \
    LabelApprovalJobsService
from treasury.services.gateways.ttb_api.test.testing.base_api_service_test_case import BaseApiServiceTestCase


class TestQueriesLabelApprovalJobsRelated(BaseApiServiceTestCase):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(
            *args,
            api_service_config_base=ApiServiceConfig(),
            **kwargs
        )

    def setUp(self):
        super().setUp()
        QueriesCommon._label_approval_jobs_service = MagicMock(spec=LabelApprovalJobsService)

    def _create_mock_job_dto(self, brand_name: str = "Test Brand", status: str = "pending") -> LabelApprovalJobDTO:
        """Helper to create a properly initialized LabelApprovalJobDTO"""
        job_metadata = JobMetadataDTO(
            reviewer_id="reviewer_123",
            reviewer_name="Test Reviewer",
            review_comments=["Initial review"],
            alcohol_content="5.0%",
            net_contents="355"
        )

        return LabelApprovalJobDTO(
            id=uuid.uuid4(),
            brand_name=brand_name,
            product_class="beer",
            status=status,
            job_metadata=job_metadata,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            created_by_entity="user",
            created_by_entity_id="user-123",
            created_by_entity_domain="test-org",
            updated_by_entity="user"
        )

    def test_list_jobs_success(self):
        """Test successfully listing label approval jobs via GraphQL"""
        # Create mock jobs
        mock_job1 = self._create_mock_job_dto(brand_name="Budweiser", status="pending")
        mock_job2 = self._create_mock_job_dto(brand_name="Corona", status="approved")

        # Mock service response
        mock_response = ListLabelApprovalJobsResponse(
            jobs=[mock_job1, mock_job2],
            total_count=2,
            offset=0,
            limit=100,
            success=True,
            message="Found 2 jobs"
        )
        QueriesCommon._label_approval_jobs_service.list_label_approval_jobs.return_value = mock_response

        # GraphQL query
        query = """
            query ListJobs($input: ListLabelApprovalJobsInput!) {
                listLabelApprovalJobs(input: $input) {
                    jobs {
                        id
                        brandName
                        productClass
                        status
                    }
                    totalCount
                    offset
                    limit
                    success
                    message
                }
            }
        """

        variables = {
            "input": {
                "brandNameLike": None,
                "status": None,
                "offset": 0,
                "limit": 100
            }
        }

        # Execute query
        response = self.post("/graphql", json={"query": query, "variables": variables})

        # Verify response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("data", data)
        list_jobs_response = data["data"]["listLabelApprovalJobs"]
        self.assertTrue(list_jobs_response["success"])
        self.assertEqual(len(list_jobs_response["jobs"]), 2)
        self.assertEqual(list_jobs_response["totalCount"], 2)
        self.assertEqual(list_jobs_response["offset"], 0)
        self.assertEqual(list_jobs_response["limit"], 100)

    def test_list_jobs_with_brand_filter(self):
        """Test listing jobs with brand_name_like filter"""
        # Create mock job
        mock_job = self._create_mock_job_dto(brand_name="Budweiser", status="pending")

        # Mock service response
        mock_response = ListLabelApprovalJobsResponse(
            jobs=[mock_job],
            total_count=1,
            offset=0,
            limit=100,
            success=True,
            message="Found 1 jobs"
        )
        QueriesCommon._label_approval_jobs_service.list_label_approval_jobs.return_value = mock_response

        # GraphQL query
        query = """
            query ListJobs($input: ListLabelApprovalJobsInput!) {
                listLabelApprovalJobs(input: $input) {
                    jobs {
                        id
                        brandName
                    }
                    totalCount
                    success
                }
            }
        """

        variables = {
            "input": {
                "brandNameLike": "Bud",
                "status": None,
                "offset": 0,
                "limit": 100
            }
        }

        # Execute query
        response = self.post("/graphql", json={"query": query, "variables": variables})

        # Verify response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        list_jobs_response = data["data"]["listLabelApprovalJobs"]
        self.assertTrue(list_jobs_response["success"])
        self.assertEqual(len(list_jobs_response["jobs"]), 1)
        self.assertEqual(list_jobs_response["totalCount"], 1)

    def test_list_jobs_with_pagination(self):
        """Test listing jobs with pagination"""
        # Create mock jobs
        mock_jobs = [
            self._create_mock_job_dto(brand_name=f"Brand_{i}", status="pending")
            for i in range(10)
        ]

        # Mock service response
        mock_response = ListLabelApprovalJobsResponse(
            jobs=mock_jobs,
            total_count=50,
            offset=10,
            limit=10,
            success=True,
            message="Found 10 jobs"
        )
        QueriesCommon._label_approval_jobs_service.list_label_approval_jobs.return_value = mock_response

        # GraphQL query
        query = """
            query ListJobs($input: ListLabelApprovalJobsInput!) {
                listLabelApprovalJobs(input: $input) {
                    jobs {
                        id
                    }
                    totalCount
                    offset
                    limit
                    success
                }
            }
        """

        variables = {
            "input": {
                "brandNameLike": None,
                "status": None,
                "offset": 10,
                "limit": 10
            }
        }

        # Execute query
        response = self.post("/graphql", json={"query": query, "variables": variables})

        # Verify response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        list_jobs_response = data["data"]["listLabelApprovalJobs"]
        self.assertTrue(list_jobs_response["success"])
        self.assertEqual(len(list_jobs_response["jobs"]), 10)
        self.assertEqual(list_jobs_response["totalCount"], 50)
        self.assertEqual(list_jobs_response["offset"], 10)
        self.assertEqual(list_jobs_response["limit"], 10)

    def test_list_jobs_empty_result(self):
        """Test listing jobs when no jobs exist"""
        # Mock service response with empty list
        mock_response = ListLabelApprovalJobsResponse(
            jobs=[],
            total_count=0,
            offset=0,
            limit=100,
            success=True,
            message="Found 0 jobs"
        )
        QueriesCommon._label_approval_jobs_service.list_label_approval_jobs.return_value = mock_response

        # GraphQL query
        query = """
            query ListJobs($input: ListLabelApprovalJobsInput!) {
                listLabelApprovalJobs(input: $input) {
                    jobs {
                        id
                    }
                    totalCount
                    success
                }
            }
        """

        variables = {
            "input": {
                "brandNameLike": "NonExistent",
                "status": None,
                "offset": 0,
                "limit": 100
            }
        }

        # Execute query
        response = self.post("/graphql", json={"query": query, "variables": variables})

        # Verify response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        list_jobs_response = data["data"]["listLabelApprovalJobs"]
        self.assertTrue(list_jobs_response["success"])
        self.assertEqual(len(list_jobs_response["jobs"]), 0)
        self.assertEqual(list_jobs_response["totalCount"], 0)

