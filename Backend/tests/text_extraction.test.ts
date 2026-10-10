import { describe, it } from "node:test";
import assert from "node:assert/strict";
import {
    extractResumeText,
    extractTextFromPdf,
    extractTextFromDocx
} from "../src/services/textExtraction.service";
import { ApiError } from "../src/utils/ApiError";

describe("Text Extraction Service (EC-01, EC-02, EC-04, EC-16)", () => {
    // Valid minimal PDF containing text >= 50 characters
    const validPdfBuffer = Buffer.from(
        "%PDF-1.4\n" +
        "1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n" +
        "2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n" +
        "3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> >> >>\nendobj\n" +
        "4 0 obj\n<< /Length 85 >>\nstream\n" +
        "BT\n/F1 12 Tf\n50 700 Td\n(Senior Full Stack Developer specializing in Node.js, TypeScript, and MongoDB architectures.) Tj\nET\n" +
        "endstream\nendobj\n" +
        "xref\n0 5\n0000000000 65535 f \n0000000010 00000 n \n0000000060 00000 n \n0000000117 00000 n \n0000000282 00000 n \n" +
        "trailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n418\n%%EOF"
    );

    // PDF with short text (< 50 characters) simulating scanned document without OCR text layer (EC-04)
    const scannedSimulationPdf = Buffer.from(
        "%PDF-1.4\n" +
        "1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n" +
        "2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n" +
        "3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> >> >>\nendobj\n" +
        "4 0 obj\n<< /Length 20 >>\nstream\n" +
        "BT\n/F1 12 Tf\n50 700 Td\n(Hi) Tj\nET\n" +
        "endstream\nendobj\n" +
        "xref\n0 5\n0000000000 65535 f \n0000000010 00000 n \n0000000060 00000 n \n0000000117 00000 n \n0000000282 00000 n \n" +
        "trailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n353\n%%EOF"
    );

    it("should successfully extract text from valid PDF document", async () => {
        const result = await extractResumeText(validPdfBuffer, "pdf");

        assert.ok(result.text.includes("Senior Full Stack Developer"));
        assert.ok(result.text.includes("TypeScript"));
        assert.ok(result.characterCount >= 50);
    });

    it("should detect scanned PDF or insufficient text and reject with 422 (EC-04)", async () => {
        await assert.rejects(
            async () => {
                await extractTextFromPdf(scannedSimulationPdf);
            },
            (err: any) => {
                assert.ok(err instanceof ApiError);
                assert.strictEqual(err.statusCode, 422);
                assert.match(err.message, /scanned document/i);
                return true;
            }
        );
    });

    it("should detect corrupted PDF binary and reject with 422 (EC-02)", async () => {
        const corruptPdf = Buffer.from("%PDF-1.4 damaged broken payload with missing xref and tables");

        await assert.rejects(
            async () => {
                await extractTextFromPdf(corruptPdf);
            },
            (err: any) => {
                assert.ok(err instanceof ApiError);
                assert.strictEqual(err.statusCode, 422);
                assert.match(err.message, /corrupted or malformed/i);
                return true;
            }
        );
    });

    it("should detect corrupted DOCX archive and reject with 422 (EC-02)", async () => {
        const corruptDocx = Buffer.from([
            0x50, 0x4b, 0x03, 0x04, 0x14, 0x00, 0x00, 0x00,
            0x08, 0x00, 0xde, 0xad, 0xbe, 0xef, 0x00, 0x00
        ]);

        await assert.rejects(
            async () => {
                await extractTextFromDocx(corruptDocx);
            },
            (err: any) => {
                assert.ok(err instanceof ApiError);
                assert.strictEqual(err.statusCode, 422);
                assert.match(err.message, /corrupted or invalid/i);
                return true;
            }
        );
    });
});
