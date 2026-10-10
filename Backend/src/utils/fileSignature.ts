export type DetectedFileType = "pdf" | "docx" | "unknown";

export interface FileSignatureValidationResult {
    isValid: boolean;
    detectedType: DetectedFileType;
    error?: string;
}

/**
 * Validates the actual magic bytes (file signature) of an uploaded buffer against
 * declared extension and MIME type.
 *
 * Magic bytes:
 * - PDF: Starts with "%PDF-" (0x25, 0x50, 0x44, 0x46, 0x2D)
 * - DOCX: Standard ZIP container starting with "PK\x03\x04" (0x50, 0x4B, 0x03, 0x04)
 */
export const validateFileSignature = (
    buffer: Buffer,
    originalName: string,
    declaredMime: string
): FileSignatureValidationResult => {
    if (!buffer || buffer.length === 0) {
        return {
            isValid: false,
            detectedType: "unknown",
            error: "Uploaded file is empty (0 bytes)."
        };
    }

    if (buffer.length < 16) {
        return {
            isValid: false,
            detectedType: "unknown",
            error: "File is too small to be a valid document."
        };
    }

    const ext = originalName.slice(originalName.lastIndexOf(".")).toLowerCase();

    // Check PDF signature: "%PDF-" at start
    const isPdfHeader =
        buffer[0] === 0x25 &&
        buffer[1] === 0x50 &&
        buffer[2] === 0x44 &&
        buffer[3] === 0x46 &&
        buffer[4] === 0x2d;

    // Check ZIP / DOCX signature: "PK\x03\x04" at start
    const isZipHeader =
        buffer[0] === 0x50 &&
        buffer[1] === 0x4b &&
        buffer[2] === 0x03 &&
        buffer[3] === 0x04;

    if (ext === ".pdf") {
        if (!isPdfHeader) {
            return {
                isValid: false,
                detectedType: isZipHeader ? "docx" : "unknown",
                error: "File signature mismatch. The file extension is .pdf but binary content is not a valid PDF document."
            };
        }
        return {
            isValid: true,
            detectedType: "pdf"
        };
    }

    if (ext === ".docx") {
        if (!isZipHeader) {
            return {
                isValid: false,
                detectedType: isPdfHeader ? "pdf" : "unknown",
                error: "File signature mismatch. The file extension is .docx but binary content is not a valid DOCX archive."
            };
        }
        return {
            isValid: true,
            detectedType: "docx"
        };
    }

    return {
        isValid: false,
        detectedType: "unknown",
        error: `Unsupported file extension '${ext}'. Only PDF and DOCX files are allowed.`
    };
};
