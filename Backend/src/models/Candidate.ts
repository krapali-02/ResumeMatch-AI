import mongoose, { Document, Schema } from "mongoose";

export interface ICandidate extends Document {
  name: string;
  email?: string;
  phone?: string;

  skills: string[];

  experienceYears: number;

  education?: string;

  createdBy: mongoose.Types.ObjectId;

  createdAt: Date;
  updatedAt: Date;
}

const candidateSchema = new Schema<ICandidate>(
  {
    name: {
      type: String,
      required: true,
      trim: true
    },

    email: {
      type: String,
      lowercase: true,
      trim: true
    },

    phone: {
      type: String,
      trim: true
    },

    skills: {
      type: [String],
      default: []
    },

    experienceYears: {
      type: Number,
      default: 0,
      min: 0
    },

    education: {
      type: String,
      trim: true
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

candidateSchema.index({ createdBy: 1, createdAt: -1 });

export const Candidate = mongoose.model<ICandidate>(
  "Candidate",
  candidateSchema
);