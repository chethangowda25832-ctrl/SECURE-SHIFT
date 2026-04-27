import { createClient } from '@supabase/supabase-js';
import { PUBLIC_SUPABASE_URL, PUBLIC_SUPABASE_ANON_KEY } from '$env/static/public';

const isPlaceholder =
  !PUBLIC_SUPABASE_URL ||
  PUBLIC_SUPABASE_URL.includes('your-project') ||
  PUBLIC_SUPABASE_URL.includes('xxxx') ||
  !PUBLIC_SUPABASE_ANON_KEY ||
  PUBLIC_SUPABASE_ANON_KEY === 'your_supabase_anon_key';

if (isPlaceholder) {
  console.warn(
    '⚠️  Supabase credentials are placeholders. Auth will not work.\n' +
    '   Update PUBLIC_SUPABASE_URL and PUBLIC_SUPABASE_ANON_KEY in frontend/.env'
  );
}

// Use dummy-but-valid-shaped values so createClient doesn't throw
const supabaseUrl = isPlaceholder ? 'https://placeholder.supabase.co' : PUBLIC_SUPABASE_URL;
const supabaseKey = isPlaceholder
  ? 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJyb2xlIjoiYW5vbiJ9.placeholder'
  : PUBLIC_SUPABASE_ANON_KEY;

export const supabase = createClient(supabaseUrl, supabaseKey, {
  auth: {
    persistSession: true,
    autoRefreshToken: true,
    detectSessionInUrl: true,
  },
});
