import { Router } from "express";
import {
    create,
    list,
    getOne,
    remove
} from "../controllers/candidate.controller";
import {
    uploadResume,
    listResumes,
    getResume,
    getResumeText,
    deleteResume
} from "../controllers/resume.controller";
import { authenticate } from "../middlewares/auth.middleware";
import { validate } from "../middlewares/validate.middleware";
import { resumeUploadMiddleware } from "../middlewares/upload.middleware";
import {
    createCandidateSchema,
    candidateIdParamSchema,
    candidateResumeParamsSchema
} from "../validators/candidate.validator";
import { asyncHandler } from "../utils/asyncHandler";

const router = Router();

// Enforce authentication across all candidate & resume endpoints
router.use(authenticate);

// Candidate CRUD
router.post(
    "/",
    validate({ body: createCandidateSchema }),
    asyncHandler(create)
);

router.get(
    "/",
    asyncHandler(list)
);

router.get(
    "/:id",
    validate({ params: candidateIdParamSchema }),
    asyncHandler(getOne)
);

router.delete(
    "/:id",
    validate({ params: candidateIdParamSchema }),
    asyncHandler(remove)
);

// Resume Ingestion and Lifecycle
router.post(
    "/:id/resumes",
    validate({ params: candidateIdParamSchema }),
    resumeUploadMiddleware,
    asyncHandler(uploadResume)
);

router.get(
    "/:id/resumes",
    validate({ params: candidateIdParamSchema }),
    asyncHandler(listResumes)
);

router.get(
    "/:id/resumes/:resumeId",
    validate({ params: candidateResumeParamsSchema }),
    asyncHandler(getResume)
);

router.get(
    "/:id/resumes/:resumeId/text",
    validate({ params: candidateResumeParamsSchema }),
    asyncHandler(getResumeText)
);

router.delete(
    "/:id/resumes/:resumeId",
    validate({ params: candidateResumeParamsSchema }),
    asyncHandler(deleteResume)
);

export default router;
