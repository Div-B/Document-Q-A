import { describe, it, expect } from 'vitest';
import { getDocuments, deleteDocument } from '../services/api';

describe('api service', () => {
  it('getDocuments returns list of documents', async () => {
    const docs = await getDocuments();
    expect(docs).toHaveLength(2);
    expect(docs[0].name).toBe('test.pdf');
  });

  it('deleteDocument resolves without error', async () => {
    await expect(deleteDocument('1')).resolves.not.toThrow();
  });
});