import { describe, it, before, after } from "node:test";
import assert from "node:assert/strict";
import http from "node:http";
import { AddressInfo } from "node:net";
import app from "../src/app";

describe("Protected Routes Authorization Guards", () => {
    let server: http.Server;
    let baseUrl: string;

    before(() => {
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

    it("GET /api/v1/auth/me should reject request without Authorization header with 401", async () => {
        const res = await fetch(`${baseUrl}/api/v1/auth/me`);
        const body = (await res.json()) as any;

        assert.strictEqual(res.status, 401);
        assert.strictEqual(body.success, false);
        assert.match(body.message, /token required/i);
    });

    it("GET /api/v1/auth/me should reject request with malformed or invalid token with 401", async () => {
        const res = await fetch(`${baseUrl}/api/v1/auth/me`, {
            headers: {
                Authorization: "Bearer invalid.fake.token"
            }
        });
        const body = (await res.json()) as any;

        assert.strictEqual(res.status, 401);
        assert.strictEqual(body.success, false);
        assert.match(body.message, /Invalid or expired token/i);
    });

    it("POST /api/v1/jobs should reject unauthenticated request with 401", async () => {
        const res = await fetch(`${baseUrl}/api/v1/jobs`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                title: "Software Engineer",
                description: "Build scalable cloud services"
            })
        });
        const body = (await res.json()) as any;

        assert.strictEqual(res.status, 401);
        assert.strictEqual(body.success, false);
    });

    it("GET /api/v1/jobs should reject unauthenticated request with 401", async () => {
        const res = await fetch(`${baseUrl}/api/v1/jobs`);
        const body = (await res.json()) as any;

        assert.strictEqual(res.status, 401);
        assert.strictEqual(body.success, false);
    });

    it("GET /api/v1/jobs/:id should reject unauthenticated request with 401", async () => {
        const res = await fetch(`${baseUrl}/api/v1/jobs/507f1f77bcf86cd799439011`);
        const body = (await res.json()) as any;

        assert.strictEqual(res.status, 401);
        assert.strictEqual(body.success, false);
    });
});
