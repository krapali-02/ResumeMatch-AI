import { describe, it, before, after } from "node:test";
import assert from "node:assert/strict";
import http from "node:http";
import { AddressInfo } from "node:net";
import app from "../src/app";

describe("Health and Readiness Probes", () => {
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

    it("GET /health should return 200 OK (liveness) when database is unavailable", async () => {
        const res = await fetch(`${baseUrl}/health`);
        const body = (await res.json()) as any;

        assert.strictEqual(res.status, 200);
        assert.strictEqual(body.success, true);
        assert.strictEqual(body.status, "healthy");
        assert.strictEqual(typeof body.uptime, "number");
        assert.strictEqual(body.database.connected, false);
    });

    it("GET /api/v1/health should return 200 OK (prefixed liveness probe)", async () => {
        const res = await fetch(`${baseUrl}/api/v1/health`);
        const body = (await res.json()) as any;

        assert.strictEqual(res.status, 200);
        assert.strictEqual(body.success, true);
        assert.strictEqual(body.status, "healthy");
    });

    it("GET /ready should return 503 Service Unavailable when database is not connected", async () => {
        const res = await fetch(`${baseUrl}/ready`);
        const body = (await res.json()) as any;

        assert.strictEqual(res.status, 503);
        assert.strictEqual(body.success, false);
        assert.strictEqual(body.status, "not_ready");
        assert.strictEqual(body.services.database.status, "disconnected");
        assert.match(body.message, /Database is not connected/i);
    });

    it("GET /api/v1/ready should return 503 Service Unavailable when database is not connected", async () => {
        const res = await fetch(`${baseUrl}/api/v1/ready`);
        const body = (await res.json()) as any;

        assert.strictEqual(res.status, 503);
        assert.strictEqual(body.success, false);
        assert.strictEqual(body.status, "not_ready");
    });
});
