import uuid
from typing import Optional

from treasury.services.gateways.ttb_api.main.adapter.out.persistence.common.db_config import DbConfig
from treasury.services.gateways.ttb_api.main.adapter.out.persistence.common.persistence_adapter_base import \
    PersistenceAdapterBase
from sqlalchemy import and_, or_, delete, func, String
from sqlalchemy.orm.session import Session

from treasury.services.gateways.ttb_api.main.application.models.domain.entity_descriptor import EntityDescriptor
from treasury.services.gateways.ttb_api.main.application.models.domain.label_approval_job import LabelApprovalJob, JobMetadata
from treasury.services.gateways.ttb_api.main.application.utils.datetime_utils import DateTimeUtils


class LabelApprovalJobsPersistenceAdapter(PersistenceAdapterBase):

    def create_approval_job(
            self,
            job: LabelApprovalJob,
            created_by: EntityDescriptor
    ) -> Optional[LabelApprovalJob]:
        """Create a new job"""
        with Session(self._orm_engine, expire_on_commit=False, autocommit=False) as session:
            created_at = DateTimeUtils.get_utc_now()

            new_job = job.model_copy()
            self._validate_for_creation(new_job=new_job)

            if new_job.id is None:
                new_job.id = uuid.uuid4()

            new_job.created_at = created_at
            new_job.updated_at = created_at

            new_job.created_by_entity = created_by.type
            new_job.created_by_entity_id = created_by.id
            new_job.created_by_entity_domain = created_by.org_id

            new_job.updated_by_entity = created_by.type
            new_job.updated_by_entity_id = created_by.id
            new_job.updated_by_entity_domain = created_by.org_id

            session.execute(DbConfig.insert_if_not_exists(new_job))
            session.commit()

        return self.get_approval_job_by_id(
            job_id=new_job.id
        )

    def get_approval_job_by_id(
            self,
            job_id: uuid.UUID
    ) -> Optional[LabelApprovalJob]:
        """Get an event by job_id"""
        with Session(self._orm_engine, expire_on_commit=False, autocommit=False) as session:
            result = session.query(LabelApprovalJob).filter(
                LabelApprovalJob.id == job_id  # type: ignore
            ).first()
            return self._ensure_job_metadata_deserialized(result)

    def set_job_status(
            self,
            job_id: uuid.UUID,
            status: str,
            updated_by: EntityDescriptor
    ) -> Optional[LabelApprovalJob]:
        """Update the status of an approval job"""
        with Session(self._orm_engine, expire_on_commit=False, autocommit=False) as session:
            job = session.query(LabelApprovalJob).filter(
                LabelApprovalJob.id == job_id  # type: ignore
            ).first()

            if job is None:
                return None

            updated_at = DateTimeUtils.get_utc_now()

            job.status = status
            job.updated_at = updated_at
            job.updated_by_entity = updated_by.type
            job.updated_by_entity_id = updated_by.id
            job.updated_by_entity_domain = updated_by.org_id

            session.commit()

        return self.get_approval_job_by_id(job_id=job_id)

    def set_job_metadata(
            self,
            job_id: uuid.UUID,
            job_metadata: dict,
            updated_by: EntityDescriptor
    ) -> Optional[LabelApprovalJob]:
        """Update the metadata of an approval job"""
        with Session(self._orm_engine, expire_on_commit=False, autocommit=False) as session:
            job = session.query(LabelApprovalJob).filter(
                LabelApprovalJob.id == job_id  # type: ignore
            ).first()

            if job is None:
                return None

            updated_at = DateTimeUtils.get_utc_now()

            job.job_metadata = job_metadata
            job.updated_at = updated_at
            job.updated_by_entity = updated_by.type
            job.updated_by_entity_id = updated_by.id
            job.updated_by_entity_domain = updated_by.org_id

            session.commit()

        return self.get_approval_job_by_id(job_id=job_id)

    def list_approval_jobs(
            self,
            brand_name_like: Optional[str] = None,
            status: Optional[str] = None,
            offset: int = 0,
            limit: int = 100
    ) -> tuple[list[LabelApprovalJob], int]:
        """
        List approval jobs with optional filters and pagination

        Args:
            brand_name_like: Optional filter for brand name (SQL LIKE pattern)
            status: Optional filter for job status
            offset: Number of records to skip (for pagination)
            limit: Maximum number of records to return

        Returns:
            Tuple of (list of jobs, total count)
        """
        with Session(self._orm_engine, expire_on_commit=False, autocommit=False) as session:
            # Build query with filters
            query = session.query(LabelApprovalJob)

            # Apply brand_name_like filter
            if brand_name_like:
                # Convert UUID to string for LIKE comparison
                query = query.filter(
                    LabelApprovalJob.brand_name.ilike(f"%{brand_name_like}%")
                )

            # Apply status filter
            if status:
                query = query.filter(LabelApprovalJob.status == status)

            # Get total count before pagination
            total_count = query.count()

            # Apply pagination and ordering
            query = query.order_by(LabelApprovalJob.created_at.desc())
            query = query.offset(offset).limit(limit)

            # Execute query
            jobs = query.all()

            # Ensure job_metadata is deserialized
            jobs = self._ensure_jobs_metadata_deserialized(jobs)

            return jobs, total_count

    @classmethod
    def _ensure_job_metadata_deserialized(cls, job: Optional[LabelApprovalJob]) -> Optional[LabelApprovalJob]:
        """Ensure job_metadata is a JobMetadata object, not a dict.

        SQLAlchemy loads the JSON column as a dict, so we need to convert it to JobMetadata.
        """
        if job is not None and isinstance(job.job_metadata, dict):
            job.job_metadata = JobMetadata(**job.job_metadata)
        return job

    @classmethod
    def _ensure_jobs_metadata_deserialized(cls, jobs: list[LabelApprovalJob]) -> list[LabelApprovalJob]:
        """Ensure job_metadata is a JobMetadata object for all jobs in the list."""
        for job in jobs:
            if isinstance(job.job_metadata, dict):
                job.job_metadata = JobMetadata(**job.job_metadata)
        return jobs

    @classmethod
    def _validate_for_creation(cls, new_job: LabelApprovalJob) -> None:
        """Validate the job before creation"""
        # TODO - Add any necessary validation logic here
        pass
