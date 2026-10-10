import { Job } from "../models/Job";
import { ApiError } from "../utils/ApiError";

interface CreateJobInput {
  title: string;
  description: string;
  requiredSkills?: string[];
  preferredSkills?: string[];
  minExperience?: number;
  maxExperience?: number;
  education?: string;
  createdBy: string;
}

export const createJob = async (
  data: CreateJobInput
) => {
  return Job.create(data);
};

export const getJobs = async (
  userId: string
) => {
  return Job.find({
    createdBy: userId
  }).sort({
    createdAt: -1
  });
};

export const getJobById = async (
  jobId: string,
  userId: string
) => {
  const job = await Job.findOne({
    _id: jobId,
    createdBy: userId
  });

  if (!job) {
    throw new ApiError(
      404,
      "Job not found"
    );
  }

  return job;
};