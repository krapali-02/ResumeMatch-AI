# Module 03: Job Management & Requirement Normalization Implementation Plan

> **Module ID:** `MOD-03`  
> **Component:** Job Requisition Lifecycle & Requirement Engineering  
> **Status:** Pending Implementation  
> **Traced Requirements:** FR-JOB-01 (Job Creation), FR-JOB-02 (JD Parsing), FR-JOB-03 (Edit Extracted), FR-JOB-04 (Required vs Preferred), FR-JOB-05 (Job Status), AC-01  

---

## 1. Module Overview & Purpose

Module 03 handles the end-to-end lifecycle of job postings (JDs). It allows recruiters to create jobs either by providing structured fields or by inputting raw, unstructured job descriptions. It interfaces with the AI microservice to automatically parse requirements, categorizes them into **Required** and **Preferred** criteria, enables recruiter manual editing before search, and manages status transitions (`draft`, `active`, `paused`, `closed`).

---

## 2. Technical Architecture & Workflow

```mermaid
flowchart LR
    Recruiter[Recruiter / Hiring Team] -->|1. Submit Raw Job Description| Express[Express Job Controller]
    Express -->|2. Forward Raw Text| FastAPI[FastAPI /ai/extract-requirements]
    FastAPI -->|3. Extract Entities & Classification| Extractor[spaCy Rule-Based Matcher]
    Extractor -->|4. Return Structured Requirements| FastAPI
    FastAPI -->|5. Structured Criteria| Express
    Express -->|6. Save Draft Job| Mongo[(MongoDB)]
    Express -->|7. Return Structured Form| UI[React Requirement Tag Editor]
    Recruiter -->|8. Review, Add/Remove Tags, Designate Required/Preferred| UI
    UI -->|9. PUT /api/jobs/:id (Final Confirm)| Express
    Express -->|10. Set Status: 'active' & Trigger Embedding| Vector[(ChromaDB)]
```

---

## 3. Data Structures & API Contracts

### 3.1 Job Requirement Contract
```typescript
interface IJobRequirements {
  requiredSkills: string[];        // Mandatory disqualifying criteria (e.g., ["Python", "FastAPI"])
  preferredSkills: string[];       // Value-add bonus criteria (e.g., ["Kubernetes", "AWS"])
  minExperienceYears: number;      // e.g., 3
  educationLevel: 'any' | 'high_school' | 'bachelor' | 'master' | 'doctorate';
  location: string;
  workMode: 'remote' | 'hybrid' | 'onsite';
}
```

### 3.2 Gateway Endpoints
- `POST /api/jobs`: Create job draft and trigger requirement extraction.
- `GET /api/jobs`: Query jobs by status, department, and pagination.
- `GET /api/jobs/:id`: Retrieve single job with its requirements and weights.
- `PUT /api/jobs/:id`: Update requirements, title, status, or scoring weights.
- `DELETE /api/jobs/:id`: Soft delete / archive job.

---

## 4. Step-by-Step Implementation Tasks

- [ ] **Task 3.1:** Implement Mongoose repository methods for Job CRUD in `backend/src/services/job.service.ts`.
- [ ] **Task 3.2:** Build FastAPI endpoint `POST /ai/extract-requirements` in `ai-service/app/api/jobs.py` to parse free text into structured skills, experience, and degree requirements.
- [ ] **Task 3.3:** Build `backend/src/controllers/job.controller.ts` with validation rules (Joi/Zod) for required fields.
- [ ] **Task 3.4:** Implement automatic status lifecycle guard: jobs cannot transition from `draft` to `active` without at least one required skill.
- [ ] **Task 3.5:** Connect job activation to embedding generation: when a job is marked `active`, the AI service creates and caches its vector representation in the vector store.
- [ ] **Task 3.6:** Build job search & filter API allowing recruiters to search their requisitions by title, status, and department.

---

## 5. Edge Cases & Safeguards

- **Vague or Overly Short Job Descriptions:** If a user submits a 1-sentence JD, extraction flags a warning: *"Job description too sparse for reliable matching. Please provide detailed responsibilities and skills."*
- **Conflicting Experience Requirements:** If JD states "0-5 years", minimum experience is normalized to 0, preventing accidental disqualification of entry-level candidates.
- **Duplicate Job Creation:** Detection heuristic checks existing active jobs by same recruiter with matching title within 24 hours.

---

## 6. Verification & Acceptance Checklist

- [ ] Recruiter can submit a free-text job description and receive auto-extracted skills, experience, and education (AC-01).
- [ ] Recruiter can edit, add, or delete skills and re-categorize between **Required** and **Preferred** (FR-JOB-03, FR-JOB-04).
- [ ] Changing job status to `closed` prevents new candidate matching runs against it (FR-JOB-05).
- [ ] Active job vector is correctly persisted in the vector database.
