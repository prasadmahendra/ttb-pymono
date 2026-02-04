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
│       └── ocr/                       # Tesseract OCR adapter (pytesseract analysis mode)
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
- `create_label_approval_job(input)` - Create a new label approval job (supports `analysis_mode` in job_metadata: `using_llm` or `pytesseract`)
- `set_label_approval_job_status(id, status)` - Update job status (pending/approved/rejected)
- `add_review_comment(job_id, comment)` - Add reviewer comments
- `analyze_label_approval_job(id, analysis_mode?)` - Trigger automated label analysis (optional `analysis_mode` override for ad-hoc runs)

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

Uses Tesseract OCR (pytesseract) for text extraction from images. This adapter is used when the `analysis_mode` is set to `pytesseract`.

**Methods:**
- `extract_text_from_url(image_url)` - OCR from image URL
- `extract_text_from_base64(base64_data)` - OCR from base64 encoded image

**Returns:**
- Extracted text with bounding boxes
- Confidence scores
- Word-level detail

**Note:** Requires Tesseract to be installed on the system (`brew install tesseract` on macOS)

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

Analyzes label images for regulatory compliance. Supports two analysis modes that can be configured per job.

**Analysis Checks (all case-insensitive except #5):**
1. **Brand Name Verification** - Case-insensitive match (e.g., "STONE'S THROW" matches "Stone's Throw")
2. **Product Class/Type** - Case-insensitive with fuzzy matching for related types (e.g., Beer/Lager Beer)
3. **Alcohol Content Format** - Case-insensitive, checks ABV percentage display
4. **Net Contents** - Case-insensitive, verifies volume information
5. **Government Health Warnings** - ONLY check requiring ALL CAPS ("GOVERNMENT WARNING" exact match)

**Analysis Modes:**

| Mode | Value | Description |
|------|-------|-------------|
| **LLM (Default)** | `using_llm` | Uses OpenAI GPT for intelligent, context-aware analysis |
| **Pytesseract** | `pytesseract` | Uses Tesseract OCR for fast, rule-based text verification |

**Setting Analysis Mode:**
- **At job creation:** Set `analysis_mode` in `job_metadata` - this value is persisted with the job
- **Ad-hoc analysis:** Pass `analysis_mode` to `analyze_label_approval_job` mutation - this overrides the stored mode but is NOT persisted

**Methods:**
- `analyze_label_data(job, analysis_mode_override)` - Comprehensive compliance check
- `answer_analysis_questions_with_llm()` - AI-powered analysis using OpenAI
- Delegates to `LabelDataAnalysisPytesseractService` for OCR-based analysis

### 3. LabelDataExtractionService

**File:** `label_data_extraction.py`

Extracts structured product information from label images. Supports both LLM and pytesseract extraction modes.

**Extracted Data:**
- Brand name
- Product class and type
- Alcohol content percentage
- Net contents (volume)
- Government warnings
- Additional metadata (bottler info, manufacturer)

**Extraction Methods by Mode:**

**LLM Mode (`using_llm`):**
- Uses OpenAI GPT with vision capabilities
- Intelligent context-aware extraction
- Handles complex label layouts

**Pytesseract Mode (`pytesseract`):**
- Uses Tesseract OCR for text extraction
- Pattern-based field detection using regex
- Faster but less context-aware

**Methods:**
- `extract_label_data(base64_image, analysis_mode)` - Extract and parse product information
- `_extract_label_data_with_llm()` - LLM-powered extraction
- `_extract_label_data_with_pytesseract()` - OCR-based extraction with pattern matching
- Validates extracted data with Pydantic models

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
Analyze Request (with optional analysis_mode override)
    ↓
LabelApprovalJobsService.analyze_label_approval_job()
    ↓
Determine analysis_mode (override > job stored mode > default)
    ↓
LabelDataExtractionService.extract_label_data()
    ├── [using_llm]    → LLMAdapter.complete_prompt_with_media() → OpenAI API
    └── [pytesseract]  → OCRAdapter.extract_text() → Tesseract OCR
    ↓
LabelDataAnalysisService.analyze_label_data()
    ├── [using_llm]    → LLMAdapter (GPT analysis)
    └── [pytesseract]  → Pattern matching & regex validation
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
- **LLM:** OpenAI API (GPT-4o, GPT-5) - used for `using_llm` analysis mode
- **OCR:** Tesseract via pytesseract - used for `pytesseract` analysis mode
- **Validation:** Pydantic
- **Server:** Gunicorn/Uvicorn with Uvloop
