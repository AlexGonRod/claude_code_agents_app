<script>
  import { onMount } from 'svelte';
  import ImageInput from './ImageInput.svelte';
  import ImagePreview from './ImagePreview.svelte';
  import InvoiceForm from './InvoiceForm.svelte';
  import SaveButton from './SaveButton.svelte';
  import Spinner from './Spinner.svelte';
  import { appState } from '../stores/app.js';
  import { get } from 'svelte/store';
  import { supabase } from '../lib/supabase.js';
  import { ca } from '../lib/i18n.js';
  const t = ca;

  let imageData = null;
  let invoiceData = {};
  let isProcessing = false;
  let isVerifying = false;
  let error = null;
  let success = null;
  let isAuthenticated = false;
  let checked = false;

  appState.subscribe(($appState) => {
    imageData = $appState.currentImage;
    invoiceData = $appState.invoiceData;
    isProcessing = $appState.isProcessing;
    isVerifying = $appState.isVerifying;
    error = $appState.error;
    success = $appState.success;
    isAuthenticated = $appState.isAuthenticated || false;
  });

  onMount(async () => {
    const { data: { session } } = await supabase.auth.getSession();

    if (!session) {
      window.location.href = '/profile';
      return;
    }

    if (!get(appState).isAuthenticated) {
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

    checked = true;
  });

  function handleImageSelected(event) {
    const images = event.detail?.images || [event.detail];
    appState.update(state => ({
      ...state,
      currentImage: images[0],
      currentImages: images,
      isProcessing: true,
      error: null,
      success: null,
      saved: false
    }));
    simulateOCRProcessing();
  }

  async function doOCRWithRetry(img, apiBase) {
    const base64Data = img.imageData.split(',')[1];
    const maxRetries = 3;
    let lastError = null;
    
    for (let attempt = 0; attempt < maxRetries; attempt++) {
      const response = await fetch(`${apiBase}/ocr/process`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image: base64Data })
      });
      
      if (response.status === 429 || response.status === 503) {
        const waitTime = Math.pow(2, attempt) * 1000;
        console.log(`Rate limited (${response.status}), waiting ${waitTime}ms...`);
        await new Promise(r => setTimeout(r, waitTime));
        lastError = `Rate limited, retry ${attempt + 1}/${maxRetries}`;
        continue;
      }
      
      if (!response.ok) {
        lastError = await response.text();
        throw new Error(lastError || `HTTP ${response.status}`);
      }
      
      return await response.json();
    }
    throw new Error(lastError || 'Max retries exceeded');
  }
  
  async function simulateOCRProcessing() {
    try {
      const currentState = get(appState);
      const images = currentState.currentImages || [currentState.currentImage];
      
      if (!images || images.length === 0) {
        throw new Error('No image data');
      }
      
      const apiBase = import.meta.env.PUBLIC_API_URL || 'http://localhost:8000';
      const allResults = [];
      
      for (const img of images) {
        if (!img?.imageData) continue;
        
        console.log('Processing image...');
        const result = await doOCRWithRetry(img, apiBase);
        console.log('OCR result:', result);
        
        if (result.error || result.detail) {
          throw new Error(result.error || result.detail);
        }
        
        if (!result.raw_text || result.raw_text.trim() === '') {
          throw new Error('No text found in image');
        }
        
        const extractedData = parseInvoiceData(result.raw_text);
        allResults.push(extractedData);
      }
      
      const combinedData = combineInvoiceResults(allResults);
      
      appState.update(s => ({
        ...s,
        invoiceData: combinedData,
        isProcessing: false,
        isVerifying: true
      }));
    } catch (err) {
      console.error('OCR processing error:', err);
      const errorMsg = err.message || 'EXTRACTION FAILED';
      appState.update(state => ({
        ...state,
        error: errorMsg,
        isProcessing: false
      }));
    }
  }

