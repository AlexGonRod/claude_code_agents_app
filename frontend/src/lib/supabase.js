import { createClient } from '@supabase/supabase-js';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || 'https://adcpdkadrnzjcugumseo.supabase.co';
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || 'sb_publishable_PDwx0EdqA81zq76SP_PUBA_rRphBq4K';
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const supabase = createClient(supabaseUrl, supabaseAnonKey);

export async function signInWithPassword(email, password) {
  return await supabase.auth.signInWithPassword({
    email: email,
    password: password
  });
}

export async function signUp(email, password) {
  return await supabase.auth.signUp({
    email: email,
    password: password
  });
}

export async function signOut() {
  const { error } = await supabase.auth.signOut();
  if (error) throw error;
}

export async function getCurrentUser() {
  const { data: { user } } = await supabase.auth.getUser();
  return user;
}

export async function getSession() {
  const { data: { session } } = await supabase.auth.getSession();
  return session;
}

export async function verifyTokenWithBackend() {
  const session = await getSession();
  if (!session?.access_token) {
    return null;
  }

  try {
    const response = await fetch(`${API_URL}/auth/verify`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ token: session.access_token })
    });

    if (!response.ok) {
      return null;
    }

    return await response.json();
  } catch (error) {
    console.error('Backend verification failed:', error);
    return null;
  }
}

export async function onAuthStateChange(callback) {
  return supabase.auth.onAuthStateChange((event, session) => {
    callback(event, session);
  });
}