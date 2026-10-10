import mongoose from "mongoose";
import { env } from "./env";

export const getDbState = () => {
    const states: Record<number, string> = {
        0: "disconnected",
        1: "connected",
        2: "connecting",
        3: "disconnecting"
    };

    const readyState = mongoose.connection.readyState;
    const isConnected = readyState === 1;

    return {
        isConnected,
        readyState,
        status: states[readyState] || "unknown",
        host: isConnected ? mongoose.connection.host : undefined,
        name: isConnected ? mongoose.connection.name : undefined
    };
};

export const isDbConnected = (): boolean => {
    return mongoose.connection.readyState === 1;
};

export const connectDB = async (
    maxRetries: number = 3,
    retryDelayMs: number = 2000
): Promise<boolean> => {
    let attempt = 0;

    while (attempt < maxRetries) {
        attempt++;
        try {
            console.log(
                `🔌 Attempting MongoDB connection (attempt ${attempt}/${maxRetries})...`
            );

            await mongoose.connect(env.mongodbUri, {
                serverSelectionTimeoutMS: 5000
            });

            console.log("✅ MongoDB connected successfully");
            return true;
        } catch (error) {
            console.error(
                `❌ MongoDB connection attempt ${attempt}/${maxRetries} failed:`
            );

            if (error instanceof Error) {
                console.error(`   ${error.message}`);
            } else {
                console.error(error);
            }

            if (attempt < maxRetries) {
                console.log(`⏳ Retrying in ${retryDelayMs / 1000}s...`);
                await new Promise((resolve) => setTimeout(resolve, retryDelayMs));
            }
        }
    }

    // Actionable diagnostic guidance
    const isLocal =
        env.mongodbUri.includes("127.0.0.1") ||
        env.mongodbUri.includes("localhost");

    console.error("\n❌ MongoDB could not be reached after maximum retries.");
    if (isLocal) {
        console.error("📋 DIAGNOSTIC & ACTION REQUIRED:");
        console.error("   The MONGODB_URI in Backend/.env is configured for a local MongoDB instance (127.0.0.1:27017),");
        console.error("   but MongoDB is not running locally on this machine.");
        console.error("   To resolve this, choose one of the following:");
        console.error("   1. (Recommended) Configure a free MongoDB Atlas cloud database:");
        console.error("      MONGODB_URI=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/resumematch?retryWrites=true&w=majority");
        console.error("   2. Install and start MongoDB Community Server locally as a Windows service.\n");
    } else {
        console.error("📋 DIAGNOSTIC & ACTION REQUIRED:");
        console.error("   Unable to connect to the configured MongoDB URI.");
        console.error("   Please verify network connectivity, Atlas IP Access List (whitelist 0.0.0.0/0 or your IP),");
        console.error("   and check database username/password credentials.\n");
    }

    return false;
};

export const disconnectDB = async (): Promise<void> => {
    if (mongoose.connection.readyState !== 0) {
        await mongoose.connection.close(false);
        console.log("🛑 MongoDB connection closed");
    }
};