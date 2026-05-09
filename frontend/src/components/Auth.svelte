<script>
  import { onMount } from 'svelte';
  import { supabase } from '../lib/supabase.js';
  import { appState } from '../stores/app.js';
  import { ca } from '../lib/i18n.js';
  const t = ca;

  let appStateValue = null;
  let isAuthenticated = false;

  appState.subscribe(value => { appStateValue = value; });

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
      } else {
        appState.update(state => ({
          ...state,
          isAuthenticated: false,
          user: null
        }));
      }
    });

    return () => subscription.unsubscribe();
  });
</script>

{#if appStateValue?.isAuthenticated && appStateValue?.user}
  <div class="flex items-center gap-1 text-secondary">
    {#if appStateValue.user.picture}
      <img src={appStateValue.user.picture} alt="" class="w-5 h-5 rounded-full" />
    {:else}
      <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="8" r="4"/><path d="M4 20c0-4 4-6 8-6s8 2 8 6"/></svg>
    {/if}
    <span class="font-mono text-xs font-medium tracking-wider">{t.auth.connected}</span>
  </div>
{:else}
  <a href="/profile" class="px-3 py-1 border-2 border text-accent-main font-mono text-xs font-semibold tracking-wider hover:bg-accent-main hover:text-surface transition-all">
    {t.auth.connect}
  </a>
{/if}