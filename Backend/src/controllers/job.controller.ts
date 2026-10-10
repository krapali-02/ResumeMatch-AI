import { Request, Response } from "express";

import {
  createJob,
  getJobs,
  getJobById
} from "../services/job.service";

import { ApiError } from "../utils/ApiError";

// Create Job
export const create = async (
  req: Request,
  res: Response
) => {
  if (!req.user) {
    throw new ApiError(
      401,
      "Authentication required"
    );
  }

  const {
    title,
    description,
    requiredSkills,
    preferredSkills,
    minExperience,
    maxExperience,
    education
  } = req.body;

  if (!title || !description) {
    throw new ApiError(
      400,
      "Title and description are required"
    );
  }

  const job = await createJob({
    title,
    description,
    requiredSkills,
    preferredSkills,
    minExperience,
    maxExperience,
    education,
    createdBy: req.user.userId
  });

  res.status(201).json({
    success: true,
    message: "Job created successfully",
    data: job
  });
};


// Get all jobs
export const list = async (
  req: Request,
  res: Response
) => {
  if (!req.user) {
    throw new ApiError(
      401,
      "Authentication required"
    );
  }

  const jobs = await getJobs(
    req.user.userId
  );

  res.status(200).json({
    success: true,
    data: jobs
  });
};


// Get single job
export const getOne = async (
  req: Request,
  res: Response
) => {
  if (!req.user) {
    throw new ApiError(
      401,
      "Authentication required"
    );
  }

  const jobId = req.params.id as string;

  const job = await getJobById(
    jobId,
    req.user.userId
  );

  res.status(200).json({
    success: true,
    data: job
  });
};

