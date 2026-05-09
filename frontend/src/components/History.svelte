<script>
  import { onMount } from 'svelte';
  import { getInvoicesFromSupabase } from '../lib/sheets.js';
  import InvoiceCard from './InvoiceCard.svelte';
  import { appState } from '../stores/app.js';
  import { supabase } from '../lib/supabase.js';
  import { ca } from '../lib/i18n.js';
  const t = ca;

  let invoices = [];
  let loading = true;
  let error = null;

  onMount(async () => {
    const { data: { session } } = await supabase.auth.getSession();

    if (!session?.user) {
      window.location.href = '/profile';
      return;
    }

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

    try {
      const result = await getInvoicesFromSupabase();
      if (result.success) {
        invoices = result.data || [];
      }
    } catch (err) {
      console.error('Error loading invoices:', err);
      error = err.message;
    } finally {
      loading = false;
    }

    const { data: { subscription } } = supabase.auth.onAuthStateChange((event, session) => {
      if (!session?.user) {
        window.location.href = '/profile';
      }
    });

    return () => subscription.unsubscribe();
  });
</script>

<div class="max-w-[600px] mx-auto px-4">
  <h1 class="font-mono text-xl font-semibold mb-4 text-primary tracking-widest">{t.history.title}</h1>

  {#if loading}
    <div class="flex justify-center gap-2 py-8">
      <span class="w-2 h-2 bg-accent-main"></span>
      <span class="w-2 h-2 bg-accent-main"></span>
      <span class="w-2 h-2 bg-accent-main"></span>
    </div>
  {:else if error}
    <div class="text-error font-mono text-xs">{error}</div>
  {:else if invoices.length === 0}
    <div class="text-center text-secondary py-8 font-mono text-xs tracking-widest">{t.history.empty}</div>
  {:else}
    <div class="flex flex-col gap-2">
      {#each invoices as invoice}
        <InvoiceCard {invoice} />
      {/each}
    </div>
  {/if}
</div>

