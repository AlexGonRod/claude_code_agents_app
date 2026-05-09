<script>
  import { toast } from '../stores/toast.js';
</script>

{#if $toast.visible && $toast.message}
  <div class="fixed top-0 left-0 right-0 z-[100] flex justify-center p-4">
    <div class="w-full max-w-[500px] {$toast.type === 'success' ? 'bg-surface-2 border-success text-success' : 'bg-surface-2 border-error text-error'} border-2 px-4 py-2 shadow-swiss">
      <span class="font-mono text-xs font-semibold tracking-widest block text-center">{$toast.message}</span>
    </div>
  </div>
{/if}