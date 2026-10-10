import { Request, Response, NextFunction } from "express";
import { ApiError } from "../utils/ApiError";

export const notFoundMiddleware = (
    _req: Request,
    _res: Response,
    next: NextFunction
): void => {
    next(new ApiError(404, "Route not found"));
};