# Label Approval Jobs - GraphQL Mutations

This document provides examples of how to use the Label Approval Jobs GraphQL mutations via curl commands.

## Prerequisites

- The API server must be running
- You need a valid authentication token with appropriate permissions
- Replace `<YOUR_AUTH_TOKEN>` with your actual authentication token
- Replace `<API_URL>` with your API endpoint (e.g., `http://localhost:8000/graphql`)

## Authentication

All mutations require authentication. Include your token in the Authorization header:

```bash
Authorization: Bearer <YOUR_AUTH_TOKEN>
```

Required permissions:
- `create_label_approval_job`: `TTB_LABEL_REVIEWS_CREATE`
- `set_label_approval_job_status`: `TTB_LABEL_REVIEWS_UPDATE`
- `add_review_comment`: `TTB_LABEL_REVIEWS_UPDATE`
- `list_jobs`: `TTB_LABEL_REVIEWS_LIST`

---

## 1. Create Label Approval Job

Creates a new label approval job with metadata including alcohol content, net contents, and label images.

### GraphQL Mutation

```graphql
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
    }
  }
}
```

### curl Command

```bash
curl -X POST http://localhost:8080/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <YOUR_AUTH_TOKEN>" \
  -d '{
    "query": "mutation CreateLabelApprovalJob($input: CreateLabelApprovalJobInput!) { createLabelApprovalJob(input: $input) { success message job { id brandName productClass status jobMetadata { reviewerId reviewerName reviewComments alcoholContent netContents bottlerInfo manufacturer warnings } createdAt updatedAt createdByEntity createdByEntityId } } }",
    "variables": {
      "input": {
        "brandName": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        "productClass": "beer",
        "status": "pending",
        "jobMetadata": {
          "alcoholContentPercentage": "5.2%",
          "netContentsInMilliLitres": "355",
          "bottlerInfo": "Acme Bottling Co.",
          "manufacturer": "Craft Brewery Inc.",
          "warnings": "Contains alcohol. Drink responsibly.",
          "labelImageBase64": "data:image/jpg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAH/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwA="
        }
      }
    }
  }'
```

### Example Response

```json
{
  "data": {
    "createLabelApprovalJob": {
      "success": true,
      "message": "Label approval job created successfully",
      "job": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "brandName": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        "productClass": "beer",
        "status": "pending",
        "jobMetadata": {
          "reviewerId": "reviewer_123",
          "reviewerName": "John Reviewer",
          "reviewComments": ["Review initiated"],
          "alcoholContent": "5.2%",
          "netContents": "355",
          "bottlerInfo": "Acme Bottling Co.",
          "manufacturer": "Craft Brewery Inc.",
          "warnings": "Contains alcohol. Drink responsibly."
        },
        "createdAt": "2025-12-04T10:30:00Z",
        "updatedAt": "2025-12-04T10:30:00Z",
        "createdByEntity": "user",
        "createdByEntityId": "user-456"
      }
    }
  }
}
```

---

## 2. Set Label Approval Job Status

Updates the status of an existing label approval job and optionally adds a review comment.

### GraphQL Mutation

```graphql
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
      updatedAt
    }
  }
}
```

### curl Command (with review comment)

```bash
curl -X POST http://localhost:8080/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <YOUR_AUTH_TOKEN>" \
  -d '{
    "query": "mutation SetLabelApprovalJobStatus($input: SetLabelApprovalJobStatusInput!) { setLabelApprovalJobStatus(input: $input) { success message job { id status jobMetadata { reviewComments } updatedAt } } }",
    "variables": {
      "input": {
        "jobId": "550e8400-e29b-41d4-a716-446655440000",
        "status": "approved",
        "reviewComment": "Label design approved. All requirements met."
      }
    }
  }'
```

### curl Command (without review comment)

```bash
curl -X POST http://localhost:8080/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <YOUR_AUTH_TOKEN>" \
  -d '{
    "query": "mutation SetLabelApprovalJobStatus($input: SetLabelApprovalJobStatusInput!) { setLabelApprovalJobStatus(input: $input) { success message job { id status updatedAt } } }",
    "variables": {
      "input": {
        "jobId": "550e8400-e29b-41d4-a716-446655440000",
        "status": "rejected"
      }
    }
  }'
```

### Example Response

```json
{
  "data": {
    "setLabelApprovalJobStatus": {
      "success": true,
      "message": "Label approval job status updated successfully",
      "job": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "status": "approved",
        "jobMetadata": {
          "reviewComments": [
            "Review initiated",
            "Label design approved. All requirements met."
          ]
        },
        "updatedAt": "2025-12-04T11:45:00Z"
      }
    }
  }
}
```

