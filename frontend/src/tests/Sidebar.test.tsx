import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Sidebar } from '../components/Sidebar';
import type { Document } from '../types';

const mockDocuments: Document[] = [
  { id: '1', name: 'test.pdf', created_at: '2024-01-01T00:00:00' },
  { id: '2', name: 'report.pdf', created_at: '2024-01-02T00:00:00' },
];

describe('Sidebar', () => {
  const defaultProps = {
    documents: mockDocuments,
    isLoading: false,
    isUploading: false,
    error: null,
    onUpload: vi.fn(),
    onDelete: vi.fn(),
  };

  it('renders document list', () => {
    render(<Sidebar {...defaultProps} />);
    expect(screen.getByText(/test.pdf/)).toBeInTheDocument();
    expect(screen.getByText(/report.pdf/)).toBeInTheDocument();
  });

  it('shows loading state', () => {
    render(<Sidebar {...defaultProps} isLoading={true} documents={[]} />);
    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });

  it('shows empty state when no documents', () => {
    render(<Sidebar {...defaultProps} documents={[]} />);
    expect(screen.getByText(/No documents yet/)).toBeInTheDocument();
  });

  it('shows error message when error exists', () => {
    render(<Sidebar {...defaultProps} error="Failed to upload document." />);
    expect(screen.getByText('Failed to upload document.')).toBeInTheDocument();
  });

  it('shows document count', () => {
    render(<Sidebar {...defaultProps} />);
    expect(screen.getByText(/Documents \(2\)/)).toBeInTheDocument();
  });
  it('calls onDelete when delete is confirmed', async () => {
    const onDelete = vi.fn();
    vi.spyOn(window, 'confirm').mockReturnValueOnce(true); // only returns true once
  
    render(<Sidebar {...defaultProps} onDelete={onDelete} />);
  
    const deleteButtons = screen.getAllByTitle('Delete document');
    await userEvent.click(deleteButtons[0]);
  
    expect(onDelete).toHaveBeenCalledWith('1');
  });
  
  it('does not call onDelete when delete is cancelled', async () => {
    const onDelete = vi.fn();
    vi.spyOn(window, 'confirm').mockReturnValueOnce(false); // only returns false once
  
    render(<Sidebar {...defaultProps} onDelete={onDelete} />);
  
    const deleteButtons = screen.getAllByTitle('Delete document');
    await userEvent.click(deleteButtons[0]);
  
    expect(onDelete).not.toHaveBeenCalled();
  });
});