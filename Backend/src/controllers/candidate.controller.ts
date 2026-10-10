import { Request, Response } from "express";
import {
    createCandidate,
    getCandidates,
    getCandidateById,
    deleteCandidate
} from "../services/candidate.service";
import { ApiError } from "../utils/ApiError";

export const create = async (req: Request, res: Response) => {
    if (!req.user) {
        throw new ApiError(401, "Authentication required");
    }

    const candidate = await createCandidate(req.body, req.user.userId);

    res.status(201).json({
        success: true,
        message: "Candidate created successfully",
        data: candidate
    });
};

export const list = async (req: Request, res: Response) => {
    if (!req.user) {
        throw new ApiError(401, "Authentication required");
    }

    const candidates = await getCandidates(req.user.userId);

    res.status(200).json({
        success: true,
        data: candidates
    });
};

export const getOne = async (req: Request, res: Response) => {
    if (!req.user) {
        throw new ApiError(401, "Authentication required");
    }

    const candidateId = req.params.id as string;
    const candidate = await getCandidateById(candidateId, req.user.userId);

    res.status(200).json({
        success: true,
        data: candidate
    });
};

export const remove = async (req: Request, res: Response) => {
    if (!req.user) {
        throw new ApiError(401, "Authentication required");
    }

    const candidateId = req.params.id as string;
    await deleteCandidate(candidateId, req.user.userId);

    res.status(200).json({
        success: true,
        message: "Candidate and associated resumes deleted successfully"
    });
};
