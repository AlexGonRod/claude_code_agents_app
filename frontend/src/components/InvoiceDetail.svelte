<script>
  import { onMount } from 'svelte';
  import { getInvoiceById } from '../lib/sheets.js';
  import { ca } from '../lib/i18n.js';
  const t = ca;

  export let id;

  let invoice = null;
  let loading = true;
  let error = null;

  onMount(async () => {
    try {
      const result = await getInvoiceById(id);
      if (result.success) {
        invoice = result.data;
      }
    } catch (err) {
      console.error('Error loading invoice:', err);
      error = err.message;
    } finally {
      loading = false;
    }
  });

  const fields = [
    { label: 'NUMERO', key: 'invoice_number', format: v => v || '-' },
    { label: 'FECHA', key: 'invoice_date', format: v => v ? new Date(v).toLocaleDateString('ca-ES') : '-' },
    { label: 'TOTAL', key: 'total', format: v => v ? new Intl.NumberFormat('ca-ES', { style: 'currency', currency: 'EUR' }).format(v) : '€0.00' },
    { label: 'NIF', key: 'nif', format: v => v || '-' },
    { label: 'PROVEEDOR', key: 'vendor', format: v => v || '-' }
  ];
</script>

<div class="max-w-[600px] mx-auto px-4">
  <a href="/history" class="inline-block mb-4 text-accent-main no-underline font-mono text-xs font-semibold tracking-wider">← {t.detail.back}</a>

  {#if loading}
    <div class="flex justify-center gap-2 py-8">
      <span class="w-2 h-2 bg-accent-main"></span>
    </div>
  {:else if error}
    <div class="text-error font-mono text-xs">{error}</div>
  {:else if invoice}
    <div class="font-mono text-xl font-semibold mb-4 text-primary tracking-wide">{invoice.vendor || 'FACTURA'}</div>

    <div class="grid grid-cols-2 gap-2">
      {#each fields as field}
        <div class="bg-surface-2 border-2 border p-3 flex flex-col gap-1">
          <span class="font-mono text-xs uppercase tracking-widest text-secondary">{field.label}</span>
          <span class="font-mono text-sm text-primary font-medium">{field.format(invoice[field.key])}</span>
        </div>
      {/each}
    </div>

    {#if invoice.line_items?.length}
      <div class="mt-4">
        <div class="font-mono text-xs uppercase tracking-widest text-secondary mb-2">{t.detail.lines}</div>
        <div class="flex flex-col gap-1">
          {#each invoice.line_items as item}
            <div class="bg-surface-2 border-2 border p-2 grid grid-cols-[1fr_auto_auto] gap-3 items-center">
              <span class="font-mono text-sm text-primary">{item.description || '-'}</span>
              <span class="font-mono text-xs text-secondary">{item.quantity} × {item.unit_price?.toFixed(2)}€</span>
              <span class="font-mono text-sm text-primary text-right font-medium">{item.total?.toFixed(2)}€</span>
            </div>
          {/each}
        </div>
      </div>
    {/if}
  {/if}
</div>