function parseInvoiceData(text) {
    let extractedData = null;
    
    try {
      const cleanJson = text.replace(/```json\n?/g, '').replace(/```\n?/g, '');
      extractedData = JSON.parse(cleanJson);
    } catch (e) {
      extractedData = null;
    }

    const hasValidData = extractedData && (extractedData.proveedor || extractedData.num_de_documento || extractedData.lineas?.length > 0);
    
    if (!extractedData || !hasValidData) {
      const lines = text.split('\n').map(l => l.trim()).filter(l => l);
      let invoiceNumber = '', vendor = '', invoiceDate = '', nif = '', notes = '', lineItems = [];
      
      const isNumericLine = (line) => /^[\d,.]+$/.test(line);
      const isHeaderLine = (line) => /^(KILO|PRECI|IMPORT|TOTAL|UNDS|UDS|PIEZAS|KG|CANT)/i.test(line);
      
      for (let i = 0; i < lines.length; i++) {
        const line = lines[i].trim();
        if (isNumericLine(line) || isHeaderLine(line) || line.length < 4) continue;
        if (line.match(/^(calle|av|plaza|paseo|ctra|tel|nif|cif|fax)/i)) continue;
        
        const nums = [];
        for (let j = i + 1; j < Math.min(i + 5, lines.length); j++) {
          const nextLine = lines[j].trim();
          if (isNumericLine(nextLine)) {
            const val = parseFloat(nextLine.replace(',', '.'));
            if (val > 0) nums.push({ value: val, raw: nextLine });
          } else if (isHeaderLine(nextLine)) {
            continue;
          } else {
            break;
          }
        }
        
        if (nums.length >= 2 && line.length > 5) {
          lineItems.push({
            unit: line,
            quantity: nums[0].value,
            unitPrice: nums[1].value,
            total: nums[2] ? nums[2].value : (nums[0].value * nums[1].value)
          });
        }
      }

      lineItems = lineItems.filter(item => {
        const unit = item.unit.toLowerCase();
        return !unit.includes('cl/') && !unit.includes('av ') && !unit.includes('pl/') &&
               !unit.match(/^\d{5}$/) && !unit.match(/^[a-zà-öø-ÿ]+$/i) &&
               !unit.match(/^[a-z]{2,}\d{6,}$/i) && !unit.match(/^\d{8,}$/i) &&
               item.unit.length > 8 && !item.unit.includes('ALBERT') && !item.unit.includes('CAT');
      });

      const invoiceNumberPatterns = [/N\.O\s*Factura:?\s*([0-9]+[.-]?[0-9]+)/i, /Factura:?\s*#?\s*([0-9]+[.-]?[0-9]+)/i, /#\s*([0-9]+[.-]?[0-9]+)/i];
      const datePatterns = [/(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})/];
      const nifPatterns = [/\b([A-Z]\d{8}[A-Z])\b/i, /(?:NIF|CIF)[:\s]*([A-Z0-9]{9})/i];

      for (const line of lines) {
        if (!invoiceNumber) { for (const pattern of invoiceNumberPatterns) { const m = line.match(pattern); if (m) { invoiceNumber = m[1]; break; }}}
        if (!invoiceDate) { for (const pattern of datePatterns) { const m = line.match(pattern); if (m) { invoiceDate = m[1].replace(/[\/\-\.]/g, '-'); break; }}}
        if (!nif) { for (const pattern of nifPatterns) { const m = line.match(pattern); if (m) { nif = m[1]; break; }}}
      }

      if (!invoiceNumber) {
        for (const line of lines) {
          if (!line.match(/^\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d/) && line.match(/^[0-9.\-]+$/) && line.length > 2 && line.length < 20) {
            invoiceNumber = line;
          }
        }
      }

      for (const line of lines) {
        if (!vendor && line.length > 10 && line.length < 60) {
          const lowerLine = line.toLowerCase();
          if (!lowerLine.includes('invoice') && !lowerLine.includes('total') && !lowerLine.includes('date') &&
              !lowerLine.match(/^\d+$/) && !lowerLine.match(/^[\d\s]+$/) &&
              !lowerLine.match(/^(calle|av|plaza|paseo|ctra|nif|cif|ce€|cee)/i) &&
              !lowerLine.includes('tel') && line !== 'CEE' && line !== 'ALBAR') {
            if (line.includes('DE') || line.includes('SL') || line.includes('SA') || line.includes('Y')) {
              vendor = line;
              break;
            }
          }
        }
      }

      notes = (nif ? `NIF: ${nif} | ` : '') + lines.slice(0, 5).join(' | ');
      const nifFromNotes = notes.match(/NIF[:\s]*([A-Z]?[0-9]{8}[A-Z]?)/i)?.[1] || '';

      if (lineItems.length === 0) lineItems.push({ unit: 'Servei', quantity: 1, unitPrice: 0, total: 0 });
      const grandTotal = lineItems.reduce((sum, item) => sum + (item.total || 0), 0);

      return { invoiceNumber: invoiceNumber || 'N/A', vendor: vendor || 'UNKNOWN', invoiceDate: invoiceDate || new Date().toISOString().split('T')[0], lineItems, total: grandTotal, nif: nifFromNotes || nif, notes };
    }

    return {
      invoiceNumber: extractedData.num_de_documento || '',
      vendor: extractedData.proveedor || '',
      invoiceDate: extractedData.fecha || '',
      nif: extractedData.NIF_CIF || '',
      total: parseFloat(String(extractedData.total).replace(',', '.')) || 0,
      lineItems: (extractedData.lineas || []).map(line => ({
        unit: line.concepto || '',
        quantity: parseFloat(String(line.cantidad).replace(',', '.')) || 1,
        unitPrice: parseFloat(String(line.precio_unitario).replace(',', '.')) || 0,
        total: parseFloat(String(line.importe).replace(',', '.')) || 0
      }))
    };
}

  function combineInvoiceResults(results) {
    if (!results || results.length === 0) return { invoiceNumber: '', vendor: '', invoiceDate: '', lineItems: [], total: 0, nif: '' };
    if (results.length === 1) return results[0];
    
    const invoices = results.map(r => ({ invoiceNumber: r.invoiceNumber || '', vendor: r.vendor || '', invoiceDate: r.invoiceDate || '', nif: r.nif || '', total: r.total || 0, lineItems: r.lineItems || [] }));
    
    const combined = { invoices, invoiceNumber: results[0].invoiceNumber || '', vendor: results[0].vendor || '', invoiceDate: results[0].invoiceDate || '', nif: results[0].nif || '', lineItems: [], total: results[results.length - 1].total || 0 };
    
    for (const result of results) {
      if (result.lineItems?.length > 0) combined.lineItems = combined.lineItems.concat(result.lineItems);
    }
    return combined;
  }

  function handleInvoiceUpdated(event) {
    appState.update(state => ({ ...state, invoiceData: event.detail }));
  }

  async function handleSaveInvoice() {
    appState.update(state => ({ ...state, error: null, success: null }));
    try {
      await new Promise(resolve => setTimeout(resolve, 1500));
      appState.update(state => ({ ...state, success: t.success.savedToDrive, currentImage: null, invoiceData: {}, isVerifying: false }));
    } catch (err) {
      appState.update(state => ({ ...state, error: 'SAVE FAILED' }));
    }
  }

  function resetToCapture() {
    appState.update(state => ({ ...state, currentImage: null, invoiceData: {}, isVerifying: false, error: null, success: null }));
  }
