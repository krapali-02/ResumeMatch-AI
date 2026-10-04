# Module 08: Backend API Gateway & Orchestration Layer Implementation Plan

> **Module ID:** `MOD-08`  
> **Component:** Application Gateway, REST API & Service Orchestrator  
> **Status:** Pending Implementation  
> **Traced Requirements:** SRS §7 (API Requirements), §7.1 (API Behavior), FR-CAN-02 (Secure Storage), FR-MATCH-01, FR-EVID-04 to 06  

---

## 1. Module Overview & Purpose

Module 08 is the central coordination hub of the platform. Implemented in **Node.js with Express and TypeScript**, it handles all client-facing REST APIs, validates request payloads, enforces security policies, coordinates uploads with AWS S3 / MinIO, issues short-lived presigned URLs for secure resume previews, and orchestrates calls between the database, queues, and the AI microservice.

---

## 2. API Architecture & Routing Layout

```
backend/src/
├── routes/
│   ├── auth.routes.ts          # /api/auth (login, me, refresh)
│   ├── job.routes.ts           # /api/jobs (CRUD, parse-requirements, activate)
│   ├── candidate.routes.ts     # /api/candidates (CRUD, upload, presigned-url)
│   ├── match.routes.ts         # /api/jobs/:id/match, /api/matches/:id/evidence
│   └── audit.routes.ts         # /api/audit (admin access to audit trail)
├── controllers/
│   ├── auth.controller.ts
│   ├── job.controller.ts
│   ├── candidate.controller.ts
│   ├── match.controller.ts
│   └── audit.controller.ts
├── middleware/
│   ├── auth.ts                 # JWT verification
│   ├── rbac.ts                 # Role enforcement
│   ├── upload.ts               # Multer memory storage & magic byte validation
│   ├── validator.ts            # Zod schema validation
│   └── errorHandler.ts         # Centralized error handler & status mapper
└── services/
    ├── s3.service.ts           # AWS S3 upload & presigned URL generator
    ├── aiClient.service.ts     # Axios client communicating with FastAPI
    └── audit.service.ts        # Async audit logger
```

---

## 3. Key Endpoint Specifications

| Endpoint | Method | Role | Request Payload | Response Contract |
| :--- | :--- | :--- | :--- | :--- |
| `/api/jobs/:id/match` | `POST` | Recruiter | `{ minScore?: number, filters?: object }` | `{ jobId, matchCount, status: "completed" }` |
| `/api/jobs/:id/matches`| `GET` | Recruiter | Query: `?page=1&limit=20&sortBy=overallScore` | `{ candidates: RankedCandidate[], total: number }` |
| `/api/matches/:id/evidence` | `GET` | Recruiter | None | Granular evidence, matched/missing skills, snippets |
| `/api/candidates/:id/resumes` | `POST` | Recruiter | `multipart/form-data` (`file`) | `{ candidateId, resumeId, status: "queued" }` |
| `/api/candidates/:id/resume-url`| `GET` | Recruiter | None | `{ downloadUrl: string, expiresInSeconds: 900 }` |
| `/api/candidates/:id/status` | `PATCH` | Recruiter | `{ status: "shortlisted", note?: string }` | `{ candidateId, status, updatedAt }` |

---

## 4. Step-by-Step Implementation Tasks

- [ ] **Task 8.1:** Initialize Express app with Helmet, CORS, and compression middleware.
- [ ] **Task 8.2:** Implement Zod request validator middleware for strict type and payload validation.
- [ ] **Task 8.3:** Implement `upload.ts` using Multer with memory storage, 10MB file limit, and MIME/magic-byte checks (EC-03).
- [ ] **Task 8.4:** Build `s3.service.ts` for uploading resumes to AWS S3/MinIO with private ACLs and issuing 15-minute presigned URLs (FR-CAN-02, FR-EVID-04).
- [ ] **Task 8.5:** Implement `aiClient.service.ts` with Axios retry and timeout configurations (10s default).
- [ ] **Task 8.6:** Build `match.controller.ts` orchestrating vector search, candidate fetching, and score calculation.
- [ ] **Task 8.7:** Implement centralized error handler mapping domain errors to standard HTTP status codes (`400`, `401`, `403`, `404`, `500`).

---

## 5. Security & Error Handling

- **S3 Object Security:** No public S3 access is permitted. All resume previews must use temporary presigned URLs.
- **Consistent Error Schemas:** All error responses return:
  ```json
  {
    "success": false,
    "error": {
      "code": "VALIDATION_ERROR",
      "message": "Required skill list cannot be empty.",
      "timestamp": "2026-10-04T18:50:00Z"
    }
  }
  ```

---

## 6. Verification & Acceptance Checklist

- [ ] Unauthenticated requests are rejected with 401 Unauthorized (AC-09).
- [ ] File uploads reject unauthorized file extensions and corrupt binaries (EC-02, EC-03).
- [ ] Presigned URLs allow authorized preview of candidate resumes in browser (FR-EVID-04).
- [ ] End-to-end match orchestration returns ranked results and saves audit records.
