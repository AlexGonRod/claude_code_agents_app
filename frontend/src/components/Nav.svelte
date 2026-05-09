<script>
  import { onMount } from 'svelte';
  import { appState } from '../stores/app.js';
  import { supabase } from '../lib/supabase.js';
  import { ca } from '../lib/i18n.js';
  const t = ca;

  let isAuthenticated = false;

  onMount(async () => {
    const { data: { session } } = await supabase.auth.getSession();
    isAuthenticated = !!session;

    const { data: { subscription } } = supabase.auth.onAuthStateChange((event, session) => {
      isAuthenticated = !!session;
      if (session) {
        appState.update(state => ({
          ...state,
          isAuthenticated: true,
          user: {
            id: session.user.id,
            email: session.user.email,
            name: session.user.user_metadata?.full_name || session.user.email,
            picture: session.user.user_metadata?.avatar_url || null
          }
        }));
      }
    });

    return () => subscription.unsubscribe();
  });
</script>

<nav class="bg-surface-2 border-t border-border fixed bottom-0 left-0 right-0 z-50">
  <ul class="flex w-full justify-around py-2">
    <li class="flex-1 text-center">
      {#if isAuthenticated}
        <a href="/" class="flex flex-col items-center text-tertiary hover:text-secondary transition-colors py-1">
          <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="3" y="3" width="18" height="18" rx="0"/>
            <circle cx="12" cy="12" r="3"/>
          </svg>
          <span class="text-[0.625rem] font-semibold tracking-wider mt-[2px]">{t.nav.scan}</span>
        </a>
      {:else}
        <a href="/profile" class="flex flex-col items-center text-tertiary/40 hover:text-secondary transition-colors py-1">
          <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="3" y="3" width="18" height="18" rx="0"/>
            <circle cx="12" cy="12" r="3"/>
          </svg>
          <span class="text-[0.625rem] font-semibold tracking-wider mt-[2px]">{t.nav.scan}</span>
        </a>
      {/if}
    </li>
    <li class="flex-1 text-center">
      {#if isAuthenticated}
        <a href="/history" class="flex flex-col items-center text-tertiary hover:text-secondary transition-colors py-1">
          <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2"/>
            <path d="M9 3a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2H8V3z"/>
          </svg>
          <span class="text-[0.625rem] font-semibold tracking-wider mt-[2px]">{t.nav.history}</span>
        </a>
      {:else}
        <a href="/profile" class="flex flex-col items-center text-tertiary/40 hover:text-secondary transition-colors py-1">
          <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2"/>
            <path d="M9 3a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2H8V3z"/>
          </svg>
          <span class="text-[0.625rem] font-semibold tracking-wider mt-[2px]">{t.nav.history}</span>
        </a>
      {/if}
    </li>
    <li class="flex-1 text-center">
      <a href="/profile" class="flex flex-col items-center text-tertiary hover:text-secondary transition-colors py-1">
        <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="8" r="4"/>
          <path d="M4 20c0-4 4-6 8-6s8 2 8 6"/>
        </svg>
        <span class="text-[0.625rem] font-semibold tracking-wider mt-[2px]">{t.nav.profile}</span>
      </a>
    </li>
  </ul>
</nav>