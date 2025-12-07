# ttb-pymono

A Treasury Label Approval Management API built with Clean Architecture principles.

## Table of Contents
- [Clean Architecture Overview](#clean-architecture-overview)
- [Folder Structure](#folder-structure)[README (1).md](../../../Downloads/README%20%281%29.md)
- [Adapters](#adapters)
- [Use Cases](#use-cases)
- [Data Flow](#data-flow)

## Clean Architecture Overview

This project follows the **Hexagonal/Ports-and-Adapters Clean Architecture** pattern, which provides:
- Clear separation of concerns between layers
- Independence from external frameworks and tools
- Testability and maintainability
- Flexibility to swap implementations

### Layer Organization

```
┌─────────────────────────────────────────────────────┐
│           Presentation Layer (Adapters)             │
│              GraphQL API Interface                  │
└────────────────┬────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────┐
│          Application Layer (Use Cases)              │
│         Business Logic & Orchestration              │
└────────────────┬────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────┐
│            Domain Layer (Entities)                  │
│         Core Business Models & Rules                │
└─────────────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────┐
│        Infrastructure Layer (Adapters)              │
│    Database, LLM, OCR External Services            │
└─────────────────────────────────────────────────────┘
```

## Folder Structure

```
treasury/services/gateways/ttb_api/main/
│
├── adapter/                           # External Interface Layer
│   ├── inp/                           # Input Adapters (Inbound Ports)
│   │   └── gql/                       # GraphQL Interface
│   │       ├── queries/               # GraphQL query resolvers
│   │       ├── mutations/             # GraphQL mutation resolvers
│   │       ├── query.py              # Query schema
│   │       ├── mutation.py           # Mutation schema
│   │       └── error_handler.py      # Error handling
│   │
│   └── out/                           # Output Adapters (Outbound Ports)
│       ├── persistence/               # Database adapter
│       ├── llm/                       # OpenAI LLM adapter
│       └── ocr/                       # Tesseract OCR adapter
│
├── application/                       # Application & Domain Layers
│   ├── usecases/                      # Use Cases (Business Logic)
│   │   ├── label_approval_jobs.py    # Main orchestration service
│   │   ├── label_data_analysis.py    # Analysis service
│   │   ├── label_data_extraction.py  # Extraction service
│   │   ├── user_management.py        # User service
│   │   └── security/                 # Security context
│   │
│   ├── models/                        # Data Models
│   │   ├── domain/                   # Domain Entities
│   │   ├── dto/                      # Data Transfer Objects
│   │   ├── gql/                      # GraphQL Models
│   │   └── mappers/                  # Object Mappers
│   │
│   ├── config/                        # Configuration
│   ├── exceptions/                    # Custom Exceptions
│   └── utils/                         # Utility Functions
│
└── tools/                             # Development Tools
```

## Adapters

Adapters serve as the bridge between the core application and external systems. They implement the Ports-and-Adapters pattern.

### Input Adapters (Inbound Ports)

**Location:** `adapter/inp/gql/`

Input adapters handle incoming requests from external clients.

#### GraphQL Adapter

Exposes the application through a GraphQL API.

**Query Operations** (`queries/label_approval_jobs_related.py`):
- `get_label_approval_job(id)` - Fetch a single label approval job
- `list_label_approval_jobs(filter, sort, pagination)` - List jobs with filtering and pagination
- `hello()` - Health check query

**Mutation Operations** (`mutations/label_approval_jobs_related.py`):
- `create_label_approval_job(input)` - Create a new label approval job
- `set_label_approval_job_status(id, status)` - Update job status (pending/approved/rejected)
- `add_review_comment(job_id, comment)` - Add reviewer comments
- `analyze_label_approval_job(id)` - Trigger automated label analysis

**Error Handling** (`error_handler.py`):
- Custom GraphQL error handling extension
- Maps application exceptions to GraphQL errors

### Output Adapters (Outbound Ports)

**Location:** `adapter/out/`

Output adapters interact with external services and infrastructure.

#### 1. Persistence Adapter

**File:** `persistence/label_approvals_persistence_adapter.py`

Handles database operations for label approval jobs.

**Methods:**
- `create_approval_job(job_data)` - Persist new job to database
- `get_approval_job_by_id(job_id)` - Retrieve job by ID
- `list_approval_jobs(filters, sort, pagination)` - Query jobs with filters
- `set_job_status(job_id, status, entity_descriptor)` - Update job status
- `set_job_metadata(job_id, metadata)` - Update job metadata

**Technology:** SQLAlchemy/SQLModel with PostgreSQL

#### 2. LLM Adapter

**File:** `llm/openai_adapter.py`

Integrates with OpenAI API for AI-powered label analysis and data extraction.

**Methods:**
- `complete_prompt(prompt, model)` - Generate text completions
- `complete_prompt_with_media(prompt, media_urls, model)` - Analyze images with AI

**Supported Models:**
- GPT-5-Mini (cost-effective)
- GPT-5.1 (advanced reasoning)
- GPT-4o (multimodal)

**Use Cases:**
- Extract product information from label images
- Analyze labels for regulatory compliance
- Verify brand names, alcohol content, health warnings

#### 3. OCR Adapter

**File:** `ocr/ocr_adapter.py`

Uses Tesseract OCR for text extraction from images.

**Methods:**
- `extract_text_from_url(image_url)` - OCR from image URL
- `extract_text_from_base64(base64_data)` - OCR from base64 encoded image

**Returns:**
- Extracted text with bounding boxes
- Confidence scores
- Word-level detail

## Use Cases

**Location:** `application/usecases/`

Use cases contain the core business logic and orchestrate operations across adapters.

### 1. LabelApprovalJobsService

**File:** `label_approval_jobs.py`

Main orchestration service for managing label approval workflows.

**Responsibilities:**
- Create label approval jobs
- Update job status (pending → approved/rejected)
- Manage review comments
- Orchestrate analysis workflow
- Coordinate between persistence, analysis, and user management

**Key Methods:**
- `create_label_approval_job()` - Initialize new approval job
- `set_label_approval_job_status()` - Update status with audit trail
- `add_review_comment()` - Add reviewer feedback
- `analyze_label_approval_job()` - Trigger automated analysis

**Dependencies:** Lazy-loaded adapters (Persistence, Analysis, User Management)

### 2. LabelDataAnalysisService

**File:** `label_data_analysis.py`

Analyzes label images for regulatory compliance.

**Analysis Checks:**
1. **Brand Name Verification** - Confirms brand name is visible
2. **Product Class/Type** - Validates product classification
3. **Alcohol Content Format** - Checks ABV percentage display
4. **Net Contents** - Verifies volume information
5. **Government Health Warnings** - Confirms required warnings

**Analysis Modes:**
- **LLM Mode:** Uses OpenAI GPT for intelligent analysis
- **OCR Mode:** Uses Tesseract for text-based verification (Implementation pending)

**Methods:**
- `analyze_label_data()` - Comprehensive compliance check
- `_analyze_with_llm()` - AI-powered analysis
- `_analyze_with_ocr()` - OCR-based analysis (Implementation pending)

### 3. LabelDataExtractionService

**File:** `label_data_extraction.py`

Extracts structured product information from label images using LLM.

**Extracted Data:**
- Brand name
- Product class and type
- Alcohol content percentage
- Net contents (volume)
- Additional metadata

**Methods:**
- `extract_label_data()` - Extract and parse product information
- Validates extracted data with Pydantic models
- Handles JSON parsing and markdown code blocks

### 4. UserManagementService

**File:** `user_management.py`

Manages user authentication and authorization.

**Methods:**
- `get_user_by_entity_descriptor()` - Retrieve authenticated user
- User session management

**Note:** Currently uses hardcoded test user; designed for integration with auth service

### 5. Security Service

**File:** `security/security_context.py`

Manages request security and authentication context.

**Responsibilities:**
- Extract security context from HTTP requests
- Bearer token verification
- Entity descriptor management (tracks who made changes)
- Request metadata capture (IP, user-agent)

**Methods:**
- `create_security_context()` - Initialize security context for request
- Header extraction and validation

## Data Flow

### Typical Request Flow

```
1. GraphQL Request
   ↓
2. Input Adapter (Query/Mutation Resolver)
   ├── Extract request parameters
   ├── Create security context
   └── Validate input
   ↓
3. Use Case Service
   ├── Execute business logic
   ├── Validate business rules
   └── Coordinate operations
   ↓
4. Domain Models
   ├── Apply domain rules
   └── Maintain consistency
   ↓
5. Output Adapters
   ├── Persistence Adapter → PostgreSQL
   ├── LLM Adapter → OpenAI
   └── OCR Adapter → Tesseract
   ↓
6. Response DTO
   ├── Map domain objects
   └── Format response
   ↓
7. GraphQL Response
```

### Example: Create Label Approval Job

```
Client Request (GraphQL Mutation)
    ↓
GraphQL Mutation Resolver (inp/gql/mutations/)
    ↓
LabelApprovalJobsService.create_label_approval_job()
    ↓
LabelApprovalJob Domain Entity (validation)
    ↓
PersistenceAdapter.create_approval_job()
    ↓
PostgreSQL Database
    ↓
LabelApprovalJob DTO
    ↓
GraphQL Response
```

### Example: Analyze Label

```
Analyze Request
    ↓
LabelApprovalJobsService.analyze_label_approval_job()
    ↓
LabelDataAnalysisService.analyze_label_data()
    ├──→ LLMAdapter.complete_prompt_with_media()
    │    └──→ OpenAI API
    │
    └──→ OCRAdapter.extract_text_from_url()
         └──→ Tesseract OCR
    ↓
Analysis Results (compliance checks)
    ↓
PersistenceAdapter.set_job_metadata()
    ↓
Updated Job with Analysis
```

## Key Design Principles

1. **Dependency Inversion** - Core logic doesn't depend on external frameworks
2. **Single Responsibility** - Each adapter handles one external system
3. **Lazy Dependency Injection** - Services instantiate dependencies on demand
4. **Entity Descriptors** - Audit trail tracking who made changes
5. **DTO Pattern** - Separate domain models from API models
6. **Security Context** - Request-scoped security information
7. **Error Boundaries** - Custom error handlers at framework level
[README (1).md](../../../Downloads/README%20%281%29.md)
## Technology Stack

- **API Framework:** FastAPI/Starlette with GraphQL (Strawberry)
- **Database:** PostgreSQL with SQLAlchemy/SQLModel ORM
- **LLM:** OpenAI API (GPT-4o, GPT-5)
- **OCR:** Tesseract
- **Validation:** Pydantic
- **Server:** Gunicorn/Uvicorn with Uvloop
