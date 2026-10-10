import http from "http";
import app from "./app";
import { connectDB, disconnectDB } from "./config/db";
import { env } from "./config/env";

const startServer = (): http.Server => {
    console.log("🚀 Starting ResumeMatch AI backend...");

    // Start HTTP server first to decouple process liveness from DB availability
    const server = app.listen(env.port, () => {
        console.log(`ResumeMatch AI Backend listening on port ${env.port}`);
        console.log(`Environment: ${env.nodeEnv}`);
        console.log(`Liveness check:  http://localhost:${env.port}/health`);
        console.log(`Readiness check: http://localhost:${env.port}/ready`);
    });

    // Initiate bounded database connection in the background
    connectDB()
        .then((connected) => {
            if (!connected) {
                console.warn(
                    "⚠️  Backend is running with database OFFLINE. Database-dependent endpoints will be unavailable until connected."
                );
            }
        })
        .catch((err) => {
            console.error("Unexpected error during database connection:", err);
        });

    // Graceful shutdown handlers
    const handleShutdown = (signal: string) => {
        console.log(`\n🛑 Received ${signal}. Initiating graceful shutdown...`);

        server.close(async () => {
            console.log("🔒 HTTP server closed.");
            try {
                await disconnectDB();
            } catch (err) {
                console.error("Error closing database connection:", err);
            }
            console.log("👋 Process terminated cleanly.");
            process.exit(0);
        });

        // Force shutdown after timeout if pending connections hang
        setTimeout(() => {
            console.error("⚠️ Forced shutdown after timeout.");
            process.exit(1);
        }, 10000).unref();
    };

    process.on("SIGINT", () => handleShutdown("SIGINT"));
    process.on("SIGTERM", () => handleShutdown("SIGTERM"));

    return server;
};

startServer();

export default startServer;