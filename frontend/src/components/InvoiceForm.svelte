<script>
  import { createEventDispatcher } from 'svelte';
  import { ca } from '../lib/i18n.js';
  const dispatch = createEventDispatcher();
  export let invoiceData = { invoiceNumber: '', vendor: '', invoiceDate: '', lineItems: [], total: 0, nif: '', notes: '' };
  export let loading = false;
  export let error = null;
  const t = ca;

  let localInvoiceData = { ...invoiceData };
  let isEditing = false;

  $: if (invoiceData) localInvoiceData = { ...invoiceData };

  function updateLineItem(index, field, value) {
    localInvoiceData.lineItems[index][field] = value;
    if (field === 'quantity' || field === 'unitPrice') {
      const item = localInvoiceData.lineItems[index];
      item.total = (item.quantity || 0) * (item.unitPrice || 0);
    }
    localInvoiceData.total = localInvoiceData.lineItems.reduce((sum, item) => sum + (item.total || 0), 0);
    dispatchUpdate();
  }

  function updateField(field, value) {
    localInvoiceData[field] = value;
    dispatchUpdate();
  }

  function addLineItem() {
    localInvoiceData.lineItems = [...localInvoiceData.lineItems, { unit: '', quantity: 1, unitPrice: 0, total: 0 }];
    dispatchUpdate();
  }

  function removeLineItem(index) {
    localInvoiceData.lineItems = localInvoiceData.lineItems.filter((_, i) => i !== index);
    localInvoiceData.total = localInvoiceData.lineItems.reduce((sum, item) => sum + (item.total || 0), 0);
    dispatchUpdate();
  }

  function dispatchUpdate() { dispatch('invoice-updated', localInvoiceData); }
  function toggleEdit() { isEditing = !isEditing; }
</script>

