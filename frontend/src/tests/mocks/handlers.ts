import {http, HttpResponse} from 'msw';

const mockDocuments = [
    { id: '1', name: 'test.pdf', created_at: '2024-01-01T00:00:00' },
  { id: '2', name: 'report.pdf', created_at: '2024-01-02T00:00:00' },
];
export const handlers = [
    // Get documents
    http.get('http://localhost:8000/documents/', () => {
      return HttpResponse.json(mockDocuments);
    }),
  
    // Upload document
    http.post('http://localhost:8000/documents/upload', () => {
      return HttpResponse.json({
        id: '3',
        name: 'uploaded.pdf',
        created_at: '2024-01-03T00:00:00',
      });
    }),
  
    // Delete document
    http.delete('http://localhost:8000/documents/:id', () => {
      return HttpResponse.json({ message: 'Deleted successfully' });
    }),
  
    // Query document
    http.post('http://localhost:8000/documents/query', () => {
      return HttpResponse.json({
        answer: 'This is a test answer.',
        sources: [{ page_number: 1, content: 'Relevant content here.' }],
      });
    }),
  ];