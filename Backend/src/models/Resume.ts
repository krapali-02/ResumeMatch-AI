import mongoose, { Document, Schema } from "mongoose";

export type ResumeStatus =
  | "uploaded"
  | "processing"
  | "processed"
  | "failed";

export interface IResume extends Document {
  candidateId: mongoose.Types.ObjectId;

  originalFileName: string;
  storageKey: string;
  fileUrl: string;

  mimeType: string;
  fileSize: number;

  extractedText?: string;

  status: ResumeStatus;

  processingError?: string;

  createdBy: mongoose.Types.ObjectId;

  createdAt: Date;
  updatedAt: Date;
}

const resumeSchema = new Schema<IResume>(
  {
    candidateId: {
      type: Schema.Types.ObjectId,
      ref: "Candidate",
      required: true,
      index: true
    },

    originalFileName: {
      type: String,
      required: true
    },

    storageKey: {
      type: String,
      required: true,
      unique: true,
      index: true
    },

    fileUrl: {
      type: String,
      required: true
    },

    mimeType: {
      type: String,
      required: true
    },

    fileSize: {
      type: Number,
      required: true
    },

    extractedText: {
      type: String
    },

    status: {
      type: String,
      enum: ["uploaded", "processing", "processed", "failed"],
      default: "uploaded",
      index: true
    },

    processingError: {
      type: String
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

resumeSchema.index({ candidateId: 1, createdAt: -1 });

export const Resume = mongoose.model<IResume>(
  "Resume",
  resumeSchema
);