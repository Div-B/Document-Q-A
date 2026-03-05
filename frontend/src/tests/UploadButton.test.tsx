import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { UploadButton } from '../components/UploadButton';

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

  it('rejects non-pdf files', () => {
    const onUpload = vi.fn();
    const alertMock = vi.spyOn(window, 'alert').mockImplementation(() => {});
    render(<UploadButton onUpload={onUpload} isUploading={false} />);

    const file = new File(['dummy content'], 'test.png', { type: 'image/png' });
    const input = document.querySelector('input[type="file"]') as HTMLInputElement;

    // Use fireEvent to bypass the accept attribute filter
    Object.defineProperty(input, 'files', {
      value: [file],
      configurable: true,
    });
    fireEvent.change(input);

    expect(onUpload).not.toHaveBeenCalled();
    expect(alertMock).toHaveBeenCalledWith('Only PDF files are allowed.');
  });
});