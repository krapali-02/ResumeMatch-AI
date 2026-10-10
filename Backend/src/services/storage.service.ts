import fs from "fs";
import path from "path";
import crypto from "crypto";
import { env } from "../config/env";
import { ApiError } from "../utils/ApiError";

const getUploadDirectory = (): string => {
    const uploadPath = path.resolve(process.cwd(), env.uploadDir);
    if (!fs.existsSync(uploadPath)) {
        fs.mkdirSync(uploadPath, { recursive: true });
    }
    return uploadPath;
};

export const generateSafeStorageKey = (originalName: string): string => {
    const rawExt = path.extname(originalName).toLowerCase();
    const safeExt = rawExt === ".docx" ? ".docx" : ".pdf";
    const timestamp = Date.now();
    const randomSuffix = crypto.randomBytes(8).toString("hex");

    return `resume_${timestamp}_${randomSuffix}${safeExt}`;
};

export const saveFileToStorage = async (
    buffer: Buffer,
    storageKey: string
): Promise<{ absolutePath: string; relativePath: string }> => {
    const uploadDir = getUploadDirectory();
    const sanitizedKey = path.basename(storageKey);

    const targetPath = path.resolve(uploadDir, sanitizedKey);

    // Verify path stays strictly inside upload directory
    if (!targetPath.startsWith(uploadDir)) {
        throw new ApiError(400, "Invalid storage destination path");
    }

    await fs.promises.writeFile(targetPath, buffer, {
        mode: 0o600 // Read/write by owner only
    });

    return {
        absolutePath: targetPath,
        relativePath: `${env.uploadDir}/${sanitizedKey}`
    };
};

export const getStoredFilePath = (storageKey: string): string => {
    const uploadDir = getUploadDirectory();
    const sanitizedKey = path.basename(storageKey);
    const targetPath = path.resolve(uploadDir, sanitizedKey);

    if (!targetPath.startsWith(uploadDir) || !fs.existsSync(targetPath)) {
        throw new ApiError(404, "Stored resume file not found on disk");
    }

    return targetPath;
};

export const deleteStoredFile = async (storageKey: string): Promise<boolean> => {
    try {
        const uploadDir = getUploadDirectory();
        const sanitizedKey = path.basename(storageKey);
        const targetPath = path.resolve(uploadDir, sanitizedKey);

        if (!targetPath.startsWith(uploadDir)) {
            return false;
        }

        if (fs.existsSync(targetPath)) {
            await fs.promises.unlink(targetPath);
            return true;
        }
        return false;
    } catch (err) {
        console.error(`Failed to delete stored file ${storageKey}:`, err);
        return false;
    }
};
