<script>
  import { ca } from '../lib/i18n.js';
  const t = ca;
  export let imageSrc = null;
  export let loading = false;
  export let error = null;
</script>

<div class="w-full aspect-[4/3] max-h-60 bg-surface-2 border-2 border overflow-hidden relative">
  {#if loading}
    <div class="w-full h-full flex flex-col items-center justify-center gap-3 text-tertiary font-mono text-xs font-medium tracking-wider">
      <div class="flex items-end gap-1 h-8">
        <div class="w-1 bg-accent-main border-2 border" style="height: 12px; animation: pulse 0.8s infinite;"></div>
        <div class="w-1 bg-accent-main border-2 border" style="height: 24px; animation: pulse 0.8s infinite 0.2s;"></div>
        <div class="w-1 bg-accent-main border-2 border" style="height: 18px; animation: pulse 0.8s infinite 0.4s;"></div>
      </div>
      <span class="animate-pulse">{t.preview.loading}</span>
    </div>
  {:else if error}
    <div class="w-full h-full flex flex-col items-center justify-center gap-3 text-error font-mono text-xs font-medium tracking-wider">
      <svg class="w-8 h-8" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 8v4M12 16h.01"/></svg>
      <span>{error}</span>
    </div>
  {:else if imageSrc}
    <div class="w-full h-full relative">
      <img src={imageSrc} alt="Invoice preview" class="w-full h-full object-contain bg-surface" />
      <div class="absolute inset-0 pointer-events-none bg-gradient-to-t from-black/30 to-transparent"></div>
      <div class="absolute top-2 left-2 w-3 h-3 border-2 border-accent-main"></div>
      <div class="absolute top-2 right-2 w-3 h-3 border-2 border-accent-main"></div>
      <div class="absolute bottom-2 left-2 w-3 h-3 border-2 border-accent-main"></div>
      <div class="absolute bottom-2 right-2 w-3 h-3 border-2 border-accent-main"></div>
    </div>
  {:else}
    <div class="w-full h-full flex flex-col items-center justify-center gap-3 text-tertiary font-mono text-xs font-medium tracking-wider">
      <svg class="w-12 h-12 opacity-50" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
        <rect x="3" y="3" width="18" height="18" rx="2"/>
        <circle cx="8.5" cy="8.5" r="1.5"/>
        <path d="M21 15l-5-5L5 21"/>
      </svg>
      <span>{t.preview.empty}</span>
    </div>
  {/if}
</div>

