import multer from "multer";
import path from "path";
import { Request, Response, NextFunction } from "express";
import { env } from "../config/env";
import { ApiError } from "../utils/ApiError";

const storage = multer.memoryStorage();

const ALLOWED_EXTENSIONS = [".pdf", ".docx"];

const ALLOWED_MIME_TYPES = [
    "application/pdf",
    "application/x-pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/msword",
    "application/octet-stream"
];

const fileFilter = (
    _req: Request,
    file: Express.Multer.File,
    cb: multer.FileFilterCallback
) => {
    const ext = path.extname(file.originalname).toLowerCase();

    if (!ALLOWED_EXTENSIONS.includes(ext)) {
        return cb(
            new ApiError(
                400,
                `Unsupported file extension '${ext}'. Only PDF (.pdf) and DOCX (.docx) files are supported.`
            )
        );
    }

    if (!ALLOWED_MIME_TYPES.includes(file.mimetype)) {
        return cb(
            new ApiError(
                400,
                `Unsupported MIME type '${file.mimetype}'. Only PDF and DOCX documents are accepted.`
            )
        );
    }

    cb(null, true);
};

const maxSizeBytes = env.maxUploadSizeMb * 1024 * 1024;

const upload = multer({
    storage,
    limits: {
        fileSize: maxSizeBytes,
        files: 1
    },
    fileFilter
});

export const resumeUploadMiddleware = (
    req: Request,
    res: Response,
    next: NextFunction
) => {
    const singleUpload = upload.single("resume");

    singleUpload(req, res, (err: unknown) => {
        if (!err) {
            if (!req.file) {
                return next(new ApiError(400, "Resume file is required under field name 'resume'."));
            }
            return next();
        }

        if (err instanceof multer.MulterError) {
            if (err.code === "LIMIT_FILE_SIZE") {
                return next(
                    new ApiError(
                        413,
                        `Uploaded file exceeds maximum limit of ${env.maxUploadSizeMb}MB.`
                    )
                );
            }
            if (err.code === "LIMIT_UNEXPECTED_FILE") {
                return next(
                    new ApiError(
                        400,
                        "Unexpected multipart field. Please upload the file using field name 'resume'."
                    )
                );
            }
            return next(new ApiError(400, `Upload error: ${err.message}`));
        }

        next(err);
    });
};
