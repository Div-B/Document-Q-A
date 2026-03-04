export const sanitizeFileName = (name: string): string => {
    return name
      .replace(/[<>'"]/g, "")
      .trim()
      .slice(0, 255);
  };