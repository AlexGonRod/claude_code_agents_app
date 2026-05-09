<script>
  import { createEventDispatcher } from 'svelte';
  import { ca } from '../lib/i18n.js';
  const t = ca;
  const dispatch = createEventDispatcher();
  let fileInput;
  let loading = false;
  let error = null;
  let isDragOver = false;
  let selectedFiles = [];

  async function handleFileChange(event) {
    const files = event.target.files;
    if (!files || files.length === 0) return;
    loading = true;
    error = null;
    selectedFiles = [];
    try {
      const maxFiles = 5;
      const fileCount = Math.min(files.length, maxFiles);
      for (let i = 0; i < fileCount; i++) {
        const file = files[i];
        if (!file.type.startsWith('image/')) throw new Error('INVALID FILE');
        if (file.size > 10 * 1024 * 1024) throw new Error('FILE TOO LARGE');
        const imageData = await readFileAsBase64(file);
        selectedFiles.push({ file, imageData, name: file.name, size: file.size, type: file.type });
      }
      dispatch('images-selected', { images: selectedFiles });
    } catch (err) { error = err.message; }
    finally { loading = false; if (fileInput) fileInput.value = ''; }
  }

  function readFileAsBase64(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result);
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
  }

  function handleClick() { fileInput?.click(); }
  function handleDragOver(event) { event.preventDefault(); isDragOver = true; }
  function handleDragLeave(event) { event.preventDefault(); isDragOver = false; }
  function handleDrop(event) {
    event.preventDefault();
    isDragOver = false;
    const files = event.dataTransfer?.files;
    if (files && files.length > 0) {
      const dt = new DataTransfer();
      for (let i = 0; i < Math.min(files.length, 5); i++) dt.items.add(files[i]);
      fileInput.files = dt.files;
      fileInput.dispatchEvent(new Event('change'));
    }
  }
</script>

<div class="flex flex-col gap-3">
  <input type="file" accept="image/*" capture="environment" multiple on:change={handleFileChange} bind:this={fileInput} class="hidden" />

  <button type="button" class="w-full aspect-[4/3] max-h-72 bg-surface-2 border-2 {isDragOver ? 'border-accent-main' : 'border'} cursor-pointer transition-all hover:border-accent-main active:scale-[0.98] disabled:opacity-60 disabled:cursor-not-allowed flex items-center justify-center" class:border-dashed={!loading} class:border-solid={loading || isDragOver} on:click={handleClick} on:dragover={handleDragOver} on:dragleave={handleDragLeave} on:drop={handleDrop} disabled={loading}>
    {#if loading}
      <div class="flex flex-col items-center gap-3">
        <div class="flex items-end gap-1 h-10">
          <div class="w-1 bg-accent-main animate-pulse"></div>
          <div class="w-1 bg-accent-main animate-pulse" style="animation-delay: 0.2s;"></div>
          <div class="w-1 bg-accent-main animate-pulse" style="animation-delay: 0.4s;"></div>
        </div>
        <span class="font-mono text-sm text-accent-main">{t.capture.loading}</span>
      </div>
    {:else}
      <div class="flex flex-col items-center gap-3">
        <div class="w-14 h-14 text-tertiary transition-colors hover:text-accent-main hover:scale-110">
          <svg class="w-full h-full" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="3" y="3" width="18" height="18" rx="2"/>
            <circle cx="12" cy="12" r="3"/>
            <path d="M3 9h2M19 9h2M9 3v2M9 19v2"/>
          </svg>
        </div>
        <span class="font-mono text-sm font-semibold text-secondary tracking-widest">{t.capture.title}</span>
      </div>
    {/if}
  </button>

  {#if error}
    <div class="flex items-center gap-2 text-error font-mono text-xs font-semibold tracking-wider">
      <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 8v4M12 16h.01"/></svg>
      {error}
    </div>
  {/if}
</div>

