import { z } from "zod";

const objectIdRegex = /^[0-9a-fA-F]{24}$/;

export const candidateIdParamSchema = z.object({
    id: z
        .string()
        .regex(objectIdRegex, "Invalid candidate ID format. Must be a 24-character hexadecimal ObjectId")
});

export const candidateResumeParamsSchema = z.object({
    id: z
        .string()
        .regex(objectIdRegex, "Invalid candidate ID format. Must be a 24-character hexadecimal ObjectId"),
    resumeId: z
        .string()
        .regex(objectIdRegex, "Invalid resume ID format. Must be a 24-character hexadecimal ObjectId")
});

export const createCandidateSchema = z.object({
    name: z
        .string()
        .trim()
        .min(2, "Name must be at least 2 characters")
        .max(100, "Name cannot exceed 100 characters"),

    email: z
        .string()
        .trim()
        .email("Invalid email format")
        .toLowerCase()
        .optional(),

    phone: z
        .string()
        .trim()
        .optional(),

    skills: z
        .array(z.string().trim().min(1, "Skill cannot be empty"))
        .optional()
        .default([]),

    experienceYears: z
        .number()
        .min(0, "Experience years cannot be negative")
        .optional()
        .default(0),

    education: z
        .string()
        .trim()
        .optional()
});

export type CreateCandidateInput = z.infer<typeof createCandidateSchema>;
