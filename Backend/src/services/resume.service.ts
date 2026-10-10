import mongoose from "mongoose";
import { Resume, IResume } from "../models/Resume";
import { getCandidateById } from "./candidate.service";
import { validateFileSignature } from "../utils/fileSignature";
import { extractResumeText } from "./textExtraction.service";
import {
    generateSafeStorageKey,
    saveFileToStorage,
    deleteStoredFile
} from "./storage.service";
import { ApiError } from "../utils/ApiError";

export interface ResumeMetadataResponse {
    id: string;
    candidateId: string;
    originalFileName: string;
    mimeType: string;
    fileSize: number;
    status: string;
    createdAt: Date;
    updatedAt: Date;
}

const mapResumeToMetadata = (resume: IResume): ResumeMetadataResponse => ({
    id: resume._id.toString(),
    candidateId: resume.candidateId.toString(),
    originalFileName: resume.originalFileName,
    mimeType: resume.mimeType,
    fileSize: resume.fileSize,
    status: resume.status,
    createdAt: resume.createdAt,
    updatedAt: resume.updatedAt
});

export const ingestResume = async (
    candidateId: string,
    file: Express.Multer.File,
    userId: string
): Promise<{ resume: ResumeMetadataResponse; textSample: string }> => {
    // 1. Validate binary magic bytes / signatures against extension first (fail fast)
    const sigCheck = validateFileSignature(
        file.buffer,
        file.originalname,
        file.mimetype
    );

    if (!sigCheck.isValid || sigCheck.detectedType === "unknown") {
        throw new ApiError(400, sigCheck.error || "File signature verification failed.");
    }

    // 2. Resource-level ownership check on candidate
    const candidate = await getCandidateById(candidateId, userId);

    // 3. Extract text from document stream
    const extraction = await extractResumeText(
        file.buffer,
        sigCheck.detectedType
    );

    // 4. Generate safe server-side storage identifier and save to private disk
    const storageKey = generateSafeStorageKey(file.originalname);
    await saveFileToStorage(file.buffer, storageKey);

    // 5. Persist metadata in MongoDB with rollback guard
    let resume: IResume;
    try {
        resume = await Resume.create({
            candidateId: candidate._id,
            originalFileName: file.originalname,
            storageKey,
            fileUrl: `/internal/resumes/${storageKey}`,
            mimeType: file.mimetype,
            fileSize: file.size,
            extractedText: extraction.text,
            status: "processed",
            createdBy: new mongoose.Types.ObjectId(userId)
        });
    } catch (dbErr) {
        // Rollback: clean up orphaned file on disk if database persistence fails
        await deleteStoredFile(storageKey);
        throw dbErr;
    }

    return {
        resume: mapResumeToMetadata(resume),
        textSample: extraction.text.slice(0, 160) + (extraction.text.length > 160 ? "..." : "")
    };
};

export const getCandidateResumes = async (
    candidateId: string,
    userId: string
): Promise<ResumeMetadataResponse[]> => {
    await getCandidateById(candidateId, userId);

    const resumes = await Resume.find({
        candidateId: new mongoose.Types.ObjectId(candidateId)
    })
        .select("-extractedText")
        .sort({ createdAt: -1 });

    return resumes.map(mapResumeToMetadata);
};

export const getCandidateResumeById = async (
    candidateId: string,
    resumeId: string,
    userId: string
): Promise<ResumeMetadataResponse> => {
    await getCandidateById(candidateId, userId);

    const resume = await Resume.findOne({
        _id: new mongoose.Types.ObjectId(resumeId),
        candidateId: new mongoose.Types.ObjectId(candidateId)
    });

    if (!resume) {
        throw new ApiError(404, "Resume not found for this candidate");
    }

    return mapResumeToMetadata(resume);
};

export const getCandidateResumeText = async (
    candidateId: string,
    resumeId: string,
    userId: string
): Promise<{ resumeId: string; candidateId: string; extractedText: string; characterCount: number }> => {
    await getCandidateById(candidateId, userId);

    const resume = await Resume.findOne({
        _id: new mongoose.Types.ObjectId(resumeId),
        candidateId: new mongoose.Types.ObjectId(candidateId)
    });

    if (!resume) {
        throw new ApiError(404, "Resume not found for this candidate");
    }

    if (!resume.extractedText) {
        throw new ApiError(404, "No extracted text available for this resume");
    }

    return {
        resumeId: resume._id.toString(),
        candidateId: resume.candidateId.toString(),
        extractedText: resume.extractedText,
        characterCount: resume.extractedText.length
    };
};

export const deleteCandidateResume = async (
    candidateId: string,
    resumeId: string,
    userId: string
): Promise<void> => {
    await getCandidateById(candidateId, userId);

    const resume = await Resume.findOne({
        _id: new mongoose.Types.ObjectId(resumeId),
        candidateId: new mongoose.Types.ObjectId(candidateId)
    });

    if (!resume) {
        throw new ApiError(404, "Resume not found for this candidate");
    }

    if (resume.storageKey) {
        await deleteStoredFile(resume.storageKey);
    }

    await Resume.findByIdAndDelete(resume._id);
};
