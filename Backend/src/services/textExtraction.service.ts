import mammoth from "mammoth";
import { ApiError } from "../utils/ApiError";

// In pdf-parse v2, the class is exported as PDFParse
// eslint-disable-next-line @typescript-eslint/no-var-requires
const { PDFParse } = require("pdf-parse");

export interface ExtractionResult {
    text: string;
    pageCount?: number;
    characterCount: number;
}

const normalizeExtractedText = (rawText: string): string => {
    return rawText
        .replace(/\r\n/g, "\n")
        .replace(/\r/g, "\n")
        .replace(/[ \t]+/g, " ")
        .replace(/\n{3,}/g, "\n\n")
        .trim();
};

export const extractTextFromPdf = async (buffer: Buffer): Promise<ExtractionResult> => {
    let parser: any;
    try {
        parser = new PDFParse({ data: buffer });
        await parser.load();
        const result = await parser.getText();
        const rawText = result?.text || "";
        const pageCount = result?.total || result?.pages?.length || 1;

        const normalized = normalizeExtractedText(rawText);

        // EC-01 & EC-04: Scanned PDF or empty text layer
        if (normalized.length < 50) {
            throw new ApiError(
                422,
                "Scanned document or unextractable text detected. The resume must contain an extractable text layer."
            );
        }

        return {
            text: normalized,
            pageCount,
            characterCount: normalized.length
        };
    } catch (err) {
        if (err instanceof ApiError) {
            throw err;
        }

        const errorMessage = (err instanceof Error ? err.message : String(err)).toLowerCase();

        // EC-16: Password-Protected / Encrypted PDF
        if (
            errorMessage.includes("password") ||
            errorMessage.includes("encrypt") ||
            errorMessage.includes("securityhandler")
        ) {
            throw new ApiError(
                422,
                "The PDF is password-protected or encrypted. Please provide an unencrypted resume."
            );
        }

        // EC-02: Corrupted or Malformed Binary File
        throw new ApiError(
            422,
            "Corrupted or malformed PDF file. Unable to extract document text."
        );
    } finally {
        if (parser && typeof parser.destroy === "function") {
            try {
                await parser.destroy();
            } catch {
                // Ignore cleanup error
            }
        }
    }
};

export const extractTextFromDocx = async (buffer: Buffer): Promise<ExtractionResult> => {
    try {
        const result = await mammoth.extractRawText({ buffer });
        const rawText = result?.value || "";
        const normalized = normalizeExtractedText(rawText);

        // EC-01 & Insufficient text check
        if (normalized.length < 50) {
            throw new ApiError(
                422,
                "Document contains insufficient extractable text. Please provide a complete resume."
            );
        }

        return {
            text: normalized,
            characterCount: normalized.length
        };
    } catch (err) {
        if (err instanceof ApiError) {
            throw err;
        }

        // EC-02: Corrupted or Malformed DOCX File
        throw new ApiError(
            422,
            "Corrupted or invalid DOCX document. Unable to parse document archive."
        );
    }
};

export const extractResumeText = async (
    buffer: Buffer,
    fileType: "pdf" | "docx"
): Promise<ExtractionResult> => {
    if (fileType === "pdf") {
        return extractTextFromPdf(buffer);
    } else if (fileType === "docx") {
        return extractTextFromDocx(buffer);
    }

    throw new ApiError(400, `Unsupported document format for text extraction: '${fileType}'.`);
};
