import { z } from "zod";

const objectIdRegex = /^[0-9a-fA-F]{24}$/;

export const jobIdParamSchema = z.object({
    id: z
        .string()
        .regex(objectIdRegex, "Invalid job ID format. Must be a 24-character hexadecimal ObjectId")
});

export const createJobSchema = z.object({
    title: z
        .string()
        .trim()
        .min(3, "Title must be at least 3 characters")
        .max(200, "Title cannot exceed 200 characters"),

    description: z
        .string()
        .trim()
        .min(10, "Description must be at least 10 characters"),

    requiredSkills: z
        .array(z.string().trim().min(1, "Skill cannot be empty"))
        .optional()
        .default([]),

    preferredSkills: z
        .array(z.string().trim().min(1, "Skill cannot be empty"))
        .optional()
        .default([]),

    minExperience: z
        .number()
        .min(0, "Minimum experience cannot be negative")
        .optional()
        .default(0),

    maxExperience: z
        .number()
        .min(0, "Maximum experience cannot be negative")
        .optional(),

    education: z
        .string()
        .trim()
        .optional()
}).refine(
    (data) => {
        if (data.maxExperience !== undefined && data.minExperience !== undefined) {
            return data.maxExperience >= data.minExperience;
        }
        return true;
    },
    {
        message: "Maximum experience must be greater than or equal to minimum experience",
        path: ["maxExperience"]
    }
);

export type CreateJobInput = z.infer<typeof createJobSchema>;
export type JobIdParam = z.infer<typeof jobIdParamSchema>;
