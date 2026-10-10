import { Request, Response } from "express";
import {
    ingestResume,
    getCandidateResumes,
    getCandidateResumeById,
    getCandidateResumeText,
    deleteCandidateResume
} from "../services/resume.service";
import { ApiError } from "../utils/ApiError";

export const uploadResume = async (req: Request, res: Response) => {
    if (!req.user) {
        throw new ApiError(401, "Authentication required");
    }

    if (!req.file) {
        throw new ApiError(400, "Resume file is required");
    }

    const candidateId = req.params.id as string;
    const result = await ingestResume(candidateId, req.file, req.user.userId);

    res.status(201).json({
        success: true,
        message: "Resume ingested and text extracted successfully",
        data: result
    });
};

export const listResumes = async (req: Request, res: Response) => {
    if (!req.user) {
        throw new ApiError(401, "Authentication required");
    }

    const candidateId = req.params.id as string;
    const resumes = await getCandidateResumes(candidateId, req.user.userId);

    res.status(200).json({
        success: true,
        data: resumes
    });
};

export const getResume = async (req: Request, res: Response) => {
    if (!req.user) {
        throw new ApiError(401, "Authentication required");
    }

    const candidateId = req.params.id as string;
    const resumeId = req.params.resumeId as string;

    const resume = await getCandidateResumeById(
        candidateId,
        resumeId,
        req.user.userId
    );

    res.status(200).json({
        success: true,
        data: resume
    });
};

export const getResumeText = async (req: Request, res: Response) => {
    if (!req.user) {
        throw new ApiError(401, "Authentication required");
    }

    const candidateId = req.params.id as string;
    const resumeId = req.params.resumeId as string;

    const result = await getCandidateResumeText(
        candidateId,
        resumeId,
        req.user.userId
    );

    res.status(200).json({
        success: true,
        data: result
    });
};

export const deleteResume = async (req: Request, res: Response) => {
    if (!req.user) {
        throw new ApiError(401, "Authentication required");
    }

    const candidateId = req.params.id as string;
    const resumeId = req.params.resumeId as string;

    await deleteCandidateResume(candidateId, resumeId, req.user.userId);

    res.status(200).json({
        success: true,
        message: "Resume deleted successfully"
    });
};
