# Module 01: Database & Data Models Implementation Plan

> **Module ID:** `MOD-01`  
> **Component:** Data Persistence & ODM Layer  
> **Status:** Pending Implementation  
> **Traced Requirements:** SRS §6 (Data Requirements), §6.1 (Core Entities), §6.2 (Data Quality), §6.3 (Retention)  

---

## 1. Module Overview & Purpose

Module 01 defines and implements the persistence tier for ResumeMatch AI using **MongoDB** with **Mongoose ODM**. It provides type-safe schemas, indexes for high-throughput queries, soft-deletion handling, audit immutability, and data retention hooks.

---

## 2. Entity Specifications & Mongoose Schemas

### 2.1 User Schema (`backend/src/models/User.ts`)
- **Fields:**
  - `userId`: `String` (Indexed, UUID v4 or NanoID with prefix `usr_`)
  - `name`: `String` (Required, trimmed, min 2 chars)
  - `email`: `String` (Required, unique, lowercase, trimmed, indexed)
  - `passwordHash`: `String` (Required, bcrypt/argon2 hash)
  - `role`: `String` (Enum: `recruiter`, `admin`, default: `recruiter`)
  - `status`: `String` (Enum: `active`, `suspended`, default: `active`)
  - `organizationId`: `String` (Indexed for future multi-tenancy)
  - `timestamps`: `createdAt`, `updatedAt`

### 2.2 Job Schema (`backend/src/models/Job.ts`)
- **Fields:**
  - `jobId`: `String` (Unique, indexed, prefix `job_`)
  - `title`: `String` (Required, indexed for text search)
  - `department`: `String` (Required)
  - `description`: `String` (Required, raw JD text)
  - `requirements`:
    - `requiredSkills`: `[String]` (Canonical lowercase strings, indexed)
    - `preferredSkills`: `[String]`
    - `minExperienceYears`: `Number` (Default: 0)
    - `educationLevel`: `String` (Enum: `any`, `high_school`, `bachelor`, `master`, `doctorate`)
    - `location`: `String`
    - `workMode`: `String` (Enum: `remote`, `hybrid`, `onsite`)
  - `weightConfig`:
    - `w_sem`: `Number` (Default: 0.35)
    - `w_skill`: `Number` (Default: 0.40)
    - `w_exp`: `Number` (Default: 0.15)
    - `w_edu`: `Number` (Default: 0.10)
  - `status`: `String` (Enum: `draft`, `active`, `paused`, `closed`, default: `draft`, indexed)
  - `vectorId`: `String` (Reference to Chroma/Qdrant collection point)
  - `createdBy`: `String` (Foreign key to `User.userId`)

### 2.3 Candidate Schema (`backend/src/models/Candidate.ts`)
- **Fields:**
  - `candidateId`: `String` (Unique, indexed, prefix `cand_`)
  - `profileMetadata`:
    - `fullName`: `String` (Required)
    - `email`: `String` (Indexed)
    - `phone`: `String`
    - `location`: `String`
    - `currentTitle`: `String`
    - `totalExperienceYears`: `Number`
  - `resumeReferences`: `[{ resumeId, version, s3Key, originalFileName, fileType, fileHash, uploadedAt, isActive }]`
  - `extractedProfile`:
    - `skills`: `[String]` (Canonicalized)
    - `rawSkillsDetected`: `[String]`
    - `experience`: `[{ company, title, startDate, endDate, descriptionText, technologiesUsed: [String] }]`
    - `education`: `[{ institution, degree, fieldOfStudy, graduationYear }]`
    - `certifications`: `[String]`
    - `projects`: `[{ name, description, technologies: [String] }]`
  - `parseStatus`: `String` (Enum: `pending`, `processing`, `completed`, `failed`, `low_confidence`, indexed)
  - `parseErrorDetails`: `String`
  - `recruiterStatus`: `String` (Enum: `new`, `reviewed`, `shortlisted`, `hold`, `rejected`, default: `new`, indexed)
  - `recruiterNotes`: `[{ noteId, authorId, text, createdAt }]`

### 2.4 Match Result Schema (`backend/src/models/Match.ts`)
- **Fields:**
  - `matchId`: `String` (Unique, indexed, prefix `match_`)
  - `jobId`: `String` (Indexed compound with candidateId)
  - `candidateId`: `String` (Indexed)
  - `overallScore`: `Number` (Indexed descending, 0 to 100)
  - `componentScores`:
    - `semanticScore`: `Number`
    - `skillScore`: `Number`
    - `experienceScore`: `Number`
    - `educationScore`: `Number`
  - `evidence`:
    - `matchedRequiredSkills`: `[String]`
    - `matchedPreferredSkills`: `[String]`
    - `missingRequiredSkills`: `[String]`
    - `supportingSnippets`: `[{ skillOrCriterion, evidenceSnippet, sourceSection }]`
  - `modelVersion`: `String` (Required for reproducibility)
  - `calculatedAt`: `Date` (TTL index option for retention)

### 2.5 Audit Log Schema (`backend/src/models/AuditLog.ts`)
- **Fields:**
  - `eventId`: `String` (Unique, indexed)
  - `actorId`: `String` (Indexed)
  - `actorRole`: `String`
  - `action`: `String` (Indexed)
  - `resourceType`: `String`
  - `resourceId`: `String`
  - `metadata`: `Schema.Types.Mixed`
  - `ipAddress`: `String`
  - `userAgent`: `String`
  - `timestamp`: `Date` (Indexed)

---

## 3. Step-by-Step Implementation Tasks

- [ ] **Task 1.1:** Setup Mongoose connection utility in `backend/src/config/db.ts` with connection pooling, reconnect policies, and health checks.
- [ ] **Task 1.2:** Implement `User` model with pre-save password hashing and credential verification helper methods.
- [ ] **Task 1.3:** Implement `Job` model with compound indexes on `(status, createdAt)` and text search index on `title`.
- [ ] **Task 1.4:** Implement `Candidate` model with subdocuments for resumes and extracted profile; configure compound index on `('profileMetadata.email', 'resumeReferences.fileHash')` for duplicate detection.
- [ ] **Task 1.5:** Implement `Match` model with compound index on `(jobId, overallScore: -1)`.
- [ ] **Task 1.6:** Implement `AuditLog` model with immutable write restrictions (disallow `update` and `delete`).
- [ ] **Task 1.7:** Create database seed script (`backend/src/scripts/seed.ts`) generating default admin, recruiter, sample job requisitions, and demo candidates.

---

## 4. Edge Cases & Data Quality Safeguards

- **EC-06 (Duplicate Candidates/Resumes):** Unique hash index on `resumeReferences.fileHash` detects identical files uploaded across different candidates.
- **EC-08 (Missing Information):** Schemas default missing values to `undefined` or `"not_specified"`, preventing default false positives.
- **Soft Deletion & Retention:** Configurable TTL index on temporary matches and support for GDPR/retention soft-delete flags.

---

## 5. Verification & Acceptance Checklist

- [ ] Connection connects successfully to local MongoDB and handles retry gracefully on failure.
- [ ] All schema validation rules enforce correct types, rejecting malformed documents.
- [ ] Unique constraints on user email and candidate IDs are enforced.
- [ ] Seeding script populates realistic recruitment data without errors.
