import jwt from "jsonwebtoken";
import { env } from "../config/env";

export interface JwtPayload {
  userId: string;
  role: "recruiter" | "admin";
}

export const generateAccessToken = (
  payload: JwtPayload
): string => {
  return jwt.sign(payload, env.jwtAccessSecret, {
    expiresIn: env.jwtAccessExpiresIn
  } as jwt.SignOptions);
};

export const verifyAccessToken = (
  token: string
): JwtPayload => {
  return jwt.verify(
    token,
    env.jwtAccessSecret
  ) as JwtPayload;
};