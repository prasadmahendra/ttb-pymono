import unittest
import uuid
from sqlmodel import SQLModel
from sqlalchemy.orm import Session

from treasury.services.gateways.ttb_api.main.adapter.out.persistence.common.db_config import DbConfig
from treasury.services.gateways.ttb_api.main.adapter.out.persistence.label_approvals_persistence_adapter import \
    LabelApprovalJobsPersistenceAdapter
from treasury.services.gateways.ttb_api.main.application.models.domain.entity_descriptor import EntityDescriptor
from treasury.services.gateways.ttb_api.main.application.models.domain.label_approval_job import LabelApprovalJob, \
    JobMetadata, LabelApprovalStatus


class TestLabelApprovalJobsPersistenceAdapter(unittest.TestCase):
    test_org_id = uuid.uuid4()
    test_user_id = uuid.uuid4()

    orm_engine = DbConfig.get_orm_engine(in_memory=True, local_on_disk=False)
    SQLModel.metadata.create_all(bind=orm_engine)

    def setUp(self) -> None:
        self.adapter = LabelApprovalJobsPersistenceAdapter(orm_engine=self.orm_engine)
        # Clear all events from the database
        with Session(self.orm_engine) as session:
            session.query(LabelApprovalJob).delete()
            session.commit()

    def test_create_approval_job_with_id(self):
        """Test creating a new approval job with a provided ID"""
        job_id = uuid.uuid4()
        brand_name = str(uuid.uuid4())
        created_by = EntityDescriptor.of_user(id=str(self.test_user_id), org_id=self.test_org_id)

        metadata = JobMetadata(reviewer_id="test_reviewer")
        job = LabelApprovalJob(
            id=job_id,
            brand_name=brand_name,
            product_class="beer",
            status=LabelApprovalStatus.pending,
            job_metadata=metadata
        )

        result = self.adapter.create_approval_job(job=job, created_by=created_by)

        self.assertIsNotNone(result)
        self.assertEqual(result.id, job_id)
        self.assertEqual(result.brand_name, brand_name)
        self.assertEqual(result.product_class, "beer")
        self.assertEqual(result.status, LabelApprovalStatus.pending)
        metadata_obj = result.get_job_metadata()
        self.assertIsInstance(metadata_obj, JobMetadata)
        self.assertEqual(metadata_obj.reviewer_id, "test_reviewer")
        self.assertIsNotNone(result.created_at)
        self.assertIsNotNone(result.updated_at)
        self.assertEqual(result.created_at, result.updated_at)
        self.assertEqual(result.created_by_entity, "user")
        self.assertEqual(result.created_by_entity_id, str(self.test_user_id))
        self.assertEqual(result.created_by_entity_domain, str(self.test_org_id))
        self.assertEqual(result.updated_by_entity, "user")
        self.assertEqual(result.updated_by_entity_id, str(self.test_user_id))
        self.assertEqual(result.updated_by_entity_domain, str(self.test_org_id))

    def test_create_approval_job_without_id(self):
        """Test creating a new approval job without providing an ID (should auto-generate)"""
        brand_name = str(uuid.uuid4())
        created_by = EntityDescriptor.of_user(id=str(self.test_user_id), org_id=self.test_org_id)

        metadata = JobMetadata(reviewer_id="test_reviewer", reviewer_name="Test User")
        job = LabelApprovalJob(
            brand_name=brand_name,
            product_class="wine",
            status=LabelApprovalStatus.pending,
            job_metadata=metadata
        )

        result = self.adapter.create_approval_job(job=job, created_by=created_by)

        self.assertIsNotNone(result)
        self.assertIsNotNone(result.id)
        self.assertEqual(result.brand_name, brand_name)
        self.assertEqual(result.product_class, "wine")
        self.assertEqual(result.status, LabelApprovalStatus.pending)
        metadata_obj = result.get_job_metadata()
        self.assertIsInstance(metadata_obj, JobMetadata)
        self.assertEqual(metadata_obj.reviewer_id, "test_reviewer")
        self.assertEqual(metadata_obj.reviewer_name, "Test User")

    def test_create_approval_job_with_system_entity(self):
        """Test creating a new approval job with system entity descriptor"""
        brand_name = str(uuid.uuid4())
        created_by = EntityDescriptor.of_system()

        metadata = JobMetadata()
        job = LabelApprovalJob(
            brand_name=brand_name,
            product_class="spirits",
            status=LabelApprovalStatus.pending,
            job_metadata=metadata
        )

        result = self.adapter.create_approval_job(job=job, created_by=created_by)

        self.assertIsNotNone(result)
        self.assertEqual(result.created_by_entity, "system")
        self.assertEqual(result.created_by_entity_id, "system")
        self.assertEqual(result.created_by_entity_domain, "system")
        metadata_obj = result.get_job_metadata()
        self.assertIsInstance(metadata_obj, JobMetadata)

    def test_get_approval_job_by_id_exists(self):
        """Test retrieving an existing approval job by ID"""
        brand_name = str(uuid.uuid4())
        created_by = EntityDescriptor.of_user(id=str(self.test_user_id), org_id=self.test_org_id)

        metadata = JobMetadata(reviewer_id="test_reviewer", review_comments=["Initial comment"])
        job = LabelApprovalJob(
            brand_name=brand_name,
            product_class="beer",
            status=LabelApprovalStatus.pending,
            job_metadata=metadata
        )

        created_job = self.adapter.create_approval_job(job=job, created_by=created_by)
        self.assertIsNotNone(created_job)

        retrieved_job = self.adapter.get_approval_job_by_id(job_id=created_job.id)

        self.assertIsNotNone(retrieved_job)
        self.assertEqual(retrieved_job.id, created_job.id)
        self.assertEqual(retrieved_job.brand_name, brand_name)
        self.assertEqual(retrieved_job.product_class, "beer")
        self.assertEqual(retrieved_job.status, LabelApprovalStatus.pending)
        metadata_obj = retrieved_job.get_job_metadata()
        self.assertIsInstance(metadata_obj, JobMetadata)
        self.assertEqual(metadata_obj.reviewer_id, "test_reviewer")
        self.assertEqual(metadata_obj.review_comments, ["Initial comment"])

    def test_get_approval_job_by_id_not_exists(self):
        """Test retrieving a non-existent approval job by ID (should return None)"""
        non_existent_id = uuid.uuid4()

        result = self.adapter.get_approval_job_by_id(job_id=non_existent_id)

        self.assertIsNone(result)

    def test_create_multiple_approval_jobs(self):
        """Test creating multiple approval jobs and ensure they are distinct"""
        created_by = EntityDescriptor.of_user(id=str(self.test_user_id), org_id=self.test_org_id)

        metadata1 = JobMetadata()
        job1 = LabelApprovalJob(
            brand_name=str(uuid.uuid4()),
            product_class="beer",
            status=LabelApprovalStatus.pending,
            job_metadata=metadata1
        )

        metadata2 = JobMetadata()
        job2 = LabelApprovalJob(
            brand_name=str(uuid.uuid4()),
            product_class="wine",
            status=LabelApprovalStatus.approved,
            job_metadata=metadata2
        )

        result1 = self.adapter.create_approval_job(job=job1, created_by=created_by)
        result2 = self.adapter.create_approval_job(job=job2, created_by=created_by)

        self.assertIsNotNone(result1)
        self.assertIsNotNone(result2)
        self.assertNotEqual(result1.id, result2.id)
        self.assertEqual(result1.product_class, "beer")
        self.assertEqual(result2.product_class, "wine")
        self.assertEqual(result1.status, LabelApprovalStatus.pending)
        self.assertEqual(result2.status, LabelApprovalStatus.approved)
        metadata_obj1 = result1.get_job_metadata()
        metadata_obj2 = result2.get_job_metadata()
        self.assertIsInstance(metadata_obj1, JobMetadata)
        self.assertIsInstance(metadata_obj2, JobMetadata)

    def test_create_approval_job_with_different_entity_types(self):
        """Test creating approval jobs with different entity descriptor types"""
        brand_name = str(uuid.uuid4())

        # Test with organization entity
        org_entity = EntityDescriptor.of_organization(id=self.test_org_id)
        metadata1 = JobMetadata()
        job1 = LabelApprovalJob(
            brand_name=brand_name,
            product_class="spirits",
            status=LabelApprovalStatus.pending,
            job_metadata=metadata1
        )
        result1 = self.adapter.create_approval_job(job=job1, created_by=org_entity)
        self.assertEqual(result1.created_by_entity, "organization")
        metadata_obj1 = result1.get_job_metadata()
        self.assertIsInstance(metadata_obj1, JobMetadata)

        # Test with tools entity
        tools_entity = EntityDescriptor.of_tools(id="tool_123", org_id=self.test_org_id)
        metadata2 = JobMetadata()
        job2 = LabelApprovalJob(
            brand_name=brand_name,
            product_class="wine",
            status=LabelApprovalStatus.pending,
            job_metadata=metadata2
        )
        result2 = self.adapter.create_approval_job(job=job2, created_by=tools_entity)
        self.assertEqual(result2.created_by_entity, "tools")
        metadata_obj2 = result2.get_job_metadata()
        self.assertIsInstance(metadata_obj2, JobMetadata)

    def test_create_approval_job_preserves_metadata(self):
        """Test that job metadata is properly stored and retrieved"""
        brand_name = str(uuid.uuid4())
        created_by = EntityDescriptor.of_user(id=str(self.test_user_id), org_id=self.test_org_id)

        metadata = JobMetadata(
            reviewer_id="reviewer_123",
            reviewer_name="John Doe",
            review_comments=["Looks good", LabelApprovalStatus.approved]
        )

        job = LabelApprovalJob(
            brand_name=brand_name,
            product_class="spirits",
            status=LabelApprovalStatus.pending,
            job_metadata=metadata
        )

        result = self.adapter.create_approval_job(job=job, created_by=created_by)

        self.assertIsNotNone(result)
        metadata_obj = result.get_job_metadata()
        self.assertIsInstance(metadata_obj, JobMetadata)
        self.assertEqual(metadata_obj.reviewer_id, "reviewer_123")
        self.assertEqual(metadata_obj.reviewer_name, "John Doe")
        self.assertEqual(metadata_obj.review_comments, ["Looks good", LabelApprovalStatus.approved])

        # Verify by retrieving the job
        retrieved = self.adapter.get_approval_job_by_id(job_id=result.id)
        retrieved_metadata = retrieved.get_job_metadata()
        self.assertIsInstance(retrieved_metadata, JobMetadata)
        self.assertEqual(retrieved_metadata.reviewer_id, "reviewer_123")
        self.assertEqual(retrieved_metadata.reviewer_name, "John Doe")
        self.assertEqual(retrieved_metadata.review_comments, ["Looks good", LabelApprovalStatus.approved])

    def test_set_job_status_success(self):
        """Test updating job status successfully"""
        brand_name = str(uuid.uuid4())
        created_by = EntityDescriptor.of_user(id=str(self.test_user_id), org_id=self.test_org_id)

        # Create initial job
        metadata = JobMetadata()
        job = LabelApprovalJob(
            brand_name=brand_name,
            product_class="beer",
            status=LabelApprovalStatus.pending,
            job_metadata=metadata
        )

        created_job = self.adapter.create_approval_job(job=job, created_by=created_by)
        self.assertIsNotNone(created_job)
        self.assertEqual(created_job.status, LabelApprovalStatus.pending)

        # Update status
        updated_by = EntityDescriptor.of_user(id=str(uuid.uuid4()), org_id=self.test_org_id)
        updated_job = self.adapter.set_job_status(
            job_id=created_job.id,
            status=LabelApprovalStatus.approved,
            updated_by=updated_by
        )

        # Verify status was updated
        self.assertIsNotNone(updated_job)
        self.assertEqual(updated_job.status, LabelApprovalStatus.approved)
        self.assertEqual(updated_job.id, created_job.id)
        self.assertEqual(updated_job.brand_name, brand_name)

        # Verify updated_by fields were set correctly
        self.assertEqual(updated_job.updated_by_entity, "user")
        self.assertEqual(updated_job.updated_by_entity_id, updated_by.id)
        self.assertEqual(updated_job.updated_by_entity_domain, str(self.test_org_id))

        # Verify updated_at is different from created_at
        self.assertNotEqual(updated_job.updated_at, updated_job.created_at)

        # Verify created_by fields remain unchanged
        self.assertEqual(updated_job.created_by_entity, "user")
        self.assertEqual(updated_job.created_by_entity_id, str(self.test_user_id))

    def test_set_job_status_not_found(self):
        """Test updating status of non-existent job returns None"""
        non_existent_id = uuid.uuid4()
        updated_by = EntityDescriptor.of_user(id=str(self.test_user_id), org_id=self.test_org_id)

        result = self.adapter.set_job_status(
            job_id=non_existent_id,
            status=LabelApprovalStatus.approved,
            updated_by=updated_by
        )

        self.assertIsNone(result)

    def test_set_job_status_multiple_updates(self):
        """Test multiple status updates on same job"""
        brand_name = str(uuid.uuid4())
        created_by = EntityDescriptor.of_user(id=str(self.test_user_id), org_id=self.test_org_id)

        # Create initial job
        metadata = JobMetadata()
        job = LabelApprovalJob(
            brand_name=brand_name,
            product_class="wine",
            status=LabelApprovalStatus.pending,
            job_metadata=metadata
        )

        created_job = self.adapter.create_approval_job(job=job, created_by=created_by)
        self.assertEqual(created_job.status, LabelApprovalStatus.pending)

        # First update
        updated_by1 = EntityDescriptor.of_system()
        updated_job1 = self.adapter.set_job_status(
            job_id=created_job.id,
            status=LabelApprovalStatus.approved,
            updated_by=updated_by1
        )
        self.assertEqual(updated_job1.status, LabelApprovalStatus.approved)
        self.assertEqual(updated_job1.updated_by_entity, "system")

        # Second update
        updated_by2 = EntityDescriptor.of_user(id=str(uuid.uuid4()), org_id=self.test_org_id)
        updated_job2 = self.adapter.set_job_status(
            job_id=created_job.id,
            status=LabelApprovalStatus.rejected,
            updated_by=updated_by2
        )
        self.assertEqual(updated_job2.status, LabelApprovalStatus.rejected)
        self.assertEqual(updated_job2.updated_by_entity, "user")
        self.assertEqual(updated_job2.updated_by_entity_id, updated_by2.id)

    def test_set_job_metadata_success(self):
        """Test updating job metadata successfully"""
        brand_name = str(uuid.uuid4())
        created_by = EntityDescriptor.of_user(id=str(self.test_user_id), org_id=self.test_org_id)

        # Create initial job with basic metadata
        initial_metadata = JobMetadata(reviewer_id="initial_reviewer")
        job = LabelApprovalJob(
            brand_name=brand_name,
            product_class="spirits",
            status=LabelApprovalStatus.pending,
            job_metadata=initial_metadata
        )

        created_job = self.adapter.create_approval_job(job=job, created_by=created_by)
        self.assertIsNotNone(created_job)
        metadata_obj = created_job.get_job_metadata()
        self.assertEqual(metadata_obj.reviewer_id, "initial_reviewer")
        self.assertIsNone(metadata_obj.reviewer_name)

        # Update metadata
        updated_by = EntityDescriptor.of_user(id=str(uuid.uuid4()), org_id=self.test_org_id)
        new_metadata = JobMetadata(
            reviewer_id="new_reviewer",
            reviewer_name="Jane Smith",
            review_comments=["Updated comment"]
        )

        updated_job = self.adapter.set_job_metadata(
            job_id=created_job.id,
            job_metadata=new_metadata.model_dump(exclude_none=False),
            updated_by=updated_by
        )

        # Verify metadata was updated
        self.assertIsNotNone(updated_job)
        updated_metadata = updated_job.get_job_metadata()
        self.assertEqual(updated_metadata.reviewer_id, "new_reviewer")
        self.assertEqual(updated_metadata.reviewer_name, "Jane Smith")
        self.assertEqual(updated_metadata.review_comments, ["Updated comment"])

        # Verify updated_by fields were set correctly
        self.assertEqual(updated_job.updated_by_entity, "user")
        self.assertEqual(updated_job.updated_by_entity_id, updated_by.id)
        self.assertEqual(updated_job.updated_by_entity_domain, str(self.test_org_id))

        # Verify updated_at is different from created_at
        self.assertNotEqual(updated_job.updated_at, updated_job.created_at)

        # Verify other fields remain unchanged
        self.assertEqual(updated_job.status, LabelApprovalStatus.pending)
        self.assertEqual(updated_job.brand_name, brand_name)

    def test_set_job_metadata_not_found(self):
        """Test updating metadata of non-existent job returns None"""
        non_existent_id = uuid.uuid4()
        updated_by = EntityDescriptor.of_user(id=str(self.test_user_id), org_id=self.test_org_id)
        new_metadata = JobMetadata(reviewer_id="test")

        result = self.adapter.set_job_metadata(
            job_id=non_existent_id,
            job_metadata=new_metadata.model_dump(exclude_none=False),
            updated_by=updated_by
        )

        self.assertIsNone(result)

    def test_set_job_metadata_complete_replacement(self):
        """Test that metadata is completely replaced, not merged"""
        brand_name = str(uuid.uuid4())
        created_by = EntityDescriptor.of_user(id=str(self.test_user_id), org_id=self.test_org_id)

        # Create job with multiple metadata fields
        initial_metadata = JobMetadata(
            reviewer_id="reviewer_1",
            reviewer_name="John Doe",
            review_comments=["Initial comment", "Second comment"]
        )
        job = LabelApprovalJob(
            brand_name=brand_name,
            product_class="spirits",
            status=LabelApprovalStatus.pending,
            job_metadata=initial_metadata
        )

        created_job = self.adapter.create_approval_job(job=job, created_by=created_by)

        # Update with new metadata containing only some fields
        updated_by = EntityDescriptor.of_system()
        new_metadata = JobMetadata(
            reviewer_id="reviewer_2"
        )

        updated_job = self.adapter.set_job_metadata(
            job_id=created_job.id,
            job_metadata=new_metadata.model_dump(exclude_none=False),
            updated_by=updated_by
        )

        # Verify metadata was completely replaced
        updated_metadata = updated_job.get_job_metadata()
        self.assertEqual(updated_metadata.reviewer_id, "reviewer_2")
        self.assertIsNone(updated_metadata.reviewer_name)  # Should be None, not "John Doe"
        self.assertIsNone(updated_metadata.review_comments)  # Should be None, not ["Initial comment", "Second comment"]

    def test_list_approval_jobs_no_filters(self):
        """Test listing all approval jobs without filters"""
        created_by = EntityDescriptor.of_user(id=str(self.test_user_id), org_id=self.test_org_id)

        # Create multiple jobs
        metadata = JobMetadata()
        job1 = LabelApprovalJob(brand_name="Budweiser", product_class="beer", status=LabelApprovalStatus.pending, job_metadata=metadata)
        job2 = LabelApprovalJob(brand_name="Corona", product_class="beer", status=LabelApprovalStatus.approved, job_metadata=metadata)
        job3 = LabelApprovalJob(brand_name="Heineken", product_class="beer", status=LabelApprovalStatus.rejected, job_metadata=metadata)

        self.adapter.create_approval_job(job=job1, created_by=created_by)
        self.adapter.create_approval_job(job=job2, created_by=created_by)
        self.adapter.create_approval_job(job=job3, created_by=created_by)

        # List all jobs
        jobs, total_count = self.adapter.list_approval_jobs()

        self.assertEqual(len(jobs), 3)
        self.assertEqual(total_count, 3)

    def test_list_approval_jobs_with_brand_name_filter(self):
        """Test listing jobs with brand_name_like filter"""
        created_by = EntityDescriptor.of_user(id=str(self.test_user_id), org_id=self.test_org_id)

        # Create jobs with different brand names
        metadata = JobMetadata()
        job1 = LabelApprovalJob(brand_name="Budweiser", product_class="beer", status=LabelApprovalStatus.pending, job_metadata=metadata)
        job2 = LabelApprovalJob(brand_name="Bud Light", product_class="beer", status=LabelApprovalStatus.approved, job_metadata=metadata)
        job3 = LabelApprovalJob(brand_name="Corona", product_class="beer", status=LabelApprovalStatus.pending, job_metadata=metadata)

        self.adapter.create_approval_job(job=job1, created_by=created_by)
        self.adapter.create_approval_job(job=job2, created_by=created_by)
        self.adapter.create_approval_job(job=job3, created_by=created_by)

        # List jobs with brand name containing "Bud"
        jobs, total_count = self.adapter.list_approval_jobs(brand_name_like="Bud")

        self.assertEqual(len(jobs), 2)
        self.assertEqual(total_count, 2)
        brand_names = [job.brand_name for job in jobs]
        self.assertIn("Budweiser", brand_names)
        self.assertIn("Bud Light", brand_names)
        self.assertNotIn("Corona", brand_names)

    def test_list_approval_jobs_with_status_filter(self):
        """Test listing jobs with status filter"""
        created_by = EntityDescriptor.of_user(id=str(self.test_user_id), org_id=self.test_org_id)

        # Create jobs with different statuses
        metadata = JobMetadata()
        job1 = LabelApprovalJob(brand_name="Budweiser", product_class="beer", status=LabelApprovalStatus.pending, job_metadata=metadata)
        job2 = LabelApprovalJob(brand_name="Corona", product_class="beer", status=LabelApprovalStatus.approved, job_metadata=metadata)
        job3 = LabelApprovalJob(brand_name="Heineken", product_class="beer", status=LabelApprovalStatus.pending, job_metadata=metadata)

        self.adapter.create_approval_job(job=job1, created_by=created_by)
        self.adapter.create_approval_job(job=job2, created_by=created_by)
        self.adapter.create_approval_job(job=job3, created_by=created_by)

        # List only pending jobs
        jobs, total_count = self.adapter.list_approval_jobs(status=LabelApprovalStatus.pending)

        self.assertEqual(len(jobs), 2)
        self.assertEqual(total_count, 2)
        for job in jobs:
            self.assertEqual(job.status, LabelApprovalStatus.pending)

    def test_list_approval_jobs_with_both_filters(self):
        """Test listing jobs with both brand_name_like and status filters"""
        created_by = EntityDescriptor.of_user(id=str(self.test_user_id), org_id=self.test_org_id)

        # Create jobs with different combinations
        metadata = JobMetadata()
        job1 = LabelApprovalJob(brand_name="Budweiser", product_class="beer", status=LabelApprovalStatus.pending, job_metadata=metadata)
        job2 = LabelApprovalJob(brand_name="Bud Light", product_class="beer", status=LabelApprovalStatus.approved, job_metadata=metadata)
        job3 = LabelApprovalJob(brand_name="Corona", product_class="beer", status=LabelApprovalStatus.pending, job_metadata=metadata)
        job4 = LabelApprovalJob(brand_name="Bud Ice", product_class="beer", status=LabelApprovalStatus.pending, job_metadata=metadata)

        self.adapter.create_approval_job(job=job1, created_by=created_by)
        self.adapter.create_approval_job(job=job2, created_by=created_by)
        self.adapter.create_approval_job(job=job3, created_by=created_by)
        self.adapter.create_approval_job(job=job4, created_by=created_by)

        # List pending jobs with brand name containing "Bud"
        jobs, total_count = self.adapter.list_approval_jobs(brand_name_like="Bud", status=LabelApprovalStatus.pending)

        self.assertEqual(len(jobs), 2)
        self.assertEqual(total_count, 2)
        for job in jobs:
            self.assertEqual(job.status, LabelApprovalStatus.pending)
            self.assertIn("Bud", job.brand_name)

    def test_list_approval_jobs_with_pagination(self):
        """Test listing jobs with offset and limit pagination"""
        created_by = EntityDescriptor.of_user(id=str(self.test_user_id), org_id=self.test_org_id)

        # Create 5 jobs
        metadata = JobMetadata()
        for i in range(5):
            job = LabelApprovalJob(
                brand_name=f"Brand_{i}",
                product_class="beer",
                status=LabelApprovalStatus.pending,
                job_metadata=metadata
            )
            self.adapter.create_approval_job(job=job, created_by=created_by)

        # Get first 2 jobs
        jobs_page1, total_count = self.adapter.list_approval_jobs(offset=0, limit=2)
        self.assertEqual(len(jobs_page1), 2)
        self.assertEqual(total_count, 5)

        # Get next 2 jobs
        jobs_page2, total_count = self.adapter.list_approval_jobs(offset=2, limit=2)
        self.assertEqual(len(jobs_page2), 2)
        self.assertEqual(total_count, 5)

        # Get last job
        jobs_page3, total_count = self.adapter.list_approval_jobs(offset=4, limit=2)
        self.assertEqual(len(jobs_page3), 1)
        self.assertEqual(total_count, 5)

        # Verify no overlap between pages
        page1_ids = {job.id for job in jobs_page1}
        page2_ids = {job.id for job in jobs_page2}
        page3_ids = {job.id for job in jobs_page3}
        self.assertEqual(len(page1_ids & page2_ids), 0)
        self.assertEqual(len(page2_ids & page3_ids), 0)
        self.assertEqual(len(page1_ids & page3_ids), 0)

    def test_list_approval_jobs_empty_result(self):
        """Test listing jobs when no jobs match the filters"""
        created_by = EntityDescriptor.of_user(id=str(self.test_user_id), org_id=self.test_org_id)

        # Create jobs with specific characteristics
        metadata = JobMetadata()
        job = LabelApprovalJob(brand_name="Budweiser", product_class="beer", status=LabelApprovalStatus.pending, job_metadata=metadata)
        self.adapter.create_approval_job(job=job, created_by=created_by)

        # Search for non-existent brand
        jobs, total_count = self.adapter.list_approval_jobs(brand_name_like="NonExistent")

        self.assertEqual(len(jobs), 0)
        self.assertEqual(total_count, 0)

    def test_list_approval_jobs_no_jobs_exist(self):
        """Test listing jobs when no jobs exist in database"""
        jobs, total_count = self.adapter.list_approval_jobs()

        self.assertEqual(len(jobs), 0)
        self.assertEqual(total_count, 0)

    def test_list_approval_jobs_ordering(self):
        """Test that jobs are ordered by created_at descending"""
        created_by = EntityDescriptor.of_user(id=str(self.test_user_id), org_id=self.test_org_id)

        # Create jobs in sequence
        metadata = JobMetadata()
        job1 = LabelApprovalJob(brand_name="First", product_class="beer", status=LabelApprovalStatus.pending, job_metadata=metadata)
        job2 = LabelApprovalJob(brand_name="Second", product_class="beer", status=LabelApprovalStatus.pending, job_metadata=metadata)
        job3 = LabelApprovalJob(brand_name="Third", product_class="beer", status=LabelApprovalStatus.pending, job_metadata=metadata)

        created1 = self.adapter.create_approval_job(job=job1, created_by=created_by)
        created2 = self.adapter.create_approval_job(job=job2, created_by=created_by)
        created3 = self.adapter.create_approval_job(job=job3, created_by=created_by)

        # List all jobs
        jobs, total_count = self.adapter.list_approval_jobs()

        # Should be in reverse chronological order (newest first)
        self.assertEqual(jobs[0].id, created3.id)
        self.assertEqual(jobs[1].id, created2.id)
        self.assertEqual(jobs[2].id, created1.id)
