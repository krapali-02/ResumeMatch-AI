import mongoose, { Document, Schema } from "mongoose";

export interface IMatch extends Document {
  jobId: mongoose.Types.ObjectId;
  candidateId: mongoose.Types.ObjectId;

  overallScore: number;

  semanticScore: number;
  skillsScore: number;
  experienceScore: number;
  educationScore: number;

  matchedSkills: string[];
  missingSkills: string[];

  evidence: {
    criterion: string;
    snippet: string;
    source: string;
  }[];

  createdAt: Date;
  updatedAt: Date;
}

const matchSchema = new Schema<IMatch>(
  {
    jobId: {
      type: Schema.Types.ObjectId,
      ref: "Job",
      required: true,
      index: true
    },

    candidateId: {
      type: Schema.Types.ObjectId,
      ref: "Candidate",
      required: true,
      index: true
    },

    overallScore: {
      type: Number,
      required: true,
      min: 0,
      max: 100
    },

    semanticScore: {
      type: Number,
      default: 0
    },

    skillsScore: {
      type: Number,
      default: 0
    },

    experienceScore: {
      type: Number,
      default: 0
    },

    educationScore: {
      type: Number,
      default: 0
    },

    matchedSkills: {
      type: [String],
      default: []
    },

    missingSkills: {
      type: [String],
      default: []
    },

    evidence: [
      {
        criterion: String,
        snippet: String,
        source: String
      }
    ]
  },
  {
    timestamps: true
  }
);

matchSchema.index(
  { jobId: 1, candidateId: 1 },
  { unique: true }
);

matchSchema.index({
  jobId: 1,
  overallScore: -1
});

export const Match = mongoose.model<IMatch>(
  "Match",
  matchSchema
);