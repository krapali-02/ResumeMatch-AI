import mongoose from "mongoose";
import { Candidate, ICandidate } from "../models/Candidate";
import { Resume } from "../models/Resume";
import { deleteStoredFile } from "./storage.service";
import { isDbConnected } from "../config/db";
import { ApiError } from "../utils/ApiError";

export interface CreateCandidateInput {
    name: string;
    email?: string;
    phone?: string;
    skills?: string[];
    experienceYears?: number;
    education?: string;
}

export const createCandidate = async (
    data: CreateCandidateInput,
    userId: string
): Promise<ICandidate> => {
    return Candidate.create({
        ...data,
        createdBy: new mongoose.Types.ObjectId(userId)
    });
};

export const getCandidates = async (userId: string): Promise<ICandidate[]> => {
    return Candidate.find({
        createdBy: new mongoose.Types.ObjectId(userId)
    }).sort({ createdAt: -1 });
};

export const getCandidateById = async (
    candidateId: string,
    userId: string
): Promise<ICandidate> => {
    if (!isDbConnected()) {
        throw new ApiError(503, "Database is not connected. Candidate lookup is currently unavailable.");
    }

    const candidate = await Candidate.findById(candidateId);

    if (!candidate) {
        throw new ApiError(404, "Candidate not found");
    }

    if (candidate.createdBy.toString() !== userId) {
        throw new ApiError(403, "You do not have permission to access this candidate");
    }

    return candidate;
};

export const deleteCandidate = async (
    candidateId: string,
    userId: string
): Promise<void> => {
    const candidate = await getCandidateById(candidateId, userId);

    // Clean up all associated resumes on disk and DB
    const resumes = await Resume.find({ candidateId: candidate._id });
    for (const resume of resumes) {
        if (resume.storageKey) {
            await deleteStoredFile(resume.storageKey);
        }
    }
    await Resume.deleteMany({ candidateId: candidate._id });

    await Candidate.findByIdAndDelete(candidate._id);
};
