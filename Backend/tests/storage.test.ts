import { describe, it, after } from "node:test";
import assert from "node:assert/strict";
import fs from "fs";
import {
    generateSafeStorageKey,
    saveFileToStorage,
    getStoredFilePath,
    deleteStoredFile
} from "../src/services/storage.service";

describe("Storage Service & Path Traversal Protections", () => {
    let createdKey: string;

    after(async () => {
        if (createdKey) {
            await deleteStoredFile(createdKey);
        }
    });

    it("should generate a sanitized server-side filename with safe extension", () => {
        const untrustedName = "../../../malicious/path/my_resume.pdf";
        const safeKey = generateSafeStorageKey(untrustedName);

        assert.ok(safeKey.startsWith("resume_"));
        assert.ok(safeKey.endsWith(".pdf"));
        assert.ok(!safeKey.includes("/"));
        assert.ok(!safeKey.includes("\\"));
        assert.ok(!safeKey.includes(".."));
    });

    it("should save buffer to private local storage and retrieve absolute path", async () => {
        const testContent = Buffer.from("Temporary test content for storage validation");
        createdKey = generateSafeStorageKey("candidate_sample.pdf");

        const saved = await saveFileToStorage(testContent, createdKey);
        assert.ok(fs.existsSync(saved.absolutePath));

        const resolvedPath = getStoredFilePath(createdKey);
        assert.strictEqual(resolvedPath, saved.absolutePath);

        const readBack = await fs.promises.readFile(resolvedPath);
        assert.deepStrictEqual(readBack, testContent);
    });

    it("should delete stored file cleanly", async () => {
        const deleted = await deleteStoredFile(createdKey);
        assert.strictEqual(deleted, true);

        assert.throws(() => {
            getStoredFilePath(createdKey);
        });

        // Clear reference so after hook doesn't re-delete
        createdKey = "";
    });
});
