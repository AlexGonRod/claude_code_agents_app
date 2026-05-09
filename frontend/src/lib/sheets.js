const API_BASE = import.meta.env.PUBLIC_API_URL || 'http://localhost:8000';

export async function appendInvoiceToSheet(invoiceData) {
  console.log('>>> appendInvoiceToSheet sending:', invoiceData);
  
  const response = await fetch(`${API_BASE}/drive/invoices`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(invoiceData)
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(error || `HTTP ${response.status}`);
  }

  return await response.json();
}

export async function appendJustificacio(invoiceData) {
  console.log('>>> appendJustificacio sending:', { invoiceNumber: invoiceData.invoiceNumber, vendor: invoiceData.vendor, invoiceDate: invoiceData.invoiceDate, nif: invoiceData.nif, total: invoiceData.total });
  
  // If has multiple line items from different invoices, save each separately
  if (invoiceData.invoices && invoiceData.invoices.length > 1) {
    const results = [];
    for (const inv of invoiceData.invoices) {
      const response = await fetch(`${API_BASE}/drive/justificacio`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          invoiceNumber: inv.invoiceNumber,
          vendor: inv.vendor,
          invoiceDate: inv.invoiceDate,
          nif: inv.nif || null,
          total: inv.total
        })
      });
      if (!response.ok) {
        const error = await response.text();
        throw new Error(error || `HTTP ${response.status}`);
      }
      results.push(await response.json());
    }
    return results;
  }
  
  // Single invoice
  const response = await fetch(`${API_BASE}/drive/justificacio`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      invoiceNumber: invoiceData.invoiceNumber,
      vendor: invoiceData.vendor,
      invoiceDate: invoiceData.invoiceDate,
      nif: invoiceData.nif || null,
      total: invoiceData.total
    })
  });
  if (!response.ok) {
    const error = await response.text();
    throw new Error(error || `HTTP ${response.status}`);
  }
  return await response.json();
}

function parseDateSpanish(dateStr) {
  const parts = dateStr.split('/');
  if (parts.length === 3) {
    return `${parts[2]}-${parts[1]}-${parts[0]}`;
  }
  return dateStr;
}

function transformLineItems(lineItems) {
  return lineItems.map(item => ({
    description: item.unit || item.description || '',
    quantity: parseFloat(item.quantity || item.amount || 0),
    unit_price: parseFloat(item.unitPrice || item.unit_price || 0),
    total: parseFloat(item.total || 0)
  })).filter(item => item.description);
}

export async function saveInvoiceToSupabase(invoiceData) {
  console.log('>>> saveInvoiceToSupabase sending:', invoiceData);
  
  const response = await fetch(`${API_BASE}/supabase/invoices`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      invoice_number: invoiceData.invoiceNumber,
      vendor: invoiceData.vendor,
      invoice_date: parseDateSpanish(invoiceData.invoiceDate),
      nif: invoiceData.nif || null,
      total: invoiceData.total,
      line_items: transformLineItems(invoiceData.lineItems || [])
    })
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(error || `HTTP ${response.status}`);
  }

  return await response.json();
}

export async function getInvoicesFromSupabase() {
  console.log('>>> getInvoicesFromSupabase');
  
  const response = await fetch(`${API_BASE}/supabase/invoices`);

  if (!response.ok) {
    const error = await response.text();
    throw new Error(error || `HTTP ${response.status}`);
  }

  return await response.json();
}

export async function getInvoiceById(id) {
  console.log('>>> getInvoiceById:', id);
  
  const response = await fetch(`${API_BASE}/supabase/invoices/${id}`);

  if (!response.ok) {
    const error = await response.text();
    throw new Error(error || `HTTP ${response.status}`);
  }

  return await response.json();
}