import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ChatWindow } from '../components/ChatWindow';
import type { Message } from '../types';

const mockMessages: Message[] = [
  { id: '1', role: 'user', content: 'What is this document about?' },
  { id: '2', role: 'assistant', content: 'This document is about machine learning.' },
];

describe('ChatWindow', () => {
  const defaultProps = {
    messages: [],
    isLoading: false,
    error: null,
    onSend: vi.fn(),
    onClear: vi.fn(),
  };

  it('shows empty state when no messages', () => {
    render(<ChatWindow {...defaultProps} />);
    expect(screen.getByText(/Ask anything about your documents/)).toBeInTheDocument();
  });

  it('renders messages correctly', () => {
    render(<ChatWindow {...defaultProps} messages={mockMessages} />);
    expect(screen.getByText('What is this document about?')).toBeInTheDocument();
    expect(screen.getByText('This document is about machine learning.')).toBeInTheDocument();
  });

  it('calls onSend when send button is clicked', async () => {
    const onSend = vi.fn();
    render(<ChatWindow {...defaultProps} onSend={onSend} />);

    const textarea = screen.getByPlaceholderText(/Ask a question/);
    await userEvent.type(textarea, 'What is this about?');
    await userEvent.click(screen.getByText('Send'));

    expect(onSend).toHaveBeenCalledWith('What is this about?');
  });

  it('calls onSend when Enter is pressed', async () => {
    const onSend = vi.fn();
    render(<ChatWindow {...defaultProps} onSend={onSend} />);

    const textarea = screen.getByPlaceholderText(/Ask a question/);
    await userEvent.type(textarea, 'What is this about?{Enter}');

    expect(onSend).toHaveBeenCalledWith('What is this about?');
  });

  it('does not send empty messages', async () => {
    const onSend = vi.fn();
    render(<ChatWindow {...defaultProps} onSend={onSend} />);

    await userEvent.click(screen.getByText('Send'));

    expect(onSend).not.toHaveBeenCalled();
  });

  it('disables input when loading', () => {
    render(<ChatWindow {...defaultProps} isLoading={true} />);
    expect(screen.getByPlaceholderText(/Ask a question/)).toBeDisabled();
  });

  it('shows error message when error exists', () => {
    render(<ChatWindow {...defaultProps} error="Failed to get answer." />);
    expect(screen.getByText('Failed to get answer.')).toBeInTheDocument();
  });

  it('shows clear button when messages exist', () => {
    render(<ChatWindow {...defaultProps} messages={mockMessages} />);
    expect(screen.getByText('Clear chat')).toBeInTheDocument();
  });

  it('calls onClear when clear button is clicked', async () => {
    const onClear = vi.fn();
    render(<ChatWindow {...defaultProps} messages={mockMessages} onClear={onClear} />);

    await userEvent.click(screen.getByText('Clear chat'));
    expect(onClear).toHaveBeenCalled();
  });
});