### Valid Status Values

- `pending` - Job is awaiting review
- `approved` - Job has been approved
- `rejected` - Job has been rejected

---

## 3. Add Review Comment

Adds a review comment to an existing label approval job without changing its status.

### GraphQL Mutation

```graphql
mutation AddReviewComment($input: AddReviewCommentInput!) {
  addReviewComment(input: $input) {
    success
    message
    job {
      id
      jobMetadata {
        reviewComments
      }
      updatedAt
    }
  }
}
```

### curl Command

```bash
curl -X POST http://localhost:8080/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <YOUR_AUTH_TOKEN>" \
  -d '{
    "query": "mutation AddReviewComment($input: AddReviewCommentInput!) { addReviewComment(input: $input) { success message job { id jobMetadata { reviewComments } updatedAt } } }",
    "variables": {
      "input": {
        "jobId": "550e8400-e29b-41d4-a716-446655440000",
        "reviewComment": "Please revise the alcohol content font size to meet TTB requirements."
      }
    }
  }'
```

### Example Response

```json
{
  "data": {
    "addReviewComment": {
      "success": true,
      "message": "Review comment added successfully",
      "job": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "jobMetadata": {
          "reviewComments": [
            "Review initiated",
            "Label design approved. All requirements met.",
            "Please revise the alcohol content font size to meet TTB requirements."
          ]
        },
        "updatedAt": "2025-12-04T14:20:00Z"
      }
    }
  }
}
```

---

## 4. List Label Approval Jobs

Retrieves a paginated list of label approval jobs with optional filtering by brand name and status.

### GraphQL Query

```graphql
query ListJobs($input: ListLabelApprovalJobsInput!) {
  labelApprovalJobsRelated {
    listJobs(input: $input) {
      jobs {
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
        }
        createdAt
        updatedAt
      }
      totalCount
      offset
      limit
      success
      message
    }
  }
}
```

### curl Command (list all jobs)

```bash
curl -X POST http://localhost:8080/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <YOUR_AUTH_TOKEN>" \
  -d '{
    "query": "query ListJobs($input: ListLabelApprovalJobsInput!) { labelApprovalJobsRelated { listJobs(input: $input) { jobs { id brandName productClass status createdAt } totalCount offset limit success message } } }",
    "variables": {
      "input": {
        "brandNameLike": null,
        "status": null,
        "offset": 0,
        "limit": 100
      }
    }
  }'
```

### curl Command (filter by brand name)

```bash
curl -X POST http://localhost:8080/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <YOUR_AUTH_TOKEN>" \
  -d '{
    "query": "query ListJobs($input: ListLabelApprovalJobsInput!) { labelApprovalJobsRelated { listJobs(input: $input) { jobs { id brandName status } totalCount success } } }",
    "variables": {
      "input": {
        "brandNameLike": "Bud",
        "status": null,
        "offset": 0,
        "limit": 100
      }
    }
  }'
```

### curl Command (filter by status with pagination)

```bash
curl -X POST http://localhost:8080/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <YOUR_AUTH_TOKEN>" \
  -d '{
    "query": "query ListJobs($input: ListLabelApprovalJobsInput!) { labelApprovalJobsRelated { listJobs(input: $input) { jobs { id brandName status createdAt } totalCount offset limit success } } }",
    "variables": {
      "input": {
        "brandNameLike": null,
        "status": "pending",
        "offset": 0,
        "limit": 10
      }
    }
  }'
```

### Example Response

```json
{
  "data": {
    "labelApprovalJobsRelated": {
      "listJobs": {
        "jobs": [
          {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "brandName": "Budweiser",
            "productClass": "beer",
            "status": "pending",
            "jobMetadata": {
              "reviewerId": "reviewer_123",
              "reviewerName": "John Reviewer",
              "reviewComments": ["Review initiated"],
              "alcoholContent": "5.2%",
              "netContents": "355"
            },
            "createdAt": "2025-12-04T10:30:00Z",
            "updatedAt": "2025-12-04T10:30:00Z"
          },
          {
            "id": "650e8400-e29b-41d4-a716-446655440001",
            "brandName": "Corona",
            "productClass": "beer",
            "status": "approved",
            "jobMetadata": {
              "reviewerId": "reviewer_456",
              "reviewerName": "Jane Reviewer",
              "reviewComments": ["Approved"],
              "alcoholContent": "4.6%",
              "netContents": "355"
            },
            "createdAt": "2025-12-03T14:20:00Z",
            "updatedAt": "2025-12-04T09:15:00Z"
          }
        ],
        "totalCount": 2,
        "offset": 0,
        "limit": 100,
        "success": true,
        "message": "Found 2 jobs"
      }
    }
  }
}
```

