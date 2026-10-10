import mongoose, { Document, Schema } from "mongoose";

export interface IAuditLog extends Document {
  userId?: mongoose.Types.ObjectId;

  action: string;

  resource?: string;

  resourceId?: string;

  metadata?: Record<string, unknown>;

  ipAddress?: string;

  createdAt: Date;
}

const auditLogSchema = new Schema<IAuditLog>(
  {
    userId: {
      type: Schema.Types.ObjectId,
      ref: "User"
    },

    action: {
      type: String,
      required: true,
      index: true
    },

    resource: {
      type: String
    },

    resourceId: {
      type: String
    },

    metadata: {
      type: Schema.Types.Mixed
    },

    ipAddress: {
      type: String
    }
  },
  {
    timestamps: {
      createdAt: true,
      updatedAt: false
    }
  }
);

auditLogSchema.index({ createdAt: -1 });

export const AuditLog = mongoose.model<IAuditLog>(
  "AuditLog",
  auditLogSchema
);