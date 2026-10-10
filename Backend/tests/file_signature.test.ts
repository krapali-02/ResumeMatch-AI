import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { validateFileSignature } from "../src/utils/fileSignature";

describe("File Signature & Magic Bytes Validation (EC-01, EC-03)", () => {
    it("should accept valid PDF magic bytes (%PDF-)", () => {
        const validPdfHeader = Buffer.from("%PDF-1.4 header and content for test");
        const result = validateFileSignature(validPdfHeader, "resume.pdf", "application/pdf");

        assert.strictEqual(result.isValid, true);
        assert.strictEqual(result.detectedType, "pdf");
        assert.strictEqual(result.error, undefined);
    });

    it("should accept valid DOCX zip header (PK\\x03\\x04)", () => {
        const validDocxHeader = Buffer.from([
            0x50, 0x4b, 0x03, 0x04, 0x14, 0x00, 0x06, 0x00,
            0x08, 0x00, 0x00, 0x00, 0x21, 0x00, 0x00, 0x00
        ]);
        const result = validateFileSignature(
            validDocxHeader,
            "resume.docx",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        );

        assert.strictEqual(result.isValid, true);
        assert.strictEqual(result.detectedType, "docx");
        assert.strictEqual(result.error, undefined);
    });

    it("should reject 0-byte empty file (EC-01)", () => {
        const emptyBuffer = Buffer.alloc(0);
        const result = validateFileSignature(emptyBuffer, "empty.pdf", "application/pdf");

        assert.strictEqual(result.isValid, false);
        assert.match(result.error || "", /empty/i);
    });

    it("should reject truncated file smaller than 16 bytes", () => {
        const tinyBuffer = Buffer.from("tiny");
        const result = validateFileSignature(tinyBuffer, "tiny.pdf", "application/pdf");

        assert.strictEqual(result.isValid, false);
        assert.match(result.error || "", /too small/i);
    });

    it("should reject spoofed PDF containing plain text (EC-03)", () => {
        const fakePdf = Buffer.from("This is a plain text file masquerading as a PDF document.");
        const result = validateFileSignature(fakePdf, "fake.pdf", "application/pdf");

        assert.strictEqual(result.isValid, false);
        assert.match(result.error || "", /signature mismatch/i);
    });

    it("should reject spoofed DOCX containing executable header (EC-03)", () => {
        // MZ executable header
        const fakeDocx = Buffer.from([
            0x4d, 0x5a, 0x90, 0x00, 0x03, 0x00, 0x00, 0x00,
            0x04, 0x00, 0x00, 0x00, 0xff, 0xff, 0x00, 0x00
        ]);
        const result = validateFileSignature(
            fakeDocx,
            "malicious.docx",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        );

        assert.strictEqual(result.isValid, false);
        assert.match(result.error || "", /signature mismatch/i);
    });

    it("should reject unsupported extensions like .txt, .exe, .png", () => {
        const buffer = Buffer.from("Some arbitrary content that is long enough");
        const result = validateFileSignature(buffer, "notes.txt", "text/plain");

        assert.strictEqual(result.isValid, false);
        assert.match(result.error || "", /unsupported file extension/i);
    });
});
