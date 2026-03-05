import '@testing-library/jest-dom';
import { server } from './mocks/server';
import { beforeAll, afterEach, afterAll } from 'vitest';
//#jsdom doesnt implement scroll into v iew,window alert
window.HTMLElement.prototype.scrollIntoView = vi.fn();
window.alert = vi.fn();

beforeAll(() => server.listen());
afterEach(() => {
                server.resetHandlers();
                vi.restoreAllMocks();
            });
afterAll(() => server.close());