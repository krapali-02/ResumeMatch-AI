import dotenv from "dotenv";
import { z } from "zod";

dotenv.config();

const envSchema = z.object({
    NODE_ENV: z
        .enum(["development", "production", "test"])
        .default("development"),

    PORT: z.coerce.number().default(5000),

    MONGODB_URI: z
        .string()
        .min(1, "MONGODB_URI is required")
        .refine(
            (uri) => uri.startsWith("mongodb://") || uri.startsWith("mongodb+srv://"),
            "MONGODB_URI must start with 'mongodb://' or 'mongodb+srv://'"
        ),

    JWT_ACCESS_SECRET: z
        .string()
        .min(10, "JWT_ACCESS_SECRET must be at least 10 characters"),

    JWT_REFRESH_SECRET: z
        .string()
        .min(10, "JWT_REFRESH_SECRET must be at least 10 characters"),

    JWT_ACCESS_EXPIRES_IN: z.string().default("15m"),

    JWT_REFRESH_EXPIRES_IN: z.string().default("7d"),

    FRONTEND_URL: z.string().default("http://localhost:5173"),

    MAX_UPLOAD_SIZE_MB: z.coerce.number().default(10),

    UPLOAD_DIR: z.string().default("uploads")
});

const parsedEnv = envSchema.safeParse(process.env);

if (!parsedEnv.success) {
    console.error("❌ Invalid environment variables:");
    console.error(parsedEnv.error.flatten().fieldErrors);
    process.exit(1);
}

export const env = {
    nodeEnv: parsedEnv.data.NODE_ENV,
    port: parsedEnv.data.PORT,
    mongodbUri: parsedEnv.data.MONGODB_URI,
    jwtAccessSecret: parsedEnv.data.JWT_ACCESS_SECRET,
    jwtRefreshSecret: parsedEnv.data.JWT_REFRESH_SECRET,
    jwtAccessExpiresIn: parsedEnv.data.JWT_ACCESS_EXPIRES_IN,
    jwtRefreshExpiresIn: parsedEnv.data.JWT_REFRESH_EXPIRES_IN,
    frontendUrl: parsedEnv.data.FRONTEND_URL,
    maxUploadSizeMb: parsedEnv.data.MAX_UPLOAD_SIZE_MB,
    uploadDir: parsedEnv.data.UPLOAD_DIR
};