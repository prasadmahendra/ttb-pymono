from enum import Enum


class IamRolePermissions(str, Enum):
    TTB_LABEL_REVIEWS_LIST = "ttb_label_reviews_list"
    TTB_LABEL_REVIEWS_GET = "ttb_label_reviews_get"
    TTB_LABEL_REVIEWS_CREATE = "ttb_label_reviews_create"
    TTB_LABEL_REVIEWS_UPDATE = "ttb_label_reviews_update"
    TTB_LABEL_REVIEWS_DELETE = "ttb_label_reviews_delete"
    TTB_REPORTS_LIST = "ttb_reports_list"
    TTB_REPORTS_GET = "ttb_reports_get"
    TTB_REPORTS_CREATE = "ttb_reports_create"
    TTB_REPORTS_UPDATE = "ttb_reports_update"
    TTB_REPORTS_DELETE = "ttb_reports_delete"