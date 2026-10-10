import { Router } from "express";
import { create, list, getOne } from "../controllers/job.controller";
import { authenticate } from "../middlewares/auth.middleware";
import { validate } from "../middlewares/validate.middleware";
import { createJobSchema, jobIdParamSchema } from "../validators/job.validator";
import { asyncHandler } from "../utils/asyncHandler";

const router = Router();

// All job management routes require authentication
router.use(authenticate);

router.post(
    "/",
    validate({ body: createJobSchema }),
    asyncHandler(create)
);

router.get(
    "/",
    asyncHandler(list)
);

router.get(
    "/:id",
    validate({ params: jobIdParamSchema }),
    asyncHandler(getOne)
);

export default router;