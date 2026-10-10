import bcrypt from "bcryptjs";
import { User } from "../models/User";
import { ApiError } from "../utils/ApiError";
import { generateAccessToken } from "../utils/jwt";

export interface RegisterInput {
    name: string;
    email: string;
    password: string;
}

export const registerUser = async (data: RegisterInput) => {
    const existingUser = await User.findOne({
        email: data.email.toLowerCase()
    });

    if (existingUser) {
        throw new ApiError(409, "User with this email already exists");
    }

    const hashedPassword = await bcrypt.hash(data.password, 12);

    const user = await User.create({
        name: data.name,
        email: data.email.toLowerCase(),
        password: hashedPassword,
        role: "recruiter"
    });

    const accessToken = generateAccessToken({
        userId: user._id.toString(),
        role: user.role
    });

    return {
        user: {
            id: user._id,
            name: user.name,
            email: user.email,
            role: user.role
        },
        accessToken
    };
};

export const loginUser = async (email: string, password: string) => {
    const user = await User.findOne({
        email: email.toLowerCase()
    }).select("+password");

    if (!user) {
        throw new ApiError(401, "Invalid email or password");
    }

    const passwordMatch = await bcrypt.compare(password, user.password);

    if (!passwordMatch) {
        throw new ApiError(401, "Invalid email or password");
    }

    if (!user.isActive) {
        throw new ApiError(403, "Account is disabled");
    }

    const accessToken = generateAccessToken({
        userId: user._id.toString(),
        role: user.role
    });

    return {
        user: {
            id: user._id,
            name: user.name,
            email: user.email,
            role: user.role
        },
        accessToken
    };
};

export const getCurrentUser = async (userId: string) => {
    const user = await User.findById(userId);

    if (!user) {
        throw new ApiError(404, "User not found");
    }

    if (!user.isActive) {
        throw new ApiError(403, "Account is disabled");
    }

    return {
        id: user._id,
        name: user.name,
        email: user.email,
        role: user.role,
        isActive: user.isActive,
        createdAt: user.createdAt
    };
};