### Query Parameters

- **brandNameLike** (Optional[String]): Filter jobs by brand name using SQL LIKE pattern matching. For example, "Bud" will match "Budweiser", "Bud Light", etc.
- **status** (Optional[String]): Filter jobs by exact status match. Valid values: `pending`, `approved`, `rejected`
- **offset** (Integer, default=0): Number of records to skip for pagination
- **limit** (Integer, default=100): Maximum number of records to return

### Pagination Example

To retrieve the second page of 10 results:

```bash
curl -X POST http://localhost:8080/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <YOUR_AUTH_TOKEN>" \
  -d '{
    "query": "query ListJobs($input: ListLabelApprovalJobsInput!) { labelApprovalJobsRelated { listJobs(input: $input) { jobs { id brandName } totalCount offset limit success } } }",
    "variables": {
      "input": {
        "offset": 10,
        "limit": 10
      }
    }
  }'
```

---

## Error Responses

All mutations return consistent error responses:

### Job Not Found

```json
{
  "data": {
    "setLabelApprovalJobStatus": {
      "success": false,
      "message": "Label approval job with id 550e8400-e29b-41d4-a716-446655440000 not found",
      "job": null
    }
  }
}
```

### Authentication Error

```json
{
  "errors": [
    {
      "message": "Authentication required",
      "extensions": {
        "code": "UNAUTHENTICATED"
      }
    }
  ]
}
```

### Permission Denied

```json
{
  "errors": [
    {
      "message": "Insufficient permissions",
      "extensions": {
        "code": "FORBIDDEN",
        "requiredPermission": "TTB_LABEL_REVIEWS_UPDATE"
      }
    }
  ]
}
```

### Validation Error

```json
{
  "data": {
    "createLabelApprovalJob": {
      "success": false,
      "message": "Invalid alcohol content percentage. Alcohol content percentage must be between 0% and 100%",
      "job": null
    }
  }
}
```

---

## Tips for Testing

### Using jq for Pretty Output

Install `jq` and pipe the curl output for better readability:

```bash
curl -X POST http://localhost:8080/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <YOUR_AUTH_TOKEN>" \
  -d '{ ... }' | jq
```

### Testing Locally

If running the API locally on port 8000:

```bash
export API_URL="http://localhost:8000/graphql"
export AUTH_TOKEN="your-test-token-here"

curl -X POST $API_URL \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  -d '{ ... }'
```

### Validating UUIDs

Make sure to use valid UUIDs for:
- `brandName` (UUID format required)
- `jobId` (UUID format required)

You can generate UUIDs using:

```bash
# On macOS/Linux
uuidgen | tr '[:upper:]' '[:lower:]'

# Using Python
python3 -c "import uuid; print(uuid.uuid4())"
```

---

## Workflow Example

Here's a typical workflow using all three mutations:

```bash
# 1. Create a new label approval job
JOB_ID=$(curl -X POST $API_URL \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  -d '{
    "query": "mutation CreateLabelApprovalJob($input: CreateLabelApprovalJobInput!) { createLabelApprovalJob(input: $input) { job { id } } }",
    "variables": {
      "input": {
        "brandName": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        "productClass": "beer",
        "jobMetadata": {
          "alcoholContentPercentage": "5.2%",
          "netContentsInMilliLitres": "355",
          "labelImageBase64": "data:image/jpg;base64,..."
        }
      }
    }
  }' | jq -r '.data.createLabelApprovalJob.job.id')

# 2. Add a review comment
curl -X POST $API_URL \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  -d "{
    \"query\": \"mutation AddReviewComment(\$input: AddReviewCommentInput!) { addReviewComment(input: \$input) { success message } }\",
    \"variables\": {
      \"input\": {
        \"jobId\": \"$JOB_ID\",
        \"reviewComment\": \"Initial review complete. Minor adjustments needed.\"
      }
    }
  }"

# 3. Update status to approved
curl -X POST $API_URL \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  -d "{
    \"query\": \"mutation SetLabelApprovalJobStatus(\$input: SetLabelApprovalJobStatusInput!) { setLabelApprovalJobStatus(input: \$input) { success message } }\",
    \"variables\": {
      \"input\": {
        \"jobId\": \"$JOB_ID\",
        \"status\": \"approved\",
        \"reviewComment\": \"All requirements met. Approved for production.\"
      }
    }
  }"
```

---

## Additional Resources

- [GraphQL Documentation](https://graphql.org/learn/)
- [TTB Label Requirements](https://www.ttb.gov/)
- API Schema: Available via GraphQL introspection at `http://localhost:8080`

For more information or support, please contact the development team.