import { Router } from "express";
import { register, login, getMe } from "../controllers/auth.controller";
import { authenticate } from "../middlewares/auth.middleware";
import { validate } from "../middlewares/validate.middleware";
import { registerSchema, loginSchema } from "../validators/auth.validator";
import { asyncHandler } from "../utils/asyncHandler";

const router = Router();

router.post(
    "/register",
    validate({ body: registerSchema }),
    asyncHandler(register)
);

router.post(
    "/login",
    validate({ body: loginSchema }),
    asyncHandler(login)
);

router.get(
    "/me",
    authenticate,
    asyncHandler(getMe)
);

export default router;