<div class="flex flex-col gap-3">
  {#if error}
    <div class="flex items-center gap-2 p-3 bg-error text-white border-2 border-error font-mono text-xs font-semibold tracking-wider">
      <svg class="w-4 h-4 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 8v4M12 16h.01"/></svg>
      {error}
    </div>
  {/if}

  <div class="bg-surface-2 border-2 border p-3">
    <div class="flex justify-between items-center mb-3">
      <span class="font-mono text-xs font-semibold uppercase tracking-widest text-tertiary">{t.document.title}</span>
      <button class="bg-none border-none text-accent-main font-mono text-xs font-semibold tracking-wider cursor-pointer" on:click={toggleEdit}>{isEditing ? t.document.done : t.document.edit}</button>
    </div>
    <div class="flex flex-col gap-2">
      <div>
        <label class="font-mono text-xs uppercase tracking-widest text-secondary block mb-1">{t.document.number}</label>
        {#if isEditing}
          <input type="text" bind:value={localInvoiceData.invoiceNumber} on:input={(e) => updateField('invoiceNumber', e.target.value)} placeholder={t.placeholders.invoiceNumber} disabled={loading} class="w-full p-2 bg-surface-3 border-2 border text-primary font-mono text-sm" />
        {:else}
          <div class="font-mono text-sm text-primary">{localInvoiceData.invoiceNumber || '—'}</div>
        {/if}
      </div>
      <div>
        <label class="font-mono text-xs uppercase tracking-widest text-secondary block mb-1">{t.document.vendor}</label>
        {#if isEditing}
          <input type="text" bind:value={localInvoiceData.vendor} on:input={(e) => updateField('vendor', e.target.value)} placeholder={t.placeholders.vendorName} disabled={loading} class="w-full p-2 bg-surface-3 border-2 border text-primary font-mono text-sm" />
        {:else}
          <div class="font-mono text-sm text-primary">{localInvoiceData.vendor || '—'}</div>
        {/if}
      </div>
      <div>
        <label class="font-mono text-xs uppercase tracking-widest text-secondary block mb-1">{t.document.date}</label>
        {#if isEditing}
          <input type="date" bind:value={localInvoiceData.invoiceDate} on:input={(e) => updateField('invoiceDate', e.target.value)} disabled={loading} class="w-full p-2 bg-surface-3 border-2 border text-primary font-mono text-sm" />
        {:else}
          <div class="font-mono text-sm text-primary">{localInvoiceData.invoiceDate || '—'}</div>
        {/if}
      </div>
    </div>
  </div>

  <div class="bg-surface-2 border-2 border p-3">
    <div class="flex justify-between items-center mb-3">
      <span class="font-mono text-xs font-semibold uppercase tracking-widest text-tertiary">{t.lines.title}</span>
      {#if isEditing}
        <button class="bg-none border-none text-accent-main font-mono text-xs font-semibold tracking-wider cursor-pointer" on:click={addLineItem}>{t.lines.add}</button>
      {/if}
    </div>
    {#each localInvoiceData.lineItems || [] as item, index}
      <div class="mb-3 pb-3 border-b-2 border last:mb-0 last:pb-0 last:border-b-0">
        <div class="flex items-center gap-2">
          <div class="flex-1">
            <label class="font-mono text-xs uppercase tracking-widest text-secondary block mb-1">{t.lines.unit}</label>
            {#if isEditing}
              <input type="text" value={item.unit} on:input={(e) => updateLineItem(index, 'unit', e.target.value)} placeholder={t.lines.description} disabled={loading} class="w-full p-2 bg-surface-3 border-2 border text-primary font-mono text-sm" />
            {:else}
              <div class="font-mono text-sm text-primary">{item.unit || '—'}</div>
            {/if}
          </div>
          {#if isEditing}
            <button class="text-error font-mono text-lg font-semibold cursor-pointer mt-4" on:click={() => removeLineItem(index)}>×</button>
          {/if}
        </div>
        <div class="grid grid-cols-2 gap-2 mt-2">
          <div>
            <label class="font-mono text-xs uppercase tracking-widest text-secondary block mb-1">{t.lines.quantity}</label>
            {#if isEditing}
              <input type="number" value={item.quantity} on:input={(e) => updateLineItem(index, 'quantity', parseFloat(e.target.value) || 0)} min="0" step="1" disabled={loading} class="w-full p-2 bg-surface-3 border-2 border text-primary font-mono text-sm" />
            {:else}
              <div class="font-mono text-sm text-primary">{item.quantity || '0'}</div>
            {/if}
          </div>
          <div>
            <label class="font-mono text-xs uppercase tracking-widest text-secondary block mb-1">{t.lines.unitPrice}</label>
            {#if isEditing}
              <input type="number" value={item.unitPrice} on:input={(e) => updateLineItem(index, 'unitPrice', parseFloat(e.target.value) || 0)} min="0" step="0.01" disabled={loading} class="w-full p-2 bg-surface-3 border-2 border text-primary font-mono text-sm" />
            {:else}
              <div class="font-mono text-sm text-primary">€{item.unitPrice?.toFixed(2) || '0.00'}</div>
            {/if}
          </div>
        </div>
        <div class="text-right mt-2">
          <span class="font-mono text-sm text-accent-main font-semibold">€{item.total?.toFixed(2) || '0.00'}</span>
        </div>
      </div>
    {/each}
  </div>

  <div class="bg-surface-2 border-2 border p-3">
    <div class="flex justify-between items-center">
      <span class="font-mono text-xs font-semibold uppercase tracking-widest text-tertiary">{t.total.label}</span>
      <span class="font-mono text-lg text-accent-main font-semibold">€{(localInvoiceData.total || 0).toFixed(2)}</span>
    </div>
  </div>

  <div class="bg-surface-2 border-2 border p-3">
    <div class="mb-2">
      <span class="font-mono text-xs font-semibold uppercase tracking-widest text-tertiary">{t.notes.label}</span>
    </div>
    {#if isEditing}
      <textarea bind:value={localInvoiceData.notes} on:input={(e) => updateField('notes', e.target.value)} placeholder={t.notes.placeholder} rows="2" disabled={loading} class="w-full p-2 bg-surface-3 border-2 border text-primary font-mono text-sm"></textarea>
    {:else}
      <div class="font-mono text-sm text-secondary">{localInvoiceData.notes || t.notes.empty}</div>
    {/if}
  </div>
</div>

