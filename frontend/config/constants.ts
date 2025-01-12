export const FILE_UPLOAD_CONFIG = {
  MAX_FILE_SIZE_MB: Number(process.env.NEXT_PUBLIC_MAX_FILE_SIZE_MB || '50'),
  ALLOWED_FILE_TYPES: (process.env.NEXT_PUBLIC_ALLOWED_FILE_TYPES || 'image/*,application/pdf,text/*').split(','),
} as const; 