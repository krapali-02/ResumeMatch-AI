import mongoose, { Document, Schema } from "mongoose";

export type JobStatus = "draft" | "active" | "paused" | "closed";

export interface IJob extends Document {
  title: string;
  description: string;

  requiredSkills: string[];
  preferredSkills: string[];

  minExperience: number;
  maxExperience?: number;

  education?: string;

  status: JobStatus;

  createdBy: mongoose.Types.ObjectId;

  createdAt: Date;
  updatedAt: Date;
}

const jobSchema = new Schema<IJob>(
  {
    title: {
      type: String,
      required: true,
      trim: true
    },

    description: {
      type: String,
      required: true,
      trim: true
    },

    requiredSkills: {
      type: [String],
      default: []
    },

    preferredSkills: {
      type: [String],
      default: []
    },

    minExperience: {
      type: Number,
      default: 0,
      min: 0
    },

    maxExperience: {
      type: Number,
      min: 0
    },

    education: {
      type: String,
      trim: true
    },

    status: {
      type: String,
      enum: ["draft", "active", "paused", "closed"],
      default: "draft",
      index: true
    },

    createdBy: {
      type: Schema.Types.ObjectId,
      ref: "User",
      required: true,
      index: true
    }
  },
  {
    timestamps: true
  }
);

jobSchema.index({ createdBy: 1, status: 1 });

export const Job = mongoose.model<IJob>("Job", jobSchema);