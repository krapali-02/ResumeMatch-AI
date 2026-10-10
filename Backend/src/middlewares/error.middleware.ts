import { Request, Response, NextFunction } from "express";
import { ApiError } from "../utils/ApiError";

export const errorMiddleware = (
    error: unknown,
    _req: Request,
    res: Response,
    _next: NextFunction
): void => {
    // Log unexpected errors for server diagnostics
    if (!(error instanceof ApiError)) {
        console.error("Unhandled Server Error:", error);
    }

    if (error instanceof ApiError) {
        res.status(error.statusCode).json({
            success: false,
            message: error.message,
            ...(error.errors && error.errors.length > 0 ? { errors: error.errors } : {})
        });
        return;
    }

    // Handle Mongoose CastError (e.g., malformed ObjectId)
    if (
        typeof error === "object" &&
        error !== null &&
        "name" in error &&
        (error as { name: string }).name === "CastError"
    ) {
        res.status(400).json({
            success: false,
            message: "Invalid resource identifier format"
        });
        return;
    }

    // Handle Mongoose duplicate key error (code 11000)
    if (
        typeof error === "object" &&
        error !== null &&
        "code" in error &&
        (error as { code: number }).code === 11000
    ) {
        res.status(409).json({
            success: false,
            message: "A record with this unique field already exists"
        });
        return;
    }

    res.status(500).json({
        success: false,
        message: "Internal server error"
    });
};