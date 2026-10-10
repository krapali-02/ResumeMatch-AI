import { Request, Response, NextFunction } from "express";
import { ZodType, ZodError } from "zod";
import { ApiError } from "../utils/ApiError";

export interface RequestValidationSchemas {
    body?: ZodType;
    params?: ZodType;
    query?: ZodType;
}

export const validate = (schemas: RequestValidationSchemas) => {
    return async (
        req: Request,
        _res: Response,
        next: NextFunction
    ): Promise<void> => {
        try {
            if (schemas.body) {
                req.body = await schemas.body.parseAsync(req.body);
            }
            if (schemas.params) {
                req.params = (await schemas.params.parseAsync(req.params)) as any;
            }
            if (schemas.query) {
                req.query = (await schemas.query.parseAsync(req.query)) as any;
            }
            next();
        } catch (error) {
            if (error instanceof ZodError) {
                const firstMessage =
                    error.issues[0]?.message || "Request validation failed";
                const errorList = error.issues.map((issue) => ({
                    field: issue.path.join("."),
                    message: issue.message
                }));
                return next(new ApiError(400, firstMessage, errorList));
            }
            next(error);
        }
    };
};
