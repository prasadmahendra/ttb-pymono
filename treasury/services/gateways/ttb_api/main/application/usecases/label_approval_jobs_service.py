from typing import Optional

from strawberry.types import Info

from treasury.services.gateways.ttb_api.main.adapter.out.persistence.label_approvals_persistence_adapter import \
    LabelApprovalJobsPersistenceAdapter
from treasury.services.gateways.ttb_api.main.application.config.config import GlobalConfig
from treasury.services.gateways.ttb_api.main.application.models.domain.iam_role_permissions import IamRolePermissions
from treasury.services.gateways.ttb_api.main.application.models.domain.label_approval_job import LabelApprovalJob, \
    JobMetadata, LabelImage
from treasury.services.gateways.ttb_api.main.application.models.domain.user import User
from treasury.services.gateways.ttb_api.main.application.models.dto.label_approval_job_dto import LabelApprovalJobDTO, \
    JobMetadataDTO
from treasury.services.gateways.ttb_api.main.application.models.gql.label_approvals.create_label_approval_job_request import (
    CreateLabelApprovalJobInput,
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
from treasury.services.gateways.ttb_api.main.application.models.mappers.object_mapper import ObjectMapper
from treasury.services.gateways.ttb_api.main.application.usecases.security.security_context import SecurityContext
from treasury.services.gateways.ttb_api.main.application.usecases.user_management_service import UserManagementService


class LabelApprovalJobsService:
    def __init__(
            self,
            label_approval_jobs_persistence_adapter: LabelApprovalJobsPersistenceAdapter = None,
            user_management_service: UserManagementService = None
    ) -> None:
        self._logger = GlobalConfig.get_logger(__name__)
        self._label_approval_jobs_persistence_adapter_lazy = label_approval_jobs_persistence_adapter
        self._user_management_service_lazy = user_management_service

    @classmethod
    def get_singleton_instance_of(cls) -> 'LabelApprovalJobsService':
        return LabelApprovalJobsService()

    @property
    def _user_management_service(self) -> UserManagementService:
        # Lazy initialization of the user management service
        if self._user_management_service_lazy is None:
            self._user_management_service_lazy = UserManagementService()
        return self._user_management_service_lazy

    @property
    def _label_approval_jobs_persistence_adapter(self) -> LabelApprovalJobsPersistenceAdapter:
        # Lazy initialization of the persistence adapter
        if self._label_approval_jobs_persistence_adapter_lazy is None:
            self._label_approval_jobs_persistence_adapter_lazy = LabelApprovalJobsPersistenceAdapter()
        return self._label_approval_jobs_persistence_adapter_lazy

    def create_label_approval_job(
            self,
            info: Info,
            input: CreateLabelApprovalJobInput
    ) -> CreateLabelApprovalJobResponse:
        security_context = SecurityContext.from_info(info)

        @security_context.role_permissions_required(
            permissions=[IamRolePermissions.TTB_LABEL_REVIEWS_CREATE]
        )
        def role_restricted_call() -> CreateLabelApprovalJobResponse:
            return self._create_label_approval_job(
                info=info,
                input=input
            )

        return role_restricted_call()

    def _create_label_approval_job(
            self,
            info: Info,
            input: CreateLabelApprovalJobInput
    ) -> CreateLabelApprovalJobResponse:
        """Create a new label approval job"""
        try:
            security_context = SecurityContext.from_info(info)
            authenticated_entity = security_context.get_authenticated_entity_from_security_ctx()
            authenticated_user: Optional[User] = self._user_management_service.get_user_by_authenticated_entity(
                entity=authenticated_entity
            )
            if authenticated_user is None:
                # This should not happen as the security context check passed!
                return CreateLabelApprovalJobResponse(
                    job=None,
                    success=False,
                    message="Authenticated user not found"
                )

            # Validate input metadata - alcohol content percentage
            try:
                self._verify_alcohol_content_percentage_or_raise(input.job_metadata.alcohol_content_percentage)
            except ValueError as ve:
                return CreateLabelApprovalJobResponse(
                    job=None,
                    success=False,
                    message="Invalid alcohol content percentage. " + str(ve)
                )

            # Validate input metadata - net contents in milli litres
            try:
                self._verify_net_contents_in_milli_litres_or_raise(input.job_metadata.net_contents_in_milli_litres)
            except ValueError as ve:
                return CreateLabelApprovalJobResponse(
                    job=None,
                    success=False,
                    message="Invalid net contents in milli litres: " + str(ve)
                )

            # Validate input metadata - one image required (jpg, png or gif)
            try:
                self._verify_label_image_or_raise(input.job_metadata.label_image_base64, permitted_types=["jpg", "png", "gif"])
            except ValueError as ve:
                return CreateLabelApprovalJobResponse(
                    job=None,
                    success=False,
                    message="Invalid net contents in milli litres: " + str(ve)
                )

            # Convert input metadata to JobMetadata domain model
            job_metadata = JobMetadata()
            if input.job_metadata:
                job_metadata = JobMetadata(
                    reviewer_id=str(authenticated_user.id),
                    reviewer_name=authenticated_user.name,
                    review_comments=["Review initiated"],
                    alcohol_content_percentage=input.job_metadata.alcohol_content_percentage,
                    net_contents_in_milli_litres=input.job_metadata.net_contents_in_milli_litres,
                    bottler_info=input.job_metadata.bottler_info,
                    manufacturer=input.job_metadata.manufacturer,
                    warnings=input.job_metadata.warnings,
                    label_images=self._create_label_images_list_from_base64(input.job_metadata.label_image_base64)
                )

            # Create the job domain object
            job = LabelApprovalJob(
                brand_name=input.brand_name,
                product_class=input.product_class,
                status=input.status or "pending",
                job_metadata=job_metadata
            )

            # Persist the job
            created_job = self._label_approval_jobs_persistence_adapter.create_approval_job(
                job=job,
                created_by=authenticated_entity
            )

            if created_job is None:
                return CreateLabelApprovalJobResponse(
                    job=None,
                    success=False,
                    message="Failed to create label approval job"
                )

            # Convert to DTO
            # job_metadata_dto: JobMetadataDTO = ObjectMapper.map(created_job.get_job_metadata(), JobMetadataDTO)
            job_dto: LabelApprovalJobDTO = ObjectMapper.map(created_job, LabelApprovalJobDTO)

            return CreateLabelApprovalJobResponse(
                job=job_dto,
                success=True,
                message="Label approval job created successfully"
            )

        except Exception as e:
            self._logger.error(f"Error creating label approval job: {str(e)}")
            return CreateLabelApprovalJobResponse(
                job=None,
                success=False,
                message=f"Error creating label approval job: {str(e)}"
            )

    @classmethod
    def _verify_net_contents_in_milli_litres_or_raise(cls, net_contents_in_milli_litres: Optional[str]) -> None:
        """Verify that the net contents in milli litres is a valid positive number string"""
        if net_contents_in_milli_litres is None:
            return
        try:
            value = float(net_contents_in_milli_litres)
        except ValueError:
            raise ValueError("Net contents in milli litres must be a valid number")

        if value < 0:
            raise ValueError("Net contents in milli litres must be a positive number")

    @classmethod
    def _verify_alcohol_content_percentage_or_raise(cls, alcohol_content_percentage: Optional[str]) -> None:
        """Verify that the alcohol content percentage is a valid percentage string (e.g., '5%', '12.5%')"""
        if alcohol_content_percentage is None:
            return
        if alcohol_content_percentage.endswith('%'):
            alcohol_content_percentage = alcohol_content_percentage.replace('%', '')

        try:
            value = float(alcohol_content_percentage)
        except ValueError:
            raise ValueError("Alcohol content percentage must be a valid number followed by '%'")

        if value < 0 or value > 100:
            raise ValueError("Alcohol content percentage must be between 0% and 100%")

    @classmethod
    def _verify_label_image_or_raise(cls, label_image_base64: str, permitted_types: list[str]) -> None:
        """Verify that the label image is provided and is of a permitted type (e.g., jpg, png, gif)"""
        if not label_image_base64:
            raise ValueError("Label image is required")

        # Simple check for permitted types in base64 string
        if not any(label_image_base64.startswith(f"data:image/{img_type};base64,") for img_type in permitted_types):
            raise ValueError(f"Label image must be one of the following types: {', '.join(permitted_types)}")

    @classmethod
    def _create_label_images_list_from_base64(cls, label_image_base64: str) -> list[LabelImage]:
        """Create a list of label images from the base64 string"""
        if not label_image_base64:
            return []

        image_content_type = None
        if label_image_base64.startswith("data:image/jpg;base64,"):
            image_content_type = "image/jpg"
        elif label_image_base64.startswith("data:image/png;base64,"):
            image_content_type = "image/png"
        elif label_image_base64.startswith("data:image/gif;base64,"):
            image_content_type = "image/gif"

        # In a real-world scenario, we would handle multiple images and their metadata
        return [LabelImage(
            image_url=None,
            image_content_type=image_content_type,
            base64=label_image_base64,
            upload_date=None,
            approved=None,
            approved_date=None,
            rejected=None,
            rejected_date=None
        )]

    def set_label_approval_job_status(
            self,
            info: Info,
            input: SetLabelApprovalJobStatusInput
    ) -> SetLabelApprovalJobStatusResponse:
        """Set the status of a label approval job"""
        security_context = SecurityContext.from_info(info)

        @security_context.role_permissions_required(
            permissions=[IamRolePermissions.TTB_LABEL_REVIEWS_UPDATE]
        )
        def role_restricted_call() -> SetLabelApprovalJobStatusResponse:
            return self._set_label_approval_job_status(
                info=info,
                input=input
            )

        return role_restricted_call()

    def _set_label_approval_job_status(
            self,
            info: Info,
            input: SetLabelApprovalJobStatusInput
    ) -> SetLabelApprovalJobStatusResponse:
        """Internal method to set the status of a label approval job"""
        try:
            security_context = SecurityContext.from_info(info)
            authenticated_entity = security_context.get_authenticated_entity_from_security_ctx()
            authenticated_user: Optional[User] = self._user_management_service.get_user_by_authenticated_entity(
                entity=authenticated_entity
            )
            if authenticated_user is None:
                return SetLabelApprovalJobStatusResponse(
                    job=None,
                    success=False,
                    message="Authenticated user not found"
                )

            # Fetch the existing job
            existing_job = self._label_approval_jobs_persistence_adapter.get_approval_job_by_id(
                event_id=input.job_id
            )

            if existing_job is None:
                return SetLabelApprovalJobStatusResponse(
                    job=None,
                    success=False,
                    message=f"Label approval job with id {input.job_id} not found"
                )

            # Get existing metadata and add review comment if provided
            job_metadata = existing_job.get_job_metadata()
            if input.review_comment:
                review_comments = job_metadata.review_comments or []
                review_comments.append(input.review_comment)
                job_metadata.review_comments = review_comments

            # Update the job status
            updated_job = self._label_approval_jobs_persistence_adapter.set_job_status(
                job_id=input.job_id,
                status=input.status,
                updated_by=authenticated_entity
            )

            # Update metadata with the new review comment
            if input.review_comment:
                updated_job = self._label_approval_jobs_persistence_adapter.set_job_metadata(
                    job_id=input.job_id,
                    job_metadata=job_metadata.model_dump(exclude_none=False),
                    updated_by=authenticated_entity
                )

            if updated_job is None:
                return SetLabelApprovalJobStatusResponse(
                    job=None,
                    success=False,
                    message="Failed to update label approval job status"
                )

            # Convert to DTO
            job_dto: LabelApprovalJobDTO = ObjectMapper.map(updated_job, LabelApprovalJobDTO)

            return SetLabelApprovalJobStatusResponse(
                job=job_dto,
                success=True,
                message="Label approval job status updated successfully"
            )

        except Exception as e:
            self._logger.error(f"Error setting label approval job status: {str(e)}")
            return SetLabelApprovalJobStatusResponse(
                job=None,
                success=False,
                message=f"Error setting label approval job status: {str(e)}"
            )

    def add_review_comment(
            self,
            info: Info,
            input: AddReviewCommentInput
    ) -> AddReviewCommentResponse:
        """Add a review comment to a label approval job"""
        security_context = SecurityContext.from_info(info)

        @security_context.role_permissions_required(
            permissions=[IamRolePermissions.TTB_LABEL_REVIEWS_UPDATE]
        )
        def role_restricted_call() -> AddReviewCommentResponse:
            return self._add_review_comment(
                info=info,
                input=input
            )

        return role_restricted_call()

    def _add_review_comment(
            self,
            info: Info,
            input: AddReviewCommentInput
    ) -> AddReviewCommentResponse:
        """Internal method to add a review comment to a label approval job"""
        try:
            security_context = SecurityContext.from_info(info)
            authenticated_entity = security_context.get_authenticated_entity_from_security_ctx()
            authenticated_user: Optional[User] = self._user_management_service.get_user_by_authenticated_entity(
                entity=authenticated_entity
            )
            if authenticated_user is None:
                return AddReviewCommentResponse(
                    job=None,
                    success=False,
                    message="Authenticated user not found"
                )

            # Fetch the existing job
            existing_job = self._label_approval_jobs_persistence_adapter.get_approval_job_by_id(
                event_id=input.job_id
            )

            if existing_job is None:
                return AddReviewCommentResponse(
                    job=None,
                    success=False,
                    message=f"Label approval job with id {input.job_id} not found"
                )

            # Get existing metadata and add review comment
            job_metadata = existing_job.get_job_metadata()
            review_comments = job_metadata.review_comments or []
            review_comments.append(input.review_comment)
            job_metadata.review_comments = review_comments

            # Update metadata with the new review comment
            updated_job = self._label_approval_jobs_persistence_adapter.set_job_metadata(
                job_id=input.job_id,
                job_metadata=job_metadata.model_dump(exclude_none=False),
                updated_by=authenticated_entity
            )

            if updated_job is None:
                return AddReviewCommentResponse(
                    job=None,
                    success=False,
                    message="Failed to add review comment"
                )

            # Convert to DTO
            job_dto: LabelApprovalJobDTO = ObjectMapper.map(updated_job, LabelApprovalJobDTO)

            return AddReviewCommentResponse(
                job=job_dto,
                success=True,
                message="Review comment added successfully"
            )

        except Exception as e:
            self._logger.error(f"Error adding review comment: {str(e)}")
            return AddReviewCommentResponse(
                job=None,
                success=False,
                message=f"Error adding review comment: {str(e)}"
            )

    def list_label_approval_jobs(
            self,
            info: Info,
            input: ListLabelApprovalJobsInput
    ) -> ListLabelApprovalJobsResponse:
        """List label approval jobs with optional filters and pagination"""
        security_context = SecurityContext.from_info(info)

        @security_context.role_permissions_required(
            permissions=[IamRolePermissions.TTB_LABEL_REVIEWS_LIST]
        )
        def role_restricted_call() -> ListLabelApprovalJobsResponse:
            return self._list_label_approval_jobs(
                info=info,
                input=input
            )

        return role_restricted_call()

    def _list_label_approval_jobs(
            self,
            info: Info,
            input: ListLabelApprovalJobsInput
    ) -> ListLabelApprovalJobsResponse:
        """Internal method to list label approval jobs with optional filters and pagination"""
        try:
            # Call persistence layer to get jobs
            jobs, total_count = self._label_approval_jobs_persistence_adapter.list_approval_jobs(
                brand_name_like=input.brand_name_like,
                status=input.status,
                offset=input.offset,
                limit=input.limit
            )

            # Convert to DTOs
            job_dtos: list[LabelApprovalJobDTO] = [
                ObjectMapper.map(job, LabelApprovalJobDTO) for job in jobs
            ]

            return ListLabelApprovalJobsResponse(
                jobs=job_dtos,
                total_count=total_count,
                offset=input.offset,
                limit=input.limit,
                success=True,
                message=f"Found {len(job_dtos)} jobs"
            )

        except Exception as e:
            self._logger.error(f"Error listing label approval jobs: {str(e)}")
            return ListLabelApprovalJobsResponse(
                jobs=[],
                total_count=0,
                offset=input.offset,
                limit=input.limit,
                success=False,
                message=f"Error listing label approval jobs: {str(e)}"
            )
