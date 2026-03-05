import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { UploadButton } from '../components/UploadButton';
import toast from 'react-hot-toast';

vi.mock('react-hot-toast', () => ({
  default: {
    error: vi.fn(),
    success: vi.fn(),
    loading: vi.fn(),
  },
}));

describe('UploadButton', () => {
  it('renders upload button', () => {
    render(<UploadButton onUpload={vi.fn()} isUploading={false} />);
    expect(screen.getByText('Upload PDF')).toBeInTheDocument();
  });

  it('shows uploading state when isUploading is true', () => {
    render(<UploadButton onUpload={vi.fn()} isUploading={true} />);
    expect(screen.getByText('Uploading...')).toBeInTheDocument();
  });

  it('disables button when uploading', () => {
    render(<UploadButton onUpload={vi.fn()} isUploading={true} />);
    expect(screen.getByRole('button')).toBeDisabled();
  });

  it('calls onUpload with file when pdf is selected', async () => {
    const onUpload = vi.fn();
    render(<UploadButton onUpload={onUpload} isUploading={false} />);

    const file = new File(['dummy content'], 'test.pdf', { type: 'application/pdf' });
    const input = document.querySelector('input[type="file"]') as HTMLInputElement;

    await userEvent.upload(input, file);
    expect(onUpload).toHaveBeenCalledWith(file);
  });

  it('rejects non-pdf files and shows toast error', () => {
    const onUpload = vi.fn();
    render(<UploadButton onUpload={onUpload} isUploading={false} />);

    const file = new File(['dummy content'], 'test.png', { type: 'image/png' });
    const input = document.querySelector('input[type="file"]') as HTMLInputElement;

    Object.defineProperty(input, 'files', {
      value: [file],
      configurable: true,
    });
    fireEvent.change(input);

    expect(onUpload).not.toHaveBeenCalled();
    expect(toast.error).toHaveBeenCalledWith('Only PDF files are allowed.');
  });
});