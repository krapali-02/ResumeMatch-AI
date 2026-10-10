import { describe, it, before, after } from "node:test";
import assert from "node:assert/strict";
import http from "node:http";
import { AddressInfo } from "node:net";
import app from "../src/app";
import { generateAccessToken } from "../src/utils/jwt";

describe("Input Validation & Zod Schema Guards", () => {
    let server: http.Server;
    let baseUrl: string;
    let validToken: string;

    before(() => {
        validToken = generateAccessToken({
            userId: "507f1f77bcf86cd799439011",
            role: "recruiter"
        });

        return new Promise<void>((resolve) => {
            server = app.listen(0, "127.0.0.1", () => {
                const addr = server.address() as AddressInfo;
                baseUrl = `http://127.0.0.1:${addr.port}`;
                resolve();
            });
        });
    });

    after(() => {
        return new Promise<void>((resolve) => {
            server.close(() => resolve());
        });
    });

    it("POST /api/v1/auth/register should reject missing fields with 400", async () => {
        const res = await fetch(`${baseUrl}/api/v1/auth/register`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({})
        });
        const body = (await res.json()) as any;

        assert.strictEqual(res.status, 400);
        assert.strictEqual(body.success, false);
        assert.ok(Array.isArray(body.errors));
    });

    it("POST /api/v1/auth/register should reject invalid email format with 400", async () => {
        const res = await fetch(`${baseUrl}/api/v1/auth/register`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                name: "Alex Recruiter",
                email: "not-an-email",
                password: "SecurePassword123!"
            })
        });
        const body = (await res.json()) as any;

        assert.strictEqual(res.status, 400);
        assert.strictEqual(body.success, false);
        assert.match(body.message, /invalid email/i);
    });

    it("POST /api/v1/auth/register should reject password shorter than 8 chars with 400", async () => {
        const res = await fetch(`${baseUrl}/api/v1/auth/register`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                name: "Alex Recruiter",
                email: "alex@example.com",
                password: "short"
            })
        });
        const body = (await res.json()) as any;

        assert.strictEqual(res.status, 400);
        assert.strictEqual(body.success, false);
        assert.match(body.message, /at least 8 characters/i);
    });

    it("POST /api/v1/auth/login should reject empty body with 400", async () => {
        const res = await fetch(`${baseUrl}/api/v1/auth/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({})
        });
        const body = (await res.json()) as any;

        assert.strictEqual(res.status, 400);
        assert.strictEqual(body.success, false);
    });

    it("POST /api/v1/jobs should reject description shorter than 10 chars with 400", async () => {
        const res = await fetch(`${baseUrl}/api/v1/jobs`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${validToken}`
            },
            body: JSON.stringify({
                title: "Frontend Engineer",
                description: "Too short"
            })
        });
        const body = (await res.json()) as any;

        assert.strictEqual(res.status, 400);
        assert.strictEqual(body.success, false);
        assert.match(body.message, /at least 10 characters/i);
    });

    it("POST /api/v1/jobs should reject when maxExperience < minExperience with 400", async () => {
        const res = await fetch(`${baseUrl}/api/v1/jobs`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${validToken}`
            },
            body: JSON.stringify({
                title: "Senior Architect",
                description: "Lead the technical architecture and scaling strategy",
                minExperience: 8,
                maxExperience: 3
            })
        });
        const body = (await res.json()) as any;

        assert.strictEqual(res.status, 400);
        assert.strictEqual(body.success, false);
        assert.match(body.message, /greater than or equal/i);
    });

    it("GET /api/v1/jobs/:id should reject malformed ObjectId with 400", async () => {
        const res = await fetch(`${baseUrl}/api/v1/jobs/not-a-valid-objectid`, {
            headers: {
                Authorization: `Bearer ${validToken}`
            }
        });
        const body = (await res.json()) as any;

        assert.strictEqual(res.status, 400);
        assert.strictEqual(body.success, false);
        assert.match(body.message, /Invalid job ID format/i);
    });
});