</script>

<div class="w-full">
  {#if isProcessing}
    <div class="flex flex-col items-center justify-center gap-6 py-8">
      <Spinner />
      <h2 class="font-mono text-sm font-semibold text-accent tracking-widest animate-pulse">{t.app.extracting}</h2>
    </div>
  {:else if isVerifying && invoiceData}
    <div class="flex flex-col gap-4">
      <button class="flex items-center gap-1 bg-none border-none text-secondary font-mono text-xs font-medium tracking-wider cursor-pointer" on:click={resetToCapture}>
        <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>
        {t.app.back}
      </button>
      
      <div class="border-2 border overflow-hidden">
        <ImagePreview imageSrc={imageData?.imageData} loading={false} error={null} />
      </div>

      <div class="mt-2">
        <InvoiceForm invoiceData={invoiceData} loading={false} error={error} on:invoice-updated={handleInvoiceUpdated} />
      </div>

      <SaveButton on:save-invoice={handleSaveInvoice} />
    </div>
  {:else}
    <div class="flex flex-col gap-6 pt-6">
      <div class="text-center py-8">
        <div class="w-20 h-20 mx-auto mb-4 text-tertiary animate-bounce">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <rect x="3" y="3" width="18" height="18" rx="2"/>
            <circle cx="12" cy="12" r="3"/>
            <path d="M3 9h2M19 9h2M9 3v2M9 19v2"/>
          </svg>
        </div>
        <h2 class="font-display text-2xl font-bold text-primary tracking-wide mb-1">{t.app.scanInvoice}</h2>
        <p class="text-sm text-secondary">{t.app.selectOrCapture}</p>
      </div>
      
      <ImageInput on:images-selected={handleImageSelected} />
    </div>
  {/if}

  {#if error}
    <div class="fixed top-4 left-1/2 -translate-x-1/2 flex items-center gap-2 px-4 py-2 bg-error text-white border-2 border-error font-mono text-xs font-semibold tracking-wider animate-slide-down z-50">
      <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 8v4M12 16h.01"/></svg>
      {error}
    </div>
  {/if}
</div>

