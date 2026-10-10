import {
  Request,
  Response,
  NextFunction
} from "express";

import {
  verifyAccessToken,
  JwtPayload
} from "../utils/jwt";

import { ApiError } from "../utils/ApiError";

declare global {
  namespace Express {
    interface Request {
      user?: JwtPayload;
    }
  }
}

export const authenticate = (
  req: Request,
  _res: Response,
  next: NextFunction
) => {
  const authHeader = req.headers.authorization;

  if (
    !authHeader ||
    !authHeader.startsWith("Bearer ")
  ) {
    return next(
      new ApiError(
        401,
        "Authentication token required"
      )
    );
  }

  const token = authHeader.split(" ")[1];

  try {
    const payload = verifyAccessToken(token);

    req.user = payload;

    next();
  } catch {
    next(
      new ApiError(
        401,
        "Invalid or expired token"
      )
    );
  }
};

export const authorize =
  (...roles: ("recruiter" | "admin")[]) =>
  (
    req: Request,
    _res: Response,
    next: NextFunction
  ) => {
    if (!req.user) {
      return next(
        new ApiError(
          401,
          "Authentication required"
        )
      );
    }

    if (!roles.includes(req.user.role)) {
      return next(
        new ApiError(
          403,
          "You do not have permission"
        )
      );
    }

    next();
  };