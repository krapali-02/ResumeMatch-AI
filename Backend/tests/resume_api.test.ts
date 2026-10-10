import { describe, it, before, after } from "node:test";
import assert from "node:assert/strict";
import http from "node:http";
import { AddressInfo } from "node:net";
import app from "../src/app";
import { generateAccessToken } from "../src/utils/jwt";

describe("Candidate and Resume Ingestion API Endpoints", () => {
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

    it("POST /api/v1/candidates/:id/resumes should reject unauthenticated request with 401", async () => {
        const res = await fetch(`${baseUrl}/api/v1/candidates/507f1f77bcf86cd799439011/resumes`, {
            method: "POST"
        });
        const body = (await res.json()) as any;

        assert.strictEqual(res.status, 401);
        assert.strictEqual(body.success, false);
    });

    it("GET /api/v1/candidates/:id/resumes should reject unauthenticated request with 401", async () => {
        const res = await fetch(`${baseUrl}/api/v1/candidates/507f1f77bcf86cd799439011/resumes`);
        const body = (await res.json()) as any;

        assert.strictEqual(res.status, 401);
        assert.strictEqual(body.success, false);
    });

    it("GET /api/v1/candidates/:id/resumes/:resumeId/text should reject unauthenticated request with 401", async () => {
        const res = await fetch(
            `${baseUrl}/api/v1/candidates/507f1f77bcf86cd799439011/resumes/507f1f77bcf86cd799439022/text`
        );
        const body = (await res.json()) as any;

        assert.strictEqual(res.status, 401);
        assert.strictEqual(body.success, false);
    });

    it("DELETE /api/v1/candidates/:id/resumes/:resumeId should reject unauthenticated request with 401", async () => {
        const res = await fetch(
            `${baseUrl}/api/v1/candidates/507f1f77bcf86cd799439011/resumes/507f1f77bcf86cd799439022`,
            {
                method: "DELETE"
            }
        );
        const body = (await res.json()) as any;

        assert.strictEqual(res.status, 401);
        assert.strictEqual(body.success, false);
    });

    it("POST /api/v1/candidates/:id/resumes should reject malformed candidate ObjectId with 400", async () => {
        const res = await fetch(`${baseUrl}/api/v1/candidates/malformed-id/resumes`, {
            method: "POST",
            headers: {
                Authorization: `Bearer ${validToken}`
            }
        });
        const body = (await res.json()) as any;

        assert.strictEqual(res.status, 400);
        assert.strictEqual(body.success, false);
        assert.match(body.message, /invalid candidate id format/i);
    });

    it("POST /api/v1/candidates/:id/resumes should reject request without multipart file with 400", async () => {
        const formData = new FormData();
        formData.append("otherField", "test");

        const res = await fetch(`${baseUrl}/api/v1/candidates/507f1f77bcf86cd799439011/resumes`, {
            method: "POST",
            headers: {
                Authorization: `Bearer ${validToken}`
            },
            body: formData
        });
        const body = (await res.json()) as any;

        assert.strictEqual(res.status, 400);
        assert.strictEqual(body.success, false);
        assert.match(body.message, /resume file is required/i);
    });

    it("POST /api/v1/candidates/:id/resumes should reject unsupported file format (.txt) with 400", async () => {
        const formData = new FormData();
        const fakeTxtBlob = new Blob(["Plain text resume content"], { type: "text/plain" });
        formData.append("resume", fakeTxtBlob, "candidate.txt");

        const res = await fetch(`${baseUrl}/api/v1/candidates/507f1f77bcf86cd799439011/resumes`, {
            method: "POST",
            headers: {
                Authorization: `Bearer ${validToken}`
            },
            body: formData
        });
        const body = (await res.json()) as any;

        assert.strictEqual(res.status, 400);
        assert.strictEqual(body.success, false);
        assert.match(body.message, /unsupported file extension/i);
    });

    it("POST /api/v1/candidates/:id/resumes should reject MIME-spoofed PDF file with 400 (EC-03)", async () => {
        const formData = new FormData();
        const spoofedBlob = new Blob(
            ["This is plain text with no PDF magic header disguised as a PDF"],
            { type: "application/pdf" }
        );
        formData.append("resume", spoofedBlob, "spoofed.pdf");

        const res = await fetch(`${baseUrl}/api/v1/candidates/507f1f77bcf86cd799439011/resumes`, {
            method: "POST",
            headers: {
                Authorization: `Bearer ${validToken}`
            },
            body: formData
        });
        const body = (await res.json()) as any;

        assert.strictEqual(res.status, 400);
        assert.strictEqual(body.success, false);
        assert.match(body.message, /signature mismatch/i);
    });
});
