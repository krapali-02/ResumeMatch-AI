export class ApiError extends Error {
    statusCode: number;
    errors?: Array<{ field: string; message: string }>;

    constructor(
        statusCode: number,
        message: string,
        errors?: Array<{ field: string; message: string }>
    ) {
        super(message);

        this.statusCode = statusCode;
        this.errors = errors;
        this.name = "ApiError";

        Object.setPrototypeOf(this, ApiError.prototype);
    }
}