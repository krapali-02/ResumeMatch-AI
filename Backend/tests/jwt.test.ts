import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { generateAccessToken, verifyAccessToken } from "../src/utils/jwt";

describe("JWT Utilities", () => {
    it("should generate a valid JWT and decode expected payload", () => {
        const payload = {
            userId: "usr_1234567890",
            role: "recruiter" as const
        };

        const token = generateAccessToken(payload);
        assert.ok(typeof token === "string");
        assert.ok(token.split(".").length === 3);

        const decoded = verifyAccessToken(token);
        assert.strictEqual(decoded.userId, payload.userId);
        assert.strictEqual(decoded.role, payload.role);
    });

    it("should fail verification for a tampered or invalid token", () => {
        assert.throws(() => {
            verifyAccessToken("invalid.token.here");
        });
    });
});
