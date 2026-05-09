<script>
  import { ca } from '../lib/i18n.js';
  const t = ca;
  export let invoice;
  
  function formatDate(dateStr) {
    if (!dateStr) return '-';
    return new Date(dateStr).toLocaleDateString('ca-ES');
  }
  
  function formatCurrency(amount) {
    if (!amount) return '€0.00';
    return new Intl.NumberFormat('ca-ES', { style: 'currency', currency: 'EUR' }).format(amount);
  }
</script>

<a href="/history/{invoice.id}" class="block bg-surface-2 border-2 border no-underline text-inherit hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-swiss-sm transition-all">
  <div class="flex justify-between items-center p-3 border-b-2 border">
    <span class="font-mono text-sm font-semibold text-primary tracking-wide">{invoice.vendor || '-'}</span>
  </div>
  <div class="p-3 flex flex-col gap-1">
    <div class="flex justify-between items-center">
      <span class="font-mono text-xs uppercase tracking-widest text-secondary">{t.invoice.date}</span>
      <span class="font-mono text-sm text-primary">{formatDate(invoice.invoice_date)}</span>
    </div>
    <div class="flex justify-between items-center">
      <span class="font-mono text-xs uppercase tracking-widest text-secondary">{t.invoice.total}</span>
      <span class="font-mono text-sm text-primary font-medium">{formatCurrency(invoice.total)}</span>
    </div>
    {#if invoice.nif}
      <div class="flex justify-between items-center">
        <span class="font-mono text-xs uppercase tracking-widest text-secondary">{t.invoice.nif}</span>
        <span class="font-mono text-sm text-primary">{invoice.nif}</span>
      </div>
    {/if}
    <span class="flex justify-end font-mono text-xs font-semibold tracking-widest text-success px-1">{t.invoice.saved}</span>
  </div>
</a>