import strawberry
from strawberry.types import Info

from treasury.services.gateways.ttb_api.main.adapter.inp.gql.mutations.common import MutationsCommon
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
from treasury.services.gateways.ttb_api.main.application.models.gql.label_approvals.analyze_label_approval_job_input import (
    AnalyzeLabelApprovalJobInput,
    AnalyzeLabelApprovalJobResponse
)


@strawberry.type
class LabelApprovalJobsRelated(MutationsCommon):

    @strawberry.mutation  # type: ignore
    def create_label_approval_job(self, input: CreateLabelApprovalJobInput, info: Info) -> CreateLabelApprovalJobResponse:
        """Create a new label approval job"""
        return MutationsCommon._label_approval_jobs_service.create_label_approval_job(
            info=info,
            input=input
        )

    @strawberry.mutation  # type: ignore
    def set_label_approval_job_status(self, input: SetLabelApprovalJobStatusInput, info: Info) -> SetLabelApprovalJobStatusResponse:
        """Set the status of a label approval job"""
        return MutationsCommon._label_approval_jobs_service.set_label_approval_job_status(
            info=info,
            input=input
        )

    @strawberry.mutation  # type: ignore
    def add_review_comment(self, input: AddReviewCommentInput, info: Info) -> AddReviewCommentResponse:
        """Add a review comment to a label approval job"""
        return MutationsCommon._label_approval_jobs_service.add_review_comment(
            info=info,
            input=input
        )

    @strawberry.mutation  # type: ignore
    def analyze_label_approval_job(self, input: AnalyzeLabelApprovalJobInput, info: Info) -> AnalyzeLabelApprovalJobResponse:
        """Analyze label images for a label approval job"""
        return MutationsCommon._label_approval_jobs_service.analyze_label_approval_job(
            info=info,
            input=input
        )