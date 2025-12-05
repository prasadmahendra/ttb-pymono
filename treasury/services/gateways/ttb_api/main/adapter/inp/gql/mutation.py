import strawberry

from treasury.services.gateways.ttb_api.main.adapter.inp.gql.mutations.label_approval_jobs_related import LabelApprovalJobsRelated


@strawberry.type
class Mutation(
    LabelApprovalJobsRelated
):
    pass
