import { Request, Response } from "express";
import {
    loginUser,
    registerUser,
    getCurrentUser
} from "../services/auth.service";
import { ApiError } from "../utils/ApiError";

export const register = async (req: Request, res: Response) => {
    const { name, email, password } = req.body;

    const result = await registerUser({
        name,
        email,
        password
    });

    res.status(201).json({
        success: true,
        message: "User registered successfully",
        data: result
    });
};

export const login = async (req: Request, res: Response) => {
    const { email, password } = req.body;

    const result = await loginUser(email, password);

    res.status(200).json({
        success: true,
        message: "Login successful",
        data: result
    });
};

export const getMe = async (req: Request, res: Response) => {
    if (!req.user) {
        throw new ApiError(401, "Authentication required");
    }

    const user = await getCurrentUser(req.user.userId);

    res.status(200).json({
        success: true,
        data: {
            user
        }
    });
};