import express, { Request, Response } from "express";
import cors from "cors";
import helmet from "helmet";
import morgan from "morgan";
import rateLimit from "express-rate-limit";

import { env } from "./config/env";
import { getDbState, isDbConnected } from "./config/db";
import authRoutes from "./routes/auth.routes";
import jobRoutes from "./routes/job.routes";
import candidateRoutes from "./routes/candidate.routes";
import { notFoundMiddleware } from "./middlewares/notFound.middleware";
import { errorMiddleware } from "./middlewares/error.middleware";

const app = express();

app.use(helmet());

app.use(
    cors({
        origin: env.frontendUrl,
        credentials: true
    })
);

app.use(express.json({ limit: "10mb" }));
app.use(express.urlencoded({ extended: true }));

if (env.nodeEnv !== "test") {
    app.use(morgan("dev"));
}

app.use(
    rateLimit({
        windowMs: 15 * 60 * 1000,
        limit: 100,
        standardHeaders: true,
        legacyHeaders: false
    })
);

// Liveness Probe: reports whether the process is alive (200 always when alive)
const handleHealthCheck = (_req: Request, res: Response) => {
    const dbState = getDbState();

    res.status(200).json({
        success: true,
        status: "healthy",
        message: "ResumeMatch AI API process is alive",
        environment: env.nodeEnv,
        uptime: process.uptime(),
        timestamp: new Date().toISOString(),
        database: {
            status: dbState.status,
            connected: dbState.isConnected
        }
    });
};

// Readiness Probe: reports whether the system is ready to serve traffic (200 if DB ready, 503 if not)
const handleReadinessCheck = (_req: Request, res: Response) => {
    const dbState = getDbState();

    if (isDbConnected()) {
        res.status(200).json({
            success: true,
            status: "ready",
            services: {
                database: {
                    status: dbState.status,
                    readyState: dbState.readyState,
                    host: dbState.host,
                    name: dbState.name
                }
            }
        });
    } else {
        res.status(503).json({
            success: false,
            status: "not_ready",
            services: {
                database: {
                    status: dbState.status,
                    readyState: dbState.readyState
                }
            },
            message:
                "Database is not connected. Database-dependent operations are currently unavailable."
        });
    }
};

app.get("/health", handleHealthCheck);
app.get("/api/v1/health", handleHealthCheck);

app.get("/ready", handleReadinessCheck);
app.get("/api/v1/ready", handleReadinessCheck);

// API Routes
app.use("/api/v1/auth", authRoutes);
app.use("/api/v1/jobs", jobRoutes);
app.use("/api/v1/candidates", candidateRoutes);

// Error Handling
app.use(notFoundMiddleware);
app.use(errorMiddleware);

export default app;