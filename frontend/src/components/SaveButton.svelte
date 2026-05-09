<script>
  import { createEventDispatcher } from 'svelte';
  import { appState } from '../stores/app.js';
  import { showToast } from '../stores/toast.js';
  import { appendInvoiceToSheet, appendJustificacio, saveInvoiceToSupabase } from '../lib/sheets.js';
  import { get } from 'svelte/store';

  const dispatch = createEventDispatcher();
  let loading = false;
  let saved = false;

  appState.subscribe(state => {
    saved = state.saved || false;
  });

  async function handleSave() {
    if (loading || saved) return;
    
    const state = get(appState);
    loading = true;
    
    const invoiceData = state.invoiceData || {};
    
    console.log('=== Saving invoice ===');
    console.log('invoiceData:', invoiceData);
    
    try {
      console.log('Calling /drive/invoices...');
      const invoiceResult = await appendInvoiceToSheet(invoiceData);
      console.log('Invoice result:', invoiceResult);
      
      console.log('Calling /drive/justificacio...');
      const justificacioResult = await appendJustificacio(invoiceData);
      console.log('Justificacio result:', justificacioResult);
      
      if (invoiceResult.success && justificacioResult.success) {
        try {
          console.log('Calling /supabase/invoices...');
          await saveInvoiceToSupabase(invoiceData);
          console.log('Supabase save successful');
        } catch (supabaseErr) {
          console.error('Supabase save error:', supabaseErr);
        }
        
        showToast('GUARDAT A DRIVE', 'success', 3000);
        appState.update(s => ({ ...s, saved: true }));
        dispatch('save-invoice');
      }
    } catch (err) {
      console.error('Save error:', err);
      dispatch('error', { message: err.message });
    } finally {
      loading = false;
    }
  }
</script>

<div class="w-full pt-4">
  <button
    type="button"
    class="w-full flex items-center justify-center gap-2 px-4 py-3 bg-accent-main text-surface border-2 border-accent-main font-mono text-xs font-semibold tracking-wider cursor-pointer shadow-swiss hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-swiss-sm transition-all disabled:bg-success disabled:text-surface disabled:border-success disabled:cursor-not-allowed disabled:shadow-none"
    class:bg-success={saved}
    class:border-success={saved}
    on:click={handleSave}
    disabled={loading || saved}
  >
    {#if loading}
      <span class="w-1.5 h-1.5 bg-surface animate-pulse"></span>
      <span class="w-1.5 h-1.5 bg-surface animate-pulse" style="animation-delay: 0.2s;"></span>
      <span class="w-1.5 h-1.5 bg-surface animate-pulse" style="animation-delay: 0.4s;"></span>
    {:else}
      <span>{saved ? 'SAVED' : 'SAVE TO DRIVE'}</span>
    {/if}
  </button>
</div>

